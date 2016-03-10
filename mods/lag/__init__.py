# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import lag
reload(lag)

from sysb import commands
from lag import lang
from lag import _


commands.addHandler('lag', 'lag( (?P<target>.*))?', {
    'sintax': 'lag <target>?',
    'example': 'lag imcat',
    'desc': _('muestra el lag de un usuario', lang)},
    anyuser=True)
