#!/bin/bash

nitrogen --restore &
nm-applet &
xscreensaver &
xautolock -time 10 -notify 10 -notifier "notify-send -t 5000 -i gtk-dialog-info 'Locking in 10 seconds'" &
