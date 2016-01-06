# -*- coding: utf-8 -*-

import re
from canaima import conf
from canaima import to_kick
from irc.center import mode

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

                    for tuple in to_kick:
                        _host, msg = tuple
                        if host == _host:
                            to_kick.remove(tuple)

                    to_kick.append((host.lower(), conf['badwords']['warning']))
                    irc.who(conf['channel'])

                    mode(irc.base.name, conf['channel'], '-b *!*@' + host, 86400)
                    del RELAPSE[host]
                    return True

load()