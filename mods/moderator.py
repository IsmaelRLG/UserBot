# -*- coding: utf-8 -*-

SERVER = 'localhost'
CHANNEL = '#canaima'
URLPATT = 'file:///home/hp/badwords'
URLIGNO = 'file:///home/hp/ignored'
IGNORED = []
PATTERN = []
NODATA = []
RELAPSE = {}
KICKER = 'hp'
LIMIT_RELAPSE = 4
porcent = float(75)

KICK_MESS = 'kick %s %s ADVERTENCIA N-%s - Lenguaje vulgar, obsceno u ofensivo'
KICK_DATA = 'kick %s %s ADVERTENCIA N-%s - No debes compartir o solicitar datos personales'
WARN_UPPE = '¡ %s ! \00305\2ADVERTENCIA\3\2 N-%s - Evita el uso de las mayusculas'
WARN_REPE = '¡ %s ! \00305\2ADVERTENCIA\3\2 N-%s - Uso excesivo de una misma letra'
WARN_DATA = '¡ %s ! \00305\2ADVERTENCIA\3\2 N-%s - No debes compartir o solicitar datos personales'
BAN_MESS = 'b %s %s 1d mal comportamiento, lenguaje vulgar, obsceno u ofensivo'
WARN_MESS = '¡Hola %s! Soy un robot y esto es un mensaje automatico, '
WARN_MESS += '¿parece que te estas portando mal? No continues por favor :( '
WARN_MESS += 'o seras expulsado por un dia completo!!! Eso significa que no'
WARN_MESS += ' podras volver al chat hasta que se cumplan 24 horas!!! Esta es'
WARN_MESS += ' tu ultima advertencia. Y algo mas, ¡NO RESPONDAS! Como dije: '
WARN_MESS += 'Soy un robot automatizado y no comprendere nada de lo que digas'


from irc.handlers import handler
from irc.connection import servers as base
import urllib
import re


def loadpattern():
    for pattern in urllib.urlopen(URLPATT).read().splitlines():
        if len(pattern) == 0:
            continue
        PATTERN.append(re.compile(pattern, 2))


def loadnodata():
    ls = [
        ('(.{1,})?(\+58)?0?(4(12|14|16|24|26)|212)\d{6,7}', 1),
        ('(.{1,})?facebook', 1),
        ('(.{1,})?twitter', 0),
        ('(.{1,})?instagram', 0),
        ('(.{1,})?bbm', 0),
        ('(.{1,})?@gmail', 1),
        ('(.{1,})?@hotmail', 1),
        ('(.{1,})?@yahoo', 1),
        ('(.{1,})skype', 0),
        ('(.{1,})whatsapp', 1),
        ('(.{1,})telegram', 0),
        ('(.{1,})telefono', 1),
        ('(.{1,})celular', 1),
        ('(.{1,})cantv', 0),
        ('(.{1,})digitel', 0),
        ('(.{1,})movistar', 0)
        ]

    for pattern, lvl in ls:
        NODATA.append((re.compile(pattern, 2), lvl))


def loadignored():
    for host in urllib.urlopen(URLIGNO).read().splitlines():
        IGNORED.append(host)


def badwords(irc, nick, host, message):
    for pattern in PATTERN:
        for lin in message.split():
            if pattern.match(lin):
                if not host in RELAPSE:
                    RELAPSE[host] = 1
                else:
                    RELAPSE[host] = 5

                if RELAPSE[host] < LIMIT_RELAPSE:
                    irc.privmsg(KICKER, KICK_MESS % (CHANNEL, nick, RELAPSE[host]))
                    RELAPSE[host] = 3
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
                RELAPSE[host] = 5

            if RELAPSE[host] < LIMIT_RELAPSE:
                if lvl == 0:
                    irc.privmsg(CHANNEL, WARN_DATA % (nick, RELAPSE[host]))
                if lvl == 1:
                    irc.privmsg(KICKER, KICK_DATA % (CHANNEL, nick, RELAPSE[host]))
                    RELAPSE[host] = 3
                if (LIMIT_RELAPSE - RELAPSE[host]) == 1:
                    irc.privmsg(nick, WARN_MESS % nick)
                return True
            else:
                irc.privmsg(KICKER, BAN_MESS % (CHANNEL, nick))
                del RELAPSE[host]
                return True


def noupper(irc, nick, host, message):
    upper = 0
    lower = 0
    if len(message) <= 4:
        return

    for letter in message:
        if not letter.isalpha():
            continue
        elif letter.isupper():
            upper += 1
        else:
            lower += 1

    print [len(message), upper, lower]
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
        if group('target').lower() == self.base.nick.lower():
            if badwords(self, *group('nick', 'host', 'message')):
                return True
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
        else:
            if badwords(self, *group('nick', 'host', 'nick')):
                return True
            elif nodata(self, *group('nick', 'host', 'nick')):
                return True


loadignored()
loadpattern()
loadnodata()

from sysb import commands


@commands.addHandler('moderator', 'canaima (?P<command>add|del|ignore|unignore|on|off|reload)( (?P<optional>[^ ]+))?', {
    'sintax': 'canaima <on|off|add|del|ignore|unignore|reload>',
    'example': 'canaima ignore localhost',
    'desc': 'comando especial de moderacion para canaima'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o')
def moderator(irc, result, group, other):
    command = result('command').lower()
    option = result('optional')
    if command == 'on':
        if 9 in irc.local_handlers and pipe in irc.local_handlers[9]:
            pass
        else:
            base[SERVER][0].add_handler(pipe, 9, 'local')
        irc.notice(CHANNEL, 'moderador activado')
        return

    if command == 'off':
        if 9 in irc.local_handlers and pipe in irc.local_handlers[9]:
            del irc.local_handlers[9]
        irc.notice(CHANNEL, 'moderador desactivado')
        return

    if command == 'add':
        try:
            PATTERN.append(re.compile(option, 2))
        except:
            irc.notice(CHANNEL, 'error al agregar la badword')
        else:
            irc.notice(CHANNEL, 'badword agregada correctamente')
        return

    if command == 'del':
        try:
            for pattern in PATTERN:
                ok = False
                if pattern.match(option):
                    ok = True
                elif pattern.pattern == option:
                    ok = True

                if ok:
                    PATTERN.remove(pattern)
                    irc.notice(CHANNEL, 'expresion regular eliminada: ' + pattern.pattern)
        except:
            irc.notice(CHANNEL, 'error al agregar la badword')
        return

    if command == 'ignore':
        if option is None:
            irc.notice(CHANNEL, 'error no ingreso el parametro')
            return

        IGNORED.append(option)
        irc.notice(CHANNEL, 'se agrego %s a la lista de ignorados' % option)
        return

    if command == 'unignore':
        try:
            IGNORED.remove(option)
        except:
            irc.notice(CHANNEL, 'error al eliminar %s de la lista de ignorados' % option)
        else:
            irc.notice(CHANNEL, 'se elimino %s de la lista de ignorados' % option)
        return

    if command == 'reload':
        def clear(ls_varnames):
            for name in ls_varnames:
                try:
                    var = eval(name)
                    while 1:
                        var.pop()
                except:
                    continue

        clear(['IGNORED', 'PATTERN'])
        loadignored()
        loadpattern()
        irc.notice(CHANNEL, 'recargado correctamente!')
        return
