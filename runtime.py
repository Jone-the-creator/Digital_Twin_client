# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot
# runtime.py
# -- collates all objects and functions to run the digital twin program --

from Classes import PS5Controller
from Controllers.PID_stabiliser import PIDstabiliser
from Comms_Plugins import CRTP_logger
import functions, threading, time, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThread
import pygame
import numpy as np
from GUI.windows.setup_window import run_setup
from GUI.windows.main_window import MainWindow
from Models.state_space_model import Nonlinear_Model
from Controllers.PID_stabiliser import PIDstabiliser
from Controllers.PP_stabiliser import PPstabiliser
from Models.state_observer import Observer

running = True
viewer_exists = False
LOOP_RATE = 300 # control loop rate in Hz
dt = 1/LOOP_RATE # dt based on loop rate (in seconds)

# -- FUNCTION TO UPDATE THE ACTIVE PLANT --
def update_active(obs, quad, sim, u, altitude, dt):
    quad.update_controls(
            yaw_rate = u[0,0],
            pitch = u[1,0],
            roll = u[2,0],
            thrust = u[3,0],
            z = altitude
        )
    obs.update(np.array([
            [np.deg2rad(u[2,0])], # roll rate
            [-np.deg2rad(u[1,0])], # pitch rate
            [-np.deg2rad(u[0,0])], # yaw rate
            [u[3,0]]]), # thrust
            dt
        )
    if quad.simulation_mode:
        sim.update(np.array([
            [np.deg2rad(u[2,0])], # roll rate
            [-np.deg2rad(u[1,0])], # pitch rate
            [-np.deg2rad(u[0,0])], # yaw rate
            [u[3,0]]]), # thrust
            dt
        )


    # ---- CONTROL LOOP ----
def control_loop(obs, quad, PID, sim, PP):
    # -- CONTROL VARIABLES --
    quad._thrust_smoothed = 0
    alpha = 0.1
    count = 0
    eff_count = 0
    u = np.zeros((4,1))
    att_u = np.zeros((3,1))
    thrust_raw = 0
    altitude = 0.0
    target_altitude = 0.0
    

    while running:
        start_time = time.time()
        if quad.controller:
            try:
                lx, ly, lt, l1, rx, ry, rt, r1, cross, circle, square, triangle = quad.controller.read()

            except Exception as e:
                print(f"Controller error: {e}")
            # --- ACTIVATE KILL SWITCH --- (requires reboot to restart)
            if square: 
                quad.killed = True
                print("KILL SWITCH PRESSED")
            
            # --- MANUAL CONTROL MODE ---
            # Arm with R1 (bumper), only works if kill switch not pressed and test flight not happening
            if r1 and not quad.killed and not quad.test_flight and eff_count % 2 == 0:
                roll, pitch, yaw_rate, altitude = \
                functions.joystick_to_setpoint(lx, ly, lt, rx, ry, rt, loop_time)   
                PID.pitch_setpoint = -pitch
                PID.roll_setpoint = roll
                u[0,0] = yaw_rate
                if quad.control_system == "PID":
                    PID.pitch_setpoint = -pitch
                    PID.roll_setpoint = roll
                    u[1,0], u[2,0], thrust_raw = PID.hover(altitude)
                elif quad.control_system == "Pole-placement":
                    PP.pitch_setpoint = -pitch
                    PP.roll_setpoint = roll
                    PP.yaw_setpoint = yaw_rate
                    att_u = PP.attitude_control()
                    u = np.vstack([att_u, np.zeros((1,1))])
                    thrust_raw = PP.altitude_control(altitude, dt)

            # Cancel test flight if circle pressed
            elif circle: 
                    quad.test_flight = False
                    PID.reset()
                    if quad.recording_active:
                        quad.viewer.stop_record_signal.emit()
                        quad.recording_active = False
                    target_altitude = 0.0

            
            # Start test flight with triangle, only works if kill switch not pressed and manual mode not armed
            elif triangle and not quad.killed and eff_count % 2 == 0:
                quad.test_flight = True

            # Reset altitude and thrust when r1 cross is pressed
            elif cross and eff_count % 4 == 0:
                thrust_raw = 0
                functions.joystick_to_setpoint.altitude = 0.0
                PID.reset()
                u = np.zeros((4,1))
                PID.zero() # Zeros the trim in the quadcopter object
            elif not quad.test_flight and eff_count % 10 == 0:
                thrust_raw = 0
                altitude = 0.0
                functions.joystick_to_setpoint.altitude = 0.0
                PID.reset()
                u = np.zeros((4,1))

            # --- TEST FLIGHT MODE (AUTOMATIC) ---
            if quad.test_flight is True:
                if count == 0:
                    target_altitude = 0.0     
                    PID.zero() # Zeros the setpoints
                flight_time = count * dt

                # -- TEST FLIGHT SEQUENCE --
                if flight_time < 2:
                    target_altitude = 0.25 * flight_time # slowly increase to 0.5

                elif flight_time < 6:
                    target_altitude = 0.5 # hold at altitude for 4 seconds

                elif flight_time < 8:
                    # Only start a recording thread if one hasn't started
                    if not quad.recording_active:
                        # Start Recording thread
                        quad.viewer.start_record_signal.emit()
                        quad.recording_active = True
                    target_altitude += 0.25 * dt # slowly increase to 1m

                elif flight_time < 16:
                    target_altitude = 1.0 # hold at altitude for 8 seconds   
                    
                elif flight_time < 20:
                    target_altitude -= 0.25 * dt # slowly decrease to 0m
                    if target_altitude < 0.5: # stop recording at 0.5m
                        if quad.recording_active:
                            quad.viewer.stop_record_signal.emit()
                            quad.recording_active = False

                else:
                    quad.test_flight = False
                    PID.reset()
                    target_altitude = 0.0
                    # stop recording if still recording
                    if quad.recording_active:
                        quad.viewer.stop_record_signal.emit()
                        quad.recording_active = False

                u[1,0], u[2,0], thrust_raw = PID.hover(target_altitude)

            elif not r1:
                # If no test flight started reset stabiliser and disable recording
                PID.reset()
                if quad.recording_active:
                        quad.viewer.stop_record_signal.emit()
                        quad.recording_active = False
                count = 0

            # # Smooth the thrust using an 'alpha' value
            quad._thrust_smoothed = (
                (1 - alpha) * quad._thrust_smoothed + alpha * thrust_raw
            )
            u[3,0] = np.clip(int(quad._thrust_smoothed), 0.0, quad.max_thrust)                         
            
            # update control values in quadcopter object, these are read to send controls to quadcopter
            if quad.test_flight:
                update_active(obs, quad, sim, u, target_altitude, dt)
            else:
                update_active(obs, quad, sim, u, altitude, dt)
                

        if quad.test_flight:
            count += 1

        # --- KILL SWITCH EFFECT ---
        if quad.killed: 
            u = np.zeros((4,1))

        # --- CONTROL LOOP TIMING ---
        loop_time = time.time() - start_time
        while(loop_time < dt):
            time.sleep(0.00001)
            loop_time = time.time() - start_time

        if eff_count % (LOOP_RATE/2) == 0:
            quad.dt = loop_time
            quad.loop_rate = 1/loop_time # save loop rate for client every 0.5s

        eff_count += 1

def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # ---- QUADCOPTER/STABILISER INSTANTIATE/SETUP ----
    quad = run_setup()
    obs = Observer(quad)
    sim = Nonlinear_Model(quad)
    PID = PIDstabiliser(quad)
    PP = PPstabiliser(obs)

    if quad is None:
        print("User cancelled startup.")
        sys.exit(0)
    try:
        controller = PS5Controller()
    except RuntimeError as e:
        print(f"{e}, proceeding without")
        controller = None
    quad.controller = controller
    
    print("Quad ready:", quad)

    # Run as a separate thread (CHANGE TO asynchIO in the future)
    threading.Thread(target=control_loop, args=(obs,quad,PID,sim,PP)).start()

    # ---- COMMS ----
    comms = None
    if quad.comms == "Crazyradio":
        comms = CRTP_logger(quad)
        comms.start()
        print("Started Crazyradio logging")

    # ---- QT VIEWER ----
    # app = QApplication(sys.argv)

    def pump_pygame():
        pygame.event.pump()

    timer = QTimer()
    timer.timeout.connect(pump_pygame)
    timer.start(10)  # 100 Hz

    if quad.control_system == "PID":
        quad.viewer = MainWindow(quad, PID)
    elif quad.control_system == "Pole-placement":
        quad.viewer = MainWindow(quad, PP)

    # Explicit shutdown function
    def shutdown():
        global running
        print("Shutting down...")
        running = False

        if comms:
            comms.stop()

        time.sleep(0.2)

    app.aboutToQuit.connect(shutdown)

    quad.viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

