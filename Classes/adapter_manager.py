class AdapterManager:
# manages protocol detection and routes incoming bytes to the appropriate Protocol Adapter
    def __init__(self, Quadcopter):
        self.Quadcopter = Quadcopter
        self._adapter_classes = []
        self._active_adapter = None

    # registers a protocol adapter subclass
    def register_adapter(self, adapter_cls):
        self._adapter_classes.append(adapter_cls)

    # checks if data matches any of the registered classes, makes it active if found
    def _detect_and_create_adapter(self, data:bytes):
        for adapter_cls in self._adapter_classes:
            if adapter_cls.detect(data):
                self._active_adapter = adapter_cls(self.Quadcopter)
                self._active_adapter.feed(data)
                return
            
        raise ValueError("No protocol adapter found.")

    # when data is received, either feeds this data to the active adapter or detects and creates one
    def feed(self, data: bytes):
        if self._active_adapter is None:
            self._detect_and_create_adapter(data)
        else:
            self._active_adapter.feed(data)