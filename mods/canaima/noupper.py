# -*- coding: utf-8 -*-

from canaima import conf
from irc.center import mode
from irc.request import who

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
                msg = conf['warn']
                msg = msg.format(nick=nick, relapse_num=RELAPSE[host])
                irc.notice(conf['channel'], msg)

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