# -*- coding: utf-8 -*-

from thread import start_new
from threading import Thread as Th
import logging as logg
#import logg

log = logg.getLogger(__name__)
thd = {}


def thread(init=None, n=None, no_class=None):
    def func_obt(func):
        def wrapper(*args, **kwargs):

            name = str(func).split().pop().replace('>', '') if not n else n
            mess = 'iniciado'

            if no_class:
                start_new(func, args, kwargs)
            else:
                thd[name] = Th(target=func, name=name, args=args, kwargs=kwargs)

                if init:
                    thd[name].start()
                else:
                    mess = 'agregado'

            log.debug('thread(%s)[%s] %s' % (n, name, mess))

            def does_nothing(*a, **b):
                if no_class:
                    return None
                elif name:
                    return name

            return does_nothing(*args, **kwargs)
        return wrapper
    return func_obt


def start(target):
    thd[target].start()
    log.debug('thread({0})[{0}] inciado'.format(target))