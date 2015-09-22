# -*- coding: utf-8 -*-

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
    PERMISSION_DENIED)

trn = pylocale.turn('es', config.obtconfig('trs'), pylocale.parsename(__name__))
_ = trn.turn_tr_str
usr = katheryn.tona
dlc = config.obtconfig('default_lang')


@commands.addHandler(
    'user register (?P<username>[^ ]+) (?P<password>.*)',
    'user register',
    _('registra un usuario nuevo en userbot', dlc),
    'user register <username> <password>',
    '',
    __name__,
    any=True,
    prv=True)
def register(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    r = usr.register(irc.base.name, result('username'), result('password'))
    if r is OPERATION_SUCCESSFUL:
        irc.notice(group('nick'),
        _('usuario "%s" registrado con exito.', lang) % result('username'))
    elif r is USER_REGISTERED:
        irc.err(group('nick'),
        _('usuario "%s" ya registrado', lang) % result('username'))


@commands.addHandler(
    'user (auth|id|identify) (?P<username>[^ ]+) (?P<password>.*)',
    'user id',
    _('identifica a un usuario como el dueño de una cuenta en userbot', dlc),
    'user auth <username> <password>',
    '',
    __name__,
    any=True,
    prv=True)
def id(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    r = usr.identify(
        irc.base.name,
        result('username'),
        group('host'),
        result('password'))

    if r is USER_NOT_REGISTERED:
        irc.err(group('nick'),
        _('no se encuentra registrado, favor registrese.', lang))
    elif r is INVALID_PARAMETER:
        irc.err(group('nick'), _('usuario o contraseña erronea', lang))
    elif r is OPERATION_SUCCESSFUL:
        irc.notice(group('nick'), _('autenticado con exito', lang))


@commands.addHandler(
    'user (drop|delete|del|remove)',
    'user drop',
    _('elimina a un usuario de la base de datos de userbot', dlc),
    'user drop',
    '',
    __name__,
    prv=True)
def drop(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    r = usr.drop(irc.base.name, group('nick'))
    if isinstance(r, str):
        irc.notice(group('nick'), _('su codigo de eliminacion es: ', lang) + r)
        irc.notice(group('nick'), _('envie: user confirm-drop ', lang) % r)


@commands.addHandler(
    'user (comfirm(-drop)?) (?P<code>.*)'
    'user confirm-drop',
    _('confirma la eleminacion de un usuario.', dlc),
    'user confirm-drop <code>',
    '',
    __name__,
    prv=True)
def confirm_drop(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    r = usr.confirm_drop(result('code'))
    if r is OPERATION_SUCCESSFUL:
        irc.notice(group('nick'), _('se elimino su cuenta con exito.', lang))
    elif r is INVALID_PARAMETER:
        irc.err(group('nick'), _('codigo de confirmacion invalido.', lang))


@commands.addHandler(
    'user info (?P<username>[^ ]+)',
    'user info',
    _('muestra la informacion de un usuario en userbot', dlc),
    'user info <username>',
    '',
    __name__,
    any=True)
def info(irc, group, result, other):
    lang = usr.default_lang(irc.LC, irc.base.name, group('nick'))
    r = usr.info(irc.base.name, result('username'))
    if r:
        n = other['target']
        irc.notice(n, _('nombre: ', lang) + r['name'])
        irc.notice(n, _('lenguaje: ', lang) + pylocale.LC_ALL[r['lang']])
        irc.notice(n, _('estado de cuenta: ', lang) + r['status'])
        if usr.isLocked(irc.base.name, result('username')):
            irc.notice(n, _('razon : ', lang) + r['info']['lockReason'])

        id = usr.identified(irc.base.name, result('username'))
        if id is OPERATION_SUCCESSFUL:
            id = 'True'
        elif id is OPERATION_FAILED:
            id = 'False'

        irc.notice(n, _('identificado: ', lang) + id)
        irc.notice(n, _('registrado en: ', lang) + r['data'])

        if usr.isOper(irc.base.name, group('nick')):
            irc.notice(group('nick'), _('*** informacion extra ***', lang))
            irc.notice(group('nick'), _('contraseña: ', lang) + r['passwd'])
            if eval(id):
                import time
                id = util.uuid(username)  # lint:ok
                irc.notice(group('nick'), _('visto por ultima vez: ', lang) +
                str(time.time() - usr.online[irc.base.name][id]['IDLE']))
                irc.notice(group('nick'), 'host: ' +
                usr.online[irc.base.name][id]['HOST'])
            irc.notice(group('nick'), _('*** fin ***', lang))
    else:
        irc.err(n, _('usuario "%s" no registrado', lang) % result('username'))


@commands.addHandler(
    'user set lang (?P<lc>.*)',
    'user set lang',
    _('cambia el lenguaje que se muestra por userbot', dlc),
    'user set <langcode>',
    '',
    __name__,
    prv=True)
def set_lc(irc, group, result, other):
    nick = group('nick')
    lang = usr.default_lang(irc.LC, irc.base.name, nick)
    if result('lc') in trn._tr_aval():
        usr.users[irc.base.name][util.uuid(nick)]['lang'] = result('lc')
        lang = usr.default_lang(irc.LC, irc.base.name, nick)
        irc.notice(nick, _('su lenguje se ha actualizado.', lang))
    else:
        irc.err(nick, _('lenguaje "%s" no disponible', lang) % result('lc'))


@commands.addHandler(
    'user set password (?P<passwd>[^ ]+) (?P<new_passwd>[^ ]+)',
    'user set password',
    _('cambia la contraseña que se usara en userbot', dlc),
    'user set password <old_password> <new_password>'
    '',
    __name__,
    prv=True)
def set_passwd(irc, group, result, other):
    nick = group('nick')
    lang = usr.default_lang(irc.LC, irc.base.name, nick)
    old_ = usr.info(irc.base.name, nick)['passwd']
    _old = util.hash(result('passwd'))
    if old_ == _old:
        new = result('new_password')
        usr.ch_passwd(irc.base.name, nick, new)
        irc.notice(nick, _('su contraseña se actualizo a: %s', lang) % new)
        irc.notice(nick, _('Por favor, autentíquese nuevamente', lang))
        irc.notice(nick, _('Envie: user id %s %s', lang) % (nick, new))
    else:
        irc.err(nick, _('contraseña invalida', lang))
