# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import google
reload(google)

from sysb import commands
from google import lang
from google import _


commands.addHandler('google', 'img (?P<text2find>.*)', {
    'sintax': 'img <text to find>',
    'example': 'img cats',
    'desc': _('muestra una imagen de algo', lang)},
    anyuser=True)(google.images)


commands.addHandler('google', '(google|gl|search) (?P<text2find>.*)', {
    'sintax': 'google <text to find>',
    'example': 'google google',
    'alias': ('gl', 'search'),
    'desc': _('busca algo en google', lang)},
    anyuser=True)(google.search)
