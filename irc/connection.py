# -*- coding: utf-8 -*-

import client

from sysb.config import core as config
from handlers import *

import katheryn

chn = katheryn.nieto

SERVER_OBJECTS = {}

# Cargamos los controladores necesarios...
global_handler = client.ServerConnection.global_handlers
if not 0 in global_handler:
    global_handler.update({0: []})
    global_handler = global_handler[0].append

global_handler(ponger)
global_handler(error)
global_handler(version)
global_handler(real_nick)
global_handler(load_feature)
global_handler(registration_successful)
global_handler(err_not_registered_nicknameinuse)
global_handler(ctcp_ping)


def load_connections():

    ircbase = config.obtconfig('ircbase')
    if ircbase is None:
        return

    for base in ircbase:
        if base.name in SERVER_OBJECTS:
            continue

        SERVER_OBJECTS.update({base.name: client.ServerConnection(base)})
        if base.connect_to_beginning:
            SERVER_OBJECTS[base.name].connect()

        for channel in chn.channel_list(base.name):
            SERVER_OBJECTS[base.name].join(channel)
