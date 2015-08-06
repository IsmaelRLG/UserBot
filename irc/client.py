# -*- coding: utf-8 -*-

import socket
import threading
import struct
import ssl
import Queue
import six
import textwrap
import traceback
import time

import logg
import features
import events
import ircregex

from config import core as config
from util import always_iterable

log = logg.getLogger(__name__)

buffer_input = Queue.Queue()
buffer_output = Queue.Queue()


class IRCBase(object):

    def __init__(self, name, host, port, ssl, passwd, nick, user, sasl, verbose,
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

        self.verbose = verbose
        self.connect_to_beginning = connect_to_beginning
        self.code = code


class ServerConnection:
    connected = False
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
        self.features = features.FeatureSet()
        self.base = base
        self.threads = {}

        # Cargando los handlers locales D:
        self.local_handlers = config.obtconfig('local_handlers')

        # Solo por si es su primera vez xD
        if self.local_handlers is None:
            self.local_handlers = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _process_line(self, line):
        """
        Procesa una linea, y agrega al Queue lo procesado.
        """
        match_result = ircregex._irc_regex_base.match(line)
        if match_result.group('nickname'):
            Mask = NickMask(match_result.group('machine'))  # lint:ok
        else:
            servername = match_result.group('server')  # lint:ok

        # Eventos D:
        if match_result.group('int'):
            int = match_result.group('int')  # lint:ok
            if int in events.numeric:
                numeric_event = (int, events.numeric[int])  # lint:ok
            else:
                numeric_event = (int,)  # lint:ok
            del int
        else:
            string_event = match_result.group('str')  # lint:ok

        # Mensajito...
        if match_result.group('message0'):
            message = match_result.group('message0')
        elif match_result.group('message1'):
            message = match_result.group('message1')
        elif match_result.group('message2'):
            message = match_result.group('message2')

        # ¿Donde o quien fue? D:
        if match_result.group('from0'):
            _from = match_result.group('from0')
        elif match_result.group('from1'):
            _from = match_result.group('from1')  # lint:ok

        # ¿Y para quien era? o.O
        if match_result.group('for'):
            _for = match_result.group('for')  # lint:ok

        # O quizas fue un ping o un error?
        if match_result.group('lol'):
            other = match_result.group('lol')  # lint:ok
            # Debe de tener algo mas...
            message = match_result.group('stupid')  # lint:ok

        # ¿Sera algo sin procesar? D: D:
        if match_result.group('unprocessed'):
            unprocessed = match_result.group('unprocessed')  # lint:ok

        # Añadimos estos resultados a la cola <3
        buffer_input.put(vars())

        # Procesando los handlers locales...
        try:
            for priority in self.local_handlers.keys().sort():
                for handler in self.local_handlers[priority]:
                    handler(vars())
        except TypeError:
            pass

        # Procesando los handlers globales...
        try:
            for priority in self.global_handlers.keys().sort():
                for handler in self.global_handlers[priority]:
                    handler(vars())
        except TypeError:
            pass

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

        assert name not in ('global', 'local')
        var = eval('self.%s_handlers' % name)

        if priority not in var:
            var.update({priority: []})

        var[priority].append(function)

        # Guardando la configuracion mas actual
        config.upconfig(name + '_handlers', var)
        log.info('handler %s añadido: %s' % (name, function.__name__))

    def admin(self, server=""):
        """Send an ADMIN command."""
        self.send_raw(" ".join(["ADMIN", server]).strip())

    def cap(self, command, sub):
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
        if self.connected:
            return log.error('Ya estas conectado a %s!' % self.base.name)

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
        except:
            log.error(traceback.format_exc().splitlines().pop())
        else:
            log.info('Ahora registrándose...')
            self.connected = True

        # Procesando la salida y entrada de datos.
        self.endless_process(start=(True, 'input', 'output'))

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

        self.user(config.obtconfig('VERSION')[0], self.base.user)
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

    def endless_process(self, stop=None, start=None):
        """
        Inicia o detiene los procesos de entrada de datos.
        Argumentos:
            stop -- Detiene los threads especificados
                sintaxis: stop=bool
            start -- Inicia los threads especificados
                sintaxis: start=bool
        """

        if stop:
            self.stop_threads = stop

        if start:
            self.threads.update({'input':
            threading.Thread(target=self.input, name='Input Data')})
            self.threads['input'].start()

    def info(self, server=""):
        """Send an INFO command."""
        self.send_raw(" ".join(["INFO", server]).strip())

    def input(self):
        "read and process input from self.socket"
        plaintext = config.obtconfig('plaintext')

        log.debug('La entrada de datos de %s se ha iniciado.' % self.base.name)
        while self.connected is True:
            try:
                for line in self.socket.recv(4028).splitlines():
                    try:
                        self._process_line(line)
                    except AttributeError:
                        for err in traceback.format_exc().splitlines():
                            log.error(err)

                    # Registrando cada linea
                    if plaintext:
                        log.debug('RECV FROM %s: %s' % (self.base.name, line))
            except socket.error:
                # The server hung up.
                self.disconnect("Connection reset by peer")
                return
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
        # Should limit len(text) here!
        self.send_raw("NOTICE %s :%s" % (target, text))

    def oper(self, nick, password):
        """Send an OPER command."""
        self.send_raw("OPER %s %s" % (nick, password))

    def part(self, channels, message=""):
        """Send a PART command."""
        channels = always_iterable(channels)
        cmd_parts = [
            'PART',
            ','.join(channels),
        ]
        if message: cmd_parts.append(message)
        self.send_raw(' '.join(cmd_parts))

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
                var.remove(func)

        # Guardando la configuracion mas actual
        config.upconfig(name + '_handlers', var)
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


class output(object):
    """
    Clase sencilla para procesar la salida de una o mas conexiones.
    """
    thread = []

    def __init__(self):
        # Solo uno xD
        if len(self.thread) > 0:
            return

        self._stop = False
        self.newthread()

    def begun(self):
        return self.thread[0].isAlive()

    def start(self):
        if self.begun():
            return log.error('¡La salida de datos ya esta iniciada!')
        self.thread[0].start()
        log.info('Salida global de datos inciada!')

    def process_queue(self):
        """
        Procesando el queue de salida.
        """

        plaintext = config.obtconfig('plaintext')
        while self._stop is False:
            out = buffer_output.get()
            if out == 0:  # Saliendo! D:
                break

            # According to the RFC http://tools.ietf.org/html/rfc2812#page-6,
            # clients should not transmit more than 512 bytes.
            if len(out['msg']) > 507:
                out.update({'msg': textwrap.wrap(out['msg'], 507)[0] + '...'})

            try:
                out['socket'].send(out['msg'] + '\r\n')
            except socket.error:
                # Ouch!
                out['disconnect']("Connection reset by peer.")
            else:
                if plaintext:
                    log.info('SEND TO %s: %s' % (out['servername'], out['msg']))

                # Messages per seconds
                time.sleep(config.obtconfig('mps'))
        log.warning('¡Se detuvo la salida de datos!')

    def stop(self):
        if not self.begun():
            return

        self._stop = True
        time.sleep(10)

        if self.begun() is True:  # Oh no!! D: Sigue vivo!
            buffer_output.put(0)
            time.sleep(10)

        # Reset
        self._stop = False

    def newthread(self):
        try:
            if self.begun():
                return
            self.thread.pop()
        except IndexError:
            pass

        self.thread.append(threading.Thread(target=self.process_queue,
                                            name='Output'))


def is_channel(string):
    """Check if a string is a channel name.

    Returns true if the argument is a channel name, otherwise false.
    """
    return string and string[0] in "#&+!"


def ip_numstr_to_quad(num):
    """
    Convert an IP number as an integer given in ASCII
    representation to an IP address string.

    >>> ip_numstr_to_quad('3232235521')
    '192.168.0.1'
    >>> ip_numstr_to_quad(3232235521)
    '192.168.0.1'
    """
    n = int(num)
    packed = struct.pack('>L', n)
    bytes = struct.unpack('BBBB', packed)
    return ".".join(map(str, bytes))


def ip_quad_to_numstr(quad):
    """
    Convert an IP address string (e.g. '192.168.0.1') to an IP
    number as a base-10 integer given in ASCII representation.

    >>> ip_quad_to_numstr('192.168.0.1')
    '3232235521'
    """
    bytes = map(int, quad.split("."))
    packed = struct.pack('BBBB', *bytes)
    return str(struct.unpack('>L', packed)[0])


class NickMask(six.text_type):
    """
    A nickmask (the source of an Event)

    >>> nm = NickMask('pinky!username@example.com')
    >>> print(nm.nick)
    pinky

    >>> print(nm.host)
    example.com

    >>> print(nm.user)
    username

    >>> isinstance(nm, six.text_type)
    True

    >>> nm = 'красный!red@yahoo.ru'
    >>> if not six.PY3: nm = nm.decode('utf-8')
    >>> nm = NickMask(nm)

    >>> isinstance(nm.nick, six.text_type)
    True

    Some messages omit the userhost. In that case, None is returned.

    >>> nm = NickMask('irc.server.net')
    >>> print(nm.nick)
    irc.server.net
    >>> nm.userhost
    >>> nm.host
    >>> nm.user
    """
    @classmethod
    def from_params(cls, nick, user, host):
        return cls('{nick}!{user}@{host}'.format(**vars()))

    @property
    def nick(self):
        nick, sep, userhost = self.partition("!")
        return nick

    @property
    def userhost(self):
        nick, sep, userhost = self.partition("!")
        return userhost or None

    @property
    def host(self):
        nick, sep, userhost = self.partition("!")
        user, sep, host = userhost.partition('@')
        return host or None

    @property
    def user(self):
        nick, sep, userhost = self.partition("!")
        user, sep, host = userhost.partition('@')
        return user or None
