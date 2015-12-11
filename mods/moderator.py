# -*- coding: utf-8 -*-

SERVER = ''
CHANNEL = ''
URLPATT = ''
URLIGNO = ''
IGNORED = []
PATTERN = []
NODATA = []
RELAPSE = {}
KICKER = ''
LIMIT_RELAPSE = 4

KICK_MESS = 'kick %s %s ADVERTENCIA N-%s - Lenguaje vulgar, obsceno u ofensivo'
WARN_UPPE = '¡ %s ! ADVERTENCIA N-%s - Evita el uso de las mayusculas'
WARN_REPE = '¡ %s ! ADVERTENCIA N-%s - Uso excesivo de una misma letra'
WARN_DATA = '¡ %s ! ADVERTENCIA N-%s - No debes compartir datos personales'
BAN_MESS = 'b %s %s 1d mal comportamiento, lenguaje vulgar, obsceno u ofensivo'
WARN_MESS = '¡Hola %s! Soy un robot y esto es un mensaje automatico, '
WARN_MESS += '¿parece que te estas portando mal? No continues por favor :( '
WARN_MESS += 'o seras expulsado por un dia completo!!! Eso significa que no'
WARN_MESS += ' podras volver al chat hasta que se cumplan 24 horas!!! Esta es'
WARN_MESS += ' tu ultima advertencia. Y algo mas, ¡NO RESPONDAS! Como dije: '
WARN_MESS += 'Soy un robot automatizado y no comprendere nada de lo que digas'


from irc.handlers import handler
from irc.connection import servers as base
from sysb.Thread import thread
import urllib
import re


def loadpattern():
    for pattern in urllib.urlopen(URLPATT).read().splitlines():
        PATTERN.append(re.compile(pattern, 2))


def loadnodata():
    ls = [
        ('(.{1,})?(\+58)?0?(4(12|14|16|24|26)|212)\d{7,6}', 1),
        ('(.{1,})?facebook', 1),
        ('(.{1,})?twitter', 0),
        ('(.{1,})?instagram', 0),
        ('(.{1,})?bbm', 0),
        ('(.{1,})?@gmail', 1),
        ('(.{1,})?@hotmail', 1),
        ('(.{1,})?@yahoo', 1),
        ('(.{1,})skype', 0),
        ('(.{1,})whatsapp', 1),
        ('(.{1,})telegram', 0)
        ]

    for pattern, lvl in ls:
        PATTERN.append((re.compile(pattern, 2), lvl))


def loadignored():
    for host in urllib.urlopen(URLIGNO).read().splitlines():
        IGNORED.append(host)


def badwords(irc, nick, host, message):
    for pattern in PATTERN:
        if pattern.match(message):
            if not host in RELAPSE:
                RELAPSE[host] = 1
            else:
                RELAPSE[host] += 3

            if RELAPSE[host] < LIMIT_RELAPSE:
                irc.privmsg(KICKER, KICK_MESS % (CHANNEL, nick, RELAPSE[host]))
                if (LIMIT_RELAPSE - RELAPSE[host]) == 1:
                    irc.privmsg(nick, WARN_MESS % nick)
                return True
            else:
                irc.privmsg(KICKER, BAN_MESS % (CHANNEL, nick))
                del RELAPSE[host]
                return True


def nodata(irc, nick, host, message):
    for pattern, lvl in NODATA:
        if pattern.match(message):
            if not host in RELAPSE:
                RELAPSE[host] = 1
            else:
                RELAPSE[host] += 2

            if RELAPSE[host] < LIMIT_RELAPSE:
                if lvl == 0:
                    irc.privmsg(CHANNEL, WARN_DATA % (nick, RELAPSE[host]))
                if lvl == 1:
                    irc.privmsg(KICKER, BAN_MESS % (CHANNEL, nick))
                if (LIMIT_RELAPSE - RELAPSE[host]) == 1:
                    irc.privmsg(nick, WARN_MESS % nick)
                if lvl == 1:
                    del RELAPSE[host]
                return True
            else:
                irc.privmsg(KICKER, BAN_MESS % (CHANNEL, nick))
                del RELAPSE[host]
                return True


def noupper(irc, nick, host, message):
    upper = 0
    lower = 0
    porcent = float(75)
    for letter in message:
        if letter.isupper():
            upper += 1
        else:
            lower += 1

    if float(upper) >= ((float(upper + lower) * porcent) / float(100)):
            if not host in RELAPSE:
                RELAPSE[host] = 1
            else:
                RELAPSE[host] += 1

            if RELAPSE[host] < LIMIT_RELAPSE:
                irc.notice(CHANNEL, WARN_UPPE % (nick, RELAPSE[host]))
                if (LIMIT_RELAPSE - RELAPSE[host]) == 1:
                    irc.privmsg(nick, WARN_MESS % nick)
                return True
            else:
                irc.privmsg(KICKER, BAN_MESS % (CHANNEL, nick))
                del RELAPSE[host]
                return True


def norepeat(irc, nick, host, message):
    last = []
    repeat = 0
    limit = 8
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

                if RELAPSE[host] < LIMIT_RELAPSE:
                    irc.notice(CHANNEL, WARN_REPE % (nick, RELAPSE[host]))
                    if (LIMIT_RELAPSE - RELAPSE[host]) == 1:
                        irc.privmsg(nick, WARN_MESS % nick)
                    return True
                else:
                    irc.privmsg(KICKER, BAN_MESS % (CHANNEL, nick))
                    del RELAPSE[host]
                    return True


@handler('privmsg notice')
#@thread(no_class=True, n='moderador')
def pipe(self, event, group):
    if group('host') in IGNORED:
        raise UnboundLocalError("it is not the required event")
    elif group('target').lower() != CHANNEL:
        raise UnboundLocalError("it is not the required event")
    else:
        if badwords(self, *group('nick', 'host', 'message')):
            return True
        elif noupper(self, *group('nick', 'host', 'message')):
            return True
        elif norepeat(self, *group('nick', 'host', 'message')):
            return True
        elif nodata(self, *group('nick', 'host', 'message')):
            return True


loadignored()
loadpattern()
loadnodata()
#base[SERVER][0].add_handler(pipe, 9, 'local')