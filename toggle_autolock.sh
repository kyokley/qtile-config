#!/bin/bash

PID=$(ps ax | grep xautolock | grep -v grep | awk '{print $1}')
RETURN_CODE=$?

if [ $RETURN_CODE -eq 0 ] && [ "$PID" != "" ]
then
    xautolock -exit
else
    xautolock -locker "$HOME/.config/qtile/force_lock.sh" -time 10 -notify 10 -notifier "notify-send -t 5000 -i gtk-dialog-info 'Locking in 10 seconds'" &
fi
