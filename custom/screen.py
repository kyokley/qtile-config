from pathlib import Path
from libqtile import bar, widget, qtile
from custom.widget import (WallpaperDir,
                           ScreenLockIndicator,
                           Weather,
                           VT,
                           GCal,
                           Krill,
                           MaxCPUGraph,
                           )
from custom.default import extension_defaults
from libqtile.config import Screen
from custom.layout import ScreenLayout
from custom.utils import OS, determine_os, mount_exists

BATTERY_PATH = Path('/sys/class/power_supply/BAT0')
WALLPAPER_DIR = Path('~/Pictures/wallpapers')
HOME_DIR = '/home'
ROOT_DIR = '/'
TERM = 'terminator'

top_widgets = [
    widget.WindowName(
        for_current_screen=True,
        font=extension_defaults.font,
        fontsize=extension_defaults.fontsize,
    ),
    ScreenLockIndicator(
        foreground='FF000D',
        font=extension_defaults.font,
        fontsize=extension_defaults.fontsize,
    ),
    widget.TextBox('WP:',
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
    widget.Spacer(length=10),
    WallpaperDir(
        directory=WALLPAPER_DIR.expanduser(),
        foreground=extension_defaults.foreground,
        font=extension_defaults.font,
        fontsize=extension_defaults.fontsize,
    ),
    widget.TextBox('Vol:',
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
    widget.Volume(
        foreground=extension_defaults.foreground,
        font=extension_defaults.font,
        fontsize=extension_defaults.fontsize,
    ),
    widget.TextBox('Disk:',
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
    widget.DF(visible_on_warn=False,
              font=extension_defaults.font,
              fontsize=extension_defaults.fontsize,
              foreground=extension_defaults.foreground,
              format='{p}: {r:.0f}%',
              partition=ROOT_DIR,
              mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(f'{TERM} -bx ncdu {ROOT_DIR}')},
              ),
]

if mount_exists(HOME_DIR):
    top_widgets.append(
        widget.DF(visible_on_warn=False,
                  foreground=extension_defaults.foreground,
                  format='{p}: {r:.0f}%',
                  partition=HOME_DIR,
                  mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(f'{TERM} -bx ncdu {HOME_DIR}')},
                  )
    )

top_widgets.extend([
    widget.TextBox('Mem:',
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
    widget.MemoryGraph(graph_color=extension_defaults.foreground,
                       mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(f'{TERM} -bx htop')},
                       samples=40,  # FIX: Weird graph issue where only drawing on left
                       border_width=2,
                       border_color='000000',
                       font=extension_defaults.font,
                       fontsize=extension_defaults.fontsize,
                       ),
    widget.TextBox('Cpu:',
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
    MaxCPUGraph(graph_color=extension_defaults.foreground,
                mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(f'{TERM} -bx htop')},
                samples=40,  # FIX: Weird graph issue where only drawing on left
                border_width=2,
                border_color='000000',
                font=extension_defaults.font,
                fontsize=extension_defaults.fontsize,
                ),
    widget.TextBox('Net:',
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
    widget.Net(foreground=extension_defaults.foreground,
               font=extension_defaults.font,
               fontsize=extension_defaults.fontsize,
               interface='enp14s0',
               format='{down:.0f}{down_suffix} ↓↑ {up:.0f}{up_suffix}',
               update_interval=2),
])

machine_os = determine_os()

if machine_os == OS.Ubuntu:
    top_widgets.extend([widget.TextBox('U:',
                                       font=extension_defaults.font,
                                       fontsize=extension_defaults.fontsize,
                                       ),
                        widget.CheckUpdates(
                            display_format='{updates}',
                            distro='Ubuntu',
                            foreground=extension_defaults.foreground,
                            colour_no_updates=extension_defaults.foreground,
                            colour_have_updates=extension_defaults.foreground,
                            update_interval=3600,  # update every hour
                            restart_indicator='*',
                            no_update_string='0',
                            font=extension_defaults.font,
                            fontsize=extension_defaults.fontsize,
                        ),
                        ])
elif machine_os in (OS.Manjaro, OS.Garuda, OS.Arch):
    top_widgets.extend([widget.TextBox('U:',
                                       font=extension_defaults.font,
                                       fontsize=extension_defaults.fontsize,
                                       ),
                        widget.CheckUpdates(
                            font=extension_defaults.font,
                            fontsize=extension_defaults.fontsize,
                            display_format='{updates}',
                            distro='Arch',
                            custom_command=(r'''
pamac checkupdates | awk 'BEGIN{RS="\n\n";FS=OFS="\n"} NR==1 {print $0}' | awk 'NR==1 {if($0!~/available/){exit}} NR>1 {print $0}' | grep -v "^$"
                            '''),
                            foreground=extension_defaults.foreground,
                            colour_no_updates=extension_defaults.foreground,
                            colour_have_updates=extension_defaults.foreground,
                            update_interval=3600,  # update every hour
                            no_update_string='0',
                        ),
                        ])

top_widgets.extend([
    widget.TextBox('W:'),
    Weather(
        normal_foreground=extension_defaults.foreground,
        update_interval=3600,  # Update every hour
        font=extension_defaults.font,
        fontsize=extension_defaults.fontsize,
    ),
])

if BATTERY_PATH.exists():
    top_widgets.extend([
        widget.TextBox('Bat:',
                       font=extension_defaults.font,
                       fontsize=extension_defaults.fontsize,
                       ),
        widget.Battery(energy_now_file='charge_now',
                       energy_full_file='charge_full',
                       power_now_file='current_now',
                       low_percentage=.3,
                       foreground=extension_defaults.foreground,
                       format='{percent:2.0%}',
                       font=extension_defaults.font,
                       fontsize=extension_defaults.fontsize,
                       ),
        widget.BatteryIcon(),
    ])

top_widgets.extend([
    widget.Systray(icon_size=extension_defaults.iconsize),
    widget.Clock(
        foreground='FFDE3B',
        format='%a %b %d %H:%M:%S',
        font=extension_defaults.font,
        fontsize=extension_defaults.fontsize,
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
                    font=extension_defaults.font,
                    fontsize=extension_defaults.fontsize,
                ),
                widget.Spacer(length=10),
                ScreenLayout(width=bar.STRETCH,
                             font=extension_defaults.font,
                             fontsize=extension_defaults.fontsize,
                             ),
                widget.TextBox('Krl:',
                               font=extension_defaults.font,
                               fontsize=extension_defaults.fontsize,
                               ),
                Krill(foreground=extension_defaults.foreground,
                      sources_file='~/workspace/krill_feed/sources.txt',
                      update_interval=21,
                      font=extension_defaults.font,
                      fontsize=extension_defaults.fontsize,
                      ),
                widget.TextBox('VT:',
                               font=extension_defaults.font,
                               fontsize=extension_defaults.fontsize,
                               ),
                VT(update_interval=10,
                   foreground=extension_defaults.foreground,
                   font=extension_defaults.font,
                   fontsize=extension_defaults.fontsize,
                   ),
                widget.TextBox('Cal:',
                               font=extension_defaults.font,
                               fontsize=extension_defaults.fontsize,
                               ),
                GCal(update_interval=11,
                     default_foreground=extension_defaults.foreground,
                     debug=False,
                     font=extension_defaults.font,
                     fontsize=extension_defaults.fontsize,
                     ),
            ],
            extension_defaults.bar_thickness,
            margin=extension_defaults.bar_margin,
        )
),
]
