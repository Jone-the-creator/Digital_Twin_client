from Classes import Quadcopter
from Comms_Plugins.Crazyradio import CRTP_logger
import PySimpleGUI as sg
import os.path


# the following runtime will only be run when script is run, NOT when imported
if __name__ == "__main__": 
    layout = [
        [
            [sg.Text("Enter your quadcopter ID:"),
            sg.Input(default_text="quad_001",size=(25,1),key = "-QUADID-")],
            [sg.Button("Enter", key = '-ENTERID-')],
        ]
    ]

    window = sg.Window("Quadcopter GUI", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == "-ENTERID-":
            quad = Quadcopter(values["-QUADID-"])
            print(quad.ID)
            break
#    quad = Quadcopter("quad_001")
    
    #comms plugin will be selected here based on selection in GUI
 #   if 1:
 #       comms = CRTP_logger(quad)

#    print("Runtime started. Press Ctrl+C to stop.")

#    comms.start()
    window.close()