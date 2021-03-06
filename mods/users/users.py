# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from sysb.config import core
from sysb import i18n
from irc.connection import servers as base
from irc.request import whois

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'users')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)


def register(irc, result, group, other):
    lc = other['global_lang']
    result = base[irc.base.name][1].register(other['rpl_whois'])
    print result
    if result == 6:
        lc = base[irc.base.name][1][other['rpl_whois']]['lang']
        irc.err(group('nick'), _('usuario ya registrado', lc))
    else:
        irc.notice(group('nick'), _('registrado correctamente: "%s"', lc) %
        base[irc.base.name][1][other['rpl_whois']]['name'])


def drop(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    code = base[irc.base.name][1].gendropcode(other['rpl_whois'])
    irc.notice(group('nick'), _('codigo de confirmacion: "%s"', lc) % code)
    irc.notice(group('nick'), _('envie: %s: user confirm_drop <codigo>', lc) %
    irc.base.nick)


def confirm_drop(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    num_resl = base[irc.base.name][1].drop(result('code'))
    if num_resl in (0, None):
        irc.err(group('nick'), _('codigo invalido', lc))
    else:
        base[irc.base.name][2].remove_user(other['rpl_whois']['is logged'])
        irc.notice(group('nick'), _('eliminado correctamente', lc))


def set_lang(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    lc = result('langcode').lower()

    if lc == 'list':
        irc.notice(group('nick'), _('codigos de lenguaje disponibles:', lc))
        for lc in locale._tr_aval():
            irc.notice(group('nick'), '[ %s ] - %s' % (lc, i18n.LC_ALL[lc]))
    elif lc in locale._tr_aval():
        base[irc.base.name][1][other['rpl_whois']]['lang'] = lc
        base[irc.base.name][1].save
        irc.notice(group('nick'), _('idioma actualizado', lc))
    else:
        irc.err(group('nick'), _('codigo de lenguaje invalido', lc))


def info(irc, result, group, other):
    rpl = whois(irc, group('nick'))
    account = result('account')
    lc = other['global_lang']
    if rpl['is logged']:
        if base[irc.base.name][1][rpl['is logged']]:
            lc = base[irc.base.name][1][rpl['is logged']]['lang']
        else:
            print None
        if not account:
            account = rpl['is logged']

    if not account:
        account = group('nick')

    user = base[irc.base.name][1][account]
    t = other['target']
    if not user:
        irc.err(t, _('usuario no registrado', lc) + ': ' + account)
        return

    irc.notice(t, _('nombre de usuario: ', lc) + user['name'])
    irc.notice(t, _('fecha de registro: ', lc) + user['time'])
    irc.notice(t, _('idioma de usuario: ', lc) + i18n.LC_ALL[user['lang']])
    irc.notice(t, _('nivel del usuario: ', lc) + user['status'])
    irc.notice(t, _('cuenta bloqueada: ', lc) + str(user['lock'][0]))
    if user['lock'][0]:
        irc.notice(t, _('razon de bloqueo: ', lc) + user['lock'][1])
