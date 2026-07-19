from Classes import PS5Controller
from Classes.PID_stabiliser import PIDstabiliser
from Comms_Plugins import CRTP_logger
import functions, threading, time, sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QThread
import pygame
import numpy as np
from GUI.setup import run_setup
from GUI.viewer import DroneViewer

running = True
viewer_exists = False
LOOP_RATE = 300 # control loop rate in Hz
dt = 1/LOOP_RATE # dt based on loop rate (in seconds)

    # ---- CONTROL LOOP ----
def control_loop(quad, stab):

    quad._thrust_smoothed = 0
    alpha = 0.1
    count = 0
    u = np.zeros((4,1))
    thrust_raw = 0

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
            if r1 and not quad.killed and not quad.test_flight:
                roll, pitch, yaw_rate, altitude = \
                functions.joystick_to_setpoint(lx, ly, lt, rx, ry, rt, dt)   
                # print(f"altitude = {altitude}")
                u[0,0] = yaw_rate
                u[1,0] = pitch
                u[2,0] = roll
                thrust_raw = quad.altitude_control(altitude, dt)
                # print(f"thrust = {thrust_raw}")
            

            # --- AUTOMATIC CONTROL MODE ---
            # Start with triangle, only works if kill switch not pressed and manual mode not armed
            elif triangle and not quad.killed:
                quad.test_flight = True

            # Reset altitude and thrust when r1 cross is pressed
            elif cross:
                thrust_raw = 0
                functions.joystick_to_setpoint.altitude = 0.0
                quad.altitude_integral = 0.0
                quad.altitude_derivative = 0.0
                quad.prev_altitude_error = 0.0
                pitch_cmd = 0.0
                roll_cmd = 0.0
            else:
                thrust_raw = 0
                functions.joystick_to_setpoint.altitude = 0.0
                quad.altitude_integral = 0.0
                quad.altitude_derivative = 0.0
                quad.prev_altitude_error = 0.0
                pitch_cmd = 0.0
                roll_cmd = 0.0

            # # Cancel test flight if circle pressed
            # if circle: quad.test_flight = False 

            # # --- TEST FLIGHT PROCESS ---
            # if quad.test_flight is True:
            #     # Only start a recording thread if one hasn't started
            #     if not quad.recording_active:
            #         quad.viewer.start_record_signal.emit()
            #         quad.recording_active = True
            #         stab.zero()
            #     if count <= 0.5*LOOP_RATE:
            #         u = stab.hover(0.2,dt)
            #         thrust_raw = u[3,0]
            #     if count <= 5*LOOP_RATE:
            #         u = stab.hover(0.8,dt)
            #         thrust_raw = u[3,0]
            #     elif count <= 6.5*LOOP_RATE:
            #         u = stab.hover(0.3,dt)
            #         thrust_raw = u[3,0]
            #     else:
            #         # Once completed reset counter and stabiliser
            #         u = np.zeros((4,1))
            #         quad.test_flight = False
            #         count = 0
            #         stab.reset()
            #         if quad.recording_active:
            #             quad.viewer.stop_record_signal.emit()
            #             quad.recording_active = False
            # else:
            #     # If no test flight started reset count and stabiliser
            #     count = 0
            #     stab.reset()
            #     u = np.zeros((4,1))
            #     if quad.recording_active:
            #             quad.viewer.stop_record_signal.emit()
            #             quad.recording_active = False

            # # Smooth the thrust using an 'alpha' value
            quad._thrust_smoothed = (
                (1 - alpha) * quad._thrust_smoothed + alpha * thrust_raw
            )
            thrust = np.clip(int(quad._thrust_smoothed), 0.0, quad.max_thrust)              
            
            if count % 100 == 0:   # once per second
                print(
                    f"thrust={thrust}, "
                    f"r1={r1}, "
                    f"killed={quad.killed}, "
                    f"test={quad.test_flight}"
                    f"z ={quad.position.z}"
                    )              
            
            # update control values in quadcopter object, these are read to send controls to quadcopter
            # print(thrust_raw)
            pitch_cmd, roll_cmd = stab.hover(dt)
            # quad.update_controls(
            #     yaw_rate = u[0,0],
            #     pitch = -pitch_cmd,
            #     roll = roll_cmd,
            #     thrust = thrust
            # )
            quad.update_controls(
                yaw_rate = u[0,0],
                pitch = u[1,0],
                roll = u[2,0],
                thrust = thrust
            )

        # if quad.test_flight:
            count += 1
            # print(f"slept time = {count/500}")

        # --- KILL SWITCH EFFECT ---
        if quad.killed: u = np.zeros((4,1))

        # --- CONTROL LOOP TIMING ---
        loop_time = time.time() - start_time
        while(loop_time < dt):
            time.sleep(0.00001)
            loop_time = time.time() - start_time
        # print(f"actual loop time = {time.time()-start_time}")

def main():
    # ---- QUADCOPTER/STABILISER INSTANTIATE/SETUP ----
    quad = run_setup()
    stab = PIDstabiliser(quad)

    if quad is None:
        print("User cancelled startup.")
        sys.exit(0)

    controller_exists = False
    try:
        controller = PS5Controller()
        controller_exists = True
    except RuntimeError as e:
        print(f"{e}, proceeding without")
        controller = None
    quad.controller = controller
    
    print("Quad ready:", quad)

    # Run as a separate thread (CHANGE TO asynchIO in the future)
    threading.Thread(target=control_loop, args=(quad,stab)).start()

    # ---- COMMS ----
    comms = None
    if quad.comms == "Crazyradio":
        comms = CRTP_logger(quad)
        comms.start()
        print("Started Crazyradio logging")

    # ---- QT VIEWER ----
    app = QApplication(sys.argv)

    def pump_pygame():
        pygame.event.pump()

    timer = QTimer()
    timer.timeout.connect(pump_pygame)
    timer.start(10)  # 100 Hz

    quad.viewer = DroneViewer(quad)

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


