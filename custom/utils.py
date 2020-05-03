import shlex
import platform
import subprocess
from enum import Enum, auto


POSSIBLE_BROWSERS = ('brave',
                     'vivaldi',
                     'google-chrome',
                     'firefox',
                     )


class OS(Enum):
    Ubuntu = auto()
    Manjaro = auto()
    Other = auto()


def determine_os():
    try:
        lsb_info = subprocess.check_output(shlex.split('lsb_release -d'))
        lsb_info = str(lsb_info).lower()
    except subprocess.CalledProcessError:
        lsb_info = ''

    is_debian = 'debian' in lsb_info or 'ubuntu' in lsb_info
    is_arch = 'arch' in lsb_info or 'manjaro' in lsb_info

    if is_debian:
        return OS.Ubuntu
    elif is_arch:
        return OS.Manjaro

    platform_description = platform.platform().lower()

    is_debian = 'debian' in platform_description or 'ubuntu' in platform_description
    is_arch = 'arch' in platform_description or 'manjaro' in platform_description

    if is_debian:
        return OS.Ubuntu
    elif is_arch:
        return OS.Manjaro
    else:
        return OS.Other


def _which_browser(browser):
    try:
        return subprocess.check_output(shlex.split(f'which {browser}')).strip().decode()
    except subprocess.CalledProcessError:
        return None


def determine_browser():
    for browser in POSSIBLE_BROWSERS:
        exe_path = _which_browser(browser)
        if exe_path:
            return exe_path
    return 'firefox'


def mount_exists(mount_point):
    cmd = f'df -h | tail -n +2 | grep -w "{mount_point}"'
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(cmd_str):
    cmd = shlex.split(cmd_str)
    return subprocess.Popen(cmd, shell=False)
