# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from irc.request import whois
from sysb.config import core
from sysb import commands
from sysb import i18n
from irc.connection import servers as base

import textwrap

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'help')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)
cmls = {}


def make_cmls():
    for module, dic in commands.commands.modules.items():
        for handlers in dic['handlers']:
            help = handlers['help']['sintax'].lower().split()
            help.reverse()

            try:
                first = help.pop()
            except IndexError:
                print help
                continue

            try:
                second = help.pop()
            except IndexError:
                second = '<'
            if not first in cmls:
                cmls[first] = {'module': handlers['module']}

            if not '<' in second and\
               not '>' in second and\
               not '?' in second and\
               not '|' in second:

                if not 'sub' in cmls[first]:
                    cmls[first].update({'sub': {}})
                cmls[first]['sub'][second] = handlers['help']
            else:
                cmls[first].update(handlers['help'])


def search(ls):
    ls.reverse()
    first = ls.pop()
    if first in cmls:
        if len(ls) == 0:
            if 'sintax' in cmls[first]:
                return [cmls[first]]
        elif 'sub' in cmls[first] and ls[len(ls) - 1] in cmls[first]['sub']:
            return [cmls[first]['sub'][ls.pop()], cmls[first]['module']]

    return [{}]


def help(irc, result, group, other):
    rpl = whois(irc, group('nick'))
    lc = other['global_lang']
    user = None
    command = result('command')
    target = other['target']
    if rpl['is logged'] and base[irc.base.name][1][rpl['is logged']]:
        user = base[irc.base.name][1][rpl['is logged']]

    if user:
        lc = user['lang']

    vrn = core.obtconfig('VERSION', cache=True)
    vrn = (vrn[0] + ' ' + '.'.join(str(num) for num in vrn[1:]))
    irc.notice(target, vrn + ' - ' + _('codigo fuente: ', lc) + 'https://goo.gl/vVSG8i')

    if command:
        res = search(command.lower().split())
        if len(res) == 1:
            res = res[0]
            if len(res) == 0:
                pass
            else:
                mod = res['module']
        else:
            mod = res[1]
            res = res[0]

        if res:
            irc.notice(target, _('ayuda para: ', lc) + command)
            if isinstance(res['desc'], tuple) or isinstance(res['desc'], list):
                irc.notice(target, _('descripcion: ', lc))
                for line in res['desc']:
                    irc.notice(target, '        ' + _(line, lc, mod=mod, err=False))
            else:
                irc.notice(target, _('descripcion: ', lc) + _(res['desc'], lc, mod=mod, err=False))
            if 'alias' in res:
                irc.notice(target, 'alias: ' + ', '.join(res['alias']))
            irc.notice(target, _('sintaxis: ', lc) + res['sintax'])
            irc.notice(target, _('ejemplo: ', lc) + res['example'])
            irc.notice(target, _('?: parametro opcional, |: opciones varias', lc))
        else:
            irc.notice(target, _('el comando no existe', lc))
    else:
        post = {}
        first = []

        for dic in cmls.items():
            if 'sub' in dic[1]:
                if not dic[0] in post:
                    post[dic[0]] = []

                for sub in dic[1]['sub']:
                    post[dic[0]].append(sub)
            else:
                first.append(dic[0])

        irc.notice(target, _('prefijo %s, comandos disponibles: ', lc) % other['global_prefix'])
        msg = textwrap.wrap(', '.join(first), 400)
        for o in msg:
            irc.notice(target, o)

        for pr, sub in post.items():
            if pr == 'admin':
                if user and user['status'] in ('noob', 'local', 'global'):
                    for o in textwrap.wrap(', '.join(sub), 400):
                        irc.notice(target, '%s: %s' % (pr, o))
                else:
                    irc.notice(target, 'admin: id')
            else:
                for o in textwrap.wrap(', '.join(sub), 400):
                    irc.notice(target, '%s: %s' % (pr, o))

        irc.notice(target, _('envie: help <comando> <subcomando>?', lc))
        irc.notice(target, _('?: parametro opcional, |: opciones varias', lc))

make_cmls()