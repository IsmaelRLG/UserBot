# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import admin
reload(admin)

from sysb import commands
from admin import lang
from admin import _


commands.addHandler('admin', 'admin id (?P<name>[^ ]+) (?P<passwd>[^ ]+)', {
    'sintax': 'admin id <name> <password>',
    'example': 'admin id root 1234',
    'desc': _('identifica a un usuario como operador en userbot', lang)},
    registered=True,
    logged=True)(admin.operid)


commands.addHandler('admin', 'admin lock (?P<account>[^ ]+) (?P<reason>.*)', {
    'sintax': 'admin lock <account> <reason>',
    'example': 'admin lock fooser bad boy',
    'desc': _('bloquea a un usuario en userbot', lang)},
    registered=True,
    oper=('local', 'global'),
    logged=True)(admin.lock_user)


commands.addHandler('admin', 'admin unlock (?P<account>[^ ]+)', {
    'sintax': 'admin unlock <account>',
    'example': 'admin unlock fooser',
    'desc': _('desbloquea a un usuario en userbot', lang)},
    oper=('local', 'global'),
    registered=True,
    logged=True)(admin.unlock_user)


commands.addHandler('admin', 'admin flags (?P<channel>[^ ]+) (?P<target>[^ ]+) (?P<flags>[^ ]+)', {
    'sintax': 'admin flags <channel> <target> <flags/template>',
    'example': 'admin flags #Foo fooser founder',
    'desc': _('fuerza el cambio de flags en un canal', lang)},
    oper=('noob', 'local', 'global'),
    logged=True,
    registered=True,
    channels=True,
    chn_registered=True,
    chan_reqs='channel')(admin.flags)


commands.addHandler('admin', 'admin add (?P<level>[^ ]+) (?P<name>[^ ]+) (?P<sh'
    'a_passwd>[^ ]+)', {'sintax': 'admin add <level> <name> <sha_passwd>',
    'example': 'admin add local/freenode root 81dc9bdb52d04dc20036dbd8313ed055',
    'desc': (
        _('añade un nuevo operador de userbot segun el nivel dado', lang),
        _('niveles disponibles: global local/servidor noob/servidor', lang))},
    oper=('global',),
    registered=True,
    logged=True)(admin.addoper)


commands.addHandler('admin', 'admin del (?P<name>[^ ]+)', {
    'sintax': 'admin del <name>',
    'example': 'admin del root',
    'desc': _('elimina un operador de userbot', lang)},
    oper=('global',),
    registered=True,
    logged=True)(admin.deloper)


commands.addHandler('admin', 'admin load (?P<module>[^ ]+)', {
    'sintax': 'admin load <module>',
    'example': 'admin load users.py',
    'desc': _('carga un modulo a userbot', lang)},
    oper=('global',),
    registered=True,
    logged=True)(admin.load_module)


commands.addHandler('admin', 'admin download (?P<module>[^ ]+)', {
    'sintax': 'admin download <module>',
    'example': 'admin download users.py',
    'desc': _('descarga un modulo de userbot', lang)},
    oper=('global',),
    registered=True,
    logged=True)(admin.download_module)


commands.addHandler('admin', 'admin join (?P<channel>[^ ]+)( (?P<passwd>[^ ]+))?', {
    'sintax': 'admin join <channel> <password>?',
    'example': 'admin join #Foo',
    'desc': _('ingresa userbot a un canal', lang)},
    oper=('noob', 'local', 'global'),
    registered=True,
    logged=True)(admin.join)


commands.addHandler('admin', 'admin mode (?P<target>[^ ]+) (?P<mode>.*)', {
    'sintax': 'admin mode <target> <mode>',
    'example': 'admin mode #Foo +b *!*@localhost',
    'desc': _('establece un modo de canal / usuario', lang)},
    oper=('local', 'global'),
    registered=True,
    logged=True)(admin.mode)


commands.addHandler('admin', 'admin say (?P<target>[^ ]+) (?P<message>.*)', {
    'sintax': 'admin say <target> <message>',
    'example': 'admin say #Foo Hi!',
    'desc': _('envia un mensaje equis a traves de userbot', lang)},
    oper=('local', 'global'),
    registered=True,
    logged=True)(admin.say)


commands.addHandler('admin', 'admin connect (?P<servername>[^ ]+)', {
    'sintax': 'admin connect <servername>',
    'example': 'admin connect localhost',
    'desc': _('conecta a userbot a un servidor especificado', lang)},
    oper=('global',),
    registered=True,
    logged=True)(admin.connect_to)


commands.addHandler('admin', 'admin disconnect (?P<servername>[^ ]+)', {
    'sintax': 'admin disconnect <servername>',
    'example': 'admin disconnect localhost',
    'desc': _('desconecta a userbot de un servidor', lang)},
    oper=('global',),
    registered=True,
    logged=True)(admin.disconnect_to)


commands.addHandler('admin', 'admin exec (?P<code>.*)', {
    'sintax': 'admin exec <code>',
    'example': 'admin exec ", ".join(commands.commands.modules.keys())',
    'desc': _('ejecuta codigo Python y responde lo retornado', lang)},
    oper=('global',),
    registered=True,
    logged=True)(admin.execute)


commands.addHandler('admin', 'admin uptime', {
    'sintax': 'admin uptime',
    'example': 'admin uptime',
    'desc': _('muestra el tiempo de actividad', lang)},
    oper=('local', 'global'),
    registered=True,
    logged=True)(admin.uptime)


commands.addHandler('admin', 'admin nick (?P<newnick>[^ ]+)', {
    'sintax': 'admin nick <newnick>',
    'example': 'admin nick Super_UserBot',
    'desc': _('cambia de nick', lang)},
    oper=('local', 'global'),
    registered=True,
    logged=True)(admin.nick)