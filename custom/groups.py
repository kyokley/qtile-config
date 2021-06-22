from libqtile.config import (Group,
                             Match,
                             ScratchPad,
                             DropDown,
                             Key,
                             )
from custom.constants import MOD, SHIFT
from libqtile.command import lazy

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
                              Match(title='brave', role='browser'),
                              Match(title='Brave', role='browser'),
                              Match(wm_class='google-chrome'),
                              Match(wm_class='Google-chrome'),
                              ],
                     label='6:Web',
                     ),
               Group('7',
                     matches=[Match(wm_class='spotify'),
                              Match(wm_class='Spotify'),
                              ],
                     label='7:Music',
                     ),
               Group('8',
                     matches=[Match(wm_class='Pidgin'),
                              Match(wm_class='Slack'),
                              ],
                     label='8:Chat',
                     ),
               Group('9',
                     matches=[Match(wm_class='Thunderbird'),
                              Match(title='Outlook'),
                              ],
                     label='9:Email',
                     ),
               Group('0'),
               Group('Proton',
                     matches=[Match(wm_class='protonmail-bridge'),
                              Match(wm_class='protonvpn'),
                              ],
                     init=False,
                     persist=False,
                     label='Proton',
                     ),
               Group('Teams',
                     matches=[Match(wm_class='Microsoft Teams - Preview'),
                              ],
                     init=False,
                     persist=False,
                     label='Teams',
                     ),
               ])

GROUP_KEYS = []
for group in GROUPS:
    if group.name in ('scratchpad', 'Proton', 'Teams'):
        continue

    GROUP_KEYS.extend([
        # mod1 + letter of group = switch to group
        Key([MOD], group.name, lazy.group[group.name].toscreen()),

        # mod1 + shift + letter = switch to & move focused window to group
        Key([MOD, SHIFT], group.name, lazy.window.togroup(group.name)),
    ])
