# -*- coding: utf-8 -*-

from sysb import schedule
schemode = schedule.irc_schedule('mode')

def mode(server, target, command, time):
    schemode.add(server, None, 'mode', (target, command), {}, 1, time, hash(' '.join([target, command])))

def umode():
    pass