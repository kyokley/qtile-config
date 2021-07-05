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


from itertools import chain
from pathlib import Path
from libqtile.config import (Drag,
                             Click,
                             Match,
                             )
from libqtile.command import lazy
from libqtile import layout, hook
from custom.screen import SCREENS
from custom.utils import run_command
from custom.keys import KEYS, MOD
from custom.groups import GROUPS, GROUP_KEYS
from custom.layout import LAYOUTS

try:
    from typing import List  # noqa: F401
except ImportError:
    pass

groups = GROUPS
keys = KEYS
keys.extend(GROUP_KEYS)

layouts = LAYOUTS
screens = SCREENS

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
float_rule_strs = [
        'confirm',
        'dialog',
        'download',
        'error',
        'file_progress',
        'notification',
        'splash',
        'toolbar',
        'confirmreset',  # gitk
        'makebranch',  # gitk
        'maketag',  # gitk
        'branchdialog',  # gitk
        'pinentry-gtk-2',  # GPG key password entry
        'ssh-askpass',  # ssh-askpass
        'Conky',  # Conky
]

floating_layout = layout.Floating(
    float_rules=chain([Match(wm_class=rule) for rule in float_rule_strs],
                      [Match(wm_type=rule) for rule in float_rule_strs],
                      [Match(func=lambda c: c.has_fixed_size()),
                       Match(func=lambda c: c.has_fixed_ratio())],
                      ),
    border_width=1,
    border_focus='FF0000')
auto_fullscreen = True
focus_on_window_activation = "smart"
bring_front_click = True

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
    run_command('nitrogen --restore')
    run_command('nm-applet')
    run_command('dunst', raise_called_process_exception=False)
    run_command('blueman-applet', raise_called_process_exception=False)
    run_command('mntray', raise_called_process_exception=False)
    run_command('protonmail-bridge', raise_called_process_exception=False)

    locker_path = Path('~/.config/qtile/force_lock.sh')
    run_command(f'''xautolock -locker "{locker_path.expanduser()}" -time 10 -notify 10 -notifier "notify-send -t 5000 -i gtk-dialog-info 'Locking in 10 seconds'"''')

    xautolock_status_path = Path('/tmp/xautolock.status')
    with open(xautolock_status_path, 'w') as f:
        f.write('enabled')

    run_command('xset dpms 600 600 600')

    # Disable screensaver
    run_command('xset s off')
