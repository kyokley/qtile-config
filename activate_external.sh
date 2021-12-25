#!/bin/bash

sleep 1

LEFT_OR_RIGHT='left'
DISPLAY_PREFIX='HDMI'

function restart_qtile() {
    USERS=$(last | grep still | cut -d " " -f1 | uniq)

    echo "Restarting qtile"
    for user in "${USERS}"; do
        DISPLAY=:0 /home/yokley/.pyenv/versions/qtile/bin/qtile cmd-obj -o cmd -f restart
    done
    echo "qtile restarted successfully"
}

# PRIMARY_DISPLAY=$(DISPLAY=:0 xrandr -q | grep primary | awk '{print $1}')
# echo "PRIMARY_DISPLAY: " $PRIMARY_DISPLAY

PRIMARY_DISPLAY='DP-2'
echo "Force primary display"
echo "PRIMARY_DISPLAY: " $PRIMARY_DISPLAY

VIRTUAL_DISPLAY=$(DISPLAY=:0 xrandr -q | grep -Po "$DISPLAY_PREFIX\S+")

if [ $? -ne 0 ]
then
    echo 'Could not find external display'
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

# VIRTUAL_MODE=$(DISPLAY=:0 xrandr -q | grep $VIRTUAL_DISPLAY | awk 'NR == 2 {print $1}')
VIRTUAL_MODE=$(DISPLAY=:0 xrandr -q | sed -n "/$VIRTUAL_DISPLAY/,"'$p' | awk 'NR == 2 {print $1}')
echo "VIRTUAL_MODE: " $VIRTUAL_MODE

# VIRTUAL_RATE=$(DISPLAY=:0 xrandr -q | grep $VIRTUAL_DISPLAY | awk 'NR == 2 {print $NF}' | grep -Po '[0-9.]+')
# echo "VIRTUAL_RATE: " $VIRTUAL_RATE

echo


echo "Activating external with resolution $VIRTUAL_MODE"
DISPLAY=:0 xrandr --output $VIRTUAL_DISPLAY --${LEFT_OR_RIGHT}-of $PRIMARY_DISPLAY --mode $VIRTUAL_MODE --output $PRIMARY_DISPLAY --primary
restart_qtile

DISPLAY_LINK_CARD=$(pactl list short cards | grep DisplayLink | awk '{print $2}')
if [ $? -eq 0 ]
then
    echo "Found card $DISPLAY_LINK_CARD"
    echo "Switching $DISPLAY_LINK_CARD to off"
    pactl set-card-profile "$DISPLAY_LINK_CARD" off
fi

echo "Done"
