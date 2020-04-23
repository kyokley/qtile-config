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

from collections import namedtuple

from libqtile.config import (Key,
                             Screen,
                             Group,
                             Drag,
                             Click,
                             Match,
                             ScratchPad,
                             DropDown,
                             )
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from custom.widget import (WallpaperDir,
                           ScreenLockIndicator,
                           Weather,
                           VT,
                           GCal,
                           Krill,
                           MaxCPUGraph,
                           )
from custom.layout import ScreenLayout

try:
    from typing import List  # noqa: F401
except ImportError:
    pass


PYTHON_ENV_DIR = '/home/yokley/.pyenv/versions/qtile'


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
    Key([MOD, SHIFT], ENTER, lazy.spawn("terminator")),
    # Key([MOD], "space", lazy.spawn("terminator")),

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

    Key([MOD], 'F11', lazy.group['scratchpad'].dropdown_toggle('term')),
    Key([MOD], 'F12', lazy.group['scratchpad'].dropdown_toggle('browser')),
]


groups = [
    ScratchPad("scratchpad", [
        # define a drop down terminal.
        # it is placed in the upper third of screen by default.
        DropDown("term",
                 "kitty --directory \"~\"",
                 opacity=0.9,
                 on_focus_lost_hide=True,
                 ),

        DropDown("browser", "firefox",
                 opacity=0.9,
                 on_focus_lost_hide=True)]),
]
groups.extend([Group(i) for i in "1234"])
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
                              Match(wm_class=['Microsoft Teams - Preview']),
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
    if i.name == 'scratchpad':
        continue

    keys.extend([
        # mod1 + letter of group = switch to group
        Key([MOD], i.name, lazy.group[i.name].toscreen()),

        # mod1 + shift + letter = switch to & move focused window to group
        Key([MOD, SHIFT], i.name, lazy.window.togroup(i.name)),
    ])

ExtensionDefault = namedtuple(
    'ExtensionDefault',
    ['font',
     'fontsize',
     'padding',
     'foreground',
     'background',
     'inactive_foreground',
     'border_focus',
     'border_normal',
     'layout_margin',
     'bar_margin',
     'bar_thickness',
     ])
extension_defaults = ExtensionDefault(
    font='sans',
    fontsize=12,
    padding=3,
    foreground='AE4CFF',
    background=None,
    inactive_foreground='404040',
    border_focus='FF0000',
    border_normal='030303',
    layout_margin=40,
    bar_margin=10,
    bar_thickness=30,
)

layouts = [
    layout.MonadTall(name='GapsTall',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     margin=extension_defaults.layout_margin,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.MonadWide(name='GapsWide',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     margin=extension_defaults.layout_margin,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.TreeTab(name='Max'),
    layout.MonadTall(name='Tall',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.MonadWide(name='Wide',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.TreeTab(name='Max'),
]

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.WindowName(for_current_screen=True),
                ScreenLockIndicator(
                    foreground='FF000D',
                ),
                widget.TextBox('WP:'),
                WallpaperDir(
                    middle_click_command=f'{PYTHON_ENV_DIR}/bin/wal -i',
                    directory=os.path.expanduser('~/Pictures/wallpapers/'),
                    foreground=extension_defaults.foreground,
                ),
                widget.TextBox('Vol:'),
                widget.Volume(
                          foreground=extension_defaults.foreground,
                          ),
                widget.TextBox('Disk:'),
                widget.DF(visible_on_warn=False,
                          foreground=extension_defaults.foreground,
                          format='{p}: {r:.0f}%'),
                widget.TextBox('Mem:'),
                widget.MemoryGraph(graph_color=extension_defaults.foreground),
                widget.TextBox('Cpu:'),
                MaxCPUGraph(graph_color=extension_defaults.foreground),
                widget.TextBox('Net:'),
                widget.Net(foreground=extension_defaults.foreground,
                           interface='wlp0s20f3',
                           # format='{interface}: {down} ↓↑ {up}',
                           format='{down} ↓↑ {up}',
                           update_interval=2),
                widget.TextBox('U:'),
                widget.CheckUpdates(
                         display_format='{updates}',
                         distro='Ubuntu',
                         foreground=extension_defaults.foreground,
                         colour_no_updates=extension_defaults.foreground,
                         colour_have_updates=extension_defaults.foreground,
                         update_interval=3600,  # Update every hour
                         restart_indicator='*',
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
            extension_defaults.bar_thickness,
            margin=extension_defaults.bar_margin,
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
            extension_defaults.bar_thickness,
            margin=extension_defaults.bar_margin,
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
