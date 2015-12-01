# -*- coding: utf-8 -*-

from sysb.config import core
from sysb import commands
from sysb import i18n
from irc.connection import servers as base

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate'),
    'opers')
_ = locale.turn_tr_str
lang = core.obtconfig('lang')


@commands.addHandler('opers', 'oper id (?P<name>[^ ]+) (?P<passwd>[^ ]+)', {
    'sintax': 'oper id <name> <password>',
    'example': 'oper id root 1234',
    'desc': _('bloquea a un usuario en userbot', lang)},
    registered=True,
    logged=True)
def operid(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    res = base[irc.base.name][1].operid(
    result('name'), result('passwd'), other['rpl_whois'])
    if res in (0, 2):
        irc.err(other['target'], _('parametros invalidos', lc))
    else:
        irc.notice(other['target'], _('autenticado correctamente', lc))


@commands.addHandler('opers', 'oper lock (?P<account>[^ ]+) (?P<reason>.*)', {
    'sintax': 'oper lock <account> <reason>',
    'example': 'oper lock fooser bad boy',
    'desc': _('bloquea a un usuario en userbot', lang)},
    registered=True,
    oper=('local', 'global'),
    logged=True)
def lock_user(irc, result, group, other):
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']
    account = result('account')
    target = other['target']
    if not base[irc.base.name][1][account]:
        irc.err(target, _('usuario "%s" inexistente', lc) % account)
    elif not base[irc.base.name][1][account]['lock'][0]:
        base[irc.base.name][1][account]['lock'][0] = True
        base[irc.base.name][1][account]['lock'].append(result('reason'))
        base[irc.base.name][1].save
        irc.notice(target, _('usuario "%s" bloqueado razon: %s', lc) %
        (account, result('reason')))
    else:
        irc.err(target, _('usuario "%s" bloqueado con anterioridad', lc) %
        account)


@commands.addHandler('opers', 'oper unlock (?P<account>[^ ]+)', {
    'sintax': 'oper unlock <account>',
    'example': 'oper unlock fooser',
    'desc': _('desbloquea a un usuario en userbot', lang)},
    oper=('local', 'global'),
    logged=True)
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


@commands.addHandler('opers', 'oper flags (?P<channel>[^ ]+) (?P<target>[^ ]+) (?P<flags>[^ ]+)', {
    'sintax': 'oper flags <channel> <target> <flags/template>',
    'example': 'oper flags #Foo fooser founder',
    'desc': _('fuerza el cambio de flags en un canal', lang)},
    oper=('local', 'global'),
    logged=True,
    registered=True,
    channels=True,
    chn_registered=True,
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
            kwargs = {'flag': result('flags')}
        else:
            kwargs = {'template': result('flags')}

        base[irc.base.name][2].flags('set',
        other['channel'], result('target').lower(), **kwargs)

        after = base[irc.base.name][2].flags(
        'get', other['channel'], result('target').lower())

        irc.notice(other['target'], _('flags actualizado:', lang) +
        " [%s] - (%s) >> (%s)" % (result('target'), before, after))


@commands.addHandler('opers', 'oper add (?P<level>[^ ]+) (?P<name>[^ ]+) (?P<sha_passwd>[^ ]+)', {
    'sintax': 'oper add <level> <name> <sha_passwd>',
    'example': 'oper add local/freenode root 81dc9bdb52d04dc20036dbd8313ed055',
    'desc': (
        _('añade un nuevo operador de userbot segun el nivel dado', lang),
        _('niveles disponibles: global local/servidor noob/servidor', lang))},
    oper=('global',),
    logged=True)
def addoper(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    opers = core.obtconfig('opers')
    level, name, password = result('level', 'name', 'sha_passwd')

    if '/' in level:
        level, server = level.split('/')
        if level == 'global':
            server = None
    else:
        server = None

    if server and not server in base:
        irc.err(other['target'], _('servidor "%s" invalido', lang) % server)
        return

    if not level in ('noob', 'local', 'global'):
        irc.err(other['target'], _('nivel "%s" invalido', lang) % level)
        return

    if not len(password) == 64 or not password.isalnum():
        irc.err(other['target'], _('la contraseña debe estar en sha256', lang))
        return

    opers.append({
        'passwd': password,
        'user': name,
        'level': level if not server else (level, server)})
    core.upconfig('opers', opers)
    irc.notice(other['target'], _('operador %s "%s" agregado', lang) % (level, name))


@commands.addHandler('opers', 'oper del (?P<name>[^ ]+)', {
    'sintax': 'oper del <name>',
    'example': 'oper del root',
    'desc': _('elimina un operador de userbot', lang)},
    oper=('global',),
    logged=True)
def deloper(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    opers = core.obtconfig('opers')

    for oper in opers:
        if oper['user'] == result('name'):
            opers.remove(oper)
            break
    core.upconfig('opers', opers)

    irc.notice(other['target'], _('operador "%s" eliminado', lang) % result('name'))


@commands.addHandler('opers', 'oper load (?P<module>[^ ]+)', {
    'sintax': 'oper load <module>',
    'example': 'oper load users.py',
    'desc': _('carga un modulo a userbot', lang)},
    oper=('global',),
    logged=True)
def load_module(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    mod = result('module')
    res = commands.commands.load_modules(mod)
    if res is None:
        irc.err(other['target'], _('el modulo "%s" no existe', lang) % mod)
        return
    elif res is True:
        irc.notice(other['target'], _('modulo "%s" cargado', lang) % mod)
    elif isinstance(res, list):
        irc.err(other['target'], _('el modulo "%s" contiene errores', lang) % mod)
        for line in res:
            irc.err(other['target'], line)


@commands.addHandler('opers', 'oper reload (?P<module>[^ ]+)', {
    'sintax': 'oper reload <module>',
    'example': 'oper reload users.py',
    'desc': _('recarga un modulo de userbot', lang)},
    oper=('global',),
    logged=True)
def reload_module(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    mod = result('module')
    res = commands.commands.reload_modules(mod)
    if res is None:
        irc.err(other['target'], _('el modulo "%s" no existe', lang) % mod)
        return
    elif res is True:
        irc.notice(other['target'], _('modulo "%s" recargado', lang) % mod)
    elif isinstance(res, list):
        irc.err(other['target'], _('el modulo "%s" contiene errores', lang) % mod)
        for line in res:
            irc.err(other['target'], line)


@commands.addHandler('opers', 'oper download (?P<module>[^ ]+)', {
    'sintax': 'oper download <module>',
    'example': 'oper download users.py',
    'desc': _('descarga un modulo de userbot', lang)},
    oper=('global',),
    logged=True)
def download_module(irc, result, group, other):
    lang = base[irc.base.name][1][other['rpl_whois']['is logged']]['lang']
    mod = result('module')
    res = commands.commands.download_module(mod)
    if not res:
        irc.err(other['target'], _('el modulo "%s" no existe', lang) % mod)
    else:
        irc.noticeo(other['target'], _('modulo "%s" descargado', lang) % mod)


@commands.addHandler('opers', 'oper join (?P<channel>[^ ]+)( (?P<passwd>[^ ]+))?', {
    'sintax': 'oper join <channel> <password>?',
    'example': 'oper join #Foo',
    'desc': _('ingresa userbot a un canal', lang)},
    oper=('noob', 'local', 'global'),
    logged=True)
def join(irc, result, group, other):
    channel = result('channel')
    if not channel.lower() in irc.joiner:
        passwd = result('passwd')
        irc.join(channel, passwd if passwd else '')
        irc.notice(other['target'], 'ok')
    else:
        irc.err(other['target'], _('userbot ya esta en el canal (%s)') % channel)


@commands.addHandler('opers', 'oper part (?P<channel>[^ ]+)( (?P<reason>.*))?', {
    'sintax': 'oper part <channel> <reason>',
    'example': 'oper part #Foo Bye',
    'desc': _('userbot abandona un canal', lang)},
    oper=('noob', 'local', 'global'),
    logged=True)
def part(irc, result, group, other):
    pass


@commands.addHandler('opers', 'oper mode (?P<target>[^ ]+) (?P<mode>[^ ]+)( (?P<mask>[^ ]+))?', {
    'sintax': 'oper mode <target> <mode> <mask>',
    'example': 'oper mode #Foo +b *!*@localhost',
    'desc': _('establece un modo de canal / usuario', lang)},
    oper=('local', 'global'),
    logged=True)
def mode(irc, result, group, other):
    pass


@commands.addHandler('opers', 'oper connect (?P<servername>[^ ]+)', {
    'sintax': 'oper connect <servername>',
    'example': 'oper connect localhost',
    'desc': _('conecta a userbot a un servidor especificado', lang)},
    oper=('global',),
    logged=True)
def connect_to(irc, result, group, other):
    pass


@commands.addHandler('opers', 'oper disconnect (?P<servername>[^ ]+)', {
    'sintax': 'oper disconnect <servername>',
    'example': 'oper disconnect localhost',
    'desc': _('desconecta a userbot de un servidor', lang)},
    oper=('global',),
    logged=True)
def disconnect_to(irc, result, group, other):
    pass


@commands.addHandler('opers', 'oper stats (?P<any>.*)', {
    'sintax': 'oper stats <any>',
    'example': 'oper stats users',
    'desc': _('muestra estadisticas si estan disponibles', lang)},
    oper=('local', 'global'),
    logged=True)
def stats(irc, result, group, other):
    pass


@commands.addHandler('opers', 'oper exec (?P<code>.*)', {
    'sintax': 'oper exec <code>',
    'example': 'oper exec ", ".join(commands.commands.modules.keys())',
    'desc': _('ejecuta codigo Python y responde lo retornado', lang)},
    oper=('global',),
    logged=True)
def execute(irc, result, group, other):
    def __exec__(code):
        import traceback

        try:
            return eval(code)
        except:
            return traceback.format_exc().splitlines()

    res = __exec__(result('code'))
    lc = base[irc.base.name][1][other['rpl_whois']]['lang']

    irc.notice(other['target'], _('*** resultado de ejecucion ***', lc))
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
    irc.notice(other['target'], _('*** fin del resultado***', lc))