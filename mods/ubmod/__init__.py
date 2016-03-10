# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015-2016, Ismael R. Lugo G.
"""

import glob
import posixpath
import builder
reload(builder)


for name in glob.glob('mods/ubmod/ubmod/*.ini'):
    builder.ubmodule(posixpath.basename(name))
