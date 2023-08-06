from enum import Enum, unique


@unique
class Package(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
