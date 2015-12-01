# -*- coding: utf-8 -*-

import time
import logg

from config import core
from irc import util
from irc import modes


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
        if not self.lang:
            time.sleep(2)
            self.lang = core.obtconfig('lang')
        self.__core__ = core.obtconfig(name + '_' + self.irc.base.name)
        if not self.__core__:
            self.__core__ = {}
            core.addconfig(name + '_' + self.irc.base.name, self.__core__)

        if isinstance(extra, dict):
            for name, item in extra.items():
                setattr(self, name, item)

    def __getitem__(self, key):
        try:
            return self.__core__[str(util.uuid(key.lower()))]
        except KeyError:
            pass

    def __setitem__(self, key, item):
        self.__core__[str(util.uuid(key.lower()))] = item
        self.save

    def __delitem__(self, key):
        del self.__core__[str(util.uuid(key.lower()))]
        self.save

    def __repr__(self):
        return repr(self.__core__)

    def __iter__(self):
        return iter(self.__core__.items())

    def __len__(self):
        return len(self.__core__)

    def update(self, object):
        self.__core__.update(object)
        self.save

    @property
    def save(self):
        core.upconfig(self.name + '_' + self.irc.base.name, self.__core__)


#==============================================================================#
#                                                                              #
#                      Gestor de base de datos: Usuarios                       #
#                                                                              #
#==============================================================================#


class users(database):

    def __getitem__(self, key):
        if not isinstance(key, str):
            key = key['is logged']
            if key is None:
                return

        try:
            return self.__core__[str(util.uuid(key))]
        except KeyError:
            pass

    def register(self, rpl_whois):
        if not rpl_whois['is logged']:
            return OPERATION_FAILED

        if self[rpl_whois['is logged']]:
            return USER_REGISTERED

        user = rpl_whois['is logged']

        self[user] = {
            'name': user,
            'time': time.ctime(),
            'lang': self.lang,
            'lock': [False],
            'status': 'user'}
        return OPERATION_SUCCESSFULL

    def drop(self, code=None):
        if code in self.post:
            try:
                account = self.post[code]
                del self.post[code]
                del self[account]
            except KeyError:
                pass
            finally:
                return OPERATION_SUCCESSFULL
        return OPERATION_FAILED

    def gendropcode(self, rpl_whois):
        from hashlib import md5
        code = md5(str(hash(self[rpl_whois['is logged']]['name']))).hexdigest()
        self.post[code] = rpl_whois['is logged']
        return code

    def operid(self, name, passwd, rpl_whois):
        for oper in core.obtconfig('opers'):
            if oper['user'] == name and oper['passwd'] == util.hash(passwd):
                if isinstance(oper['level'], tuple):
                    lvl = oper['level'][0]
                    server = oper['level'][1]
                else:
                    lvl = oper['level']
                    server = self.irc.base.name

                ok = False

                if lvl in ('local', 'noob') and server == self.irc.base.name:
                    ok = True
                elif lvl == 'global':
                    ok = True

                if ok:
                    self[rpl_whois['is logged']]['status'] = lvl
                    return OPERATION_SUCCESSFULL
                else:
                    return OPERATION_FAILED
        return INVALID_PARAMETER

#==============================================================================#
#                                                                              #
#                      Gestor de base de datos: canales                        #
#                                                                              #
#==============================================================================#


class channels(database):

    def register(self, channel, account):
        if self[channel]:
            return CHANNEL_REGISTERED

        self[channel] = {
            'flags': {},
            'templates': {
                #Default
                'founder': 'FLObikmorstv',
                'admin': 'LSObikmorstv',
                'op': 'Vbikmotv',
                'voice': 'Vitv',
                'clear': ''},
            'sets': {},
            'name': channel}
        self.flags('set', channel, account, template='founder')
        return OPERATION_SUCCESSFULL

    def flags(self, action, *args, **kwargs):
        def set(channel, account, flag=None, template=None):
            if not account in self[channel]:
                self[channel]['flags'][account] = ''

            if template:
                template = template.lower()
                if not template in self[channel]['templates']:
                    return INVALID_PARAMETER

                self[channel]['flags'][account] =\
                self[channel]['templates'][template]
            elif flag:
                for op, ___, null in modes._parse_modes(flag, 'FLOSVbikmorstv'):
                    # op (operator) == -|+
                    # __ == flag name
                    # null == None

                    if op == '-':
                        if ___ in self[channel]['flags'][account]:
                            self[channel]['flags'][account] =\
                            self[channel]['flags'][account].replace(___, '')

                    elif op == '+':
                        if not ___ in self[channel]['flags'][account]:
                            self[channel]['flags'][account] += ___

            # sorter / deleter
            if self[channel]['flags'][account] == '':
                del self[channel]['flags'][account]
            else:
                flag = [l for l in self[channel]['flags'][account]]
                flag.sort()
                self[channel]['flags'][account] = ''.join(flag)

            self.save
            return OPERATION_SUCCESSFULL

        def get(channel, account, **kwargs):
            if not account in self[channel]['flags']:
                return
            return self[channel]['flags'][account]

        return {'get': get, 'set': set}[action](*args, **kwargs)

    def remove_user(self, account):
        save = False
        for uuid, channel in self:
            for user, flags in channel['flags'].items():
                if user == account:
                    del self[channel['name']]['flags'][user]
                    save = True

        if save:
            self.save

    def privs(self, channel, account, flag):
        return flag in self[channel]['flags'][account] if account in\
        self[channel]['flags'] else False
