from enum import Enum


class DeviceNames(str, Enum):
    NODEMCU: str = "NODEMCU"
    ESP: str = "ESP"
