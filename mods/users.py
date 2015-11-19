# -*- coding: utf-8 -*-

from sysb.config import core
from sysb import commands
from sysb import i18n
from irc.connection import servers as base

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate'),
    'users')
_ = locale.turn_tr_str
lang = core.obtconfig('lang')


@commands.addHandler('users', 'user register', {
    'sintax': 'user register',
    'example': 'user register',
    'desc': _('registra un usuario en el bot', lang)},
    logged=True)
def register(irc, result, group, other):
    result = base[irc.base.name][1].register(other['rpl_whois'])
    if result == 6:
        lang = base[irc.base.name][1][other['rpl_whois']]['lang']
        irc.err(group('nick'), _('usuario ya registrado', lang))
    else:
        irc.notice(group('nick'), _('registrado correctamente: "%s"', lang) %
        base[irc.base.name][1][other['rpl_whois']])


@commands.addHandler('users', 'user drop', {
    'sintax': 'user drop',
    'example': 'user drop',
    'desc': _('elimina a un usuario registrado', lang)},
    registered=True,
    logged=True)
def drop(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']]['lang']
    code = base[irc.base.name][1].gendropcode(other['rpl_whois'])
    irc.notice(group('nick'), _('codigo de confirmacion: "%s"', lang) % code)
    irc.notice(group('nick'), _('envie: %s: user confirm_drop <codigo>', lang) %
    irc.base.nick)


@commands.addHandler('users', 'user confirm_drop (?P<code>[^ ]+)', {
    'sintax': 'user confirm_drop <code>',
    'example': 'user confirm_drop 6adf97f83acf6453d4a6a4b1070f3754',
    'desc': _('confirma la eliminacion de un usuario', lang)},
    registered=True,
    logged=True)
def confirm_drop(irc, result, group, other):
    num_resl = base[irc.base.name][1].drop(result('code'))
    lang = base[irc.base.name][1][other['rpl_whois']]['lang']
    if num_resl in (0, None):
        irc.err(group('nick'), _('codigo invalido', lang))
    else:
        base[irc.base.name][2].remove_user(other['rpl_whois']['is logged'])
        irc.notice(group('nick'), _('eliminado correctamente', lang))


@commands.addHandler('users', 'user lang (?P<langcode>[^ ]+)', {
    'sintax': 'user lang <langcode>',
    'example': 'user lang en',
    'desc': _('cambia el idioma que se muestra al usuario', lang)},
    registered=True,
    logged=True)
def set_lang(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']]['lang']
    lc = result('langcode').lower()

    if lc == 'list':
        irc.notice(group('nick'), _('codigos de lenguaje disponibles:', lang))
        for lc in locale.locale._tr_aval():
            irc.notice(group('nick'), '[ %s ] - %s' % (lc, i18n.ALL[lc]))
    elif lc in locale.locale._tr_aval():
        base[irc.base.name][1][other['rpl_whois']]['lang'] = lc
        base[irc.base.name][1].save
        irc.notice(group('nick'), _('idioma actualizado', lc))
    else:
        irc.err(group('nick'), _('codigo de lenguaje invalido', lang))


@commands.addHandler('users', 'user info( (?P<account>[^ ]+))?', {
    'sintax': 'user info <account>?',
    'example': 'user info foo',
    'desc': _('muestra informacion de un usuario en userbot', lang)},
    anyuser=True)
def info(irc, result, group, other):
    from irc.request import whois
    rpl = whois(group('nick'))
    account = result('account')
    if rpl['is logged'] and base[irc.base.name][1][rpl['is logged']]:
        lang = base[irc.base.name][1][rpl['is logged']]['lang']
        if not account:
            account = rpl['is logged']

    if not account:
        account = group('nick')

    user = base[irc.base.name][1][account]
    t = other['target']
    if not user:
        irc.err(t, _('usuario no registrado', lang))
        return

    irc.notice(t, _('nombre de usuario: ', lang) + user['name'])
    irc.notice(t, _('fecha de registro: ', lang) + user['time'])
    irc.notice(t, _('idioma de usuario: ', lang) + i18n.ALL(user['lang']))
    irc.notice(t, _('nivel del usuario: ', lang) + user['status'])
    irc.notice(t, _('cuenta bloqueada: ', lang) + user['lock'][0])
    if user['lock'][0]:
        irc.notice(t, _('razon de bloqueo: ', lang) + user['lock'][1])
