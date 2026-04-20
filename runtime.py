from Classes import Quadcopter, AdapterManager, UsbTransport, ProtocolAdapter
from Comms_Plugins.CRTP import CRTP

if __name__ == "__main__":
    quad = Quadcopter("quad_001")
    comms = CRTP(quad)

    print("Runtime started. Press Ctrl+C to stop.")

    comms.start()