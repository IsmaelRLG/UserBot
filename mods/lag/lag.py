# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from sysb import i18n
from sysb.config import core
from irc.handlers import handler
from irc.connection import global_handler

import time

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'lag')
_ = locale.turn_tr_str

__lag__ = {}
lang = core.obtconfig('lang', cache=True)


@handler('notice err_nosuchnick')
def lag_pipe(self, event, group):
    if event == 'NOTICE':
        message = group('message')
        if message.startswith("\001PING "):
            username_id = message.strip('\001').strip('PING ')
            for username_id2, tuple in __lag__.items():
                if username_id == username_id2:
                    target, username, idle = tuple
                    userlag = time.time() - idle
                    self.notice(target, '%s lag: %.2fs' % (username, userlag))
                    del __lag__[username_id]
                    return True
                elif (time.time() - tuple[2]) > 10800:
                    del __lag__[username_id2]
            raise UnboundLocalError("it is not the required event")
    elif event == 'ERR_NOSUCHNICK':
        nick = group('nick')
        username_id = str(hash(nick.lower())).replace('-', '')
        if username_id in __lag__:
            target, username, idle = __lag__[username_id]
            self.err(target, '%s: %s' % (nick, group('message')))
            del __lag__[username_id]
            return True
        raise UnboundLocalError("it is not the required event")


def lag(irc, result, group, other):
    username = result('target')
    if not username:
        username = group('nick')

    username_id = str(hash(username.lower())).replace('-', '')
    __lag__[username_id] = (other['target'], username, time.time())
    irc.ctcp('PING', username, username_id)

global_handler(lag_pipe)  # Añadimos el handler!
