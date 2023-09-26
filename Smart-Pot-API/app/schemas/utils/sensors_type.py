from enum import Enum


class SensorType(str, Enum):
    humidity = "hum"
    lux = "lux"
    temperature = "temp"
