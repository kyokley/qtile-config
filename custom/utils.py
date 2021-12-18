import shlex
import platform
import subprocess
from enum import Enum, auto


POSSIBLE_BROWSERS = ('brave',
                     'brave-browser',
                     'vivaldi',
                     'google-chrome',
                     'firefox',
                     )


class OS(Enum):
    Debian = auto()
    Ubuntu = auto()
    Manjaro = auto()
    Garuda = auto()
    Arch = auto()
    Other = auto()


def determine_os():
    try:
        lsb_info = subprocess.check_output(shlex.split('lsb_release -d'))
        lsb_info = str(lsb_info).lower()
    except subprocess.CalledProcessError:
        lsb_info = ''

    if 'debian' in lsb_info:
        return OS.Debian
    elif 'ubuntu' in lsb_info:
        return OS.Ubuntu
    elif 'arch' in lsb_info:
        return OS.Arch
    elif 'manjaro' in lsb_info:
        return OS.Manjaro
    elif 'garuda' in lsb_info:
        return OS.Garuda

    platform_description = platform.platform().lower()

    if 'debian' in platform_description:
        return OS.Debian
    elif 'ubuntu' in platform_description:
        return OS.Ubuntu
    elif 'arch' in platform_description:
        return OS.Arch
    elif 'manjaro' in platform_description:
        return OS.Manjaro
    elif 'garuda' in platform_description:
        return OS.Garuda
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


def run_command(cmd_str, raise_called_process_exception=True):
    cmd = shlex.split(cmd_str)

    if raise_called_process_exception:
        return subprocess.Popen(cmd, shell=False)
    else:
        try:
            return subprocess.Popen(cmd, shell=False)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None


def start_ssh_agent():
    cmd = "ssh-add -l; [ $? == 2 ] && eval $(ssh-agent)"

    try:
        return subprocess.Popen(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(str(e))
