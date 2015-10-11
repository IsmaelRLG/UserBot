# -*- coding: utf-8 -*-

import util
import time
import logg
import re
import modes
from hashlib import sha1

import request
from config import core as config


log = logg.getLogger(__name__)

# Valores numericos
USER_NOT_REGISTERED = 0  # Usuario no registrado
INVALID_PARAMETER = 1  # Parametri invalido
OPERATION_SUCCESSFUL = 2  # Operancion exitosa
USER_REGISTERED = 3  # Usuario ya registrado
OPERATION_FAILED = 4  # Operacion fallida
CHANNEL_REGISTERED = 5  # Canal ya registrado
PERMISSION_DENIED = 6  # Permiso denegado
CHANNEL_NOT_REGISTERED = 7  # Canal no registrado


class usr:

    post = {}
    online = {}
    lc = config.obtconfig('lc')
    users = config.obtconfig('users')
    if users is None:
        users = {}

    def ch_passwd(self, server, username, new_passwd, irc=None):
        """Cambia la contraseña de usuario."""
        inf = self.info(server, username)
        if inf is not None:
            inf['passwd'] = util.hash(new_passwd)
            if self.ident_med(server, username) == 0:
                if self.identified(server, username) == OPERATION_SUCCESSFUL:
                    del self.online[server][util.uuid(username)]
            config.upconfig('users', self.users)
            return OPERATION_SUCCESSFUL

        return USER_NOT_REGISTERED

    def ch_ident(self, server, user, num, irc=None):
        if num in (0, 1):
            info = self.info(server, user)
            if not info['id'] == num:
                if info['id'] == 0:
                    if self.identified(server, user) == OPERATION_SUCCESSFUL:
                        del self.online[server][util.uuid(user)]

                info['id'] == num
                config.upconfig('users', self.users)
                return OPERATION_SUCCESSFUL

    def confirm_drop(self, code):
        """Comfirma la eliminacion del usuario."""
        try:
            code = self.post[code]
            server, username = code.decode('base64').split()
        except:
            return INVALID_PARAMETER
        if self.registered(server, username):
            if self.ident_med(server, username) == 0:
                if self.identified(server, username) == OPERATION_SUCCESSFUL:
                    del self.online[server][util.uuid(username)]

            del self.users[server][util.uuid(username)]
            config.upconfig('users', self.users)
            log.info('Usuario "%s" eliminado de "%s"' % (username, server))
            return OPERATION_SUCCESSFUL
        else:
            USER_NOT_REGISTERED

    def drop(self, server, username):
        """Retorna el codigo de confirmacion para eliminar una cuenta."""
        if self.registered(server, username):
            code = (server + ' ' + username).encode('base64').replace('\n', '')
            s = sha1(code).hexdigest()
            self.post.update({s: code})
            return s
        return USER_NOT_REGISTERED

    def identified(self, server, username, irc=None):
        """Retorna valores numericos si el usuario esta autenticado."""
        if not self.registered(server, username):
            return USER_NOT_REGISTERED

        if self.ident_med(server, username) == 0:
            if not server in self.online:
                self.online[server] = {}

                if util.uuid(username) in self.online[server]:
                    return OPERATION_SUCCESSFUL
                return OPERATION_FAILED
        else:
            pass


    def identify(self, server, username, host, password):
        """
        Identifica al usuaio como el propietario de la cuenta.
        """
        num = USER_NOT_REGISTERED
        if not server in self.online:
            self.online[server] = {}

        if self.registered(server, username):
            num = INVALID_PARAMETER
            if util.hash(password) == self.info(server, username)['passwd']:
                num = OPERATION_SUCCESSFUL
                id = util.uuid(username)  # lint:ok
                self.online[server][id] = {}
                self.online[server][id]['IDLE'] = time.time()
                self.online[server][id]['HOST'] = host
        return num

    def identify_oper(self, server, username, mask, opername, passwd, irc=None):
        """Identifica a un usuario como operador de userbot."""
        opers = config.obtconfig('oper_ls')

        num = self.identified(server, username, irc)
        if num == OPERATION_SUCCESSFUL:
            if opername in opers:
                if util.hash(passwd) == opers[opername]['passwd']:
                    if re.match(opers[opername]['pattern'], mask):
                        self.info(server, username).update({'status': 'oper'})
                        config.upconfig('users', self.users)
                        log.info('"%s" es ahora operador (%s) en "%s"' %
                        (username, opername, server))
                        return OPERATION_SUCCESSFUL
            return OPERATION_FAILED
        return num

    def info(self, server, username):
        """Retorna la informacion del usuario."""

        if self.registered(server, username):
            return self.users[server][util.uuid(username)]

    def isOper(self, server, username):
        """Retorna boolean si el usuario es operador o no."""
        if self.registered(server, username):
            return self.info(server, username)['status'] is 'oper'

    def lockAccount(self, server, username, victim, reason):
        """Congela una cuenta. Es necesario indicar la cuenta del operador."""
        if self.isOper(server, username):
            if self.registered(server, victim):
                if self.isLocked(server, victim):
                    info = self.info(server, victim)
                    info.update({'status': 'frozen'})
                    info['info']['lockReason'] = reason
                    config.upconfig('users', self.users)
                    log.info('"%s" congela la cuenta "%s" en "%s", razon: %s' %
                    (username, victim, server, reason))
                    return OPERATION_SUCCESSFUL
                return USER_REGISTERED
            return USER_NOT_REGISTERED
        return OPERATION_FAILED

    def lockReason(self, server, user):
        info = self.info(server, user)
        if not info:
            return USER_NOT_REGISTERED

        if self.isLocked(server, user):
            return info['info']['lockReason']

        return OPERATION_FAILED

    def register(self, server, username, password):
        """Registra un usuario nuevo en la base de datos."""
        if not self.registered(server, username):
            self.users[server].update({util.uuid(username): {
            'name': username,
            'passwd': util.hash(password),
            'data': time.ctime(),
            'lang': self.lc,
            'info': {'lockReason': ''},
            'status': 'allowed',
            'id': 0}})
            log.info('Nuevo usuario ("%s") registrado en "%s"' %
            (username, server))
            config.upconfig('users', self.users)
            return OPERATION_SUCCESSFUL
        else:
            return USER_REGISTERED

    def registered(self, server, username):
        """Retorna booleano si el usuario esta registrado o no"""

        if not server in self.users:
            self.users[server] = {}

        return util.uuid(username) in self.users[server]

    def unlockAccout(self, server, username, victim):
        """Descongela una cuenta. Es necesario indicar la cuenta del operador"""
        if self.isOper(server, username):
            if self.registered(server, victim):
                self.info(server, victim).update({'status': 'allowed'})
                config.upconfig('users', self.users)
                log.info('"%s" descongela la cuenta "%s" en "%s"' %
                (username, victim, server))
                return OPERATION_SUCCESSFUL
            return USER_NOT_REGISTERED
        return OPERATION_FAILED

    def isLocked(self, server, user):
        """Retorna booleano si la cuenta esta congelada o no."""
        if self.registered(server, user):
            return self.info(server, user)['status'] not in ('allowed', 'oper')


tona = usr()


class chn:

    FLAGS = {
        'F': 'Founder',
        'L': 'Lock handlers',
        'O': 'Auto-op',
        'S': 'Sucesor',
        'V': 'Auto-voice',
        'b': 'ban',
        'i': 'Invite',
        'k': 'Kick',
        'm': 'Mode',
        'o': 'Op',
        'r': 'Join & Part',
        's': 'sets',
        't': 'topic',
        'v': 'voice',
        '*': 'FLOSVbikmorstv'}
    chans = config.obtconfig('chans')
    if chans is None:
        chans = {}

    def register(self, server, channel, founder):
        if self.registered(server, channel):
            return CHANNEL_REGISTERED

        if not tona.registered(server, founder):
            return USER_NOT_REGISTERED

        self.chans[server.lower()][util.uuid(channel)] = {
            'flags': {},
            'templats': {
                # Default
                'FOUNDER': 'FLObikmorstv',
                'ADMIN': 'LSObikmorstv',
                'OP': 'Vbikmotv',
                'VOICE': 'Viv'},
            'sets': {
                # Default
                'VERBOSE': True},
            'name': channel,
            }
        self.setFlags(server, channel, founder, templats='FOUNDER')
        return OPERATION_SUCCESSFUL

    def registered(self, server, channel):
        server = server.lower()
        if not server in self.chans:
            self.chans[server] = {}

        return util.uuid(channel) in self.chans[server]

    def flags(self, server, channel, user):
        if not self.registered(server, channel):
            return CHANNEL_NOT_REGISTERED

        if not tona.registered(server, user):
            return USER_NOT_REGISTERED

        info = self.info(server, channel)
        if user.lower() in info['flags']:
            return info['flags'][user.lower()]
        return OPERATION_FAILED

    def setFlags(self, server, channel, user, flags=None, templats=None):
        user = user.lower()
        if not self.registered(server, channel):
            return CHANNEL_NOT_REGISTERED

        if not tona.registered(server, user):
            return USER_NOT_REGISTERED

        info = self.info(server, channel)
        if not user in info['flags']:
            info['flags'].update({user: ''})

        n = info['flags'][user]

        def delete(fl):
            if not fl in self.FLAGS:
                return
            if fl in info['flags'][user]:
                info['flags'][user].replace(fl, '')
                if not info['flags'][user]:
                    del info['flags'][user]
                    return 0

        def add(fl):
            if not fl in self.FLAGS:
                return
            if not fl in info['flags'][user]:
                info['flags'][user] = info['flags'][user] + fl

        if flags:
            for u in modes._parse_modes(flags, 'FLOSVbikmorstv'):
                ch, flag, n = u
                if ch is '-' and delete(flag) is 0:
                    break
                elif ch is '+':
                    add(flag)

        elif templats:
            if templats.upper() in info['templats']:
                info['flags'][user] = info['templats'][templats.upper()]
            else:
                return OPERATION_FAILED

        else:
            return OPERATION_FAILED

        s = []
        try:
            for i in info['flags'][user]:
                s.append(i)
        except KeyError:
            config.upconfig('chans', self.chans)
            return (n, None)

        s.sort()
        s = ''.join(s)
        s = None if not s else s

        if s:
            info['flags'][user] = s
            config.upconfig('chans', self.chans)
        n = None if not n else n
        return (n, s)

    def info(self, server, channel):
        if not self.registered(server, channel):
            return CHANNEL_NOT_REGISTERED

        return self.chans[server.lower()][util.uuid(channel)]

    def channel_list(self, server):
        server = server.lower()
        if not server in self.chans:
            self.chans[server] = {}

        ls = []
        for uuid, info in self.chans[server.lower()].items():
            ls.append(info['name'])

        return ls

    def drop(self, server, channel):
        if not self.registered(server, channel):
            return CHANNEL_NOT_REGISTERED

        del self.chans[server.lower()][util.uuid(channel)]
        config.upconfig('chans', self.chans)
        return OPERATION_SUCCESSFUL

nieto = chn()