from Classes import Quadcopter
from Comms_Plugins.Crazyradio import CRTP_logger

# the following runtime will only be run when script is run, NOT when imported
if __name__ == "__main__": 
    quad = Quadcopter("quad_001")
    
    #comms plugin will be selected here based on selection in GUI
    if 1:
        comms = CRTP_logger(quad)

    print("Runtime started. Press Ctrl+C to stop.")

    comms.start()