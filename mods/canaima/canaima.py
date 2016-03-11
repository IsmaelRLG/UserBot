# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import re
import json
import time
import urllib

from irc.handlers import method_handler as handler
from irc.connection import global_handler
from irc.client import ServerConnection as __irc__

# Zona de variables
to_kick = []
genl = {}
conf = json.load(file('mods/canaima/config.json'))
stats = json.load(file('mods/canaima/stats.json'))


# Zona de importacion
import badwords
reload(badwords)

import nodata
reload(nodata)

import noupper
reload(noupper)

import noflood
reload(noflood)

import norepeat
reload(norepeat)


class canaima:

    def __init__(self):
        conf_decode = self.JSONDecoder(conf)
        conf.clear()
        conf.update(conf_decode)

        if conf['switch'] == 'on':
            self.addpipe()

    def saveconfig(self):
        json.dump(conf, file('mods/canaima/config.json', 'w'), indent=4)

    def pipe_status(self):
        return self.pipe in __irc__.global_handlers[0]

    def JSONDecoder(self, confdict, codec='utf-8'):
        SUB_Json = {}
        for value, item in confdict.items():
            if isinstance(value, unicode):
                value = value.encode(codec)
            if isinstance(item, unicode):
                item = item.encode(codec)
            if isinstance(item, dict):
                item = self.JSONDecoder(item)
            if isinstance(item, list):
                for index in item:
                    if isinstance(index, unicode):
                        posc = item.index(index)
                        item.remove(index)
                        item.insert(posc, index.encode(codec))
                        continue
                    if isinstance(index, list):
                        posc = item.index(index)
                        item.remove(index)
                        item.insert(posc, self.JSONDecoder({0: index})[0])
                        continue
                    if isinstance(index, dict):
                        posc = item.index(index)
                        item.remove(index)
                        item.insert(posc, self.JSONDecoder(index))
                        continue
            SUB_Json[value] = item
        return SUB_Json

    def addpipe(self):
        if not self.pipe_status():
            global_handler(self.pipe)
            conf['switch'] = 'on'
            self.saveconfig()
            return True
        return False

    def delpipe(self):
        if self.pipe_status():
            __irc__.global_handlers[0].remove(self.pipe)
            conf['switch'] = 'off'
            self.saveconfig()
            return True
        return False

    def geoip(self, host):
        page = urllib.urlopen('http://freegeoip.net/json/' + host)
        results = json.loads(page.read())

        for param in results:
            if not results[param]:
                results[param] = 'unknow'

            country = 'unknow'
            if 'country_name' in results:
                country = results['country_name'].lower()
                if not country in stats:
                    stats[country] = {'total': 1, 'estados': {}}
                else:
                    stats[country]['total'] += 1

            state = 'unknow'
            if 'region_name' in results:
                state = results['region_name'].lower()
                if not state in stats[country]['estados']:
                    stats[country]['estados'][state] = {'total': 1, 'ciudades': {}}
                else:
                    stats[country]['estados'][state]['total'] += 1

            city = 'unknow'
            if 'city' in results:
                city = results['city'].lower()
                if not city in stats[country]['estados'][state]['ciudades']:
                    stats[country]['estados'][state]['ciudades'][city] = {'total': 0}
                else:
                    stats[country]['estados'][state]['ciudades'][city]['total'] += 1
            json.dump(stats, file('mods/canaima/stats.json', 'w'))

    @handler('privmsg notice join rpl_whoreply rpl_endofwho')
    def pipe(self, irc, event, group):
        event = event.lower()

        if event == 'rpl_whoreply':
            multi = group('line').lower().split(' ', 7)
            channel, user, host, server, nick, s, hopcount, realname = multi
            if channel != conf["channel"].lower():
                raise UnboundLocalError("it is not the required event")
            for _host, message in to_kick:
                if _host == host and nick != irc.base.nick.lower():
                    irc.kick(conf["channel"], nick, message)
            return True
        elif event == 'rpl_endofwho':
            if len(to_kick) > conf['count_limit']:
                for obj in to_kick:
                    to_kick.remove(obj)
            return True

        try:
            host = group('host')
            nick = group('nick')
        except IndexError:
            raise UnboundLocalError("it is not the required event")

        if host in conf['ignore']:
            raise UnboundLocalError("it is not the required event")

        if event == 'join':
            if group('channel').lower() == conf['channel']:
                irc.privmsg(nick, conf['welcome'])
                irc.privmsg(nick, conf['example'])

                if conf['geoip'] == 'enable':
                    try:
                        self.geoip(host)
                    except:
                        return True
                    else:
                        return True
                else:
                    return True

        if event in ('privmsg', 'notice'):
            target = group('target').lower()
            message = group('message')
            if target != conf['channel']:
                if target == irc.base.nick.lower():
                    if badwords.func(irc, nick, host, message, pre=u'privmsg: '):
                        return True
                    elif norepeat.func(irc, nick, host, message, pre=u'privmsg: '):
                        return True
                raise UnboundLocalError("it is not the required event")

            else:
                if noflood.func(irc, nick, host, message):
                    return True
                elif badwords.func(irc, nick, host, message):
                    return True
                elif nodata.func(irc, nick, host, message):
                    return True
                elif noupper.func(irc, nick, host, message):
                    return True
                elif norepeat.func(irc, nick, host, message):
                    return True
                else:
                    if badwords.func(irc, nick, host, nick):
                        return True
                    elif nodata.func(irc, nick, host, nick):
                        return True

    def canaima_switch(self, irc, result, group, other):
        switch = result('switch')
        if switch == 'on':
            if self.addpipe():
                irc.notice(conf['channel'], 'moderador activado')
            else:
                irc.err(conf['channel'], 'moderador activado')
        elif switch == 'off':
            if self.delpipe():
                irc.notice(conf['channel'], 'moderador desactivado')
            else:
                irc.err(conf['channel'], 'moderador desactivado')

    def canaima_badwords(self, irc, result, group, other):
        phrase = result('phrase')
        switch = result('switch')
        if switch == 'add':
            try:
                badwords.PATTERNS.append(re.compile(phrase, 2))
            except:
                irc.err(conf['channel'], 'al agregar la badword')
            else:
                irc.notice(conf['channel'], 'badword agregada correctamente')
        elif switch == 'del':
            try:
                for pattern in badwords.PATTERNS:
                    ok = False
                    if pattern.match(phrase):
                        ok = True
                    elif pattern.pattern == phrase:
                        ok = True

                    if ok:
                        badwords.PATTERNS.remove(pattern)
                        irc.notice(conf['channel'],
                        'expresion regular eliminada: ' + pattern.pattern)
                raise ValueError
            except:
                irc.err(conf['channel'], 'al eliminar la badword')

    def canaima_whitelist(self, irc, result, group, other):
        host = result('hostname')

        if host in conf['ignore']:
            conf['ignore'].remove(host)
            irc.notice(conf['channel'], '%s: removido' % host)
        else:
            conf['ignore'].append(host)
            irc.notice(conf['channel'], '%s: agregado' % host)
        self.saveconfig()

    def canaima_oper(self, irc, result, group, other):
        nick = result('nickname')

        if nick in conf['opers']:
            conf['opers'].remove(nick)
            irc.notice(conf['channel'], 'operador %s removido!' % nick)
        else:
            conf['opers'].append(nick)
            irc.notice(conf['channel'], 'operador %s agregado!' % nick)
        self.saveconfig()

    def canaima_stats(self, irc, result, group, other):
        stats = result('stats')
        if stats == 'badboys':
            msg = 'Hasta ahora... '
            msg += '%d han dicho malas palabras, '
            msg += '%d han hecho flood, '
            msg += '%d han compartido o solicitado datos personales, '
            msg += '%d han usado excesivamente una misma letra, '
            msg += '%d han usado mayusculas.'
            msg = msg % (
                len(badwords.RELAPSE),
                len(noflood.RELAPSE),
                len(nodata.RELAPSE),
                len(norepeat.RELAPSE),
                len(noupper.RELAPSE))
            irc.notice(conf['channel'], msg)

        elif stats == 'ip':
            ch = other['target']
            irc.notice(ch, 'estadisticas de pais/estado/ciudad')
            for pais, item in stats.items():
                if isinstance(pais, unicode):
                    pais = pais.encode('utf-8')

                irc.notice(ch, '%s - %d' % (pais, item['total']))
                for estado, e_item in item['estados'].items():
                    if isinstance(estado, unicode):
                        estado = estado.encode('utf-8')

                    msg = '  \342\212\242 %s - %d' % (estado, e_item['total'])
                    irc.notice(ch, msg)

                    for ciudad, c_item in e_item['ciudades'].items():
                        if isinstance(ciudad, unicode):
                            ciudad = ciudad.encode('utf-8')

                        msg = '    \342\212\242 %s - %d' % (ciudad, c_item['total'])
                        irc.notice(ch, msg)

    def canaima_ayuda(self, irc, result, group, other):
        mess = result('command')
        host = group('host')
        nick = group('nick')
        target = other['target']
        if not host in genl:
            genl[host] = time.time()
        elif (time.time - genl[host]) < 3600:
            irc.privmsg(target, 'Ya hay una solicitud activa, espera un poco!')
            return
        else:
            genl[host] = time.time()

        if mess is None:
            irc.privmsg(target, '¿No agregaste el mensaje de tu problema?')
            mess = 'no especificado'

        if len(mess) < 14:
            irc.privmsg(target, conf['not'])
            return

        for nick in conf['opers']:
            irc.privmsg(nick, '%s tiene un problema: %s' % (nick, mess))

        irc.privmsg(target, 'se informo al personal de tu problema: ' + mess)
        irc.privmsg(target, conf['okay'])
