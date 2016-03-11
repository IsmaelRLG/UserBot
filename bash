#!/bin/bash

if [ -f /tmp/userbot.pid ];
    then
    USERBOT_PID=$(cat /tmp/userbot.pid)
    USERBOT_JOB=$(ps --pid $USERBOT_PID -F | grep userbot)
    if [ -z "$USERBOT_JOB" ];
        then
        cd /home/kwargs/UserBot
        ./userbot --restart
    fi
else
    cd /home/kwargs/UserBot
    ./userbot --start
fi

