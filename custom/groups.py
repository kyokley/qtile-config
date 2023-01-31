from libqtile.config import (Group,
                             Match,
                             ScratchPad,
                             DropDown,
                             Key,
                             )
from custom.constants import MOD, SHIFT
from libqtile.command import lazy


def toscreen(qtile, group_name):
    if group_name == qtile.current_screen.group.name:
        qtile.current_screen.set_group(qtile.current_screen.previous_group)
    else:
        for idx, group in enumerate(qtile.groups):
            if group_name == group.name:
                qtile.current_screen.set_group(group)
                break


GROUPS = [
    ScratchPad("scratchpad", [
        # define a drop down terminal.
        # it is placed in the upper third of screen by default.
        DropDown("term",
                 "kitty --directory \"~\"",
                 opacity=0.9,
                 on_focus_lost_hide=True,
                 height=.5,
                 ),

        DropDown("browser", "firefox",
                 opacity=0.9,
                 on_focus_lost_hide=True,
                 height=.5,
                 )]),
]
GROUPS.extend([Group(i) for i in "1234"])
GROUPS.extend([Group('5',
                     matches=[Match(wm_class='LibreOffice')],
                     label='5:LO',
                     ),
               Group('6',
                     matches=[Match(wm_class='vivaldi'),
                              Match(wm_class='Vivaldi'),
                              Match(wm_class='brave-browser'),
                              Match(wm_class='google-chrome'),
                              Match(wm_class='Google-chrome'),
                              ],
                     label='6:Web',
                     ),
               Group('7',
                     matches=[Match(wm_class='spotify'),
                              Match(wm_class='Spotify'),
                              Match(wm_class='Spotify Premium'),
                              ],
                     label='7:Music',
                     ),
               Group('8',
                     matches=[Match(wm_class='Pidgin'),
                              Match(wm_class='Slack'),
                              Match(wm_class='crx_mdpkiolbdkhdjpekfbkbmhigcaggjagi'),  # Google Chat
                              ],
                     label='8:Chat',
                     ),
               Group('9',
                     matches=[Match(wm_class='Thunderbird'),
                              Match(title='Outlook'),
                              Match(wm_class='crx_faolnafnngnfdaknnbpnkhgohbobgegn'),  # Outlook PWA
                              ],
                     label='9:Email',
                     ),
               Group('0'),
               Group('minus',
                     matches=[Match(wm_class='protonmail-bridge'),
                              Match(wm_class='protonvpn'),
                              Match(wm_class='pritunl'),
                              ],
                     label='VPN',
                     ),
               Group('equal',
                     matches=[Match(wm_class='Microsoft Teams - Preview'),
                              Match(wm_class='crx_cifhbcnohmdccbgoicgdjpfamggdegmo'),
                              ],
                     label='Exile',
                     ),
               ])

GROUP_KEYS = []
for group in GROUPS:
    if group.name in ('scratchpad',):
        continue

    GROUP_KEYS.extend([
        # mod1 + letter of group = switch to group
        Key([MOD], group.name, lazy.function(toscreen, group.name)),

        # mod1 + shift + letter = switch to & move focused window to group
        Key([MOD, SHIFT], group.name, lazy.window.togroup(group.name)),
    ])
