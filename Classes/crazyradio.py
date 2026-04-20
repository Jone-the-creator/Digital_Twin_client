from .protocol_adapter import ProtocolAdapter


class CrazyradioUsbAdapter(ProtocolAdapter):
    """Placeholder adapter for testing auto-detection.

    This adapter treats the integer value 0x1000 as its detection token.
    """

    @classmethod
    def detect(cls, data: bytes) -> bool:
        try:
            return data == 0x1000
        except Exception:
            return False

    def feed(self, data: bytes):
        # simple behavior for testing: update the quad's x position
        try:
            if isinstance(data, int):
                self.quadcopter.update_position(x=float(data & 0xFF))
        except Exception:
            pass
