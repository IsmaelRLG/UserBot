# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

from irc.request import whois
from sysb.config import core
from sysb import i18n
from irc.connection import servers as base

import httplib
import socket
import urllib
import json
import re

re_ip = re.compile('(?i)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'channels')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)


def ip(irc, result, group, other):
    rpl = whois(irc, group('nick'))
    lc = other['global_lang']
    user = None
    target = other['target']
    if rpl['is logged'] and base[irc.base.name][1][rpl['is logged']]:
        user = base[irc.base.name][1][rpl['is logged']]

    if user:
        lc = user['lang']

    host = result('hostname')
    text = urllib.quote(host)
    try:
        http = httplib.HTTPConnection("ip-api.com")
        http.request("GET", "/json/{0}?fields=65535".format(text))
        data = json.loads(http.getresponse().read().decode('utf-8'))
        if data['status'] != "success":
            raise ValueError
    except:
        irc.err(target, _('Soy una tetera!', lc))
    else:
        form = '\2{}\2: {}, '
        resp = "IP \2{}\2  ".format(host)
        if data['reverse'] != "":
            resp += "- {}  ".format(data['reverse'])
        if data['country'] != "":
            resp += form.format(_('País', lc), data['country'])
        if data['region'] != "":
            resp += form.format(_('Región', lc), data['region'])
        if data['city'] != "":
            resp += form.format(_('Ciudad', lc), data['city'])
        if data['isp'] != "":
            resp += form.format('ISP', data['isp'])
        if data['org'] != "":
            resp += form.format(_('Organización', lc), data['org'])
        if data['as'] != "":
            resp += form.format('ASN', data['as'])
        if data['timezone'] != "":
            resp += form.format(_('Zona horaria', lc), data['org'])
            resp += "\2\2: {0}, ".format(data['timezone'])
        irc.notice(target, resp[:len(resp) - 2])


def ip2(irc, result, group, other):
    rpl = whois(irc, group('nick'))
    lc = other['global_lang']
    user = None
    target = other['target']
    if rpl['is logged'] and base[irc.base.name][1][rpl['is logged']]:
        user = base[irc.base.name][1][rpl['is logged']]

    if user:
        lc = user['lang']

    host = result('hostname')
    try:
        page = urllib.urlopen('http://freegeoip.net/json/' + host)
        data = json.loads(page.read())
    except:
        irc.err(target, _('Soy una tetera!', lc))
    else:
        response = "[IP/Host Lookup] "
        if re_ip.findall(host):
            ## IP Address
            try:
                hostname = socket.gethostbyaddr(data)[0]
            except:
                hostname = _('Host desconocido', lc)
            response += 'Hostname: ' + str(hostname)
        else:
            ## Host name
            response += 'IP: ' + data['ip']
        spacing = ' |'
        for key in data:
            if not data[key]:
                data[key] = 'N/A'

        form = '%s \2{}\2: {}' % spacing
        if 'city' in data:
            response += form.format(_('Ciudad', lc), data['city'])
        if 'region_name' in data:
            response += form.format(_('Región', lc), data['region_name'])
        if 'country_name' in data:
            response += form.format(_('País', lc), data['country_name'])
        if 'zipcode' in data:
            response += form.format('ZIP', data['zipcode'])
        response += form.format(_('Latitud', lc), data['latitude'])
        response += form.format(_('Longitud', lc), data['longitude'])
        irc.notice(target, response)
