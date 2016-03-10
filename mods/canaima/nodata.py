# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import re
from canaima import conf
from canaima import to_kick
from irc.center import mode

PATTERNS = []
RELAPSE = {}
RELAPSE_LIMIT = conf['nodata']['relapse_limit']


def load():
    for pattern, level in conf['nodata']['patterns']:
        PATTERNS.append((re.compile(pattern, 2), level))


def func(irc, nick, host, message):
    if len(RELAPSE) > conf['count_limit']:
        RELAPSE.clear()

    for pattern, level in PATTERNS:
        if pattern.match(message):
            if not host in RELAPSE:
                RELAPSE[host] = 1
            else:
                RELAPSE[host] += 1

            if RELAPSE[host] < RELAPSE_LIMIT:
                if level == 0:
                    msg = conf['warn'] + conf['nodata']['warning']
                    msg = msg.format(nick=nick, relapse_num=RELAPSE[host])
                    irc.notice(conf['channel'], msg)
                if level == 1:
                    msg = conf['nodata']['warning']
                    irc.kick(conf['channel'], nick, msg)
                    RELAPSE[host] = RELAPSE_LIMIT + 1
                if (RELAPSE_LIMIT - RELAPSE[host]) == 1:
                    irc.privmsg(nick, conf['warning'].format(nick=nick))
                return True
            else:
                irc.mode(conf['channel'], '+b *!*@' + host)

                for tuple in to_kick:
                    _host, msg = tuple
                    if host == _host:
                        to_kick.remove(tuple)

                to_kick.append((host.lower(), conf['nodata']['warning']))
                irc.who(conf['channel'])

                mode(irc.base.name, conf['channel'], '-b *!*@' + host, 86400)
                del RELAPSE[host]
                return True

load()