# -*- coding: utf-8 -*-

import re
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
import config
import schedule
import features
#import strings
import buffer
import events

log = logg.getLogger(__name__)


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
            >>> server = IRCBase('local', 'localhost', 6667, False, (False,), \
                             'UserBot', 'bot', (False,), False)


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

    def __init__(self, base):
        """
        Inicializa la clase xD ¿pos no se? ¿Que mas hace?
        Argumentos:
            base -- Objeto IRCBase, (obtenido de la base de datos)
        """
        self.buffer_output = buffer.DecodingLineBuffer()
        self.buffer_input = buffer.DecodingLineBuffer()
        self.features = features.FeatureSet()
        self.base = base
        self.threads = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

    def endless_process(self, stop=(None,), start=(None,)):
        """
        Inicia o detiene los procesos de entrada y salida de datos.
        Argumentos:
            stop -- Detiene los threads especificados
                sintaxis: stop=(bool, 'input or output')
                ejemplo: stop=(True, 'input') or stop=(True, 'input', 'output')
            start -- Inicia los threads especificados
                sintaxis: start=(bool, 'input or output')
                ejemplo: start=(True, 'input') or start=(True, 'input', 'output')
        """

        if stop[0]:
            self.stop_threads = stop

        if start[0]:
            if 'input' in start:
                self.threads.update({'input':
                threading.Thread(target=self.input, name='Input Data')})

            if 'output' in start:
                self.threads.update({'output':
                threading.Thread(target=self.output, name='Output Data')})
