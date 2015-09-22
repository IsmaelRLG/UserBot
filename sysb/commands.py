# -*- coding: utf-8 -*-

import re
import os
import imp
import glob
import logg
import types
import traceback

import pylocale
import katheryn

from util import thread
from util import is_channel
from config import core as config
from irc.client import buffer_input
from irc.ircregex import ALL

log = logg.getLogger(__name__)

trn = pylocale.turn('es', config.obtconfig('trs'), pylocale.parsename(__name__))

_ = trn.turn_tr_str

usr = katheryn.tona
chn = katheryn.nieto


class commands(object):

    modules = []
    handlers = []
    locks = config.obtconfig('locks_handlers')

    def __init__(self):
        self.proccess_commands()
        if self.locks is None:
            self.locks = {}

    def removeHandler(self, pattern):
        """
        Se elimina uno o mas handlers (comandos) mediante un patron.
        pattern
        """
        for index in self.searchHandler(pattern):
            log.debug("Command (handler) deleted: " +
                      self.handlers.pop(index)['name'])

    def searchHandler(self, pattern):
        """
        Retorna las posiciones de los handlers (comandos) que coincidan
        mendiante un patron.
        Argumentos:
        * pattern -- Patron a buscar
        """
        result = []
        for handler in self.handlers:
            for val, item in handler.items():
                if val is 'func':
                    item = item.__name__

                if not val in ('help', 'regex'):
                    if isinstance(val, list):
                        for u in val:
                            if re.match(pattern, val, re.IGNORECASE):
                                result.append(self.handlers.index(handler))
                        continue

                    if re.match(pattern, val, re.IGNORECASE):
                        result.append(self.handlers.index(handler))

        return result

    def lockHandler(self, pattern, server, channel=''):
        channel = channel.lower()
        for handler in self.searchHandler(pattern):
            echo = 0
            handler = self.handlers[handler]
            if not handler['name'] in self.locks:
                self.locks.update({handler['name']: {'server': {}}})
                echo += 1

            if not server in self.locks[handler['name']]:
                self.locks[handler['name']]['server'][server] = []
                echo += 1

            if channel and \
            not channel in self.locks[handler['name']]['server'][server]:
                self.locks[handler['name']]['server'][server].append(channel)
                echo += 1

            log.debug('Handler "%s" bloqueado [ %s ] para "%s" en "%s", b' %
            (handler['name'],
            echo > 0,
            server,
            'todos los canales' if not channel else channel))

    def unlockHandler(self, pattern, server, channel=''):
        channel = channel.lower()
        for handler in self.searchHandler(pattern):
            echo = 0
            handler = self.handlers[handler]
            if not handler['name'] in self.locks:
                return

            if server in self.locks[handler['name']] and not channel:
                del self.locks[handler['name']][server]
                echo += 1

            if channel and \
            not channel in self.locks[handler['name']]['server'][server]:
                self.locks[handler['name']]['server'][server].remove(channel)
                echo += 1

            log.debug('Handler "%s" desbloqueado [ %s ] para "%s" en "%s", b' %
            (handler['name'],
            echo > 0,
            server,
            'todos los canales' if not channel else channel))

    def load_modules(self, one=''):
        """
        Carga uno o todos los modulos que no hayan sido cargados.
        Argumentos:
        * one -- Nombre del modulo a cargar, si se especifica este argumento,
                 solo se cargara dicho modulo, de lo contrario se cargaran todos
        """
        ls = self.modules.items() if not one else [(one, self.modules[one])]

        for name, args in ls:
            if isinstance(args, types.ModuleType):
                continue

            self.modules.update({name: imp.load_module(name, *args)})
            log.debug('successfully loaded module "%s"' % name)

    def isLocked(self, name, server, channel=''):
        """
        Retorna el estado del handler, si esta bloqueado o no.
        """
        if not name in self.locks:
            return False

        if len(self.locks[name]['server'][server]) == 0:
            return True
        else:
            return channel.lower() in self.locks[name]['server'][server]

    def find_modules(self, path=''):
        """
        Busca modulos para su posterior importacion.
        Argumentos:
        * path -- Directorio (opcional) donde se buscaran los modulos de userbot
        """
        path = 'modules/*.py' if not path else path
        for file in glob.glob(path):
            file = file.replace('.py', '')
            name = os.path.split(file)[1]
            if not name in self.modules:
                self.modules[name] = imp.find_module(name)
                log.debug('module found "%s"' % name)

    def download_modules(self, name):
        for module in self.modules:
            if module.__name__ == name:
                # Quitamos los posibles bloqueos de los handlers D:
                for handler in self.searchHandler(name):
                    if not handler['name'] in self.locks:
                        continue

                    del self.locks[handler['name']]
                # Eliminamos los handlers
                self.removeHandler(name)
                # Eliminamos el modulo
                self.modules.remove(module)
                # Registramos los cambios
                log.debug('module removed "%s"' % name)

    @thread('commands', 1)
    def proccess_commands(self):

        while 0:
            irc, event, group = buffer_input.get()

            # Solo se procesaran: privmsg y notice
            if not event.upper() in ('PRIVMSG', 'NOTICE'):
                continue  # ups :c no es lo que necesito... El siguiente!

            try:
                server = irc.base.name
                nick_bot = irc.base.nick
                nick = group('nick')
                host = group('host')
                user = group('user')

                # ¿Es raro no?
                if nick == nick_bot:
                    continue
            except IndexError:
                nick = user = host = None
            finally:
                if (nick, user, host) == (None, None, None):
                    mask = group('machine')
                    if mask is None:
                        continue
                else:
                    mask = '{}!{}@{}'.format(nick, user, host)

            # Verificamos si se activa con alguno de los handlers...
            for handler in self.handlers:

                prefix = handler['prefix']
                if not prefix:
                    prefix = config.obtconfig('prefix')

                target = group('target')
                if target is nick_bot:
                    if not handler['regex']:
                        pass
                    elif handler['chn_req'][0]:
                        regex = handler['chn_req'][1]
                else:
                    if not handler['regex']:
                        pass
                    else:
                        regex = "(^{}[:, ]?|{})".format(
                        re.escape(nick_bot),
                        re.escape(prefix)) + handler['regex']

                try:
                    result = re.match(regex, group('message'), 2)
                    if not result:
                        continue  # Siguiente por favor!
                    else:
                        result = result.group
                except NameError:
                    result = group

                lc = usr.default_lang(irc.LC, server, nick)
                send = irc.err
                target = group('target')
                if target is nick_bot:
                    if handler['chn_req'][0]:
                        try:
                            channel = result(handler['chn_req'][2])
                        except IndexError:
                            send(nick,
                            _('debe especificar un canal', lc))
                            continue
                    else:
                        channel = ''

                    target = nick
                else:
                    channel = target

                if not target is nick_bot and handler['prv']:
                    send(target,
                    _('el comando solo debe ser usado en chat privado', lc))
                    continue

                if not handler['any']:
                    if handler['only_global_ops'] and not usr.isGlobalOP(nick):
                        if usr.isOper(server, nick):
                            m = _('Para ejecutar este comando "%s" se ', lc)
                            s = _('requiere de un Global-OP de UserBot', lc)
                            send(target, m + s)
                            continue
                        send(target,
                        _('Este comando "%s" es solo para operadores de UserBot', lc) % handler['name'])
                        continue

                    if handler['onlyops'] and not usr.isOper(server, nick):
                        send(target,
                        _('Este comando "%s" es solo para operadores de UserBot', lc) % handler['name'])
                        continue
                    if not usr.registered(server, nick):
                        send(target,
                        _('no se encuentra registrado, favor registrese.', lc))
                        continue

                    if not usr.identified(server, nick) is 2:
                        send(nick,
                        _('no se encuentra identificado, identifíquese.', lc))
                        continue

                    if usr.isLocked(server, nick):
                        send(nick,
                        _('su cuenta esta bloqueada, razon: ', lc) +
                        usr.lockReason(server, nick))
                        continue

                    if channel:

                        if not is_channel(channel):
                            send(target,
                            _('debe especificar un canal valido', lc))
                            continue

                        if handler['no_registered'] and \
                        not chn.registered(server, channel):
                            send(channel,
                            _('canal "%s" no registrado.', lc) % channel)
                            continue

                        if not handler['privs'] and not chn.prv(
                        server, channel, user, handler['privs']):
                            send(nick, _('Permiso denegado.', lc))
                            continue

                    if self.isLocked(handler['name'], server, channel):
                        if channel:
                            ext = channel
                        else:
                            ext = server

                        send(nick,
                        _('el comando "%s" esta bloqueado temporalmente para %s', lc) %
                        (handler['name'], ext))
                        continue

                # Si sobrevive a la masacre... se ejecuta xD
                try:
                    handler['func'](irc, group, result, vars())
                    continue
                except:
                    for line in traceback.format_exc().splitlines():
                        irc.err(target, line)

commands = commands()


def addHandler(regex, name, help, example, privs, mod_name, any=False,
               prv=False, chn_req=False, onlyops=False, only_global_ops=False,
               prefix='', thread=False, no_registered=False):
    """
    Decorador para añadir un handler al bot (commanditos xD)
    Argumentos:
    * regex -- Expresion regular para el comando
    * name -- Nombre del handler (comando)
    * help -- La descripcion o ayuda del comando
    * example -- Un/unos ejemplos de como usar el comando.
    * privs -- Nivel de privilegios requeridos para usar el comando.
    * mod_name -- Nombre del modulo al que pertenece
    * any -- Se marca si cualquiera puede usar el handler (commando).
    * prv -- Se marca si solo se escuchara el chat privado.
    * chn_req -- Se marca que es neceesario especificar un canal si el comando
                 es ejecutado en chat privado.
    """
    def wawe(func):
        mod_name = pylocale.parsename(mod_name)  # lint:ok
        commands.handlers.append(vars())
        log.debug('New command (handler) added: ' + func.__name__)

        def wrapper(*args, **kwargs):
            if thread:
                import thread
                thread.start_new(func, args, kwargs)

                def does_nothing(*a, **b):
                    pass
                return does_nothing(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper