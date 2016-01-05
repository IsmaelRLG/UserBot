# -*- coding: utf-8 -*-

from canaima import conf
from irc.center import mode
from irc.request import who

RELAPSE = {}
RELAPSE_LIMIT = conf['norepeat']['relapse_limit']


def func(irc, nick, host, message):
    last = []
    repeat = 0
    limit = conf['norepeat']['limit']
    for letter in message:
        if not letter in last:
            if len(last) == 0:
                last.append(letter)
            else:
                last.pop()
                last.append(letter)
        else:
            repeat += 1
            if repeat >= limit:
                if not host in RELAPSE:
                    RELAPSE[host] = 1
                else:
                    RELAPSE[host] += 1

                if RELAPSE[host] < RELAPSE_LIMIT:
                    msg = conf['warn'] + conf['norepeat']['warning']
                    msg = msg.format(nick=nick, relapse_num=RELAPSE[host])
                    irc.notice(conf['channel'], msg)
                    if (RELAPSE_LIMIT - RELAPSE[host]) == 1:
                        irc.privmsg(nick, conf['warning'].format(nick=nick))
                    return True
                else:
                    irc.mode(conf['channel'], '+b *!*@' + host)

                    for user in who(irc, conf['channel'])['list']:
                        if user[2] == host:
                            irc.kick(conf['channel'], user[0], conf['norepeat']['warning'])

                    mode.add(irc.base.name, conf['channel'], '-b *!*@' + host)
                    del RELAPSE[host]
                    return True
