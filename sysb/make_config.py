# -*- coding: utf-8 -*-

import os
import i18n
import traceback
from config import core

try:
    from irc.client import IRCBase
except ImportError:
    pass

make_handlers = []


def handler(func):
    if not func in make_handlers:
        make_handlers.append(func)

    def ton(*args, **kwargs):
        return func(*args, **kwargs)
    return ton


class make:

    def __init__(self):
        lang = core.obtconfig('lang')
        if lang is None:
            core.addconfig('package_translate', 'db/userbot.json')
        else:
            global lang

        locale = i18n.turn('es',
                 core.obtconfig('package_translate'),
                 i18n.parsename(__name__))
        _ = locale.turn_tr_str
        sn = lambda x: raw_input(x + ' ' + _('s/N', lang) + ' ?> ').lower() in ['s', 'y']
        i = lambda x: raw_input(x + ' ?> ')

        global locale
        global _
        global sn
        global i

        if lang is None:
            self.lang()
            self.clear()

        vrn = core.obtconfig('VERSION')
        vrn = (vrn[0] + ' ' + '.'.join(str(num) for num in vrn[1:]))

        print _('Bienvenido al sistema de configuracion de ', lang) + vrn
        print _('ingrese "help" o "license" para mas informacion', lang)

        while True:
            try:
                name = i('')
                if name is '':
                    continue

                for func in make_handlers:
                    #print func.__name__
                    if func.__name__ == name:
                        func(self)
                        raise GeneratorExit
                raise AttributeError
            except AttributeError:
                print _('orden "%s" desconocida', lang) % name
            except (KeyboardInterrupt, OSError, EOFError, GeneratorExit):
                pass
            except SystemExit:
                exit()
            except:
                for line in traceback.format_exc().splitlines():
                    print line

    @handler
    def help(self):
        print _('esta es la lista de todas las ordenes disponibles', lang)
        for func in make_handlers:
            print '    ' + func.__name__
        print _('fin de la lista de ordenes', lang)

    @handler
    def clear(self):
        os.system("clear")

    @handler
    def addserver(self):
        name = i(_('nombre de la red', lang))
        host = i(_('dirección del servidor', lang))
        port = int(i(_('numero de puerto', lang)))
        ssl = sn(_('¿usar ssl?', lang))
        if sn(_('¿usar contraseña?', lang)):
            passwd = (True, i(_('contraseña del servidor', lang)))
        else:
            passwd = (False,)

        nick = i(_('nombre para userbot', lang))
        user = i(_('nombre de usuario', lang))
        if sn(_('¿usar sasl?', lang)):
            sasl = (True,
                    (i(_('nombre de la cuenta', lang)),
                    i(_('contraseña', lang))))
        else:
            sasl = (False,)

        connect_to_beginning = sn(_('¿conectar al inicio?', lang))

        ircbase = core.obtconfig('ircbase')
        if not ircbase:
            core.addconfig('ircbase', [])
            ircbase = []

        for base in ircbase:
            if base.name.lower() is name.lower():
                print ((_('el nombre "%s" ya esta en uso,', lang) % name) +
                        _('por favor utilice otro nombre', lang))
                return

        kwargs = vars()
        del kwargs['self']
        del kwargs['ircbase']

        try:
            del kwargs['base']
        except KeyError:
            pass

        ircbase.append(IRCBase(**kwargs))
        core.upconfig('ircbase', ircbase)

    @handler
    def delserver(self):
        ircbase = core.obtconfig('ircbase')
        if not ircbase:
            print _('no hay servidores agregados', lang)
            return

        print _('ingrese el nombre del servidor a eliminar.', lang)
        print _('servidores: ', lang) + ', '.join(sv.name for sv in ircbase)
        while True:
            name = i(':::')
            for server in ircbase:
                if name == server.name:
                    del ircbase[ircbase.index(server)]
                    core.upconfig('ircbase', ircbase)
                    return
            print _('el servidor no existe, vuelva a intentarlo', lang)

    @handler
    def lang(self):
        print _('Por favor ingrese su codigo de lenguaje:', 'en')
        num = 1
        print '+' + ('=' * 78) + '+'
        for langcode in locale._tr_aval():
            print '|%-78s|' % ('    [ %s ] %s: %s' %
            (num, langcode, i18n.LC_ALL[langcode].decode('utf-8')))
            num += 1
        print '+' + ('=' * 78) + '+'

        while True:
            lang = i('langcode').lower()
            if not lang in locale._tr_aval():
                print _('codigo de lenguaje invalido.', 'en')
                continue
            else:
                if core.obtconfig('lang'):
                    core.upconfig('lang', lang)
                else:
                    core.addconfig('lang', lang)
                print _('idioma actualizado', lang)
                global lang
                break

    @handler
    def license(self):
        with open('docs/license.rst') as license:
            for line in license.read().splitlines():
                print line

    @handler
    def exit(self):
        exit()

    @handler
    def addoper(self):
        opers = core.obtconfig('opers')
        if not opers:
            core.addconfig('opers', [])
            opers = []

        user = i(_('usuario', lang))
        print _('NOTA: La contraseña debe ser ingresada bajo sha256', lang)
        passwd = i(_('contraseña', lang))
        print _('niveles disponibles: ', lang) + 'global local noob'
        level = i(_('nivel', lang))
        if level is 'global':
            level = (level,)
        elif level in ('local', 'noob'):
            print _('ingrese el nombre del servidor para el operador', lang)

            ircbase = core.obtconfig('ircbase')
            if not ircbase:
                print _('no hay servidores agregados', lang)
                return

            name = i('')
            for server in ircbase:
                if name is server.name:
                    if server.name == name:
                        level = (level, server.name)
                        break

            if not isinstance(level, tuple):
                print _('el servidor no existe', lang)

        kwargs = vars()
        del kwargs['self']
        del kwargs['opers']
        try:
            del kwargs['ircbase']
            del kwargs['name']
            del kwargs['server']
        except KeyError:
            pass

        opers.append(kwargs)
        core.upconfig('opers', opers)

    @handler
    def deloper(self):
        opers = core.obtconfig('opers')
        if not opers:
            return

        for oper in opers:
            print '=' * 80
            print _('usuario', lang) + ': ' + oper['user']
            print _('nivel', lang) + ': ' + oper['level'][0]

            try:
                print _('servidores: ', lang) + oper['level'][1]
            except IndexError:
                pass
            if sn(_('¿es este el operador a eliminar?', lang)):
                opers.remove(oper)
                core.upconfig('opers', opers)
            print '=' * 80

    @handler
    def prefix(self):
        prefix = core.obtconfig('prefix')
        if prefix:
            print _('el prefijo actual es: ', lang) + prefix
        r = i('prefijo')[0]
        if r.isalpha():
            print _('prefijo invalido el caracter no debe ser alfabetico', lang)
        else:
            if not prefix:
                core.addconfig('prefix', r)
            else:
                core.upconfig('prefix', r)

    @handler
    def users_on_userbot(self):
        pass

    @handler
    def listconf(self):
        def __print__(string):
            print string

        pr = lambda x: __print__('|%-78s|' % ("    [%-10s]: [%s]" % tuple(x)))

        print '+' + ('=' * 78) + '+'
        pr([_('lenguaje', lang), i18n.LC_ALL[lang]])
        pr([_('prefijo', lang), core.obtconfig('prefix')])
        pr(['mps', core.obtconfig('mps')])
        pr(['plaintext', core.obtconfig('plaintext')])

        try:
            for server in core.obtconfig('ircbase'):
                pr(['server', server.name])
                pr([(' ' * 14) + "%-8s" % 'host', server.host])
                pr([(' ' * 14) + "%-8s" % 'port', server.port])
                pr([(' ' * 14) + "%-8s" % 'ssl', server.ssl])
                pr([(' ' * 14) + "%-8s" % 'passwd', server.passwd])
                pr([(' ' * 14) + "%-8s" % 'sasl', server.sasl])
                pr([(' ' * 14) + "%-8s" % 'nick', server.nick])
                pr([(' ' * 14) + "%-8s" % 'user', server.user])
                pr([(' ' * 14) + "%-8s" % 'auto', server.connect_to_beginning])

                #import sysb.katheryn as katheryn
                #pr([(' ' * 14) + "%-8s" % 'auto',
                #len(katheryn.tona(server.name).userlist())])
        except TypeError:
            pr(['server', _('no hay servidores agregados', lang)])
        print '+' + ('=' * 78) + '+'

    @handler
    def plaintext(self):
        if not isinstance(core.obtconfig('plaintext'), bool):
            core.addconfig('plaintext', False)

        if sn(_('¿guardar texto plano?')):
            core.upconfig('plaintext', True)

    @handler
    def mps(self):
        if not core.obtconfig('mps'):
            core.addconfig('mps', 0.4)

        r = float(i(_('mensajes por segundos', lang)))

        if r > 0:
            core.upconfig('mps', r)
