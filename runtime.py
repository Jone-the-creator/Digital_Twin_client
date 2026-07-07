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
LOOP_RATE = 500 # control loop rate in Hz
dt = 1/LOOP_RATE # dt based on loop rate (in seconds)

    # ---- CONTROL LOOP ----
def control_loop(quad, stab):

    quad._thrust_smoothed = 0
    alpha = 0.1
    count = 0
    thrust_raw = 0
    u = np.zeros((4,1))

    while running:
        if quad.controller:
            try:
                lx, ly, lt, rx, ry, rt, cross, circle, square, triangle = quad.controller.read()

                # kill switch
                if square: 
                    quad.killed = True
                    print("KILL SWITCH PRESSED")

#                roll, pitch, yaw_rate, thrust_raw = \
#                    functions.joystick_to_setpoint(lx, ly, lt, rx, ry, rt)

                # test flight mode
                if triangle:
                    quad.test_flight = True
                

                # cancel test flight if kill switch pressed or circle pressed (circle allows restarting, kill switch requires reboot)
                if quad.killed is True or circle: 
                    quad.test_flight = False
                
                # slowly increase thrust (50 counts is ~1s)

                if not hasattr(quad, "recording_active"):
                    quad.recording_active = False

                if quad.test_flight is True:

                    if not quad.recording_active:
                        quad.viewer.start_record_signal.emit()
                        print("START RECORDING THREAD")
                        quad.recording_active = True
                        stab.zero()
                    if count <= 1.5*LOOP_RATE:
                        u = stab.hover(0.5,dt)
                    elif count <= 3.5*LOOP_RATE:
                        u = stab.hover(0.8,dt)
                    elif count <= 5*LOOP_RATE:
                        u = stab.hover(1.0,dt)
                    elif count <= 5*LOOP_RATE:
                        u = stab.hover(0.5,dt)
                    else:
                        u = np.zeros((4,1))
                        quad.test_flight = False
                        count = 0
                        stab.reset()
                        if quad.recording_active:
                            quad.viewer.stop_record_signal.emit()
                            quad.recording_active = False
                else:
                    u = np.zeros((4,1))
                    count = 0
                    stab.reset()
                    if quad.recording_active:
                            quad.viewer.stop_record_signal.emit()
                            quad.recording_active = False

                # # smooth the thrust
                quad._thrust_smoothed = (
                    (1 - alpha) * quad._thrust_smoothed + alpha * u[3,0]
                )
                thrust = int(quad._thrust_smoothed)                            
                
                # update control values in quadcopter object, these are read to send controls to quadcopter
                quad.update_controls(
                    yaw_rate = u[0,0],
                    pitch = u[1,0],
                    roll = u[2,0],
                    thrust = thrust
                )

            except Exception as e:
                print(f"Controller error: {e}")

        if quad.test_flight:
            count += 1
            print(f"slept time = {count/500}")
        QThread.msleep(int(1000/LOOP_RATE))  # causes the loop rate NEED TO UPDATE LOOP TIMING

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


