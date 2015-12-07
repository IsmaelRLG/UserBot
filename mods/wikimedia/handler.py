# -*- coding: utf-8 -*-

from wikimedia import conf
from wikimedia import logs
from irc.handlers import handler
from irc.connection import servers as base


@handler(' '.join(conf['events']))
def tunneling(self, event, group):
    event = event.lower()
    if event in 'privmsg notice':
        pass
    elif event == 'join':
        pass
    elif event == 'part':
        pass
    elif event == 'quit':
        pass
    elif event == 'kick':
        pass
    elif event == 'mode':
        pass


base[conf['server']][0].add_handler(tunneling, 4, 'local')