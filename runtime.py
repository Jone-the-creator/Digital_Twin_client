from Classes import PS5Controller
from Comms_Plugins import CRTP_logger
import functions, threading, time, sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, pyqtSignal
import pygame
from GUI.setup import run_setup
from GUI.viewer import DroneViewer

running = True
viewer_exists = False

    # ---- CONTROL LOOP ----
def control_loop(quad):

    quad._thrust_smoothed = 0
    alpha = 0.1
    count = 0
    thrust_raw = 0

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
                        quad.recording_active = True
                    if count <= 75:
                        thrust_raw = 7500
                    elif count <= 150:
                        thrust_raw = 30000
                    elif count <= 250:
                        thrust_raw = 40000
                    else:
                        quad.test_flight = False
                        thrust_raw = 0
                        count = 0
                        if quad.recording_active:
                            quad.viewer.stop_record_signal.emit()
                            quad.recording_active = False
                else:
                    thrust_raw = 0
                    count = 0
                    if quad.recording_active:
                            quad.viewer.stop_record_signal.emit()
                            quad.recording_active = False

                # smooth the thrust
                quad._thrust_smoothed = (
                    (1 - alpha) * quad._thrust_smoothed + alpha * thrust_raw
                )
                thrust = int(quad._thrust_smoothed)

                # reset attitude when drone stops
#                if thrust <= 10000:
#                    pitch = 0
#                    roll = 0

                # update control values in quadcopter object, these are read to send controls to quadcopter
                quad.update_controls(
                    roll=0,
                    pitch=0,
                    yaw_rate=0,
                    thrust=thrust
                )

            except Exception as e:
                print(f"Controller error: {e}")

        if quad.test_flight:
            count += 1
            print(f"count = {count}, thrust = {thrust_raw}")
        time.sleep(0.02)  # faster, smoother (~50 Hz)

def main():
    # ---- QUADCOPTER INSTANTIATE/SETUP ----
    quad = run_setup()

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
    threading.Thread(target=control_loop, args=(quad,)).start()

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


