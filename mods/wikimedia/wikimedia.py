# -*- coding: utf-8 -*-

from sysb.config import core
from sysb import commands
from sysb import Thread
from sysb import i18n

import json

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate'),
    'wikimedia')
_ = locale.turn_tr_str
lang = core.obtconfig('lang')
conf = json.load('mods/wikimedia/config.json')
logs = []


@commands.addHandler('wikimedia', 'logs rec (start|stop)', {
    'sintax': 'logs rec <start>|<stop>',
    'example': 'logs rec start',
    'desc': _('inicia o detiene el registro de los logs para wikimedia', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o')
def logging(irc, result, group, other):
    pass


@Thread.thread(init=True, n='wm-logs')
def wmve_logs():
    pass


wmve_logs()