# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import canaima
reload(canaima)

from sysb import commands

canaima = canaima.canaima()


commands.addHandler('canaima', 'canaima( (?P<channel>#[^ ]+))? switch '
    '(?P<switch>on|off)', {'sintax': 'canaima switch <on|off>',
    'example': 'canaima switch on',
    'desc': 'habilita la moderacion para canaima'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')(canaima.canaima_switch)

commands.addHandler('canaima', 'canaima( (?P<channel>#[^ ]+))? badword '
    '(?P<switch>add|del) (?P<phrase>.*)', {
    'sintax': 'canaima badword <add|del> <phrase|regex>',
    'example': 'canaima badword del canal',
    'desc': 'agrega o elimina alguna regex'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')(canaima.canaima_badwords)

commands.addHandler('canaima', 'canaima( (?P<channel>#[^ ]+))? whitelist'
    ' (?P<hostname>[^ ]+)', {
    'sintax': 'canaima whitelist <hostname>',
    'example': 'canaima whitlist 127.0.0.7',
    'desc': 'agrega o elimina un host a la lista blanca'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')(canaima.canaima_whitelist)

commands.addHandler('canaima', 'canaima( (?P<channel>#[^ ]+))? staff '
    ' (?P<nickname>[^ ]+)', {
    'sintax': 'canaima oper <nickname>',
    'example': 'canaima oper foonick',
    'desc': 'agrega o elimina un nick para las solicitudes de ayuda'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='t',
    chan_reqs='channel')(canaima.canaima_oper)

commands.addHandler('canaima', 'canaima( (?P<channel>#[^ ]+))? stats '
    ' (?P<stats>badboys|ip)', {
    'sintax': 'canaima stats <badboys|ip>',
    'example': 'canaima stats badboys',
    'desc': 'muestra estadisticas'},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='t',
    chan_reqs='channel')(canaima.canaima_stats)

commands.addHandler('canaima', 'can(a)?i(a)?ma-ayuda( (?P<command>.*))?', {
    'sintax': 'canaima-ayuda <mensaje>',
    'example': 'canaima-ayuda ayudenme!!!! Pepe me esta pegando!!!',
    'desc': 'comando especial de moderacion para canaima'},
    anyuser=True)(canaima.canaima_ayuda)
