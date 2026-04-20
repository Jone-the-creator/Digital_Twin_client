from Classes.quadcopter import Quadcopter
from Classes.adapter_manager import AdapterManager
from Classes.crazyradio import CrazyradioUsbAdapter

def main():
    quad = Quadcopter("quad_001")

    manager = AdapterManager(quad)
    manager.register_adapter(CrazyradioUsbAdapter)

#    transport = UsbTransport() PLACEHOLDER

    print("Runtime started. Press Ctrl+C to stop.")

    while True:
        data = 0x1000
#        data = transport.read() PLACEHOLDER
        if data:
            manager.feed(data)

if __name__ == "__main__":
    main()