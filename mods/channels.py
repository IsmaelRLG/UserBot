# -*- coding: utf-8 -*-

from sysb.config import core
from sysb import commands
from sysb import i18n
from irc.connection import servers as base

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate'),
    'channels')
_ = locale.turn_tr_str
lang = core.obtconfig('lang')


@commands.addHandler('channels', 'chan register( (?P<channel>[^ ]+))?', {
    'sintax': 'chan register <channel>?',
    'example': 'chan register #Foo',
    'desc': _('registra un canal en el bot', lang)},
    registered=True,
    logged=True,
    channels=True,
    chan_reqs='channel')
def register(irc, result, group, other):
    account = other['rpl_whois']['is logged'].lower()
    lang = base[irc.base.name][1][account]['lang']

    if not other['channel'].lower() in irc.joiner:
        irc.err(other['target'],
        _('no puede registrar el canal, informe a un operador', lang))
        return

    resu = base[irc.base.name][2].register(other['channel'], account)
    if resu == 5:
        irc.err(other['target'], _('canal ya registrado', lang))
    elif resu == 7:
        irc.notice(other['target'], _('canal registrado correctamente', lang))


@commands.addHandler('channels', 'chan flags( (?P<channel>#[^ ]+))? (?P<target>[^'
    ' ]+) (?P<flags>[^ ]+)',{
    'sintax': 'chan flags <channel>? <target> <flags>',
    'example': 'chan flags #Foo-chan foo-user OP',
    'desc': _('(añade / elimina / edita / muestra) los flags', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='s',
    chan_reqs='channel')
def flags(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    if result('target', 'flags') == ('*', '*'):

        num = 1
        for us, fl in base[irc.base.name][2][other['channel']]['flags'].items():
            irc.notice(other['target'], '[ %s ] | %-25s | [ %s ]' %
            (str(num).zfill(2), us, fl))
            num += 1
        return

    if not base[irc.base.name][1][result('target')]:
        irc.err(other['target'], _('usuario no registrado en el bot', lang))
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
                irc.err(other['target'], _('permiso denegado', lang))
                return
            kwargs = {'flag': result('flags')}
        else:
            if 'founder'.lower() in result('flags'):
                irc.err(other['target'], _('permiso denegado', lang))
                return
            kwargs = {'template': result('flags')}

        base[irc.base.name][2].flags('set',
        other['channel'], result('target').lower(), **kwargs)

        after = base[irc.base.name][2].flags(
        'get', other['channel'], result('target').lower())

        irc.notice(other['target'], _('flags actualizado:', lang) +
        " [%s] - (%s) >> (%s)" % (result('target'), before, after))


@commands.addHandler('channels', 'chan drop( (?P<channel>#[^ ]+))?', {
    'sintax': 'chan flags <channel>?',
    'example': 'chan drop #foo',
    'desc': _('elimina un canal del bot', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='F',
    chan_reqs='channel')
def drop(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    del base[irc.base.name][2][other['channel']]
    irc.notice(other['target'], _('canal eliminado', lang))
    irc.part(other['channel'], _('saliendo...', lang))


