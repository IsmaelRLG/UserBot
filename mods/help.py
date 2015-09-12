# -*- coding: utf-8 -*-

import logg
import util
import time
import config

import commands
import pylocale
import katheryn
import textwrap

log = logg.getLogger(__name__)
trn = pylocale.turn('es', config.obtconfig('trs'), pylocale.parsename(__name__))
_ = trn.turn_tr_str
usr = katheryn.tona
dlc = config.obtconfig('default_lang')


class help:

    def __init__(self):
        self.dict = {}
        self.load_commands()

    @util.thread('busqueda de la "ayuda" de comandos', 1)
    def load_commands(self):
        loop_count = 0
        while True:
            loop_count += 1
            log.debug('Buscando commandos... Pasada N°' + str(loop_count))
            for handler in commands.commands.handlers:
                loop_count -= loop_count
                l = handler['name'].split().reverse()
                if len(l) == 1:
                    self.dict.update({l[0]:
                    {'help': handler['help'], 'sintax': handler['example']}})
                if len(l) == 2:
                    if not l[0].lower() in self.dict:
                        self.dict.update({l[0]: {'sub': {}}})

                    self.dict[l[0]]['sub'].update({l[1]:
                    {'help': handler['help'], 'sintax': handler['example']}})
                if len(l) == 3:
                    if not l[0].lower() in self.dict:
                        self.dict.update({l[0]: {'sub': {}}})

                    if not l[1] in self.dict[l[0]]['sub']:
                        self.dict[l[0]]['sub'].update({l[1]: {'sub': {}}})

                    self.dict[l[0]]['sub'][l[1]]['sub'].update({l[2]:
                    {'help': handler['help'], 'sintax': handler['example']}})

            if loop_count == 0:
                log.debug('se añadieron nuevos comandos a la ayuda.')
            elif loop_count > 0 and loop_count < 5:
                log.debug('no se encontraron nuevos comandos.')
                time.sleep(loop_count * 5)
            elif loop_count == 5:
                log.debug('No se encontraron mas comandos, saliendo.')
                break

    @commands.addHandler(
        'help( (?P<commands>.*))?',
        'help',
        _('muestra la ayuda de un comando', dlc),
        'help <command>',
        __name__,
        any=True)
    def view_help(self, irc, group, result, other):
        lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
        n = other['target']
        vrn = config.obtconfig('VERSION')
        vrn = (vrn[0] + ' ' + '.'.join(str(num) for num in vrn[1:]))

        irc.notice(n, _('*** inicio de la ayuda ***', lang))
        irc.notice(n, _('\2\00309%s\3, web: \00311%s', lang) %
        (vrn, config.obtconfig('webpage')))
        c = result('commands')
        if c is None:
            irc.notice(n, _('comandos disponibles:', lang))

            one = []
            t = []
            for name, h in self.dict.items():
                if not 'sub' in h:
                    one.append(name)
                else:
                    t.append((name, h))

            for msg in textwrap.wrap(', '.join(one), 400):
                irc.notice(n, msg)

            for name, h in t:
                irc.notice(n, name + ':')
                tr = []
                for sub in h['sub'].keys():
                    if 'sub' in h['sub'][sub]:
                        irc.notice(n, '    ' + sub + ':')
                        one = ', '.join(h['sub'][sub]['sub'].keys())
                        for msg in textwrap.wrap(one, 400):
                            irc.notice(n, '        ' + msg)
                    else:
                        tr.append(sub)

                for msg in textwrap.wrap(', '.join(one), 400):
                    irc.notice(n, '    ' + msg)

            irc.notice(n, _('para mas informacion envie: help <comando>', lang))
        else:
            handler = self.obtain(c.lower().split())
            if not handler:
                irc.err(n, _('el comando "%s" no existe', lang) % c)
            else:
                try:
                    irc.notice(n, _('Informacion: ', lang) + handler['help'])
                    irc.notice(n, _('Sintaxis: ', lang) + handler['example'])
                    prefix = handler['prefix']
                    if not prefix:
                        prefix = config.core.obtconfig('prefix')
                    irc.notice(n, _('Prefijo: ', lang) + prefix)

                    if handler['any'] or not handler['privs']:
                        r = _('cualquiera', lang)
                    elif handler['onlyops'] or handler['only_global_ops']:
                        r = _('solo operadores', lang)
                    elif handler['privs']:
                        r = handler['privs']
                    else:
                        r = _('desconocido', lang)

                    irc.notice(n, _('requiere: ', lang) + r)
                except KeyError:
                    irc.err(n, _('comando invalido', lang))

        irc.notice(n, _('*** fin de la ayuda ***', lang))

    def obtain(self, ls):
        if len(ls) == 1:
            return self.dict[ls[0]]
        elif len(ls) == 2:
            return self.dict[ls[0]]['sub'][ls[1]]
        elif len(ls) == 3:
            return self.dict[ls[0]]['sub'][ls[1]]['sub'][ls[2]]
        else:
            return False

help = help()  # lint:ok
