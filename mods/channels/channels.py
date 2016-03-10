# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from sysb.config import core
from sysb import i18n
from irc.connection import servers as base

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'channels')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)


def register(irc, result, group, other):
    account = other['rpl_whois']['is logged'].lower()
    lc = base[irc.base.name][1][account]['lang']

    if not other['channel'].lower() in irc.joiner:
        irc.err(other['target'],
        _('no puede registrar el canal, informe a un operador', lc))
        return

    resu = base[irc.base.name][2].register(other['channel'], account)
    if resu == 5:
        irc.err(other['target'], _('canal ya registrado', lc))
    elif resu == 7:
        irc.notice(other['target'], _('canal registrado correctamente', lc))


def flags(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    if result('target', 'flags') == ('*', '*'):

        num = 1
        for us, fl in base[irc.base.name][2][other['channel']]['flags'].items():
            irc.notice(other['target'], '[ %s ] | %-25s | [ %s ]' %
            (str(num).zfill(2), us, fl))
            num += 1
        return

    if not base[irc.base.name][1][result('target')]:
        irc.err(other['target'], _('usuario no registrado en el bot', lc))
        return

    if result('flags') == '*':
        irc.notice(other['target'], '[ 01 ] | %-25s | [ %s ]' %
        (result('target'), base[irc.base.name][2].flags('get',
        other['channel'], result('target').lower())))
        return

    else:
        before = base[irc.base.name][2].flags(
        'get', other['channel'], result('target').lower())

        if result('flags')[0] in '+-':
            if 'F' in result('flags'):
                irc.err(other['target'], _('permiso denegado', lc))
                return
            kwargs = {'flag': result('flags')}
        else:
            if 'founder'.lower() in result('flags'):
                irc.err(other['target'], _('permiso denegado', lc))
                return
            kwargs = {'template': result('flags')}

        base[irc.base.name][2].flags('set',
        other['channel'], result('target').lower(), **kwargs)

        after = base[irc.base.name][2].flags(
        'get', other['channel'], result('target').lower())

        irc.notice(other['target'], _('flags actualizado:', lc) +
        " [%s] - (%s) >> (%s)" % (result('target'), before, after))


def drop(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    del base[irc.base.name][2][other['channel']]
    irc.notice(other['target'], _('canal eliminado', lc))
    irc.part(other['channel'], _('saliendo...', lc))
