# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import channels
reload(channels)

from sysb import commands
from channels import lang
from channels import _


commands.addHandler('channels', 'chan register( (?P<channel>[^ ]+))?', {
    'sintax': 'chan register <channel>?',
    'example': 'chan register #Foo',
    'desc': _('registra un canal en el bot', lang)},
    registered=True,
    logged=True,
    channels=True,
    chan_reqs='channel')(channels.register)


commands.addHandler('channels', 'chan flags( (?P<channel>#[^ ]+))? (?P<target>['
    '^ ]+) (?P<flags>[^ ]+)', {
    'sintax': 'chan flags <channel>? <target> <flags>',
    'example': 'chan flags #Foo-chan foo-user OP',
    'desc': _('(añade / elimina / edita / muestra) los flags', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='s',
    chan_reqs='channel')(channels.flags)


commands.addHandler('channels', 'chan drop( (?P<channel>#[^ ]+))?', {
    'sintax': 'chan drop <channel>?',
    'example': 'chan drop #foo',
    'desc': _('elimina un canal del bot', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='F',
    chan_reqs='channel')(channels.drop)