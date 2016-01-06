# -*- coding: utf-8 -*-

import socket
import ssl
import Queue
import traceback
import time
import re

import features
import ircregex

from sysb import logg
from sysb import Thread
from sysb.config import core as config
from output import buffer_output
from util import always_iterable

log = logg.getLogger(__name__)
buffer_input = Queue.Queue()


class IRCBase(object):

    def __init__(self, name, host, port, ssl, passwd, nick, user, sasl,
                 connect_to_beginning=True, code='UTF-8'):
        """
        Clase base para las conexiones de IRC.
        Argumentos:

        * name -- Nombre del servidor
        * host -- Direccion del servidor
        * port -- Numero de puerto
        * ssl -- Conectar con ssl (si se desea)
        * passwd -- Contraseña del servidor (si tiene)
          Sintaxis:
              (bool, "password")
          Ejemplo:
              (True, "I'm_one_sexy_password")
              (False,) or (False, "")

        * nick -- Nombre del nick
        * user -- Nombre de usuario
        * sasl -- Autenticación simple
          Sintaxis:
              (bool, ("account", "password"))
          Ejemplo:
              (True, ("I'm_sexy_account", "I'm_one_sexy_password"))
              (False,)

        * verbose -- Activa o desactiva las notificaciones.
        * connect_to_beginning -- Establecer conexion al iniciar.
        * code -- Juego de caracteres.

        Ejemplo:
            >>> IRCBase('local', 'localhost', 6667, False, (False,), 'UserBot',
                        'botito', (False,), False)

        """

        self.name = name
        self.host = host
        self.port = port
        self.ssl = ssl
        self.passwd = passwd
        self.nick = nick
        self.user = user

        if sasl[0] is True:
            # Simple Authentication and Security Layer (SASL)
            # Copyright (C) The Internet Society (2006).
            # https://tools.ietf.org/html/rfc4422#appendix-A
            # RFC 4422
            pw = '{0}\0{0}\0{1}'.format(sasl[1][0], sasl[1][1]).encode('base64')
            self.sasl = (True, pw)
        else:
            self.sasl = sasl

        self.connect_to_beginning = connect_to_beginning
        self.code = code


class ServerConnection:
    stop_threads = False
    sleep_time = 0
    last_time = 0
    global_handlers = {}

    def __init__(self, base):
        """
        Inicializa la clase xD ¿pos no se? ¿Que mas hace?
        Argumentos:
            base -- Objeto IRCBase, (obtenido de la base de datos)
        """
        self.connected = False
        self.features = features.FeatureSet()
        self.base = base
        self.thd_input_code = None
        self.joiner = []
        self.attempted = 0
        self.attempted_limit = 9
        self.sleep = 0

        # Cargando los handlers locales D:
        self.local_handlers = None

        # Solo por si es su primera vez xD
        if self.local_handlers is None:
            self.local_handlers = {}

        self.socket = socket.socket()

    def _connect(self):
        if self.attempted > self.attempted_limit:
            self.attempted = 0
            log.info('Abortando conexion para ' + self.base.name)
            return False
        else:
            self.attempted += 1

        time.sleep(self.sleep)
        try:
            log.info('Buscando ' + self.base.host)
            self.socket.connect((self.base.host, self.base.port))

            if self.base.ssl is True:
                self.socket = ssl.wrap_socket(self.socket)
                log.info('Usando SSL para %s...' % self.base.name)

            log.info('Conectado a %s (%s) puerto %s...' % (
                self.base.host,
                self.socket.getpeername()[0],
                self.base.port))
        except Exception as error:
            log.error(error)
            if self.sleep == 0:
                self.sleep = 5
            else:
                self.sleep = ((self.sleep * 70) / 100) + self.sleep
            self._connect()
        else:
            log.info('Ahora registrándose...')
            return True

    def _process_line(self, line):
        """
        Procesa una linea, y agrega al Queue lo procesado.
        """
        # Eliminando cosas raras...
        for round in range(2):
            if line.endswith('\n') or line.endswith('\r'):
                line = line.rstrip('\n').rstrip('\r')

        for name, regex in ircregex.ALL.items():
            if name is 'ALL':
                continue

            try:
                match_result = re.match(regex, line, re.IGNORECASE)
            except Exception as error:
                log.warning('regex invalida: ' + str(error))

            if match_result:
                # Procesando los handlers globales...
                if self._process_handler(name, match_result.group, 'global'):
                    break

                # Procesando los handlers locales...
                if self._process_handler(name, match_result.group, 'local'):
                    break

                # Si llego hasta aca es que ningun handler se ejecuto.
                # Solo "NOTICE" y "PRIVMSG"
                if name in ('NOTICE', 'PRIVMSG') and \
                not match_result.group('target') in ('*', 'Auth'):
                    buffer_input.put((self, match_result.group))
                    break

    def _process_handler(self, name, method_group, level):
        assert level in ('global', 'local')

        # Formateando....
        S = eval('self.{level}_handlers'.format(level=level))
        try:
            prt = S.keys()
            prt.sort()
        except TypeError:
            log.warning('retornando... no hay handlers %s por procesar' % level)
            return

        for priority in prt:
            for handler in S[priority]:
                try:
                    return handler(self, name, method_group)
                except UnboundLocalError:
                    continue
                except:
                    for line in traceback.format_exc().splitlines():
                        log.error('%s handler %s: %s' %
                        (level, handler.func_name, line))

    def action(self, target, action):
        """Send a CTCP ACTION command."""
        self.ctcp("ACTION", target, action)

    def add_handler(self, function, priority, name):
        """
        Añadir handler, ya sea, local o global
        Argumentos:
            function -- Funcion a ejecutar
            priority -- Prioridad con la que se ejecutara.
            name -- Tipo de handler a añadir (global o local)
        """

        assert name in ('global', 'local')
        var = eval('self.%s_handlers' % name)

        if priority not in var:
            var.update({priority: []})

        var[priority].append(function)

        # Guardando la configuracion mas actual
        #config.upconfig(name + '_handlers', var)
        log.info('handler %s añadido: %s, prioridad: %s' %
        (name, function.__name__, priority))

    def admin(self, server=""):
        """Send an ADMIN command."""
        self.send_raw(" ".join(["ADMIN", server]).strip())

    def cap(self, command, sub=None):
        """
        Send a CAP command according to `the spec
        <http://ircv3.atheme.org/specification/capability-negotiation-3.1>`_.

        Example:

            .cap('LS')
            .cap('REQ', 'sasl')
            .cap('END')
        """
        self.send_raw("CAP %s%s" % (command, " : " + sub if sub else ''))

    def ctcp(self, ctcptype, target, parameter=""):
        """Send a CTCP command."""
        ctcptype = ctcptype.upper()
        tmpl = (
            "\001{ctcptype} {parameter}\001" if parameter else
            "\001{ctcptype}\001"
        )
        self.privmsg(target, tmpl.format(**vars()))

    def ctcp_reply(self, target, parameter):
        """Send a CTCP REPLY command."""
        self.notice(target, "\001%s\001" % parameter)

    def connect(self):
        """
        Conecta o reconecta a un servidor.
        """

        if not self._connect():
            return

        # Procesando la entrada de datos.
        if self.connected is False:
            self.connected = True
            self.thd_input_code = self.input()

        # Logeandonos al servidor (si tiene contraseña claro)
        if self.base.passwd[0]:
            self.pass_(self.base.passwd[1])
            time.sleep(4)

        # SASL Mechanisms
        # http://ircv3.net/docs/sasl-mechs.html
        if self.base.sasl[0]:
            log.info('Usando SASL...')
            self.cap('REQ', 'sasl')
            self.send_raw('AUTHENTICATE PLAIN')
            self.send_raw('AUTHENTICATE ' + self.base.sasl[1])
            self.cap('END')

        self.user(config.obtconfig('VERSION', cache=True)[0], self.base.user)

        self.nick(self.base.nick)

    def disconnect(self, message=''):
        """Se desconecta del servidor y se cierra el socket."""
        if not self.connected:
            return

        self.quit(message)
        # Esperamos unos dos segundos...
        time.sleep(2)
        self.connected = False

        try:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
        except socket.error:
            pass
        finally:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.registered = False
        self.joiner = []

    def err(self, target, msg):
        self.notice(target, '\2\00305error\3:\2 ' + msg)

    def stop_input(self):
        if not self.thd_input_code:
            return

        if Thread.thd[self.thd_input_code].isAlive():
            self.stop_threads = True

    def info(self, server=""):
        """Send an INFO command."""
        self.send_raw(" ".join(["INFO", server]).strip())

    @Thread.thread(no_class=True)
    def input(self):
        "read and process input from self.socket"
        plaintext = config.obtconfig('plaintext', cache=True)

        log.debug('La entrada de datos de %s se ha iniciado.' % self.base.name)
        while self.connected is True:
            try:
                for line in self.socket.recvfrom(4028)[0].splitlines():
                    # Registrando cada linea
                    if plaintext:
                        log.info('RECV FROM %s: %s' % (self.base.name, line))

                    try:
                        self._process_line(line)
                    except AttributeError:
                        for err in traceback.format_exc().splitlines():
                            log.error(err)

            except socket.error:
                # The server hung up.
                self.connected = False
                break
        log.warning('¡Se detuvo la entrada de datos de %s!' % self.base.name)

    def invite(self, nick, channel):
        """Send an INVITE command."""
        self.send_raw(" ".join(["INVITE", nick, channel]).strip())

    def ison(self, nicks):
        """Send an ISON command.

        Arguments:

            nicks -- List of nicks.
        """
        self.send_raw("ISON " + " ".join(nicks))

    def is_connected(self):
        """Return connection status.

        Returns true if connected, otherwise false.
        """
        return self.connected

    def join(self, channel, key=""):
        """Send a JOIN command."""
        self.send_raw("JOIN %s%s" % (channel, (key and (" " + key))))

    def kick(self, channel, nick, comment=""):
        """Send a KICK command."""
        tmpl = "KICK {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    def links(self, remote_server="", server_mask=""):
        """Send a LINKS command."""
        command = "LINKS"
        if remote_server:
            command = command + " " + remote_server
        if server_mask:
            command = command + " " + server_mask
        self.send_raw(command)

    def list(self, channels=None, server=""):
        """Send a LIST command."""
        command = "LIST"
        channels = ",".join(always_iterable(channels))
        if channels:
            command += ' ' + channels
        if server:
            command = command + " " + server
        self.send_raw(command)

    def lusers(self, server=""):
        """Send a LUSERS command."""
        self.send_raw("LUSERS" + (server and (" " + server)))

    def mode(self, target, command):
        """Send a MODE command."""
        self.send_raw("MODE %s %s" % (target, command))

    def motd(self, server=""):
        """Send an MOTD command."""
        self.send_raw("MOTD" + (server and (" " + server)))

    def names(self, channels=None):
        """Send a NAMES command."""
        tmpl = "NAMES {channels}" if channels else "NAMES"
        channels = ','.join(always_iterable(channels))
        self.send_raw(tmpl.format(channels=channels))

    def nick(self, newnick):
        """Send a NICK command."""
        self.send_raw("NICK " + newnick)

    def notice(self, target, text):
        """Send a NOTICE command."""
        self.send_raw("NOTICE %s :%s" % (target, text))

    def oper(self, nick, password):
        """Send an OPER command."""
        self.send_raw("OPER %s %s" % (nick, password))

    def part(self, channels, message=""):
        """Send a PART command."""
        self.send_raw("PART %s%s" % (channels, (message and (" " + message))))

    def pass_(self, password):
        """Send a PASS command."""
        self.send_raw("PASS " + password)

    def ping(self, target, target2=""):
        """Send a PING command."""
        self.send_raw("PING %s%s" % (target, target2 and (" " + target2)))

    def pong(self, target, target2=""):
        """Send a PONG command."""
        self.send_raw("PONG %s%s" % (target, target2 and (" " + target2)))

    def privmsg(self, target, text):
        """Send a PRIVMSG command."""
        self.send_raw("PRIVMSG %s :%s" % (target, text))

    def privmsg_many(self, targets, text):
        """Send a PRIVMSG command to multiple targets."""
        target = ','.join(targets)
        return self.privmsg(target, text)

    def quit(self, message=""):
        """Send a QUIT command."""
        # Note that many IRC servers don't use your QUIT message
        # unless you've been connected for at least 5 minutes!
        self.send_raw("QUIT" + (message and (" :" + message)))

    def remove(self, channel, nick, comment=""):
        """Send a REMOVE command."""
        tmpl = "REMOVE {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    def remove_handler(self, function, priority, name):
        assert name in ('global', 'local')
        var = eval('self.%s_handlers' % name)

        for func in var[priority]:
            if func.func_name == function.func_name:
                var[priority].remove(func)

        # Guardando la configuracion mas actual
        log.info('handler %s eliminado: %s' % (name, function.__name__))

    def send_raw(self, string):
        """Añade una cadena al queue para ser enviada."""
        buffer_output.put({
            'msg': string,
            'socket': self.socket,
            'servername': self.base.name,
            'disconnect': self.disconnect})

    def squit(self, server, comment=""):
        """Send an SQUIT command."""
        self.send_raw("SQUIT %s%s" % (server, comment and (" :" + comment)))

    def stats(self, statstype, server=""):
        """Send a STATS command."""
        self.send_raw("STATS %s%s" % (statstype, server and (" " + server)))

    def time(self, server=""):
        """Send a TIME command."""
        self.send_raw("TIME" + (server and (" " + server)))

    def topic(self, channel, new_topic=None):
        """Send a TOPIC command."""
        if new_topic is None:
            self.send_raw("TOPIC " + channel)
        else:
            self.send_raw("TOPIC %s :%s" % (channel, new_topic))

    def trace(self, target=""):
        """Send a TRACE command."""
        self.send_raw("TRACE" + (target and (" " + target)))

    def user(self, username, realname):
        """Send a USER command."""
        self.send_raw("USER %s 0 * :%s" % (username, realname))

    def userhost(self, nicks):
        """Send a USERHOST command."""
        self.send_raw("USERHOST " + ",".join(nicks))

    def users(self, server=""):
        """Send a USERS command."""
        self.send_raw("USERS" + (server and (" " + server)))

    def version(self, server=""):
        """Send a VERSION command."""
        self.send_raw("VERSION" + (server and (" " + server)))

    def wallops(self, text):
        """Send a WALLOPS command."""
        self.send_raw("WALLOPS :" + text)

    def who(self, target="", op=""):
        """Send a WHO command."""
        self.send_raw("WHO%s%s" % (target and (" " + target), op and (" o")))

    def whois(self, targets):
        """Send a WHOIS command."""
        self.send_raw("WHOIS " + ",".join(always_iterable(targets)))

    def whowas(self, nick, max="", server=""):
        """Send a WHOWAS command."""
        self.send_raw("WHOWAS %s%s%s" % (nick,
                                         max and (" " + max),
                                         server and (" " + server)))

