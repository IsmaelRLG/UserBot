# -*- coding: utf-8 -*-

import re
import json

to_kick = []
conf = json.loads(file('mods/canaima/config.json').read())


def encode_dict(dictionary):
    for key, items in dictionary.items():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(items, unicode):
            items = items.encode('utf-8')
        elif isinstance(items, dict):
            encode_dict(items)
        del dictionary[key]
        dictionary.update({key: items})

encode_dict(conf)

import badwords
import nodata
import noupper
import noflood
import norepeat

from sysb import commands
from irc.handlers import handler
from irc.connection import servers as base


@handler('privmsg notice join rpl_whoreply rpl_endofwho')
#@thread(no_class=True, n='moderador')
def pipe(self, event, group):
    event = event.lower()
    if event == 'rpl_whoreply':
        multi = group('line').lower().split(' ', 7)
        channel, user, host, server, nick, s, hopcount, realname = multi
        if channel != conf["channel"].lower():
            raise UnboundLocalError("it is not the required event")
        for _host, message in to_kick:
            if _host == host and nick != self.base.nick.lower():
                self.kick(conf["channel"], nick, message)
        return True
    elif event == 'rpl_endofwho':
        if len(to_kick) > conf['count_limit']:
            for obj in to_kick:
                to_kick.remove(obj)
        return True

    if group('host') in conf['ignore']:
        raise UnboundLocalError("it is not the required event")

    if event == 'join':
        if group('channel').lower() == conf['channel']:
            self.privmsg(group('nick'), conf['welcome'])
            self.privmsg(group('nick'), conf['example'])
            return True
        else:
            raise UnboundLocalError("it is not the required event")

    if group('target').lower() != conf['channel']:
        if group('target').lower() == self.base.nick.lower():
            if badwords.func(self, *group('nick', 'host', 'message')):
                return True
        raise UnboundLocalError("it is not the required event")
    else:
        if noflood.func(self, *group('nick', 'host', 'message')):
            return True
        elif badwords.func(self, *group('nick', 'host', 'message')):
            return True
        elif nodata.func(self, *group('nick', 'host', 'message')):
            return True
        elif noupper.func(self, *group('nick', 'host', 'message')):
            return True
        elif norepeat.func(self, *group('nick', 'host', 'message')):
            return True
        else:
            if badwords.func(self, *group('nick', 'host', 'nick')):
                return True
            elif nodata.func(self, *group('nick', 'host', 'nick')):
                return True


@commands.addHandler('canaima', 'canaima (?P<command>add|del|ignore|unignore|on|off|reload|oper)( (?P<optional>[^ ]+))?', {
    'sintax': 'canaima <on|off|add|del|ignore|unignore|reload|oper>',
    'example': 'canaima ignore localhost',
    'desc': 'comando especial de moderacion para canaima'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o')
def canaima(irc, result, group, other):
    command = result('command').lower()
    option = result('optional')
    if command == 'on':
        if 9 in irc.local_handlers and pipe in irc.local_handlers[9]:
            pass
        else:
            base[conf['server']][0].add_handler(pipe, 9, 'local')
        irc.notice(conf['channel'], 'moderador activado')
        return

    if command == 'off':
        if 9 in irc.local_handlers and pipe in irc.local_handlers[9]:
            del irc.local_handlers[9]
        irc.notice(conf['channel'], 'moderador desactivado')
        return

    if command == 'add':
        try:
            badwords.PATTERNS.append(re.compile(option, 2))
        except:
            irc.notice(conf['channel'], 'error al agregar la badword')
        else:
            irc.notice(conf['channel'], 'badword agregada correctamente')
        return

    if command == 'del':
        try:
            for pattern in badwords.PATTERNS:
                ok = False
                if pattern.match(option):
                    ok = True
                elif pattern.pattern == option:
                    ok = True

                if ok:
                    badwords.PATTERNS.remove(pattern)
                    irc.notice(conf['channel'], 'expresion regular eliminada: ' + pattern.pattern)
        except:
            irc.notice(conf['channel'], 'error al agregar la badword')
        return

    if command == 'ignore':
        if option is None:
            irc.notice(conf['channel'], 'error no ingreso el parametro')
            return

        conf['ignore'].append(option)
        irc.notice(conf['channel'], 'se agrego %s a la lista de ignorados' % option)
        return

    if command == 'unignore':
        try:
            conf['ignore'].remove(option)
        except:
            irc.notice(conf['channel'], 'error al eliminar %s de la lista de ignorados' % option)
        else:
            irc.notice(conf['channel'], 'se elimino %s de la lista de ignorados' % option)
        return

    if command == 'reload':
        def clear(list):
            while 1:
                try:
                    list.pop()
                except IndexError:
                    return

        clear(badwords.PATTERNS)
        clear(nodata.PATTERNS)

        badwords.load()
        nodata.load()
        irc.notice(conf['channel'], 'recargado correctamente!')
        return

    if command == 'oper':
        if option is None:
            irc.notice(conf['channel'], 'error no ingreso el parametro')
            return

        if option in conf['opers']:
            conf['opers'].remove(option)
            irc.notice(conf['channel'], 'operador %s removido!' % option)
        else:
            conf['opers'].append(option)
            irc.notice(conf['channel'], 'operador %s agregado!' % option)
        return


@commands.addHandler('canaima', 'can(a)?i(a)?ma-ayuda( (?P<command>.*))?', {
    'sintax': 'canaima-ayuda <mensaje>',
    'example': 'canaima-ayuda ayudenme!!!! Pepe me esta pegando!!!',
    'desc': 'comando especial de moderacion para canaima'},
    anyuser=True)
def ayuda(irc, result, group, other):
    mess = result('command')
    target = other['target']
    if mess is None:
        irc.privmsg(target, '¿Porque no agregaste el mensaje de tu problema?')
        mess = 'no especificado'

    if len(mess) < 14:
        irc.privmsg(target, conf['not'])
        return

    for nick in conf['opers']:
        irc.privmsg(nick, '%s tiene un problema: %s' % (group('nick'), mess))

    irc.privmsg(target, 'se informo al personal de tu problema: ' + mess)
    irc.privmsg(target, conf['okay'])