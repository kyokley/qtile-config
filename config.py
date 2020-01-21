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
import functools
import json
import multiprocessing
import shlex

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

VT_CMD = ('docker run --rm -v /home/yokley/.ssh:/root/.ssh '
          '--env VT_URL=https://almagest.dyndns.org:7001/vittlify/ '
          '--env VT_USERNAME=yokley --env VT_DEFAULT_LIST=personal '
          '--env VT_PROXY= --net=host kyokley/vt list -qu')
GCAL_CMD = ('docker run --rm '
            '-v /home/yokley/.gcalcli_oauth:/root/.gcalcli_oauth '
            'kyokley/gcalcli')
KRILL_CMD = (
    'docker run --rm --cpus=.25 kyokley/krill-feed '
    'krill++ -S /app/sources.txt --snapshot')

BUTTON_UP = 4
BUTTON_DOWN = 5
BUTTON_LEFT = 1
BUTTON_RIGHT = 3


class ScreenLockIndicator(widget.GenPollText):
    defaults = [
        ('update_interval', 10, 'Update interval'),
    ]

    def __init__(self, **config):
        config['func'] = self.check_autolock
        super().__init__(**config)
        self.add_defaults(ScreenLockIndicator.defaults)

    def check_autolock(self):
        try:
            output = subprocess.check_output(
                "ps ax | grep xautolock | grep -v grep | awk '{print $1}'",
                shell=True)

            if not output:
                return 'SL Disabled'
        except subprocess.CalledProcessError:
            return 'SL Disabled'
        return ''


class CachedProxyRequest(widget.GenPollText):
    defaults = [
        ('http_proxy', None, 'HTTP proxy to use for requests'),
        ('https_proxy', None, 'HTTPS proxy to use for requests'),
        ('socks_proxy', None, 'SOCKS proxy to use for requests'),
        ('cache_expiration',
         5,
         'Length of time in minutes that cache is valid for'),
        ('debug', False, 'Enable additional debugging'),
        ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(CachedProxyRequest.defaults)
        self._last_update = None
        self._cached_data = None
        self._locked = False

    def _print(self, msg):
        if self.debug:
            print('{}: {}'.format(self.__class__, msg))

    def cached_fetch(self):
        if self._locked:
            self._print('Instance locked. Returning cached data')
            return self._cached_data

        try:
            self._print('Setting lock')
            self._locked = True
            if (not self._cached_data or
                    not self._last_update or
                    self._last_update + timedelta(
                        minutes=self.cache_expiration) < datetime.now()):
                self._print('Getting data')
                self._cached_data = self._fetch()
                self._last_update = datetime.now()
        except Exception as e:
            self._print('Got error')
            self._print(str(e))
        finally:
            self._print('Releasing lock')
            self._locked = False
            return self._cached_data

    def _fetch(self):
        proxies = {'http': self.http_proxy,
                   'https': self.https_proxy,
                   }
        resp = requests.get(self.URL, proxies=proxies)
        resp.raise_for_status()

        return resp.json()

    def clear_cache(self):
        self._last_update = None
        self._cached_data = None


WeatherTuple = namedtuple('WeatherTuple', 'temp conditions')


class Weather(CachedProxyRequest):
    URL = ('http://api.openweathermap.org/data/2.5/weather?'
           'id=4887398&units=imperial&appid=c4f4551816bd45b67708bea102d93522')
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
        data = self.cached_fetch()
        if data:
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
        return 'N/A'

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.clear_cache()
            weather = self.get_weather()

            self.update(weather)


class VT(CachedProxyRequest):
    REGEX = re.compile(b'(?<=\x1b\[95m).*?(?=\x1b\[39m)') # noqa

    def __init__(self, **config):
        config['func'] = self.get_vt
        super().__init__(**config)
        self._current_item = None

    def get_vt(self):
        self._data = self.cached_fetch()
        self._current_item = rand.choice(
            self._data) if self._data else b'No items'
        return self._current_item.decode('utf-8')

    def _fetch(self):
        cmd = shlex.split(VT_CMD)
        proc = subprocess.check_output(cmd)
        if proc:
            lines = [VT.REGEX.search(x).group().strip()
                     for x in proc.splitlines()
                     if (x and
                         x.strip() and
                         VT.REGEX.search(x) and
                         VT.REGEX.search(x).group().strip())]
            return lines
        return [b'Failed to load']

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.get_vt()
        elif button in (BUTTON_UP, BUTTON_DOWN):
            if self._data and self._current_item in self._data:
                if button == BUTTON_UP:
                    idx = self._data.index(self._current_item) + 1
                else:
                    idx = self._data.index(self._current_item) - 1
                self._current_item = self._data[idx % len(self._data)]
                self._last_update = datetime.now() + timedelta(
                    seconds=self.update_interval)
            else:
                return

        self.update(self._current_item.decode('utf-8'))


class GCal(CachedProxyRequest):
    DATE_FORMAT = '%a %b %d %H:%M:%S %Z %Y'
    SPACE_REGEX = re.compile(b'\s+') # noqa

    defaults = [
        ('default_foreground', 'FFDE3B', 'Default foreground color'),
        ('soon_foreground', 'FF000D', 'Color used for events occuring soon'),
        ]

    def __init__(self, **config):
        config['func'] = self.get_cal
        super().__init__(**config)
        self.add_defaults(GCal.defaults)
        self._current_item = None
        self.foreground = self.default_foreground

    def get_cal(self):
        self._data = self.cached_fetch()

        if not self._data:
            return 'No Events'

        self._current_item = rand.choice(self._data)
        if self._current_item[0]:
            self.foreground = self.soon_foreground
        else:
            self.foreground = self.default_foreground

        return self._format_line(self._current_item[1])

    def _format_line(self, line):
        line = line.decode('utf-8').split()
        return '{event} ({date})'.format(event=' '.join(line[3:]),
                                         date=' '.join(line[:3]))

    def _fetch(self):
        now = datetime.now(tz=tz.gettz('America/Chicago'))
        past_dt = now - timedelta(hours=1)
        short_dt = now + timedelta(hours=1)
        future_dt = now + timedelta(hours=120)

        short_cmd = shlex.split(GCAL_CMD)
        if self.https_proxy:
            short_cmd.extend(['--proxy', self.https_proxy])

        short_cmd.extend(['--nocolor',
                          '--prefix',
                          '%a %b %d',
                          'agenda',
                          past_dt.strftime(GCal.DATE_FORMAT),
                          short_dt.strftime(GCal.DATE_FORMAT),
                          '--noallday',
                          ])

        proc = subprocess.check_output(short_cmd)

        if proc:
            lines = [(True, GCal.SPACE_REGEX.sub(b' ', x))
                     for x in proc.splitlines()
                     if x and not x.startswith(b'No Events Found')]

        long_cmd = shlex.split(GCAL_CMD)
        if self.https_proxy:
            long_cmd.extend(['--proxy', self.https_proxy])

        long_cmd.extend(['--nocolor',
                         '--prefix',
                         '%a %b %d',
                         'agenda',
                         short_dt.strftime(GCal.DATE_FORMAT),
                         future_dt.strftime(GCal.DATE_FORMAT),
                         ])

        proc = subprocess.check_output(long_cmd)

        if proc:
            lines.extend(
               [(False, GCal.SPACE_REGEX.sub(b' ', x))
                   for x in proc.splitlines()
                if x and GCal.SPACE_REGEX.sub(b' ', x) not in map(
                    lambda x: x[1], lines)])
        return lines

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.get_cal()
        elif button == BUTTON_RIGHT:
            self.clear_cache()
        elif button in (BUTTON_UP, BUTTON_DOWN):
            if self._data:
                if button == BUTTON_UP:
                    idx = self._data.index(self._current_item) + 1
                else:
                    idx = self._data.index(self._current_item) - 1
                self._current_item = self._data[idx % len(self._data)]
                self._last_update = datetime.now() + timedelta(
                        seconds=self.update_interval)
            else:
                return

        self.foreground = (
                self.soon_foreground
                if self._current_item[0] else self.default_foreground)
        self.update(self._format_line(self._current_item[1]))


class Krill(CachedProxyRequest):
    defaults = [('sources_file', None, 'File containing sources'),
                ]

    def __init__(self, **config):
        config['func'] = self.get_krill
        super().__init__(**config)
        self.add_defaults(Krill.defaults)
        self._current_item = None
        self._last_item_change_time = None

    def get_krill(self):
        if not self.sources_file:
            return 'No sources provided'

        self._data = self.cached_fetch()
        if not self._data:
            return 'Could not load data from sources'

        if (not self._last_item_change_time or
                self._last_item_change_time + timedelta(
                    seconds=self.update_interval) < datetime.now()):
            self._current_item = rand.choice(self._data)
            self._last_item_change_time = datetime.now()
        return self._current_item['title']

    def _fetch(self):
        cmd = shlex.split(KRILL_CMD)
        proc = subprocess.check_output(cmd)
        if proc:
            return json.loads(proc)
        return ['Failed to load']

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.qtile.cmd_spawn('vivaldi {}'.format(
                self._current_item['link']))
        elif button in (BUTTON_UP, BUTTON_DOWN):
            if self._data:
                if button == BUTTON_UP:
                    idx = self._data.index(self._current_item) + 1
                else:
                    idx = self._data.index(self._current_item) - 1
                self._current_item = self._data[idx % len(self._data)]
                self.update(self._current_item['title'])
                self._last_item_change_time = datetime.now() + timedelta(
                        seconds=self.update_interval)


class ScreenLayout(widget.CurrentLayout):
    def setup_hooks(self):
        def hook_layout_change(layout, group):
            self.text = layout.name
            self.bar.draw()
        hook.subscribe.layout_change(hook_layout_change)

        hook_screen_change = functools.partial(
                hook_layout_change,
                layout=None,
                group=None)
        hook.subscribe.current_screen_change(hook_screen_change)


class MaxCPUGraph(widget.CPUGraph):
    def __init__(self, **config):
        self._num_cores = multiprocessing.cpu_count()
        widget.CPUGraph.__init__(self, **config)
        self.oldvalues = self._getvalues()

    def _getvalues(self):
        proc = '/proc/stat'

        with open(proc) as file:
            file.readline()
            lines = file.readlines()

        vals = [line.split(None, 6)[1:5] for line in lines[:self._num_cores]]
        return [map(int, val) for val in vals]

    def update_graph(self):
        new_values = self._getvalues()
        old_values = self.oldvalues

        max_percent = 0
        for old, new in zip(old_values, new_values):
            try:
                old_user, new_user = next(old), next(new)
                old_nice, new_nice = next(old), next(new)
                old_sys, new_sys = next(old), next(new)
                old_idle, new_idle = next(old), next(new)
            except StopIteration:
                continue

            busy = (
                new_user + new_nice + new_sys - old_user - old_nice - old_sys)
            total = busy + new_idle - old_idle

            if total:
                percent = float(busy) / total * 100
            else:
                percent = 0

            max_percent = max(max_percent, percent)

        self.oldvalues = new_values

        if max_percent:
            self.push(max_percent)


MOD = "mod1"
SHIFT = 'shift'
CONTROL = 'control'
SPACE = 'space'
PERIOD = 'period'
COMMA = 'comma'
ENTER = 'Return'


keys = [
    # Switch between windows in current stack pane
    # Key([MOD], "j", lazy.layout.next()),
    # Key([MOD], "k", lazy.layout.previous()),

    # lazy.layout.next and layout.lazy.previous don't cycle through
    # floating windows. next_window and prev_window do but they may break
    # for setups with multiple screens. I'm leaving this until I can test.
    Key([MOD], "j", lazy.group.next_window()),
    Key([MOD], "k", lazy.group.prev_window()),

    Key([MOD], "h", lazy.layout.shrink_main()),
    Key([MOD], "l", lazy.layout.grow_main()),

    Key([MOD, SHIFT], "h", lazy.layout.shrink()),
    Key([MOD, SHIFT], "l", lazy.layout.grow()),

    Key([MOD], "n", lazy.layout.normalize()),
    Key([MOD], "m", lazy.layout.maximize()),

    # Move windows up or down in current stack
    Key([MOD, SHIFT], "j", lazy.layout.shuffle_down()),
    Key([MOD, SHIFT], "k", lazy.layout.shuffle_up()),
    Key([MOD], ENTER, lazy.layout.swap_main()),

    # Multi-monitor support
    Key([MOD], "w", lazy.to_screen(0)),
    Key([MOD], "e", lazy.to_screen(1)),

    # Swap main pane
    Key([MOD], "f", lazy.layout.flip()),
    Key([MOD, SHIFT], "f", lazy.window.toggle_fullscreen()),

    # Floating
    Key([MOD], "t", lazy.window.toggle_floating()),

    # Switch window focus to other pane(s) of stack
    # Key([MOD], "space", lazy.layout.next()),

    # Swap panes of split stack
    # Key([MOD, SHIFT], "space", lazy.layout.rotate()),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes

    # Open a new terminal
    # Key([MOD, SHIFT], ENTER, lazy.spawn("kitty -1")),
    Key([MOD, SHIFT], ENTER, lazy.spawn("terminator")),

    # Toggle between different layouts as defined below
    Key([MOD], SPACE, lazy.next_layout()),
    Key([MOD, SHIFT], "c", lazy.window.kill()),

    Key([MOD, CONTROL], "r", lazy.restart()),
    Key([MOD, CONTROL], "q", lazy.shutdown()),
    Key([MOD, CONTROL], "l", lazy.spawn(
        [os.path.expanduser('~/.config/qtile/force_lock.sh')])),
    Key([MOD, CONTROL], "d", lazy.spawn(
        [os.path.expanduser('~/.config/qtile/toggle_autolock.sh')])),
    Key([MOD, CONTROL], "c", lazy.spawn(
        [os.path.expanduser('~/.config/qtile/toggle_compton.sh')])),
    Key([MOD], "p", lazy.spawn(
        "rofi -show combi"
    )),

    # Spotify Commands
    # NEXT
    Key([MOD, CONTROL], 'n', lazy.spawn(
        [os.path.expanduser(
            "~/workspace/SpotifyController/spotify.sh"), "n"])),
    Key([MOD, CONTROL], PERIOD, lazy.spawn(
        [os.path.expanduser(
            "~/workspace/SpotifyController/spotify.sh"), "n"])),

    # PREV
    Key([MOD, CONTROL], 'p', lazy.spawn(
        [os.path.expanduser(
            "~/workspace/SpotifyController/spotify.sh"), "p"])),
    Key([MOD, CONTROL], COMMA, lazy.spawn(
        [os.path.expanduser(
            "~/workspace/SpotifyController/spotify.sh"), "p"])),

    # PAUSE
    Key([MOD, CONTROL], SPACE, lazy.spawn(
        [os.path.expanduser(
            "~/workspace/SpotifyController/spotify.sh"), "pause"])),

    # Volume Controls
    Key([], 'XF86AudioRaiseVolume', lazy.spawn('amixer -q set Master 10%+')),
    Key([], 'XF86AudioLowerVolume', lazy.spawn('amixer -q set Master 10%-')),
    Key([], 'XF86AudioMute', lazy.spawn('amixer -q set Master toggle')),

    # Brightness Controls
    Key([], 'XF86MonBrightnessUp', lazy.spawn("xbacklight -inc 10")),
    Key([], 'XF86MonBrightnessDown', lazy.spawn("xbacklight -dec 10")),
    Key([], 'XF86Tools', lazy.spawn("kb-light")),
]

groups = [Group(i) for i in "1234"]
groups.extend([Group('5',
                     matches=[Match(wm_class=['LibreOffice'])],
                     label='5:LO',
                     ),
               Group('6',
                     matches=[Match(wm_class=['vivaldi']),
                              Match(wm_class=['Vivaldi']),
                              Match(wm_class=['vivaldi-stable']),
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
        Key([MOD], i.name, lazy.group[i.name].toscreen()),

        # mod1 + shift + letter = switch to & move focused window to group
        Key([MOD, SHIFT], i.name, lazy.window.togroup(i.name)),
    ])

layouts = [
    layout.MonadTall(name='Tall',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     ),
    layout.MonadWide(name='Wide',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     ),
    layout.TreeTab(name='Max'),
    layout.MonadTall(name='Gaps',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     margin=50,
                     ),
]

ExtensionDefault = namedtuple(
    'ExtensionDefault',
    'font fontsize padding foreground background inactive_foreground')
extension_defaults = ExtensionDefault(
    font='sans',
    fontsize=12,
    padding=3,
    foreground='AE4CFF',
    background=None,
    inactive_foreground='404040',
)

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.WindowName(for_current_screen=True),
                ScreenLockIndicator(
                    foreground='FF000D',
                ),
                widget.TextBox('Vol:'),
                widget.Volume(
                          foreground=extension_defaults.foreground,
                          ),
                widget.TextBox('Disk:'),
                widget.DF(visible_on_warn=False,
                          foreground=extension_defaults.foreground,
                          format='{p}: {r:.0f}%'),
                widget.DF(visible_on_warn=False,
                          partition='/home',
                          foreground=extension_defaults.foreground,
                          format='{p}: {r:.0f}%'),
                widget.TextBox('Mem:'),
                widget.MemoryGraph(graph_color=extension_defaults.foreground),
                widget.TextBox('Cpu:'),
                MaxCPUGraph(graph_color=extension_defaults.foreground),
                widget.TextBox('Net:'),
                widget.NetGraph(graph_color=extension_defaults.foreground),
                widget.TextBox('U:'),
                widget.CheckUpdates(
                         display_format='{updates}',
                         distro='Arch',
                         foreground=extension_defaults.foreground,
                         colour_no_updates=extension_defaults.foreground,
                         colour_have_updates=extension_defaults.foreground,
                         update_interval=3600,  # Update every hour
                    ),
                widget.TextBox('Bat:'),
                widget.Battery(energy_now_file='charge_now',
                               energy_full_file='charge_full',
                               power_now_file='current_now',
                               low_percentage=.3,
                               foreground=extension_defaults.foreground,
                               format='{percent:2.0%}',
                               ),
                widget.BatteryIcon(),
                widget.TextBox('W:'),
                Weather(
                        normal_foreground=extension_defaults.foreground,
                        update_interval=3600,  # Update every hour
                        ),
                widget.Systray(),
                widget.Clock(
                    foreground='FFDE3B',
                    format='%a %b %d %H:%M:%S',
                    ),
            ],
            24,
        ),
        bottom=bar.Bar(
            [
                widget.GroupBox(
                    this_current_screen_border=extension_defaults.foreground,
                    this_screen_border=extension_defaults.inactive_foreground,
                    other_current_screen_border=extension_defaults.foreground,
                    other_screen_border=extension_defaults.inactive_foreground,
                    ),
                widget.Spacer(length=10),
                ScreenLayout(width=bar.STRETCH),
                widget.TextBox('Krl:'),
                Krill(foreground=extension_defaults.foreground,
                      sources_file='~/workspace/krill_feed/sources.txt',
                      update_interval=21),
                widget.TextBox('VT:'),
                VT(update_interval=10,
                   foreground=extension_defaults.foreground,
                   ),
                widget.TextBox('Cal:'),
                GCal(update_interval=11,
                     default_foreground=extension_defaults.foreground,
                     debug=False,
                     ),
            ],
            24,
        )
    ),
]

# Drag floating layouts.
mouse = [
    Drag([MOD], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([MOD], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([MOD], "Button2", lazy.window.bring_to_front())
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
    {'wmclass': 'pinentry-gtk-2'},  # GPG key password entry
    {'wmclass': 'ssh-askpass'},  # ssh-askpass
    {'wmclass': 'Conky'},  # Conky
],
                                  border_width=1,
                                  border_focus='FF0000')
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

    subprocess.call(
        shlex.split(
            "compton -b --config {}".format(
                os.path.expanduser("~/.config/compton/compton.conf"))
        ))
