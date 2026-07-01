import json

class IPCManager:
    def __init__(self):
        self.channels = {}

    def publish(self, channel, message):
        if channel not in self.channels:
            self.channels[channel] = []
        self.channels[channel].append(message)
        print(f"[IPC] Broadcast to channel '{channel}': {message}")
        return True

    def read_channel(self, channel):
        return self.channels.get(channel, [])

class RPCServer:
    def __init__(self):
        self.registry = {}

    def register_method(self, name, func):
        self.registry[name] = func
        return True

    def call(self, method_name, *args, **kwargs):
        if method_name not in self.registry:
            raise AttributeError(f"Method '{method_name}' not registered on RPCServer.")
        return self.registry[method_name](*args, **kwargs)
