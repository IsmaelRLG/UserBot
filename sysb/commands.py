# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import re, os, imp, logg, types, Thread, traceback, i18n

from config import core
from config import conf
from irc.client import buffer_input
from irc.request import whois
from irc.connection import servers

log = logg.getLogger(__name__)
locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'commands')
_ = locale.turn_tr_str


class commands(object):

    def __init__(self):
        self.modules = {}
        self.endless_process()
        self.lang = core.obtconfig('lang', cache=True)

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
                resul = re.match('(?P<name>.+)\.(?P<ext>py$|pyc$)', name, 2)
                if resul and resul.group('ext') == 'py':
                    name = resul.group('name')
                    __module__ = imp.find_module('mods/' + name)
                else:
                    continue

            elif os.path.isdir('mods/' + name):
                if os.path.exists('mods/%s/module.ini' % name):
                    config = conf('mods/%s/module.ini' % name)
                    log.debug('%s: configuracion de modulo cargada' % name)
                else:
                    log.info('se salta "%s" (no es un modulo)' % name)
                    continue
                status = config.get('MODULE', 'status')
                if status == 'enable':
                    pass
                elif status == 'disabled':
                    if module:
                        return 0
                    else:
                        log.debug('%s: modulo desabilitado' % name)
                        continue
                elif status == 'dev':
                    if module:
                        return 1
                    else:
                        log.debug('%s: modulo en desarrollo' % name)
                        continue

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
                error = traceback.format_exc().splitlines()
                for err in error:
                    log.error(err)
                if module:
                    return error

        try:
            self['help']['module'].make_cmls()
        except:
            pass

    def download_module(self, module):
        if self[module]:
            del self[module]
            return True

        try:
            self['help']['module'].make_cmls()
        except:
            pass

    #======================================================================#
    #                         procesando comandos                          #
    #======================================================================#

    def security(self, handler, irc, nick, channel=None, target=None):
        if handler['anyuser']:
            return True

        if handler['logged']:
            rpl_whois = whois(irc, nick)
            lang = self.lang

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
            if not user['status'] in handler['oper']:
                irc.err(nick, _('comando solo para operadores: ', lang) +
                ', '.join(handler['oper']))
                return

        if handler['channels']:
            if not channel or not channel[0] in '#':
                irc.err(nick, _('debe ingresar un canal valido', lang))
                return

            if handler['chn_registered']:
                if not servers[irc.base.name][2][channel]:
                    irc.err(nick, _('canal "%s" no registrado, registrelo.', lang) % channel)
                    return

            if handler['privs']:
                if not servers[irc.base.name][2].privs(channel,
                    rpl_whois['is logged'].lower(), handler['privs']):
                    irc.err(nick, _('permiso denegado, requiere +%s', lang) %
                    handler['privs'])
                    return

        return rpl_whois

    @Thread.thread(no_class=True)
    def endless_process(self):
        import time
        time.sleep(1)
        global_prefix = core.obtconfig('prefix', cache=True)
        time.sleep(1)
        global_lang = self.lang
        while True:
            irc, group = buffer_input.get()

            try:
                nickbot = irc.base.nick
                nick = group('nick')

                if nickbot.lower() in (nick.lower(), 'nickserv', 'chanserv'):
                    continue

                target = group('target')
                if target[0] in '#':
                    channel = target
                else:
                    channel = None

            except AttributeError:
                continue
            except IndexError:
                continue

            for mod, dict in self:
                if_break = False
                for handler in dict['handlers']:
                    try:
                        if not handler['no_prefix']:
                            prefix = ('^({}([:;, ] ?)|{})'.format(re.escape(nickbot),
                            re.escape(global_prefix)) if target != nickbot else '')
                        else:
                            prefix = ''

                        if target != nickbot:
                            if not re.match(prefix + '.*', group('message'), 2):
                                if_break = True
                                break

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
                        channel = result.group(handler['chan_reqs'])

                    if target == nickbot:
                        target = nick

                    rpl_whois = self.security(handler, irc, nick, channel)
                    if not rpl_whois:
                        if_break = False
                        break
                    else:
                        #print '%s %s %s %s' % (nick, target, channel, group('message'))
                        try:
                            handler['func'](irc, result.group, group, vars())
                        except:
                            for line in traceback.format_exc().splitlines():
                                irc.err(target, line)
                        finally:
                            if_break = True
                            break

                if if_break:
                    re.purge()
                    break

commands = commands()


def addHandler(module, regex, help, anyuser=None, registered=None, oper=None,
              channels=None, chn_registered=None, privs=None, chan_reqs=None,
              thread=None, logged=None, no_prefix=False):
    def handler(func):
        vars = {}
        vars['module'] = module
        vars['regex'] = regex
        vars['help'] = help
        vars['anyuser'] = anyuser
        vars['registered'] = registered
        vars['oper'] = oper
        vars['channels'] = channels
        vars['chn_registered'] = chn_registered
        vars['privs'] = privs
        vars['chan_reqs'] = chan_reqs
        vars['thread'] = thread
        vars['logged'] = logged
        vars['no_prefix'] = no_prefix
        vars['func'] = func

        if not vars in commands.modules[module]['handlers']:
            commands[module]['handlers'].append(vars)
            log.debug('handler [%s][%s] agregado' % (module, func.__name__))

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