from enum import Enum


class DeviceType(Enum):
    SWITCH = 0
    LIGHT = 1
    TEMPERATURE = 2
    BINARY_INPUT = 3
    BIT = 4
    INTEGER = 5


class InelsCentralUnit:
    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.host = host
        self.port = port


class InelsDeviceValue:
    def __init__(self, inelsName, inelsId, entity):
        self.inelsName = inelsName
        self.inelsId = inelsId
        self.entity = entity
        self.state = ""
        self.brightness = ""


class InelsDevice:
    def __init__(self, deviceName: str, deviceId: str, deviceType: DeviceType):
        self.deviceName = deviceName
        self.deviceId = deviceId
        self.deviceType = deviceType
