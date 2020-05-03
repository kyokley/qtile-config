#!/bin/bash

set -e

echo "Shutting down external"
xrandr --output VIRTUAL3 --off
PID=$(ps ax | grep intel-virtual-output | grep -v grep | awk '{print $1}')
sudo kill $PID
echo "Restarting qtile"
/home/yokley/.pyenv/versions/qtile/bin/qtile-cmd -o cmd -f restart > /dev/null 2>&1
echo "Done"
