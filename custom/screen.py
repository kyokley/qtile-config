import os
from pathlib import Path
from libqtile import bar, widget
from custom.widget import (WallpaperDir,
                           ScreenLockIndicator,
                           Weather,
                           VT,
                           GCal,
                           Krill,
                           MaxCPUGraph,
                           CheckUpdatesWithZero,
                           )
from custom.default import extension_defaults
from libqtile.config import Screen
from custom.layout import ScreenLayout
from custom.utils import OS, determine_os, mount_exists

PYTHON_ENV_DIR = '/home/yokley/.pyenv/versions/qtile'

BATTERY_PATH = Path('/sys/class/power_supply/BAT0')
HOME_DIR = '/home'
ROOT_DIR = '/'

top_widgets = [
    widget.WindowName(for_current_screen=True),
    ScreenLockIndicator(
        foreground='FF000D',
    ),
    widget.TextBox('WP:'),
    WallpaperDir(
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
              format='{p}: {r:.0f}%',
              partition=ROOT_DIR),
]

if mount_exists(HOME_DIR):
    top_widgets.append(
        widget.DF(visible_on_warn=False,
                  foreground=extension_defaults.foreground,
                  format='{p}: {r:.0f}%',
                  partition=HOME_DIR,
                  )
    )

top_widgets.extend([
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
])

machine_os = determine_os()

if machine_os == OS.Ubuntu:
    top_widgets.extend([widget.TextBox('U:'),
                        CheckUpdatesWithZero(
                            display_format='{updates}',
                            distro='Ubuntu',
                            foreground=extension_defaults.foreground,
                            colour_no_updates=extension_defaults.foreground,
                            colour_have_updates=extension_defaults.foreground,
                            update_interval=3600,  # update every hour
                            restart_indicator='*',
                        ),
                        ])
elif machine_os == OS.Manjaro:
    top_widgets.extend([widget.TextBox('U:'),
                        CheckUpdatesWithZero(
                            display_format='{updates}',
                            distro='Arch',
                            foreground=extension_defaults.foreground,
                            colour_no_updates=extension_defaults.foreground,
                            colour_have_updates=extension_defaults.foreground,
                            update_interval=3600,  # update every hour
                        ),
                        ])

top_widgets.extend([
    widget.TextBox('W:'),
    Weather(
        normal_foreground=extension_defaults.foreground,
        update_interval=3600,  # Update every hour
    ),
])

if BATTERY_PATH.exists():
    top_widgets.extend([
        widget.TextBox('Bat:'),
        widget.Battery(energy_now_file='charge_now',
                       energy_full_file='charge_full',
                       power_now_file='current_now',
                       low_percentage=.3,
                       foreground=extension_defaults.foreground,
                       format='{percent:2.0%}',
                       ),
        widget.BatteryIcon(),
    ])

top_widgets.extend([
    widget.Systray(),
    widget.Clock(
        foreground='FFDE3B',
        format='%a %b %d %H:%M:%S',
    ),
])

SCREENS = [
    Screen(
        top=bar.Bar(
            top_widgets,
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
