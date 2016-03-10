# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import eightball
reload(eightball)

from sysb import commands
from eightball import lang
from eightball import _

commands.addHandler('games', '(dime|ask|question|eightball) .*', {
    'sintax': "eightball <question>?",
    'example': "eightball i'm sexy?",
    'alias': ('dime', 'ask', 'question'),
    'desc': _('Juego: responde una pregunta de forma aleatoria', lang)},
    anyuser=True)(eightball.eightball)
