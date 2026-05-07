from Classes import Quadcopter, DroneViewer, PS5Controller
from Comms_Plugins import CRTP_logger
import PySimpleGUI as sg
import functions, threading, time, sys
from PyQt6.QtWidgets import QApplication
# const errors
pitch_trim = 1.02

# the following runtime will only be run when script is run, NOT when imported
if __name__ == "__main__": 
    # List of all comms plugins (UPDATE WHEN ADDING PLUGIN)
    comms_options =["Crazyradio",]
    controller_exists: bool = False

    quad = None 
    sg.theme('GrayGrayGray') # set theme for window

    defaults = functions.load_settings("init_defaults.txt")

    # layout for initialisation window
    layout = [
        [
            [sg.Text("Enter your quadcopter ID:", size=(35,1), justification='Right'),
            sg.Input(default_text=defaults.get("ID"),size=(25,1),key = "-QUADID-")],
            [sg.Text("Select supported communications system:", size=(35,1), justification='Right'),
            sg.OptionMenu(default_value= defaults.get("comms"),size =(20,2), values=comms_options, key = "-COMMS-")],
            [sg.Push(), sg.Button("Save as defaults", key = "-SAVE-"), sg.Button("Enter", key = "-ENTER-")],
        ]
    ]

    window = sg.Window("Quadcopter GUI", layout, element_padding= (4,5) )

    # -- GUI LOOP --
    while True:
        # run the initialisation window once
        event, values = window.read()

        # if window is closed skip GUI loop
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            sys.exit(0)
            break

        # when ENTER button is pressed, instantiate a quadcopter object with the set values
        if event == "-ENTER-":
            quad = Quadcopter(ID = values["-QUADID-"].strip(), comms = values["-COMMS-"], controller = controller if controller_exists else None)
            print("%s was selected as comms system for %s" % (quad.comms, quad.ID))
            break
        elif event == "-SAVE-": 
                # when save as defaults button is pressed, save the entered parameters in a .txt file
                functions.save_settings("init_defaults.txt", {
                    "ID":values["-QUADID-"].strip(),
                    "comms":values["-COMMS-"].strip()
                })

    window.close()

    # -- CONTROL --
        # instantiate controller if possible, otherwise move forward
    try:
        controller = PS5Controller()
        controller_exists = True
    except RuntimeError as e:
        print(f"{e}, proceeding without")

    # quadcopter control loop
    def control_loop(quad):
        # initialise smoothed thrust once
        quad._thrust_smoothed = 0

        alpha = 0.1  # smoothing factor

        while True:
            if controller_exists:
                # read controller inputs
                lx, ly, rx, ry, square = quad.controller.read() # controller read
                hover_pressed = square  # hover mode enabled with holding square

                if hover_pressed:
                    # hover mode
                    roll, pitch, yaw_rate, thrust_raw = functions.hover_logic()
                else:
                    # manual mode
                    roll, pitch, yaw_rate, thrust_raw = functions.joystick_to_setpoint(lx, ly, rx, ry)

                # thrust is smoothed for safety
                quad._thrust_smoothed = ((1 - alpha) * quad._thrust_smoothed +alpha * thrust_raw)
                thrust = int(quad._thrust_smoothed)
                
                # corrected for error in attitude estimation
                pitch -= pitch_trim

                # update quadcopter object control inputs with inputs from controller
                quad.update_controls(
                    roll=roll,
                    pitch=pitch,
                    yaw_rate=yaw_rate,
                    thrust=thrust
                )

            time.sleep(0.03)  # ~30 Hz

    # run control loop in separate thread
    threading.Thread(target=control_loop, args=(quad,), daemon=True).start()

    # -- LOGGING --
    # instantiate comms based on selected system
    comms = None
    
    # instantiate crazyradio comms
    if (quad.comms == "Crazyradio"):
        comms = CRTP_logger(quad)
        comms.start()
        print("Started Crazyradio logging for test")

    # instantiate client window
    app = QApplication(sys.argv)
    viewer = DroneViewer(quad)    
    viewer.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Shutting down")
        if comms:
            comms.stop()







