# -*- coding: utf-8 -*-

import re
from canaima import conf
from irc.center import mode
from irc.request import who

PATTERNS = []
RELAPSE = {}
RELAPSE_LIMIT = conf['badwords']['relapse_limit']


def load():
    for pattern in conf['badwords']['patterns']:
        PATTERNS.append(re.compile(pattern, 2))


def func(irc, nick, host, message):
    if len(RELAPSE) > conf['count_limit']:
        RELAPSE.clear()

    for pattern in PATTERNS:
        for lin in message.split():
            if pattern.match(lin):
                if not host in RELAPSE:
                    RELAPSE[host] = 1
                else:
                    RELAPSE[host] += 1

                if RELAPSE[host] < RELAPSE_LIMIT:
                    irc.kick(conf['channel'], nick, conf['badwords']['warning'])
                    irc.privmsg(nick, conf['warning'].format(nick=nick))
                    return True
                else:
                    irc.mode(conf['channel'], '+b *!*@' + host)

                    for user in who(irc, conf['channel'])['list']:
                        if user[2] == host:
                            irc.kick(conf['channel'], user[0], conf['badwords']['warning'])

                    mode.add(irc.base.name, conf['channel'], '-b *!*@' + host)
                    del RELAPSE[host]
                    return True

load()