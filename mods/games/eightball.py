# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from sysb.config import core
from sysb import i18n

import random
import json

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'games')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)
conf = json.load(file('mods/games/conf/{}/eightball.json'.format(lang)))


def eightball(irc, result, group, other):
    category = random.choice(['positive', 'negative', 'unknown'])
    irc.notice(other['target'], random.choice(conf[category]))
