#!/bin/bash

nitrogen --restore &
nm-applet &
xautolock -locker "$HOME/.config/qtile/force_lock.sh" -time 10 -notify 10 -notifier "notify-send -t 5000 -i gtk-dialog-info 'Locking in 10 seconds'" &
xset dpms 600 600 600

# Disable screensaver
# xset s off
