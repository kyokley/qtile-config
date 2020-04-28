import platform
import subprocess
from enum import Enum, auto


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


def mount_exists(mount_point):
    cmd = f'df -h | tail -n +2 | grep -w "{mount_point}"'
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False
