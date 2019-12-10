#!/bin/bash

PID=$(ps ax | grep picom | grep -v toggle_picom | grep -v vim | grep -v grep | awk '{print $1}')
RETURN_CODE=$?

if [ $RETURN_CODE -eq 0 ] && [ "$PID" != "" ]
then
    echo "PID: $PID RETURN_CODE: $RETURN_CODE"
    kill $PID
else
    picom -b --config "$HOME/.config/picom/picom.conf"
fi
