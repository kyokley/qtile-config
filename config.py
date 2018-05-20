# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess
import random
import requests
import re
from datetime import datetime, timedelta
from dateutil import tz

from collections import namedtuple

from libqtile.config import Key, Screen, Group, Drag, Click, Match
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook

try:
    from typing import List  # noqa: F401
except ImportError:
    pass

rand = random.SystemRandom()

VT_EXECUTABLE = os.path.join(os.path.expanduser('~'),
                             '.pyenv/versions/vt_env/bin/vt')
GCAL_EXECUTABLE = os.path.join(os.path.expanduser('~'),
                               '.pyenv/versions/gcal_env/bin/gcalcli')

class ProxiedRequest(widget.GenPollText):
    defaults = [
        ('http_proxy', None, 'HTTP proxy to use for requests'),
        ('https_proxy', None, 'HTTPS proxy to use for requests'),
        ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(ProxiedRequest.defaults)

    def fetch(self, is_json=True):
        proxies = {'http': self.http_proxy,
                   'https': self.https_proxy,
                   }
        resp = requests.get(self.URL, proxies=proxies)
        resp.raise_for_status()

        if is_json:
            return resp.json()
        return resp.text

WeatherTuple = namedtuple('WeatherTuple', 'temp conditions')

class Weather(ProxiedRequest):
    URL = 'http://api.openweathermap.org/data/2.5/weather?id=4887398&units=imperial&appid=c4f4551816bd45b67708bea102d93522'
    defaults = [
        ('low_temp_threshold', 45, 'Temp to trigger low foreground'),
        ('high_temp_threshold', 80, 'Temp to trigger high foreground'),
        ('low_foreground', '18BAEB', 'Low foreground'),
        ('normal_foreground', 'FFDE3B', 'Normal foreground'),
        ('high_foreground', 'FF000D', 'High foreground'),
        ]

    def __init__(self, **config):
        config['func'] = self.get_weather
        super().__init__(**config)
        self.add_defaults(Weather.defaults)

    def get_weather(self):
        data = self.fetch(is_json=True)
        conditions = rand.choice(data['weather'])['description']

        tup = WeatherTuple(data['main']['temp'], conditions)

        if tup.temp > self.high_temp_threshold:
            self.foreground = self.high_foreground
        elif tup.temp < self.low_temp_threshold:
            self.foreground = self.low_foreground
        else:
            self.foreground = self.normal_foreground

        return '{temp:.2g}F {conditions}'.format(temp=tup.temp,
                                                 conditions=tup.conditions)


class VT(widget.GenPollText):
    REGEX = re.compile(b'(?<=\x1b\[95m).*?(?=\x1b\[39m)')

    def __init__(self, **config):
        config['func'] = self.get_vt
        super().__init__(**config)

    def get_vt(self):
        proc = subprocess.check_output([VT_EXECUTABLE, 'list', '-qu'],
                                       env={'VT_DEFAULT_LIST': 'personal',
                                            'VT_URL': 'https://almagest.dyndns.org:7001/vittlify/',
                                            'VT_USERNAME': 'yokley'})
        lines = [VT.REGEX.search(x).group().strip() for x in proc.splitlines()
                    if x and x.strip() and VT.REGEX.search(x) and VT.REGEX.search(x).group().strip()]
        return rand.choice(lines).decode('utf-8') if lines else 'No items'

class GCal(widget.GenPollText):
    DATE_FORMAT = '%a %b %d %H:%M:%S %Z %Y'
    SPACE_REGEX = re.compile(b'\s+')

    def __init__(self, **config):
        config['func'] = self.get_cal
        super().__init__(**config)

    def get_cal(self):
        now = datetime.now(tz=tz.gettz('America/Chicago'))
        past_dt = now - timedelta(hours=1)
        future_dt = now + timedelta(hours=120)

        proc = subprocess.check_output([GCAL_EXECUTABLE,
                                        '--nocolor',
                                        '--prefix',
                                        '%a %b %d',
                                        'agenda',
                                        past_dt.strftime(GCal.DATE_FORMAT),
                                        future_dt.strftime(GCal.DATE_FORMAT),
                                        ],
                                       )
        lines = [GCal.SPACE_REGEX.sub(b' ', x) for x in proc.splitlines() if x]
        if not lines:
            return 'No Events'

        line = rand.choice(lines).decode('utf-8').split()
        return '{event} ({date})'.format(event=' '.join(line[3:]),
                                         date=' '.join(line[:3]))


mod = "mod1"

dmenu_font = 'sans'
dmenu_fontsize = 16

keys = [
    # Switch between windows in current stack pane
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod], "h", lazy.layout.shrink()),
    Key([mod], "l", lazy.layout.grow()),

    Key([mod], "n", lazy.layout.normalize()),
    Key([mod], "m", lazy.layout.maximize()),

    # Move windows up or down in current stack
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod], "Return", lazy.layout.swap_main()),

    # Switch window focus to other pane(s) of stack
    #Key([mod], "space", lazy.layout.next()),

    # Swap panes of split stack
    #Key([mod, "shift"], "space", lazy.layout.rotate()),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.spawn("terminator")),
    #Key([mod], "space", lazy.spawn("terminator")),

    # Toggle between different layouts as defined below
    Key([mod], "space", lazy.next_layout()),
    Key([mod, 'shift'], "c", lazy.window.kill()),

    Key([mod, "control"], "r", lazy.restart()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
    Key([mod], "p", lazy.spawn("dmenu_run -fn '{font}:pixelsize={fontsize}'".format(font=dmenu_font,
                                                                                    fontsize=dmenu_fontsize))),

    # Spotify Commands
    ## NEXT
    Key([mod, "control"], 'n', lazy.spawn([os.path.expanduser("~/workspace/SpotifyController/spotify.sh"), "n"])),
    Key([mod, "control"], 'period', lazy.spawn([os.path.expanduser("~/workspace/SpotifyController/spotify.sh"), "n"])),

    ## PREV
    Key([mod, "control"], 'p', lazy.spawn([os.path.expanduser("~/workspace/SpotifyController/spotify.sh"), "p"])),
    Key([mod, "control"], 'comma', lazy.spawn([os.path.expanduser("~/workspace/SpotifyController/spotify.sh"), "p"])),

    ## PAUSE
    Key([mod, "control"], 'space', lazy.spawn([os.path.expanduser("~/workspace/SpotifyController/spotify.sh"), "pause"])),

    ## Volume Controls
    Key([], 'XF86AudioRaiseVolume', lazy.spawn('amixer -q set Master 10%+')),
    Key([], 'XF86AudioLowerVolume', lazy.spawn('amixer -q set Master 10%-')),
    Key([], 'XF86AudioMute', lazy.spawn('amixer -q set Master toggle')),

    ## Brightness Controls
    Key([], 'XF86MonBrightnessUp', lazy.spawn("xbacklight -inc 10")),
    Key([], 'XF86MonBrightnessDown', lazy.spawn("xbacklight -dec 10")),
]

groups = [Group(i) for i in "1234"]
groups.extend([Group('5',
                     matches=[Match(wm_class=['LibreOffice'])],
                     label='5:LO',
                     ),
               Group('6',
                     matches=[Match(wm_class=['vivaldi-stable']),
                              Match(wm_class=['Vivaldi-stable']),
                              Match(wm_class=['google-chrome']),
                              Match(wm_class=['Google-chrome']),
                              ],
                     label='6:Web',
                     ),
               Group('7',
                     matches=[Match(wm_class=['spotify']),
                              Match(wm_class=['Spotify']),
                              ],
                     label='7:Music',
                     ),
               Group('8',
                     matches=[Match(wm_class=['Pidgin']),
                              Match(wm_class=['Slack']),
                              ],
                     label='8:Chat',
                     ),
               Group('9',
                     matches=[Match(wm_class=['Thunderbird']),
                              ],
                     label='9:Email',
                     ),
               Group('0'),
               ])

for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([mod], i.name, lazy.group[i.name].toscreen()),

        # mod1 + shift + letter of group = switch to & move focused window to group
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name)),
    ])

layouts = [
    layout.MonadTall(),
    layout.MonadWide(),
    layout.Max(),
]

widget_defaults = dict(
    font='sans',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.WindowName(),
                widget.TextBox('Vol:'),
                widget.Volume(
                          foreground='18BAEB',
                          ),
                widget.TextBox('Disk:'),
                widget.DF(visible_on_warn=False,
                          foreground='18BAEB',
                          format='{p}: {r:.0f}%'),
                widget.TextBox('Mem:'),
                widget.MemoryGraph(),
                widget.TextBox('Cpu:'),
                widget.CPUGraph(),
                widget.TextBox('Net:'),
                widget.NetGraph(),
                widget.TextBox('U:'),
                widget.CheckUpdates(
                               display_format='{updates}',
                               distro='Ubuntu',
                               foreground='18BAEB',
                               colour_no_updates='18BAEB',
                               colour_have_updates='18BAEB',
                               update_interval=3600, # Update every hour
                    ),
                widget.TextBox('Bat:'),
                widget.Battery(energy_now_file='charge_now',
                               energy_full_file='charge_full',
                               power_now_file='current_now',
                               low_percentage=.3,
                               foreground='18BAEB',
                               format='{percent:2.0%}',
                ),
                widget.BatteryIcon(),
                widget.TextBox('W:'),
                Weather(
                        foreground='18BAEB',
                        ),
                widget.Systray(),
                widget.Clock(format='%a %b %d %H:%M:%S'),
            ],
            24,
        ),
        bottom=bar.Bar(
            [
                widget.GroupBox(),
                widget.CurrentLayout(width=bar.STRETCH),
                widget.TextBox('VT:'),
                VT(update_interval=10,
                   foreground='18BAEB'),
                widget.TextBox('Cal:'),
                GCal(update_interval=11,
                     foreground='18BAEB',
                    ),
            ],
            24,
        )
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    {'wmclass': 'confirm'},
    {'wmclass': 'dialog'},
    {'wmclass': 'download'},
    {'wmclass': 'error'},
    {'wmclass': 'file_progress'},
    {'wmclass': 'notification'},
    {'wmclass': 'splash'},
    {'wmclass': 'toolbar'},
    {'wmclass': 'confirmreset'},  # gitk
    {'wmclass': 'makebranch'},  # gitk
    {'wmclass': 'maketag'},  # gitk
    {'wname': 'branchdialog'},  # gitk
    {'wname': 'pinentry'},  # GPG key password entry
    {'wmclass': 'ssh-askpass'},  # ssh-askpass
])
auto_fullscreen = True
focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, github issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

@hook.subscribe.startup_once
def autostart():
    script = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.call([script])
