# -*- coding: utf-8 -*-

import time
import logg

from config import core
from irc import util
from irc import modes
from irc import request


log = logg.getLogger(__name__)

#==============================================================================#
#                                                                              #
#            valores de los codigos numericos: resultados de retorno           #
#                                                                              #
#==============================================================================#

OPERATION_FAILED       = 0
PERMISSION_DENIED      = 1
INVALID_PARAMETER      = 2
USER_NOT_REGISTERED    = 3
CHANNEL_NOT_REGISTERED = 4
CHANNEL_REGISTERED     = 5
USER_REGISTERED        = 6
OPERATION_SUCCESSFULL  = 7

#==============================================================================#
#                                                                              #
#                Clase base de los gestores de base de datos                   #
#                                                                              #
#==============================================================================#


class database(object):

    def __init__(self, ircobject, name, extra=None):
        self.irc = ircobject
        self.name = name
        self.lang = core.obtconfig('lang')
        self.__core__ = core.obtconfig(name + '_' + self.irc.base.name.lower())
        if not self.core:
            self.core = {}
            core.addconfig(name + '_' + self.irc.base.name.lower(), self.core)

        if isinstance(extra, dict):
            for name, item in extra.items():
                setattr(self, name, item)

    def update(self, object):
        self.__core__.update(object)
        self.save

    @property
    def save(self):
        core.upconfig(self.name + '_' + self.irc.base.name.lower())

#==============================================================================#
#                                                                              #
#                      Gestor de base de datos: Usuarios                       #
#                                                                              #
#==============================================================================#


class users(database):

    def register(self, nickname, user, password):
        if util.uuid(user) in self.usrdatabase:
            return USER_REGISTERED

        rpl_whois = request.whois(self.irc, nickname)
        if rpl_whois['is logged'] and rpl_whois != user:
            return OPERATION_FAILED

        self.update({util.uuid(user): {
            'name': user,
            'time': time.time(),
            'lang': self.lang,
            'lock': [False],
            'status': 'user',
            'passwd': util.hash(password)}})
        return OPERATION_SUCCESSFULL

    def drop(self, code=None):
        if code in self.post:
            try:
                del self.online[self.post[code]]
                del self.__core__[self.post[code]]
            except KeyError:
                pass

        else:


