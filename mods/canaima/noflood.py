# -*- coding: utf-8 -*-

import time
from canaima import conf
from irc.center import mode
from irc.request import who

NOFLOOD = {}
RELAPSE = {}
RELAPSE_LIMIT = conf['noflood']['relapse_limit']


def func(irc, nick, host, message):
    if len(NOFLOOD) > conf['count_limit']:
        NOFLOOD.clear()

    LIMIT_T = conf['noflood']['limit_t']
    LIMIT_L = conf['noflood']['limit_l']
    LIMIT_M = conf['noflood']['limit_m']
    LIMIT_R = conf['noflood']['limit_r']

    if len(NOFLOOD) >= 100:
        NOFLOOD.clear()

    if not host in NOFLOOD:
        NOFLOOD[host] = [1, time.time(), message, 0]
    else:
        NOFLOOD[host][0] += 1

    ok = False
    if (time.time() - NOFLOOD[host][1]) <= LIMIT_T:
        if NOFLOOD[host][0] >= LIMIT_M:
            ok = True
            me = 'No envies mensajes tan rapido! Es flood!'
    else:
        NOFLOOD[host][0] = 1
        NOFLOOD[host][1] = time.time()

    if not ok:
        if (time.time() - NOFLOOD[host][1]) <= LIMIT_L:
            if NOFLOOD[host][2] == message.lower():
                NOFLOOD[host][3] += 1
            else:
                NOFLOOD[host][3] = 0
                NOFLOOD[host][2] = message.lower()

            if NOFLOOD[host][3] >= LIMIT_R:
                ok = True
                me = '¡No repitas! ¡No repitas! ¡No repitas! ¡Ya te leimos!'

    if ok:
        if len(RELAPSE) > conf['count_limit']:
            NOFLOOD.clear()

        if not host in RELAPSE:
            RELAPSE[host] = 1
        else:
            RELAPSE[host] += 1

        if (RELAPSE_LIMIT - RELAPSE[host]) == 1:
            irc.privmsg(nick, conf['warning'].format(nick=nick))

        if RELAPSE[host] < RELAPSE_LIMIT:
            msg = conf['warn'] + me
            msg = msg.format(nick=nick, relapse_num=RELAPSE[host])
            irc.notice(conf['channel'], msg)
        else:
            irc.mode(conf['channel'], '+b *!*@' + host)

            for user in who(irc, conf['channel'])['list']:
                if user[2] == host:
                    irc.kick(conf['channel'], user[0], me)

            mode.add(irc.base.name, conf['channel'], '-b *!*@' + host)

            del RELAPSE[host]
            del NOFLOOD[host]
            return True
