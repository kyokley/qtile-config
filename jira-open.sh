#!/bin/bash

source $HOME/.zpriv

function jira-cmd(){
    docker run --rm -t -e JIRA_DOMAIN=$JIRA_DOMAIN -v $HOME/.config/jirabot/creds:/root/.config/jirabot/creds kyokley/jirabot $@
}

issue=$(jira-cmd issue --quiet | sed 's/\s\+$//' | grep -vE '^$' | rofi -dmenu -i -multi-select -p "jira" | awk '{print $1}')
if [ $? -eq 0 ] && [ ! -z "$issue" ]
then
    jira-cmd issue --quiet $issue | grep 'Link' | awk '{print $2}' | xargs -r brave
fi
