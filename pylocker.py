#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Most of what is below has been taken from a gist by Airblader
# https://gist.github.com/Airblader/3a96a407e16dae155744

import os
import xcffib
from xcffib.xproto import *
from PIL import Image

XCB_MAP_STATE_VIEWABLE = 2

class Color(object):
    BLANK = '#00000000'  # blank
    CLEARISH = '#ffffff22'  # clear ish
    DEFAULT = '#ff00ffcc'  # default
    TEXT = '#ee00eeee'  # text
    WRONG = '#880000bb'  # wrong
    VERIFYING = '#bb00bbbb'  # verifying

def screenshot():
    os.system('import -window root /tmp/.i3lock.png')

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
    image = Image.open('/tmp/.i3lock.png')

    for rect in rects:
        area = (
                rect.x, rect.y,
                rect.x + rect.width,
                rect.y + rect.height
                )

        cropped = image.crop(area)
        cropped = obscure_image(cropped)
        image.paste(cropped, area)

    image.save('/tmp/.i3lock.png')

def lock_screen():
    os.system('''i3lock -i /tmp/.i3lock.png \
                    --insidevercolor={clearish}   \
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
                '''.format(blank=Color.BLANK,
                           clearish=Color.CLEARISH,
                           default=Color.DEFAULT,
                           text=Color.TEXT,
                           wrong=Color.WRONG,
                           verifying=Color.VERIFYING,
                           ))

if __name__ == '__main__':
    # 1: Take a screenshot.
    screenshot()

    # 2: Get the visible windows.
    rects = xcb_fetch_windows()

    # 3: Process the screenshot.
    obscure(rects)

    # 4: Lock the screen
    lock_screen()
