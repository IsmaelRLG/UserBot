# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import translate
reload(translate)

from sysb import commands
from translate import lang
from translate import _


commands.addHandler('translate', '(tr|translate)2 (?P<in>[^ ]+) (?P<out>[^ ]+) '
    '(?P<text>.*)', {'sintax': 'tr2 <input> <output> <text>',
    'example': 'tr2 en es Hello!',
    'alias': ('traslate2',),
    'desc': _('Traduce un texto de un idioma a otro', lang)},
    anyuser=True)(translate.translate2_1)


commands.addHandler('translate', '(tr|translate) (?P<in>[^ ]+) (?P<out>[^ ]+) ('
    '?P<text>.*)', {'sintax': 'tr <input> <output> <text>',
    'example': 'tr en es Hello!',
    'alias': ('traslate',),
    'desc': _('Traduce un texto de un idioma a otro', lang)},
    anyuser=True)(translate.translate2_2)
