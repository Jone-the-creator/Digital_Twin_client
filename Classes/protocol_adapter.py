from abc import ABC, abstractmethod

class ProtocolAdapter(ABC):
#    base class for all protocol adapters.
#    a ProtocolAdapter translates raw bytes from a transport into normalized updates applied to a Quadcopter object.

    def __init__(self, quadcopter):
        self.quadcopter = quadcopter

    @classmethod
    @abstractmethod
    def detect(cls, data: bytes) -> bool: # used to check if data matches protocol
#        return TRUE if the given data matches this protocol.
#        used during auto-detection before an adapter is instantiated.     
        pass


    @abstractmethod
    def feed(self, data: bytes):
#        feed raw bytes into the protocol parser.
#        may update the quadcopter zero or more times.
        pass
