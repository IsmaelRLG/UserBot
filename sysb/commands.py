# -*- coding: utf-8 -*-

import threading
import logg
import glob
import imp
import sys
import os
import database
import ircregex
import re
import types

from config import core as config
from client import buffer_input

log = logg.getLogger(__name__)


class commands:
    handlers = []
    locks = config.obtconfig('locks_handlers')
    modules = []
    if locks is None:
        locks = {}

    def addHandler(self, cname, csintax, chelp, cregex, privs, func, modname
                   listenonly=''):
        """
        Añade un handler al bot (commanditos :3)
        Argumentos:
        * cname -- Nombre del handler (comando)
        * csintax -- La sintaxis del comando
        * chelp -- La descripcion o ayuda del comando
        * cregex -- Expresion regular para el comando
        * privs -- Nivel de privilegios requeridos para usar el comando.
        * func -- Funcion a utilizar
        * modname -- Nombre del modulo al que pertenece
        * listenonly -- Solo escuchar un medio, por ejempo: solo el chat privado
        """
        h = {}
        h['cname'] = cname
        h['csintax'] = csintax
        h['chelp'] = chelp
        h['cregex'] = ircregex.cmd if not cregex else cregex
        h['privs'] = privs
        h['listenonly'] = listenonly
        h['func'] = func

        self.handlers.append(h)
        log.debug('Nuevo comando añadido: "%s"' % cname)

    def removeHandler(self, pattern):
        """
        Se elimina uno o mas handlers (comandos) mediante un patron.
        pattern
        """
        for index in self.searchHandler(pattern):
            cmd = self.handlers.pop(index)
            log.debug('Comando removido: "%s"' % cmd['cname'])

    def searchHandler(self, pattern):
        """
        Retorna las posiciones de los handlers (comandos) que coincidan
        mendiante un patron.
        Argumentos:
        * pattern -- Patron a buscar
        """
        result = []
        for handler in self.handlers:
            for vals in handler.items():
                if not vals in ('func', 'chelp', 'cregex'):
                    if re.match(pattern, vals, re.IGNORECASE):
                        result.append(self.handlers.index(handler))

        return result

    def lockHandler(self, pattern, server, channel=''):
        for handler in self.searchHandler(pattern):
            echo = 0
            handler = self.handlers[handler]
            if not handler['cname'] in self.locks:
                self.locks.update({handler['cname']: {'server': {}}})
                echo += 1

            if not server in self.locks[handler['cname']]:
                self.locks[handler['cname']]['server'][server] = []
                echo += 1

            if channel and \
            not channel in self.locks[handler['cname']]['server'][server]:
                self.locks[handler['cname']]['server'][server].append(channel)
                echo += 1

            log.debug('Handler "%s" bloqueado [ %s ] para "%s" en "%s", b' %
            (handler['cname'],
            echo > 0,
            server,
            'todos los canales' if not channel else channel))

    def unlockHandler(self, pattern, server, channel=''):
        for handler in self.searchHandler(pattern):
            echo = 0
            handler = self.handlers[handler]
            if not handler['cname'] in self.locks:
                return

            if server in self.locks[handler['cname']] and not channel:
                del self.locks[handler['cname']][server]
                echo += 1

            if channel and \
            not channel in self.locks[handler['cname']]['server'][server]:
                self.locks[handler['cname']]['server'][server].remove(channel)
                echo += 1

            log.debug('Handler "%s" desbloqueado [ %s ] para "%s" en "%s", b' %
            (handler['cname'],
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
            log.debug('Modulo "%s" cargado con exito.' % name)

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
                log.debug('Nuevo modulo encontrado "%s"' % name)

    def
