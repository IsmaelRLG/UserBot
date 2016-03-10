# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import ip
reload(ip)

from sysb import commands
from ip import lang
from ip import _


commands.addHandler('ip', 'ip (?P<hostname>[^ ]+)', {
    'sintax': 'ip <hostname>',
    'example': 'ip 8.8.8.8',
    'desc': _('Geolocaliza una ip', lang)},
    anyuser=True)(ip.ip)


commands.addHandler('ip', 'ip2 (?P<hostname>[^ ]+)', {
    'sintax': 'ip2 <hostname>',
    'example': 'ip2 8.8.8.8',
    'desc': _('Geolocaliza una ip', lang)},
    anyuser=True)(ip.ip2)