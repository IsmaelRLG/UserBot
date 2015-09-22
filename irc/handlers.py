# -*- coding: utf-8 -*-

from sysb.config import core as config
from time import sleep
import re


def handler(name):
    def wawe(func):
        def tururu(*args):
            if len(args) == 2:
                posc = 0
            else:
                posc = 1
            for i in name.split():
                if name.upper() is not args[posc]:
                    raise UnboundLocalError("it is not the required event")
                else:
                    return func(*args)
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
    self.disconnect(group('message'))
    sleep(4)
    self.connect()
    return True


@handler('privmsg')
def version(self, name, group):
    if group('message').endswith("\001VERSION\001") and \
        group('message').startswith("\001VERSION\001"):
        vrn = config.obtconfig('VERSION')
        vrn = (vrn[0] + ' ' + '.'.join(str(num) for num in vrn[1:]))
        self.ctcp_reply(group('nick'), vrn)
        return True


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


@handler('err_nicknameinuse')
def err_not_registered_nicknameinuse(self, name, group):
    import random

    try:
        if self.registered is False:
            self.nick(self.base.nick + '-' + str(random.choice(range(100000))))
        else:
            return None
    except AttributeError:
        self.nick(self.base.nick + '-' + str(random.choice(range(100000))))
    finally:
        return True


@handler('privmsg')
def ctcp_ping(self, name, group):
    result = re.match("\001PING (?P<code>.+)\001", group('message'))
    if result:
        self.ctcp_reply(group('nick'), 'PING ' + result.group('code'))
        return True
