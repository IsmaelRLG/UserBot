# -*- coding: utf-8 -*-

import re, os, imp, logg, types, Thread, traceback, i18n

from config import core
from irc.client import buffer_input
from irc.request import whois
from irc.connection import servers

log = logg.getLogger(__name__)
locale = i18n.turn(
    'es',
    core.obtconfig('package_translate'),
    'commands')
_ = locale.turn_tr_str


class commands(object):

    def __init__(self):
        self.modules = {}
        self.endless_process()
        self.lang = core.obtconfig('lang')

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
                error = traceback.format_exc().splitlines()
                for err in error:
                    log.error(err)
                return error

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

        user = servers[irc.base.name][1][rpl_whois['is logged']]
        if handler['registered']:
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
                    irc.err(nick, _('permiso denegado', lang))
                    return

        return rpl_whois

    @Thread.thread(no_class=True)
    def endless_process(self):
        import time
        time.sleep(2)
        print ('-' * 15) + str(1) + ('-' * 15)
        global_prefix = core.obtconfig('prefix')
        time.sleep(2)
        print ('-' * 15) + str(2) + ('-' * 15)
        global_lang = self.lang
        print ('-' * 15) + str(3) + ('-' * 15)
        while True:
            print ('-' * 15) + str(4) + ('-' * 15)
            irc, group = buffer_input.get()
            print ('-' * 15) + str(5) + ('-' * 15)

            try:
                nickbot = irc.base.nick
                nick = group('nick')
                print [nick, nickbot]

                if nickbot.lower() in (nick.lower(), 'nickserv', 'chanserv'):
                    print ('-' * 15) + str(6) + ('-' * 15)
                    continue

                target = group('target')
                if target[0] in '#':
                    channel = target
                else:
                    channel = None

            except AttributeError:
                print ('-' * 15) + str(7) + ('-' * 15)
                continue
            except IndexError:
                print ('-' * 15) + str(8) + ('-' * 15)
                continue

            for mod, dict in self:
                print ('-' * 15) + str(9) + ('-' * 15)
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
                        try:
                            handler['func'](irc, result.group, group, vars())
                        except:
                            for line in traceback.format_exc().splitlines():
                                irc.err(target, line)
                        finally:
                            if_break = True
                            break

                if if_break:
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