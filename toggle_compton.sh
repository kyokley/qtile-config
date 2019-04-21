#!/bin/bash

PID=$(ps ax | grep compton | grep -v toggle_compton | grep -v vim | grep -v grep | awk '{print $1}')
RETURN_CODE=$?

if [ $RETURN_CODE -eq 0 ] && [ "$PID" != "" ]
then
    echo "PID: $PID RETURN_CODE: $RETURN_CODE"
    kill $PID
else
    compton -b --config "$HOME/.config/compton/compton.conf"
fi
