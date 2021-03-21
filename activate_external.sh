#!/bin/bash

LEFT_OR_RIGHT='left'

function restart_qtile() {
    echo "Restarting qtile"
    /home/yokley/.pyenv/versions/qtile/bin/qtile-cmd -o cmd -f restart > /dev/null 2>&1
    echo "qtile restarted successfully"
}

(ps ax | grep intel-virtual-output | grep -v grep >/dev/null && echo "intel-virtual-output already running" ) || (intel-virtual-output && echo "Started intel-virtual-output" && sleep 1)

VIRTUAL_DISPLAY=$(xrandr -q | grep -Po 'VIRTUAL\d(?= connected)')

if [ $? -ne 0 ]
then
    echo 'Could not find external display'
    restart_qtile
    xset +dpms
    exit
fi

echo "VIRTUAL_DISPLAY: " $VIRTUAL_DISPLAY

PRIMARY_DISPLAY=$(xrandr -q | grep primary | awk '{print $1}')
echo "PRIMARY_DISPLAY: " $PRIMARY_DISPLAY

VIRTUAL_MODE=$(xrandr -q | grep $VIRTUAL_DISPLAY | awk 'NR == 2 {print $1}')
echo "VIRTUAL_MODE: " $VIRTUAL_MODE

# VIRTUAL_RATE=$(xrandr -q | grep $VIRTUAL_DISPLAY | awk 'NR == 2 {print $NF}' | grep -Po '[0-9.]+')
# echo "VIRTUAL_RATE: " $VIRTUAL_RATE

echo

echo "Activating fake resolution"
xrandr --output $VIRTUAL_DISPLAY --${LEFT_OR_RIGHT}-of $PRIMARY_DISPLAY --mode 1680x1050

echo "Sleeping for 5 secs..."
sleep 5

echo "Activating external with resolution $VIRTUAL_MODE"
xrandr --output $VIRTUAL_DISPLAY --${LEFT_OR_RIGHT}-of $PRIMARY_DISPLAY --mode $VIRTUAL_MODE

echo "Sleeping for 5 secs..."
sleep 5

restart_qtile
xset -dpms

echo "Done"
