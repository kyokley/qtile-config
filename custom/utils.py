from enum import Enum, auto
import platform


class OS(Enum):
    Ubuntu = auto()
    Manjaro = auto()
    Other = auto()


def determine_os():
    if 'debian' in platform.platform().lower():
        return OS.Ubuntu
    elif 'manjaro' in platform.platform().lower():
        return OS.Manjaro
    else:
        return OS.Other
