# -*- coding: utf-8 -*-

from canaima import conf
from canaima import to_kick
from irc.center import mode

RELAPSE = {}
RELAPSE_LIMIT = conf['noupper']['relapse_limit']


def func(irc, nick, host, message):
    if len(RELAPSE) > conf['count_limit']:
        RELAPSE.clear()

    u = 0
    l = 0
    n = 0
    if len(message) <= conf['noupper']['len_mini']:
        return

    for letter in message:
        if not letter.isalpha():
            n += 1
        elif letter.isupper():
            u += 1
        else:
            l += 1

    if float(u) >= (float(u + l + n) * conf['noupper']['porcent']) / float(100):
            if not host in RELAPSE:
                RELAPSE[host] = 1
            else:
                RELAPSE[host] += 1

            if RELAPSE[host] < RELAPSE_LIMIT:
                msg = conf['warn'] + conf['noupper']['warning']
                msg = msg.format(nick=nick, relapse_num=RELAPSE[host])
                irc.notice(conf['channel'], msg)

                if (RELAPSE_LIMIT - RELAPSE[host]) == 1:
                    irc.privmsg(nick, conf['warning'].format(nick=nick))
                return True
            else:
                irc.mode(conf['channel'], '+b *!*@' + host)
                to_kick.append((host.lower(), conf['noupper']['warning']))
                irc.who(conf['channel'])

                mode(irc.base.name, conf['channel'], '-b *!*@' + host, 86400)
                del RELAPSE[host]
                return True