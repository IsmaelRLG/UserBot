# -*- coding: utf-8 -*-

import re
import util
import commands
import pylocale
import katheryn

from config import core as config
from katheryn import (
    USER_NOT_REGISTERED,
    INVALID_PARAMETER,
    OPERATION_SUCCESSFUL,
    USER_REGISTERED,
    OPERATION_FAILED,
    PERMISSION_DENIED,
    CHANNEL_REGISTERED,
    CHANNEL_NOT_REGISTERED)

trn = pylocale.turn('es', config.obtconfig('trs'), pylocale.parsename(__name__))
_ = trn.turn_tr_str
usr = katheryn.tona
chn = katheryn.nieto
dlc = config.obtconfig('default_lang')


@commands.addHandler(
    'chan register',
    'chan register',
    _('registra un nuevo canal en userbot', dlc),
    'chan register <channel>',
    '',
    __name__,
    chn_req=(True, 'chan register (?P<channel>[^ ]+)', 'channel'),
    no_registered=True)
def register(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    r = chn.register(irc.base.name, result('channel'), group('nick'))
    if r is CHANNEL_REGISTERED:
        irc.err(other['target'], _('canal registrado', lang))
    elif r is OPERATION_SUCCESSFUL:
        irc.notice(other['target'], _('canal registrado con exito', lang))


@commands.addHandler(
    'chan (flags|access|privs) (?P<username>[^ ]+) (?P<flags>[^ ]+)',
    'chan flags',
    _('añade flags a un usuario en un canal en userbot', dlc),
    'chan <channel> flags <username> <flags>',
    'S',
    __name__,
    chn_req=(
        True,
        'chan (?P<channel>[^ ]+) flags (?P<username>[^ ]+) (?P<flags>[^ ]+)',
        'channel'))
def setFlags(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    kwargs = {'flags' if '+' in result('flags')
              or '-' in result('flags') else 'templats': result('flags')}
    r = chn.setFlags(
        irc.base.name,  # Nombre de la red
        other['channel'],  # Canal a setear los flags
        result('username'),  # Nombre del usuario
        **kwargs)  # flags

    if r is CHANNEL_NOT_REGISTERED:
        irc.err(other['target'],
        _('canal "%s" no registrado.', lang) % other['channel'])
    elif r is USER_NOT_REGISTERED:
        irc.err(other['target'],
        _('usurario "%s" no registrado', lang) % result('username'))
    elif r is OPERATION_FAILED:
        irc.err(other['target'], _('no se pudieron cambiar los flags', lang))
    elif isinstance(r, tuple):
        irc.notice(other['target'], _('flags cambiados a: ', lang) + str(r))


@commands.addHandler()
def list_flags():
    pass
