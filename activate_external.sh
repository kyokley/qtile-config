#!/bin/bash

ps ax | grep intel-virtual-output | grep -v grep >/dev/null && echo "Running" || sudo intel-virtual-output && echo "Started intel-virtual-output" && sleep 1

echo "Activating fake resolution"
xrandr --output VIRTUAL3 --right-of eDP1 --mode 1680x1050

echo "Sleeping for 5 secs..."
sleep 5

echo "Activating external with resolution 2560x1080"
xrandr --output VIRTUAL3 --right-of eDP1 --mode VIRTUAL3.449-2560x1080

echo "Sleeping for 5 secs..."
sleep 5

echo "Restarting qtile"
/home/yokley/.pyenv/versions/qtile/bin/qtile-cmd -o cmd -f restart > /dev/null 2>&1

echo "Applying new background wallpapers"
bash /home/yokley/workspace/switch-background/switch.sh

echo "Done"
