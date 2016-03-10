# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import manager
reload(manager)

from sysb import commands
from manager import lang
from manager import _


commands.addHandler('manager', 'op( (?P<channel>#[^ ]+))?( (?P<target>.*))?',
    {'sintax': 'op <channel>? <target>',
    'example': 'op #Foo fuser fuser2',
    'desc': _('asigna estatus de operador a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')(manager.op)


commands.addHandler('manager', 'deop( (?P<channel>#[^ ]+))?( (?P<target>.*))?',
    {'sintax': 'deop <channel>? <target>',
    'example': 'deop #Foo fuser fuser2',
    'desc': _('remueve el estatus de operador a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')(manager.deop)


commands.addHandler('manager', 'v(oice)?( (?P<channel>#[^ ]+))?( (?P<target>.*'
    '))?', {'sintax': 'voice <channel>? <target>',
    'example': 'voice #Foo fuser fuser2',
    'alias': ('v',),
    'desc': _('asigna voice a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='v',
    chan_reqs='channel')(manager.voice)


commands.addHandler('manager', '(devoice|dv)( (?P<channel>#[^ ]+))?( (?P<targe'
    't>.*))?', {'sintax': 'devoice <channel>? <target>',
    'example': 'devoice #Foo fuser fuser2',
    'alias': ('dv',),
    'desc': _('remueve el voice a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='v',
    chan_reqs='channel')(manager.devoice)


commands.addHandler('manager', 'join (?P<channel>[^ ]+)( (?P<passwd>[^ ]+))?',
    {'sintax': 'join <channel> <password>?',
    'example': 'join #Foo',
    'desc': _('ingresa userbot a un canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='r',
    chan_reqs='channel')(manager.join)


commands.addHandler('manager', 'part (?P<channel>[^ ]+)( (?P<reason>.*))?',
    {'sintax': 'part <channel> <reason>?',
    'example': 'part #Foo Bye',
    'desc': _('saca a userbot de un canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='r',
    chan_reqs='channel')(manager.part)


commands.addHandler('manager', '(kick|k)( (?P<channel>#[^ ]+))? (?P<target>[^ '
    ']+)( (?P<reason>.*))?', {'sintax': 'kick <channel>? <target> <reason>?',
    'example': 'kick #Foo fuser bad boy',
    'alias': ('k',),
    'desc': _('expulsa a un usuario de un canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='k',
    chan_reqs='channel')(manager.kick)


commands.addHandler('manager', 'b(an)?( (?P<channel>#[^ ]+))? (?P<target>[^ ]+'
    ')( (?P<time>(?P<num>\d)(?P<alpha>[YMDHMS]{1})))?( (?P<message>.*))?',
    {'sintax': 'ban <channel>? <target> <time>?',
    'example': 'ban #Foo fuser 1d',
    'alias': ('b',),
    'desc': _('banea a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='b',
    chan_reqs='channel')(manager.ban)


commands.addHandler('manager', '(invite|iv)( (?P<channel>#[^ ]+))? (?P<target>.*)',
    {'sintax': 'invite <channel>? <target> <target1>? <target2>? <targetN>?',
    'example': 'invite pepe',
    'alias': ('iv',),
    'desc': _('invita a un usuario al canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='i',
    chan_reqs='channel')(manager.invite)