from Classes.quadcopter import Quadcopter
from Classes.adapter_manager import AdapterManager
from Classes.crazyradio import CrazyradioUsbAdapter
from Classes.transport_classes import UsbTransport

def main():
    quad = Quadcopter("quad_001")

    manager = AdapterManager(quad)
    manager.register_adapter(CrazyradioUsbAdapter)

    transport = UsbTransport()

    print("Runtime started. Press Ctrl+C to stop.")

    while True:
        data = transport.read()
        if data:
            manager.feed(data)

if __name__ == "__main__":
    main()