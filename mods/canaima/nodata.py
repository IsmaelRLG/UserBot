# -*- coding: utf-8 -*-

import re
from canaima import conf
from irc.center import mode
from irc.request import who

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

                for user in who(irc, conf['channel'])['list']:
                    if user[2] == host:
                        irc.kick(conf['channel'], user[0], conf['nodata']['warning'])

                mode.add(irc.base.name, conf['channel'], '-b *!*@' + host)
                del RELAPSE[host]
                return True

load()