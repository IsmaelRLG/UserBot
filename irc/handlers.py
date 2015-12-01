# -*- coding: utf-8 -*-

from sysb.config import core as config
from time import sleep

import sysb.logg as logg

log = logg.getLogger(__name__)


def method_handler(events):
    def nanarana(method):
        def wrapper(self, irc, event_name, group):
            for event in events.upper().split():
                if event == event_name:
                    log.debug('handler ejecutado: ' + method.__name__)
                    return method(self, event_name, group)

            raise UnboundLocalError("it is not the required event")
        return wrapper
    return nanarana


def handler(name):
    def wawe(func):
        def tururu(self, _name_, group):
            for nam in name.split():
                #print [nam.upper(), _name_]
                if nam.upper() == _name_:
                    log.debug('handler ejecutado: ' + func.__name__)
                    return func(self, _name_, group)

            raise UnboundLocalError("it is not the required event")
        return tururu
    return wawe


@handler('ping')
def ponger(self, name, group):
    two = group('server2')
    if not two:
        two = ''

    self.pong(group('server1'), two)
    return True


@handler('error')
def error(self, name, group):
    import socket
    try:
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
    except socket.error:
        pass
    finally:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sleep(10)
    self.registered = False
    self.connect()
    return True


@handler('privmsg')
def version(self, name, group):
    if group('message').upper().endswith("\001VERSION\001") and \
        group('message').upper().startswith("\001VERSION\001"):
        vrn = config.obtconfig('VERSION')
        vrn = (vrn[0] + ' ' + '.'.join(str(num) for num in vrn[1:]))
        self.ctcp_reply(group('nick'), vrn)
        return True
    raise UnboundLocalError("it is not the required event")


@handler('kick')
def kick_rejoin(self, name, group):
    if group('victim') is self.base.nick:
        self.join(group('channel'))
        return True


@handler('nick')
def real_nick(self, name, group):
    if group('nick') is self.base.nick:
        self.base.nick = group('new_nick')
        return True


@handler('rpl_featurelist')
def load_feature(self, name, group):
    self.features.load(group('feature').split())
    return True


@handler('rpl_myinfo')
def registration_successful(self, name, group):
    self.registered = True
    from client import log
    log.info('Registro completado')
    self.attempted = 0

    from connection import servers

    for uuid, channel in servers[self.base.name][2]:
        self.join(channel['name'])


@handler('err_nicknameinuse')
def err_not_registered_nicknameinuse(self, name, group):
    import random

    rn = self.base.nick + '-' + str(random.choice(range(100000)))
    from client import log

    try:
        if self.registered is False:
            self.nick(rn)
        else:
            return None
    except AttributeError:
        self.nick(rn)
    finally:
        log.info('nick en uso %s, cambiando por %s' % (self.base.nick, rn))
        return True


@handler('privmsg')
def ctcp_ping(self, name, group):
    if group('message').startswith("\001PING "):
        self.ctcp_reply(group('nick'),
        'PING ' + group('message').strip('\001').strip('PING '))
        return True
    raise UnboundLocalError("it is not the required event")
