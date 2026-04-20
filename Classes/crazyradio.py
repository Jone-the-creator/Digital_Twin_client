#OBSELETE Crazyradio adapter, use connect_log_param instead

from .protocol_adapter import ProtocolAdapter


class CrazyradioUsbAdapter(ProtocolAdapter):

    @classmethod
    def detect(cls, data: bytes) -> bool:
        # checks that received data is both in bytes and is longer than 1 byte
        return isinstance(data, (bytes, bytearray)) and len(data) >= 1

    def __init__(self, quadcopter):
        super().__init__(quadcopter)
        self.packet_count = 0

    def feed(self, data: bytes):
        if not data:
            return
        
        status = data[0]
        payload = data[1:]
        self.packet_count += 1

        if status != 0x00:
            # transmission failed
            return
        
        if not payload:
            # valid ACK, no payload transmitted
            return
        
        self._handle_radio_payload(payload)

    def _handle_radio_payload(self, payload: bytes):

        # PLACEHOLDER FOR ENCODING

        pass
