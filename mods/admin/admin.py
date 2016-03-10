# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from sysb.config import core
from sysb import commands
from sysb import i18n
from irc.connection import servers as base

import time

__uptime__ = time.time()
locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'admin')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)


def operid(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    res = base[irc.base.name][1].operid(
    result('name'), result('passwd'), other['rpl_whois'])
    if res in (0, 2):
        irc.err(other['target'], _('parametros invalidos', lc))
    else:
        irc.notice(other['target'], _('autenticado correctamente', lc))


def lock_user(irc, result, group, other):
    iam = base[irc.base.name][1][other['rpl_whois']]
    lc = iam['lang']
    account = result('account')
    reason = result('reason')
    target = other['target']
    user = base[irc.base.name][1][account]
    if not user:
        irc.err(target, _('usuario "%s" inexistente', lc) % account)
    elif not user['lock'][0]:
        if user['status'] in ('global',):
            irc.err(target, _('permiso denegado', lc))

        user['lock'][0] = True
        user['lock'].append(reason)
        base[irc.base.name][1].save
        irc.notice(target, _('usuario "%s" bloqueado razon: %s', lc) %
        (account, reason))
    else:
        irc.err(target, _('usuario "%s" bloqueado con anterioridad', lc) %
        account)


def unlock_user(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    account = result('account')
    target = other['target']
    if not base[irc.base.name][1][account]:
        irc.err(target, _('usuario "%s" inexistente', lc) % account)
    elif base[irc.base.name][1][account]['lock'][0]:
        base[irc.base.name][1][account]['lock'] = [False]
        base[irc.base.name][1].save
        irc.notice(target, _('usuario "%s" desbloqueado', lc) % account)
    else:
        irc.err(target, _('el usuario "%s" no esta bloqueado', lc) % account)


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
            kwargs = {'flag': result('flags')}
        else:
            kwargs = {'template': result('flags')}

        base[irc.base.name][2].flags('set',
        other['channel'], result('target').lower(), **kwargs)

        after = base[irc.base.name][2].flags(
        'get', other['channel'], result('target').lower())

        irc.notice(other['target'], _('flags actualizado:', lc) +
        " [%s] - (%s) >> (%s)" % (result('target'), before, after))


def addoper(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    opers = core.obtconfig('opers')
    level, name, password = result('level', 'name', 'sha_passwd')

    if '/' in level:
        level, server = level.split('/')
        if level == 'global':
            server = None
    else:
        server = None

    if server and not server in base:
        irc.err(other['target'], _('servidor "%s" invalido', lc) % server)
        return

    if not level in ('noob', 'local', 'global'):
        irc.err(other['target'], _('nivel "%s" invalido', lc) % level)
        return

    if not len(password) == 64 or not password.isalnum():
        irc.err(other['target'], _('la contraseña debe estar en sha256', lc))
        return

    opers.append({
        'passwd': password,
        'user': name,
        'level': level if not server else (level, server)})
    core.upconfig('opers', opers)
    irc.notice(other['target'], _('operador %s "%s" agregado', lc) % (level, name))


def deloper(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    name = result('name')
    opers = core.obtconfig('opers')

    for oper in opers:
        if oper['user'] == name:
            opers.remove(oper)
            break
    core.upconfig('opers', opers)

    irc.notice(other['target'], _('operador "%s" eliminado', lc) % name)


def load_module(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    mod = result('module')
    res = commands.commands.load_modules(mod)
    target = other['target']
    if res is None:
        irc.err(target, _('el modulo "%s" no existe', lc) % mod)
        return
    elif res is True:
        irc.notice(target, _('modulo "%s" cargado', lc) % mod)
    elif res is 0:
        irc.err(target, _('modulo "%s" deshabilitado', lc))
    elif res is 1:
        irc.err(target, _('modulo "%s" en desarrollo', lc))
    elif isinstance(res, list):
        irc.err(target, _('el modulo "%s" contiene errores', lc) % mod)
        for line in res:
            irc.err(target, line)


def download_module(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    mod = result('module')
    res = commands.commands.download_module(mod)
    if not res:
        irc.err(other['target'], _('el modulo "%s" no existe', lc) % mod)
    else:
        irc.notice(other['target'], _('modulo "%s" descargado', lc) % mod)


def join(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    channel = result('channel')
    if not channel.lower() in irc.joiner:
        passwd = result('passwd')
        irc.join(channel, passwd if passwd else '')
    else:
        irc.err(other['target'], _('userbot ya esta en el canal %s', lc) % channel)


def mode(irc, result, group, other):
    irc.mode(result('target'), result('mode'))


def nick(irc, result, group, other):
    irc.nick(result('newnick'))


def say(irc, result, group, other):
    denied = 'chanserv nickserv memoserv'
    user = base[irc.base.name][1][other['rpl_whois']]
    lc = user['lang']
    message = result('message')
    target = result('target')
    if user['status'] != 'global' and target.lower() in denied:
        irc.err(target, _('permiso denegado', lc))
        return
    irc.privmsg(target, message)


def connect_to(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    server = result('servername')
    target = other['target']
    if not server in base:
        irc.err(target, _('el servidor %s no existe', lc) % server)
    if not base[server][0].is_connected():
        base[server][0].connect()
    else:
        irc.err(target, _('ya se esta conectado a %s', lc) % server)


def disconnect_to(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    server = result('servername')
    target = other['target']
    if not server in base:
        irc.err(target, _('el servidor %s no existe', lc) % server)
    if base[server][0].is_connected():
        base[server][0].disconnect()
    else:
        irc.err(target, _('ya se esta conectado a %s', lc) % server)


def execute(irc, result, group, other):
    def __exec__(code):
        import traceback

        try:
            return eval(code)
        except:
            return traceback.format_exc().splitlines()

    res = __exec__(result('code'))
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']

    if isinstance(res, type):
        res = str(res)

    try:
        res.__len__
    except AttributeError:
        res = str(res)

    if isinstance(res, type(None)) or len(res) == 0:
        irc.notice(other['target'], _('objeto %s vacio', lc) % type(res))
    elif isinstance(res, list) or isinstance(res, tuple):
        for line in res:
            irc.notice(other['target'], line)
    else:
        irc.notice(other['target'], str(res))


def uptime(irc, result, group, other):
    def servers(serv=None, ircobj=None, ch=None, usr=None, opers=None):
        ls = []
        for servername, l, in base.items():
            ircobject, user, channel = l
            if serv:
                ls.append(0)
            elif ircobj and ircobject.connected:
                ls.append(0)
            elif ch:
                for i in range(len(channel)):
                    ls.append(0)
            elif usr:
                for i in range(len(user)):
                    ls.append(0)
            elif opers:
                for uuid, __user__ in user:
                    if __user__['status'] in 'global local noob':
                        ls.append(0)

        return len(ls)

    # Time zone
    year = 0
    month = 0
    day = 0
    hours = 0
    mins = 0
    secs = 0
    future = time.time() - __uptime__
    while 1:
        if future > 377395200:
            year += 1
            future -= 377395200
            continue
        if future > 31449600:
            month += 1
            future -= 31449600
            continue
        if future > 86400:
            day += 1
            future -= 86400
            continue
        elif future > 3600:
            hours += 1
            future -= 3600
            continue
        elif future > 60:
            mins += 1
            future -= 60
            continue
        else:
            secs += future
            break

    # Thread zone
    from sysb import Thread
    import threading
    thd_tot = Thread.total[0]
    thd_run = len(threading.enumerate())

    # IRC Zone
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    message = _('andando hace: %s, threads: lanzandos %s, andando %s', lc)
    message += _(', servidores %s, conectados %s', lc)
    message += _(', canales %s, usuarios %s, operadores %s', lc)

    message = message % (
        '%s%s%s%s%s%s' % (
            _('{} año(s)', lc).format(year) if year else '',
            _('{} mes(es), ', lc).format(month) if month else '',
            _('{} dia(s), ', lc).format(day) if day else '',
            _('{} hora(s), ', lc).format(hours) if hours else '',
            _('{} minuto(s), ', lc).format(mins) if mins else '',
            _('{} segundo(s)', lc).format(secs) if secs else ''),
        thd_tot,
        thd_run,
        servers(serv=True),
        servers(ircobj=True),
        servers(ch=True),
        servers(usr=True),
        servers(opers=True)
    )
    irc.notice(other['target'], message)