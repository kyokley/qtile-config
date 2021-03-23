#!/bin/bash

LEFT_OR_RIGHT='left'
DISPLAY_PREFIX='DVI'

function restart_qtile() {
    echo "Restarting qtile"
    DISPLAY=:0 /home/yokley/.pyenv/versions/qtile/bin/qtile cmd-obj -o cmd -f restart
    echo "qtile restarted successfully"
}

# (ps ax | grep intel-virtual-output | grep -v grep >/dev/null && echo "intel-virtual-output already running" ) || (DISPLAY=:0 intel-virtual-output && echo "Started intel-virtual-output" && sleep 1)

VIRTUAL_DISPLAY=$(DISPLAY=:0 xrandr -q | grep -Po "$DISPLAY_PREFIX\S+")

if [ $? -ne 0 ]
then
    echo 'Could not find external display'
    restart_qtile
    DISPLAY=:0 xset +dpms
    exit
fi

DISPLAY=:0 xrandr -q | grep -Po "$DISPLAY_PREFIX\S+(?= disconnected)"
if [ $? -eq 0 ]
then
    echo "$VIRTUAL_DISPLAY is disconnected. Attempting to turn off"
    DISPLAY=:0 xrandr --output $VIRTUAL_DISPLAY --off
    restart_qtile
    exit
fi

echo "VIRTUAL_DISPLAY: " $VIRTUAL_DISPLAY

PRIMARY_DISPLAY=$(DISPLAY=:0 xrandr -q | grep primary | awk '{print $1}')
echo "PRIMARY_DISPLAY: " $PRIMARY_DISPLAY

# VIRTUAL_MODE=$(DISPLAY=:0 xrandr -q | grep $VIRTUAL_DISPLAY | awk 'NR == 2 {print $1}')
VIRTUAL_MODE=$(DISPLAY=:0 xrandr -q | sed -n "/$VIRTUAL_DISPLAY/,"'$p' | awk 'NR == 2 {print $1}')
echo "VIRTUAL_MODE: " $VIRTUAL_MODE

# VIRTUAL_RATE=$(DISPLAY=:0 xrandr -q | grep $VIRTUAL_DISPLAY | awk 'NR == 2 {print $NF}' | grep -Po '[0-9.]+')
# echo "VIRTUAL_RATE: " $VIRTUAL_RATE

echo

echo "Activating fake resolution"
DISPLAY=:0 xrandr --output $VIRTUAL_DISPLAY --${LEFT_OR_RIGHT}-of $PRIMARY_DISPLAY --mode 1680x1050

echo "Sleeping for 5 secs..."
sleep 5

echo "Activating external with resolution $VIRTUAL_MODE"
DISPLAY=:0 xrandr --output $VIRTUAL_DISPLAY --${LEFT_OR_RIGHT}-of $PRIMARY_DISPLAY --mode $VIRTUAL_MODE

echo "Sleeping for 5 secs..."
sleep 5

restart_qtile
DISPLAY=:0 xset -dpms

echo "Done"
