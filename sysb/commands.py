# -*- coding: utf-8 -*-

import re, os, imp, logg, types, thread, traceback, pylocale

from config import core
from irc.client import buffer_input
from irc.request import whois
from irc.connection import servers

log = logg.getLogger(__name__)
locale = pylocale.turn(
    'es',
    core.obtconfig('package_translate'),
    pylocale.parsename(__name__))
_ = locale.turn_tr_str


class commands(object):

    def __init__(self):
        self.modules = {}
        self.handler_locks = core.obtconfig('handler_locks')
        if not self.handler_locks:
            self.handler_locks = {}
            core.addconfig('handler_locks', self.handler_locks)
        self.endless_process()

    def __getitem__(self, key):
        try:
            return self.modules[key]
        except KeyError:
            pass

    def __setitem__(self, key, item):
        self.modules[key] = item

    def __delitem__(self, key):
        del self.modules[key]

    def __repr__(self):
        return repr(self.modules)

    def __iter__(self):
        return iter(self.modules.items())

    #======================================================================#
    #                    importacion de comandos/modulos                   #
    #======================================================================#

    def load_modules(self, module=None):
        for name in os.listdir('mods'):
            if module and not module == name:
                continue

            if os.path.isfile('mods/' + name):
                resul = re.match('(?P<name>.+)\.(?P<ext>(py|pyc))', name, 2)
                if resul and resul.group('ext') == 'py':
                    __module__ = imp.find_module('mods/' + resul.group('name'))
                else:
                    continue

            elif os.path.isdir('mods/' + name):
                __module__ = imp.find_module('mods/' + name)

            elif os.path.islink('mods/' + name):
                __module__ = imp.find_module(os.readlink('mods/' + name))

            self[name] = {'module': __module__, 'handlers': []}

        for name, args in self:
            if module and not module == name:
                continue
            if isinstance(args, types.ModuleType):
                continue

            try:
                self[name]['module'] = imp.load_module(name, *args['module'])
                log.debug('modulo "%s" cargado correctamente' % name)
                if module:
                    return True
            except:
                log.error('el modulo %s contiene errores' % name)
                for err in traceback.format_exc().splitlines():
                    log.error(err)

    def download_module(self, module):
        if self[module]:
            del self[module]
            return True

    def reload_module(self, module):
        self.download_module(module)
        if self[module]:
            del self[module]['handlers']
            self[module]['handlers'] = []

            try:
                self[module]['module'] = imp.reload(self[module]['module'])
                return True
            except:
                log.error('el modulo %s contiene errores' % module)
                for err in traceback.format_exc().splitlines():
                    log.error(err)

    #======================================================================#
    #                         procesando comandos                          #
    #======================================================================#

    def security(self, handler, irc, nick, channel=None, target=None):
        if handler['anyuser']:
            return True

        if handler['logged']:
            rpl_whois = whois(irc, nick)
            lang = core.obtconfig('lang')

            if not rpl_whois['is logged']:
                irc.err(nick, _('debe loguearse via nickserv', lang))
                return

        if handler['registered']:
            user = servers[irc.base.name][1][rpl_whois['is logged']]
            if not user:
                irc.err(nick, _('no se encuentra registrado, registrese', lang))
                return

            lang = user['lang']

            if user['lock'][0]:
                irc.err(nick, _('su cuenta esta bloqueada, razon: "%s"', lang) %
                user['lock'][1])
                return

        if handler['oper']:
            if user['status'] in handler['oper']:
                irc.err(nick, _('comando solo para operadores', lang))
                return

        if handler['channels']:
            if not channel or not channel[0] in irc.features.chantypes:
                irc.err(nick, _('debe ingresar un canal valido', lang))
                return

            if handler['chn_registered']:
                if not servers[irc.base.name][2][channel]:
                    irc.err(nick, _('canal no registrado, registrelo.'))

            if handler['privs']:
                if not servers[irc.base.name][2][channel]['flags'].privs(channel,
                    rpl_whois['is logged'].lower(), handler['privs']):
                    irc.err(nick, _('permiso denegado', lang))
                    return

        return rpl_whois

    @thread.thread(init=True)
    def endless_process(self):
        prefix = core.obtconfig('prefix')
        while True:
            irc, group = buffer_input.get()

            try:
                nickbot = irc.base.nick
                nick = group('nick')

                if nickbot == nick:
                    continue

                target = group('target')
                if target[0] in irc.features.chantypes:
                    channel = target
                else:
                    channel = None

            except IndexError:
                continue

            for mod, dict in self:
                for handler in dict['handlers']:

                    try:
                        if not handler['no_prefix']:
                            prefix = ('({}([:;, ] ?)|{})'.format(re.escape(nickbot),
                            re.escape(prefix)) if target != nickbot else '')
                        else:
                            prefix = ''

                        result = re.match(prefix +
                        handler['regex'], group('message'), 2)
                        if not result:
                            continue

                    except:
                        log.error('expresion regular invalida, handler %s' %
                        handler['func'].__name__)
                        for err in traceback.format_exc().splitlines():
                            log.error(err)
                        continue

                    if not channel and handler['chan_reqs']:
                        channel = group(handler['chan_reqs'])

                    if target == nickbot:
                        target = nick

                    rpl_whois = self.security(handler, irc, nick, channel)
                    if not rpl_whois:
                        break
                    else:
                        try:
                            handler['func'](irc, result.group, group, vars())
                        except:
                            for line in traceback.format_exc().splitlines():
                                irc.err(target, line)
                        finally:
                            break

commands = commands()


def addHandler(module, regex, help, anyuser=None, registered=None, oper=None,
              channels=None, chn_registered=None, privs=None, chan_reqs=None,
              thread=None, logged=None, no_prefix=False):
    def handler(func):
        if not vars() in commands.modules[module]['handlers']:
            commands[pylocale.parsename(module)]['handlers'].append(vars())

        def wrapper(*args, **kwargs):
            if thread:
                import thread
                thread.start_new(func, args, kwargs)

                def does_nothing(*a, **b):
                    pass
                return does_nothing(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return handler