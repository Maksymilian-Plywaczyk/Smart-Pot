from enum import Enum


class Tag(str, Enum):
    USERS = "Users"
    LOGIN = "Login"
    PLANTS = "Plants"
    DEVICES = "Devices"
    HEALTHCHECK = "Healthcheck"
