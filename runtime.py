from Classes import Quadcopter, PS5Controller
from Comms_Plugins import CRTP_logger
import functions, threading, time, sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import pygame
from GUI.setup import run_setup
from GUI.viewer import DroneViewer

# trims offset attitude controls
pitch_trim = 1.02
roll_trim = 0
running = True

    # ---- CONTROL LOOP ----
def control_loop(quad):
    global running

    quad._thrust_smoothed = 0
    alpha = 0.1

    while running:
        if quad.controller:
            try:
                # kill switch
                if square:
                    quad.update_controls(
                        roll=0,
                        pitch=0,
                        yaw_rate=0,
                        thrust=0
                    )
                    disabled = True

                elif not disabled:

                    lx, ly, lt, rx, ry, rt, square = quad.controller.read()

                    roll, pitch, yaw_rate, thrust_raw = \
                        functions.joystick_to_setpoint(lx, ly, lt, rx, ry, rt)

                    quad._thrust_smoothed = (
                        (1 - alpha) * quad._thrust_smoothed + alpha * thrust_raw
                    )

                    thrust = int(quad._thrust_smoothed)
                    pitch -= pitch_trim
                    roll -= roll_trim

                    # reset attitude when drone stops
                    if thrust <= 10000:
                        pitch = 0
                        roll = 0

                    # update control values in quadcopter object, these are read to send controls to quadcopter
                    quad.update_controls(
                        roll=roll,
                        pitch=pitch,
                        yaw_rate=yaw_rate,
                        thrust=thrust
                    )
                elif disabled:
                    print("Kill switch activated")
                    break

            except Exception as e:
                print(f"Controller error: {e}")

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
    threading.Thread(target=control_loop, args=(quad,), daemon=True).start()

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

    viewer = DroneViewer(quad)

    # Explicit shutdown function
    def shutdown():
        global running
        print("Shutting down...")
        running = False

        if comms:
            comms.stop()

        time.sleep(0.2)

    app.aboutToQuit.connect(shutdown)

    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


