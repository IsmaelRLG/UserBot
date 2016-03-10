# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import users
reload(users)

from sysb import commands
from users import lang
from users import _


commands.addHandler('users', 'user register', {
    'sintax': 'user register',
    'example': 'user register',
    'desc': _('registra un usuario en el bot', 'es')},
    logged=True)(users.register)


commands.addHandler('users', 'user drop', {
    'sintax': 'user drop',
    'example': 'user drop',
    'desc': _('elimina a un usuario registrado', 'es')},
    registered=True,
    logged=True)(users.drop)


commands.addHandler('users', 'user confirm_drop (?P<code>[^ ]+)', {
    'sintax': 'user confirm_drop <code>',
    'example': 'user confirm_drop 6adf97f83acf6453d4a6a4b1070f3754',
    'desc': _('confirma la eliminacion de un usuario', 'es')},
    registered=True,
    logged=True)(users.confirm_drop)


commands.addHandler('users', 'user lang (?P<langcode>[^ ]+)', {
    'sintax': 'user lang <langcode>',
    'example': 'user lang en',
    'desc': (
      _('cambia el idioma que se muestra al usuario', 'es'),
      _('extra: codigo especial "list" muestra los idiomas soportados', lang))},
    registered=True,
    logged=True)(users.set_lang)


commands.addHandler('users', 'user info( (?P<account>[^ ]+))?', {
    'sintax': 'user info <account>?',
    'example': 'user info foo',
    'desc': _('muestra informacion de un usuario en userbot', 'es')},
    anyuser=True)(users.info)