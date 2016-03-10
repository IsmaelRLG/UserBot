# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from canaima import conf
from canaima import to_kick
from irc.center import mode

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

                    for tuple in to_kick:
                        _host, msg = tuple
                        if host == _host:
                            to_kick.remove(tuple)

                    to_kick.append((host.lower(), conf['norepeat']['warning']))
                    irc.who(conf['channel'])

                    mode(irc.base.name, conf['channel'], '-b *!*@' + host, 86400)
                    del RELAPSE[host]
                    return True
