# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import help
reload(help)

from sysb import commands
from help import lang
from help import _


commands.addHandler('help', '(help|man|ayuda)( (?P<command>.*))?', {
    'sintax': 'help <command>?',
    'example': 'help help',
    'alias': ('man', 'ayuda'),
    'desc': _('muestra la ayuda de algun comando', lang)},
    anyuser=True)(help.help)
