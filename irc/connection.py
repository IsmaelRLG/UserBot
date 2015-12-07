# -*- coding: utf-8 -*-

import client
import output

from sysb.config import core
from sysb import katheryn
from handlers import *
__output__ = []
servers = {}

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
global_handler(confirm_join_part)
global_handler(kickme)


def load_connections():

    ircbase = core.obtconfig('ircbase')
    if ircbase is None:
        return

    out = output.output()
    out.start()
    __output__.append(out)

    for base in ircbase:
        servers[base.name] = [client.ServerConnection(base)]
        servers[base.name].append(
        katheryn.users(servers[base.name][0], 'usr', {'post': {}}))
        servers[base.name].append(
        katheryn.channels(servers[base.name][0], 'chn'))
        if base.connect_to_beginning:
            servers[base.name][0].connect()
