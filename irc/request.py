# -*- coding: utf-8 -*-

import Queue
import time

from handlers import handler


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
        self.execute()
        irc.add_handler(self.func_reqs, 1, 'local')
        r = self.queue.get()
        time.sleep(0.3)
        irc.remove_handler(self.func_reqs, 1, 'local')
        return r


class whois(request):

    def execute(self):
        self.irc.who(self.target)

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
            self.result['is logget'] = group('account')
            return True

        elif name is 'rpl_endofwhois' and group('nick') is self.target:
            self.queue.put(self.result)
            return True

        elif name is 'err_nosuchnick' and group('nick') is self.target:
            self.result['nosuchnick'] = 'No such nick/channel'
            self.queue.put(self.result)
            return True
        else:
            raise UnboundLocalError


class who(request):

    def execute(self):
        self.irc.who(self.target)

    @handler('rpl_whoreply rpl_endofwho err_nosuchnick')
    def func_reqs(self, name, group):
        name = name.lower()

        if name is 'rpl_whoreply' and group('channel') is self.target:
            if not 'list' in self.result:
                self.result['list'] = []

            self.result['list'].append(
            '{}!{}@{}'.format(*group('nick', 'user', 'host')))
            return True

        elif name is 'rpl_endofwho' and group('nick') is self.target:
            self.queue.put(self.result)
            return True

        elif name is 'err_nosuchnick' and group('nick') is self.target:
            self.result['nosuchnick'] = 'No such nick/channel'
            self.queue.put(self.result)
            return True

        else:
            raise UnboundLocalError


