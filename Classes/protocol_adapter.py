from abc import ABC, abstractmethod

class ProtocolAdapter(ABC):
    """
    Base class for all protocol adapters.

    A ProtocolAdapter translates raw bytes from a transport
    into normalized updates applied to a Quadcopter object.
    """

    def __init__(self, quadcopter):
        self.quadcopter = quadcopter

    @classmethod
    @abstractmethod
    def detect(cls, data: bytes) -> bool: # used to check if data matches protocol
        
        """
        Return True if the given data matches this protocol.
        Used during auto-detection before an adapter is instantiated.
        """
        pass


    @abstractmethod
    def feed(self, data: bytes):
        
        """
        Feed raw bytes into the protocol parser.
        May update the quadcopter zero or more times.
        """
        pass
