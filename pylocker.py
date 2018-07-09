#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Most of what is below has been taken from a gist by Airblader
# https://gist.github.com/Airblader/3a96a407e16dae155744

import subprocess # nosec
import shlex
import xcffib
import random
import threading
import time
import os
import sys

from xcffib.xproto import *
from PIL import Image

XCB_MAP_STATE_VIEWABLE = 2
SCREEN_SLEEP = 10 # in minutes
DPMS_CHECK = 10 # in seconds

FILE_LOCK_PATH = '/tmp/pylock.pid'

class Color(object):
    BLANK = '#00000000'  # blank
    CLEARISH = '#ffffff22'  # clear ish
    DEFAULT = '#ff00ffcc'  # default
    TEXT = '#ee00eeee'  # text
    WRONG = '#880000bb'  # wrong
    VERIFYING = '#bb00bbbb'  # verifying

def screenshot():
    args = shlex.split('import -window root /tmp/.i3lock.png') # nosec
    subprocess.run(args)

def xcb_fetch_windows():
    """ Returns an array of rects of currently visible windows. """

    x = xcffib.connect()
    root = x.get_setup().roots[0].root

    rects = []

    # iterate through top-level windows
    for child in x.core.QueryTree(root).reply().children:
        # make sure we only consider windows that are actually visible
        attributes = x.core.GetWindowAttributes(child).reply()
        if attributes.map_state != XCB_MAP_STATE_VIEWABLE:
            continue

        rects += [x.core.GetGeometry(child).reply()]

    return rects

def obscure_image(image):
    """ Obscures the given image. """
    size = image.size
    pixel_size = 8

    if size[0] < pixel_size or size[1] < pixel_size:
        return image

    image = image.resize((int(size[0] / pixel_size), int(size[1] / pixel_size)), Image.NEAREST)
    image = image.resize((int(size[0]), int(size[1])), Image.NEAREST)

    return image

def obscure(rects):
    """ Takes an array of rects to obscure from the screenshot. """
    image = Image.open('/tmp/.i3lock.png') # nosec

    for rect in rects:
        area = (
                rect.x, rect.y,
                rect.x + rect.width,
                rect.y + rect.height
                )

        cropped = image.crop(area)
        cropped = obscure_image(cropped)
        image.paste(cropped, area)

    image.save('/tmp/.i3lock.png') # nosec

def lock_screen(event, blur=False):
    cmd = ['i3lock']

    if blur:
        cmd.extend(['--blur=5'])
    else:
        cmd.extend(['-i', '/tmp/.i3lock.png']) # nosec

    args = shlex.split('''--insidevercolor={clearish}   \
                          --ringvercolor={verifying}     \
                          \
                          --insidewrongcolor={clearish} \
                          --ringwrongcolor={wrong}   \
                          \
                          --insidecolor={blank}      \
                          --ringcolor={default}        \
                          --linecolor={blank}        \
                          --separatorcolor={default}   \
                          \
                          --verifcolor={text}        \
                          --wrongcolor={text}        \
                          --timecolor={text}        \
                          --datecolor={text}        \
                          --layoutcolor={text}      \
                          --keyhlcolor={wrong}       \
                          --bshlcolor={wrong}        \
                          \
                          --clock               \
                          --indicator           \
                          --timestr="%H:%M:%S"  \
                          --datestr="" \
                          --wrongtext="FAIL" \
                          --show-failed-attempts \
                          --nofork
                       '''.format(blank=Color.BLANK,
                                  clearish=Color.CLEARISH,
                                  default=Color.DEFAULT,
                                  text=Color.TEXT,
                                  wrong=Color.WRONG,
                                  verifying=Color.VERIFYING,
                                  ))
    cmd.extend(args)
    subprocess.run(cmd)
    event.set()

def handle_power_settings():
    done_event = threading.Event()

    dpms_thread = threading.Thread(target=_force_screen_off,
                                   args=(done_event,))
    dpms_thread.start()
    return done_event

def _force_screen_off(event):
    count = 0
    while not event.is_set():
        count += 1

        if (count * DPMS_CHECK) % (SCREEN_SLEEP * 60) == 0:
            count = 0
            subprocess.run(shlex.split('xset dpms force off'))
        time.sleep(DPMS_CHECK)

def _create_pid_file():
    if os.path.exists(FILE_LOCK_PATH):
        return False
    else:
        with open(FILE_LOCK_PATH, 'w') as f:
            f.write(str(os.getpid()))

        return True

def main(blur=False):
    got_lock = _create_pid_file()

    if not got_lock:
        print('Could not get file lock! Aborting')
        sys.exit(1)

    if not blur:
        # 1: Take a screenshot.
        screenshot()

        # 2: Get the visible windows.
        rects = xcb_fetch_windows()

        # 3: Process the screenshot.
        obscure(rects)

    # 4: Lock the screen
    event = handle_power_settings()
    lock_screen(event, blur=blur)

    os.remove(FILE_LOCK_PATH)

if __name__ == '__main__':
    main(blur=random.choice([True, False])) # nosec
