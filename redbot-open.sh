#!/bin/bash

source $HOME/.zpriv

function redbot-cmd(){
    docker run --rm -t \
      -v $HOME/.config/redmine:/root/.config/redmine \
      -e KEY_PATH=/root/.config/redmine/key \
      -e USER_INDEX=${REDBOT_DEFAULT_USER_INDEX} \
      -e ALL_PROXY="socks5://${DOCKER_LOCALHOST}:8081" \
      --net host \
      kyokley/redbot $@
}

issue=$(redbot-cmd issue --quiet | sed 's/\s\+$//' | grep -vE '^$' | rofi -dmenu -i -multi-select -p "redbot" | awk '{print $1}')
if [ $? -eq 0 ] && [ ! -z "$issue" ]
then
    firefox "${REDBOT_REDMINE_URL}${issue}"
fi
