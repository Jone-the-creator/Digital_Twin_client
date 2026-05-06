from Classes import Quadcopter, DroneViewer, PS5Controller
from Comms_Plugins import CRTP_logger
import PySimpleGUI as sg
import functions
import time
import sys
from PyQt6.QtWidgets import QApplication


# the following runtime will only be run when script is run, NOT when imported
if __name__ == "__main__": 
    # List of all comms plugins (UPDATE WHEN ADDING PLUGIN)
    comms_options =["Crazyradio", "TEST"]
    controller_exists: bool = True

    # instantiate controller if possible, otherwise move forward
    try:
        controller = PS5Controller()
    except RuntimeError as e:
        print(f"{e}, proceeding without")
        controller_exists = False

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

    # -- LOGGING --
    # instantiate comms based on selected system
    comms = None
    
    # instantiate crazyradio comms
    if (quad.comms == "Crazyradio"):
        comms = CRTP_logger(quad)
        comms.start()
        print("Started Crazyradio logging for test")

    app = QApplication(sys.argv)
    viewer = DroneViewer(quad)    
    viewer.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Shutting down")
        if comms:
            comms.stop()





