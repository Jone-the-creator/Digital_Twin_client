from Classes import Quadcopter, DroneViewer, PS5Controller
from Comms_Plugins import CRTP_logger
import functions, threading, time, sys
from PyQt6.QtWidgets import QApplication

pitch_trim = 1.02
running = True


if __name__ == "__main__":

    # ---- LOAD DEFAULTS (NO GUI) ----
    defaults = functions.load_settings("init_defaults.txt")

    quad_id = defaults.get("ID", "cf1")
    comms_type = defaults.get("comms", "Crazyradio")

    print(f"Starting with ID={quad_id}, comms={comms_type}")

    # ---- INIT CONTROLLER FIRST ----
    controller = None
    try:
        controller = PS5Controller()
        print("Controller connected (pygame active)")
    except RuntimeError as e:
        print(f"{e}, proceeding without controller")

    # ---- CREATE QUAD ----
    quad = Quadcopter(
        ID=quad_id,
        comms=comms_type,
        controller=controller
    )

    # ---- CONTROL LOOP ----
    def control_loop(quad):
        global running

        quad._thrust_smoothed = 0
        alpha = 0.1

        while running:
            if quad.controller:
                try:
                    lx, ly, lt, rx, ry, rt, square = quad.controller.read()

                    roll, pitch, yaw_rate, thrust_raw = \
                        functions.joystick_to_setpoint(lx, ly, rx, ry)

                    quad._thrust_smoothed = (
                        (1 - alpha) * quad._thrust_smoothed + alpha * thrust_raw
                    )

                    thrust = int(quad._thrust_smoothed)
                    pitch -= pitch_trim

                    quad.update_controls(
                        roll=roll,
                        pitch=pitch,
                        yaw_rate=yaw_rate,
                        thrust=thrust
                    )

                    # ✅ SEND COMMANDS (if implemented)
                    if hasattr(quad, "send_setpoint"):
                        quad.send_setpoint(roll, pitch, yaw_rate, thrust)

                except Exception as e:
                    print(f"Controller error: {e}")

            time.sleep(0.02)  # faster, smoother (~50 Hz)

    threading.Thread(target=control_loop, args=(quad,), daemon=True).start()

    # ---- COMMS ----
    comms = None
    if quad.comms == "Crazyradio":
        comms = CRTP_logger(quad)
        comms.start()
        print("Started Crazyradio logging")

    # ---- QT VIEWER ----
    app = QApplication(sys.argv)
    viewer = DroneViewer(quad)

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
