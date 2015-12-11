# -*- coding: utf-8 -*-

import time
import Queue
import socket
import textwrap

from sysb import Thread
from sysb import logg
from sysb.config import core

buffer_output = Queue.Queue()
log = logg.getLogger(__name__)


class output(object):
    """
    Clase sencilla para procesar la salida de una o mas conexiones.
    """

    def __init__(self):
        self.process_queue()
        self._stop = False

    def begun(self):
        return Thread.thd['output'].isAlive()

    def start(self):
        if 'output' in Thread.thd:
            Thread.start('output')

    @Thread.thread(n='output')
    def process_queue(self):
        """
        Procesando el queue de salida.
        """

        plaintext = core.obtconfig('plaintext')
        mps = core.obtconfig('mps')
        if not mps:
            mps = 0.4
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
                time.sleep(mps)

        log.warning('¡Se detuvo la salida de datos!')

    def stop(self):
        if not self.begun():
            return

        self._stop = True
        time.sleep(5)

        if self.begun() is True:  # Oh no!! D: Sigue vivo!
            buffer_output.put(0)
            time.sleep(5)

        # Reset
        self._stop = False
