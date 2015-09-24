# -*- coding: utf-8 -*-

import Queue
import time

from cache import cache
from cache import addcache
from .. import handlers

handler = handlers.method_handler


class request(object):
    """
    clase madre para todas las solicitudes, esta clase debe ser heredada, y debe
    cumplir con una estricta escritura, de debe definir la funcion que hara la
    solicitud bajo el nombre de "execute", y el nombre de la funcion la cual
    procesara el resultado debe ser "func_reqs", esta funcion debe solicitar dos
    argumentos, el cual debe ser "name" y "group":
        * name -- contiene el nombre del evento procesado, el nombre por default
            es el nombre de una variable del modulo "ircregex"
        * group -- es el metodo "group" de un resultado de una expresion regular
            los grupos estan definidos por nombres, para consultar los nombres
            definidos revise manualmente el modulo "ircregex" y busque el nombre
            del evento y podra identificar los nombres de los grupos.

    programando una solicitud:
        Primero lo primero, la funcion "execute", enviara la solicitud equis al
        servidor, usando el objeto "irc" propio de la clase.

        Para retornar el resultado la funcion "func_reqs" se debe añadir a la
        cola y retornar "True"

    Argumentos de esta clase:
        irc - Objeto de IRC
        target - Objetivo al cual se realizara la solicitud de informacion
    """

    def __init__(self, irc, target):
        self.result = {}
        self.irc = irc
        if isinstance(target, str):
            target = target.lower()

        self.target = target
        self.queue = Queue.Queue()
        irc.add_handler(self.func_reqs, -1, 'local')
        time.sleep(0.3)
        self.execute()
        r = self.queue.get()
        addcache(self.target, r)
        irc.remove_handler(self.func_reqs, -1, 'local')
        self.result = r

    def __getitem__(self, item):
        try:
            return self.result[item]
        except KeyError:
            pass

    def __setitem__(self, name, item):
        self.result[name] = item

    def __repr__(self):
        return repr(self.result)


class whois(request):

    @cache('whois')
    def execute(self):
        self.irc.whois(self.target)

    @handler('rpl_whoisuser rpl_whoislogged rpl_endofwhois err_nosuchnick')
    def func_reqs(self, name, group):
        name = name.lower()
        if name is 'rpl_whoisuser' and group('nick') is self.target:
            self.result['mask'] = {
                'nick': group('nick'),
                'user': group('user'),
                'host': group('host'),
                'mask': '{}!{}@{}'.format(*group('nick', 'user', 'host')),
                'realname': group('realname')}
            return True

        elif name is 'rpl_whoislogged' and group('username') is self.target:
            self.result['is logged'] = group('account')
            return True

        elif name is 'rpl_endofwhois' and group('nick') is self.target:
            self.queue.put(self.result)
            return True

        elif name is 'err_nosuchnick' and group('nick') is self.target:
            self.result['error'] = 'No such nick/channel'
            self.queue.put(self.result)
            return True
        else:
            raise UnboundLocalError


class who(request):

    @cache('who')
    def execute(self):
        self.irc.who(self.target)

    @handler('rpl_whoreply rpl_endofwho err_nosuchnick')
    def func_reqs(self, name, group):
        name = name.lower()

        if name == 'rpl_whoreply':
            channel, user, host, server, nick, s, hopcount, realname = \
            group('line').split(' ', 7)
            if not self.target in (channel.lower(), nick.lower()):
                raise UnboundLocalError

            if not 'list' in self.result:
                self.result['list'] = []

            self.result['list'].append(['{}!{}@{}'.format(nick, user, host), s])
            return True

        elif name == 'rpl_endofwho' and group('name').lower() == self.target:
            self.queue.put(self.result)
            return True

        elif name == 'err_nosuchnick' and group('nick').lower() == self.target:
            self.result['error'] = 'No such nick/channel'
            self.queue.put(self.result)
            return True

        else:
            print 'soy una tetera!'
            raise UnboundLocalError


class list(request):
    mode = None

    @cache('list')
    def execute(self):
        self.irc.mode(self.target, '+' + self.mode)
        if self.mode is 'b':
            self.ls = {'end': 'rpl_endofbanlist', 'rpl': 'rpl_banlist'}
        elif self.mode is 'e':
            self.ls = {'end': 'rpl_endofexceptlist', 'rpl': 'rpl_exceptlist'}
        elif self.mode is 'i':
            self.ls = {'end': 'rpl_endofinvitelist', 'rpl': 'rpl_invitelist'}

    @handler('rpl_banlist rpl_invitelist rpl_exceptlist '
             'rpl_endofbanlist rpl_endofinvitelist rpl_endofexceptlist '
             'err_chanoprivsneeded err_notonchannel')
    def func_reqs(self, name, group):
        name = name.lower()
        channel = group('channel').lower()

        if channel is self.target and name is self.ls['rpl']:
            self.result.update(group('channel', 'mask', 'from', 'date'))
            return True
        elif channel is self.target and name is self.ls['end']:
            self.queue.put(self.result)
            return True
        elif channel is self.target and name is 'err_chanoprivsneeded':
            self.result['error'] = "I'm not channel operator"
            self.queue.put(self.result)
            return True
        elif channel is self.target and name is 'err_notonchannel':
            self.result['error'] = "I'm not on that channel"
            self.queue.put(self.result)
            return True
        else:
            raise UnboundLocalError
