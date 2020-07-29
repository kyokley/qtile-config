from libqtile.config import (Group,
                             Match,
                             ScratchPad,
                             DropDown,
                             )

GROUPS = [
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
                 on_focus_lost_hide=True,
                 height=.5,
                 )]),
]
GROUPS.extend([Group(i) for i in "1234"])
GROUPS.extend([Group('5',
                     matches=[Match(wm_class=['LibreOffice'])],
                     label='5:LO',
                     ),
               Group('6',
                     matches=[Match(wm_class=['vivaldi', 'Vivaldi']),
                              Match(title=['brave', 'Brave'], role=['browser']),
                              Match(wm_class=['google-chrome', 'Google-chrome']),
                              ],
                     label='6:Web',
                     ),
               Group('7',
                     matches=[Match(wm_class=['spotify', 'Spotify']),
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
                              Match(title=['Outlook']),
                              ],
                     label='9:Email',
                     ),
               Group('0'),
               ])