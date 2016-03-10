# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from irc import center
from irc import util
from irc.request import whois
from sysb.config import core
from sysb import i18n
from irc.connection import servers as base

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'manager')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)


def op(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    target = result('target')
    channel = other['channel']

    if not target:
        target = [group('nick')]
    else:
        target = target.split()

    for masktar in target:
        if util.val_mask(masktar):
            # Esto se activa sí... es una mascara
            for nick in util.make_nick_ls(irc, channel, masktar)[0]:
                irc.mode(channel, '+o ' + nick)
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)

        else:
            # Esto se activa sí... es un nick, o no coincide con nada
            nick_ls = util.make_nick_ls(irc, channel, '*!*@*', lower=True)[0]
            if masktar.lower() in nick_ls:
                irc.mode(channel, '+o ' + masktar)
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)


def deop(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    target = result('target')
    channel = other['channel']

    if not target:
        target = [group('nick')]
    else:
        target = target.split()

    for masktar in target:
        if util.val_mask(masktar):
            # Esto se activa sí... es una mascara
            for nick in util.make_nick_ls(irc, channel, masktar)[0]:
                irc.mode(channel, '-o ' + nick)
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)

        else:
            # Esto se activa sí... es un nick, o no coincide con nada
            nick_ls = util.make_nick_ls(irc, channel, '*!*@*', lower=True)[0]
            if masktar.lower() in nick_ls:
                irc.mode(channel, '-o ' + masktar)
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)


def voice(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    target = result('target')
    channel = other['channel']

    if not target:
        target = [group('nick')]
    else:
        target = target.split()

    print target
    for masktar in target:
        if util.val_mask(masktar):
            # Esto se activa sí... es una mascara
            for nick in util.make_nick_ls(irc, channel, masktar)[0]:
                irc.mode(channel, '+v ' + nick)
                continue
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)

        else:
            # Esto se activa sí... es un nick, o no coincide con nada
            nick_ls = util.make_nick_ls(irc, channel, '*!*@*', lower=True)[0]
            if masktar.lower() in nick_ls:
                irc.mode(channel, '+v ' + masktar)
                continue
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)


def devoice(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    target = result('target')
    channel = other['channel']

    if not target:
        target = [group('nick')]
    else:
        target = target.split()

    for masktar in target:
        if util.val_mask(masktar):
            # Esto se activa sí... es una mascara
            for nick in util.make_nick_ls(irc, channel, masktar)[0]:
                irc.mode(channel, '-v ' + nick)
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)

        else:
            # Esto se activa sí... es un nick, o no coincide con nada
            nick_ls = util.make_nick_ls(irc, channel, '*!*@*', lower=True)[0]
            if masktar.lower() in nick_ls:
                irc.mode(channel, '-v ' + masktar)
            else:
                irc.err(channel, _('nadie en el canal: ', lang) + masktar)


def join(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    channel = result('channel')
    if not channel.lower() in irc.joiner:
        passwd = result('passwd')
        irc.join(channel, passwd if passwd else '')
    else:
        irc.err(other['target'], _('userbot ya esta en el canal %s', lc) % channel)


def part(irc, result, group, other):
    channel = result('channel')
    if channel.lower() in irc.joiner:
        reason = result('reason')
        irc.part(channel, reason if reason else '')
    else:
        lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
        irc.err(other['target'], _('userbot no esta en el canal %s', lc) % channel)


def invite(irc, result, group, other):
    for nickls in result('target').split():
        irc.invite(nickls, other['channel'])


def kick(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    target = result('target')
    channel = other['channel']

    # Mensaje de expulsion!
    message = result('reason')
    p = True
    if not message:
        message = ''
        p = False
    if not message.endswith('.') and p:
        message = message + '.'
    if not message.endswith(' ') and p:
        message = message + ' '
    message = message + _('expulsado por', lang) + ' ' + group('nick')

    if util.val_mask(target):
        # Esto se activa sí... es una mascara
        for nick in util.make_nick_ls(irc, channel, target)[0]:
            if nick.lower() != irc.base.nick.lower():
                irc.kick(channel, nick, message)
        else:
            irc.err(channel, _('nadie en el canal: ', lang) + target)
    else:
        # Esto se activa sí... es un nick, o no coincide con nada
        nick_ls = util.make_nick_ls(irc, channel, '*!*@*', lower=True)[0]
        if target.lower() in nick_ls:
            if target.lower() != irc.base.nick.lower():
                irc.kick(channel, target, message)
        else:
            irc.err(channel, _('nadie en el canal: ', lang) + target)


def ban(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    time = result('time')
    target = result('target')
    channel = other['channel']

    # Mensaje de expulsion!
    message = result('message')
    p = True
    if not message:
        message = ''
        p = False
    if not message.endswith('.') and p:
        message = message + '.'
    if not message.endswith(' ') and p:
        message = message + ' '
    message = message + _('expulsado por', lang) + ' ' + group('nick')

    banned = False
    if util.val_mask(target):
        # Esto se activa sí... es una mascara
        banned = True
        irc.mode(channel, '+b ' + target)
        for nick in util.make_nick_ls(irc, channel, target)[0]:
            irc.kick(channel, nick, message)

    elif irc.features.network == 'freenode' and util.val_extban(target):
        # Esto se activa sí...
        #        La red es freenode y el ban es extendido
        banned = True
        irc.mode(channel, '+b ' + target)
    else:
        # Esto se activa sí... es un nick, o no coincide con nada
        rpl_whois = whois(irc, target)
        if rpl_whois['error']:
            irc.err(channel, rpl_whois['error'])
            return
        else:
            target = '*!*@' + rpl_whois['mask']['host']
            banned = True
            irc.mode(channel, '+b ' + target)
            for nick in util.make_nick_ls(irc, channel, target)[0]:
                irc.kick(channel, nick, message)

    if time and banned:
        try:
            time = center.mode.conv_parse_txt(time)
            center.mode.add(irc.base.name, channel, '-b ' + target)
        except ValueError:
            irc.err(other['target'], _('tiempo invalido', lang))
            return
