# -*- coding: utf-8 -*-

from irc.util import genls
from sysb.config import core
from sysb import commands
from sysb import i18n

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate'),
    'channels')
_ = locale.turn_tr_str
lang = core.obtconfig('lang')


@commands.addHandler('manager', 'op( (?P<channel>#[^ ]+))?( (?P<target>.*))?',
    {'sintax': 'op <channel>? <target>',
    'example': 'op #Foo fuser fuser2',
    'desc': _('asigna estatus de operador a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')
def op(irc, result, group, other):
    target = result('target')
    if not target:
        target = [group('nick')]
    else:
        target = target.split()
    gen = genls(target, other['channel'], irc)
    irc.mode(other['channel'], '+%s %s' % ((len(gen) * 'o'), ' '.join(gen)))


@commands.addHandler('manager', 'deop( (?P<channel>#[^ ]+))?( (?P<target>.*))?',
    {'sintax': 'deop <channel>? <target>',
    'example': 'deop #Foo fuser fuser2',
    'desc': _('remueve el estatus de operador a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='o',
    chan_reqs='channel')
def deop(irc, result, group, other):
    target = result('target')
    if not target:
        target = [group('nick')]
    else:
        target = target.split()
    gen = genls(target, other['channel'], irc)
    print gen
    irc.mode(other['channel'], '-%s %s' % ((len(gen) * 'o'), ' '.join(gen)))


@commands.addHandler('manager', 'v(oice)?( (?P<channel>#[^ ]+))?( (?P<target>.*'
    '))?', {'sintax': 'voice <channel>? <target>',
    'example': 'voice #Foo fuser fuser2',
    'desc': _('asigna voice a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='v',
    chan_reqs='channel')
def voice(irc, result, group, other):
    target = result('target')
    if not target:
        target = [group('nick')]
    else:
        target = target.split()
    gen = genls(target, other['channel'], irc)
    irc.mode(other['channel'], '+%s %s' % ((len(gen) * 'v'), ' '.join(gen)))


@commands.addHandler('manager', '(devoice|dv)( (?P<channel>#[^ ]+))?( (?P<targe'
    't>.*))?', {'sintax': 'devoice <channel>? <target>',
    'example': 'devoice #Foo fuser fuser2',
    'desc': _('remueve el voice a un usuario', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='v',
    chan_reqs='channel')
def devoice(irc, result, group, other):
    target = result('target')
    if not target:
        target = [group('nick')]
    else:
        target = target.split()
    gen = genls(target, other['channel'], irc)
    irc.mode(other['channel'], '-%s %s' % ((len(gen) * 'v'), ' '.join(gen)))


@commands.addHandler('manager', 'join (?P<channel>[^ ]+)( (?P<passwd>[^ ]+))?',
    {'sintax': 'join <channel> <password>?',
    'example': 'join #Foo',
    'desc': _('ingresa userbot a un canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='r',
    chan_reqs='channel')
def join(irc, result, group, other):
    channel = result('channel')
    if not channel.lower() in irc.joiner:
        passwd = result('passwd')
        irc.join(channel, passwd if passwd else '')
    else:
        irc.err(other['target'], _('userbot ya esta en el canal %s') % channel)


@commands.addHandler('manager', 'part (?P<channel>[^ ]+)( (?P<reason>.*))?',
    {'sintax': 'part <channel> <reason>?',
    'example': 'part #Foo Bye',
    'desc': _('saca a userbot de un canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='r',
    chan_reqs='channel')
def part(irc, result, group, other):
    channel = result('channel')
    if channel.lower() in irc.joiner:
        reason = result('reason')
        irc.part(channel, reason if reason else '')
    else:
        irc.err(other['target'], _('userbot no esta en el canal %s') % channel)


@commands.addHandler('manager', '(kick|k)( (?P<channel>#[^ ]+))? (?P<target>[^ '
    ']+)( (?P<reason>.*))?', {'sintax': 'kick <channel>? <target> <reason>?',
    'example': 'kick #Foo fuser bad boy',
    'desc': _('expulsa a un usuario de un canal', lang)},
    registered=True,
    logged=True,
    channels=True,
    chn_registered=True,
    privs='k',
    chan_reqs='channel')
def kick(irc, result, group, other):
    reason = result('reason')
    reason = reason if reason else other['nick']
    for target in genls(result('target').split(), other['channel'], irc):
        irc.kick(other['channel'], target, reason)
