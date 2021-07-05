#!/bin/bash

STATUS_FILE_PATH=/tmp/xautolock.status

if [ $(cat $STATUS_FILE_PATH 2>/dev/null)'' == 'enabled' ]
then
    xautolock -disable
    echo 'disabled' > $STATUS_FILE_PATH
else
    xautolock -enable
    echo 'enabled' > $STATUS_FILE_PATH
fi
