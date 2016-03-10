# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import json
import random
import socket
import urllib
import urllib2

from sysb.config import core
from sysb import i18n

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'google')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)
c5d = "\2\312G\304o\308o\312g\303l\304e\3\2: "


def images(irc, result, group, other):
    quote = urllib.quote(result('text2find'))
    ip = socket.gethostbyname(socket.gethostname())
    size = "imgsz=small|medium|large|xlarge"
    filetype = "png|jpg|gif"
    len = "rsz=" + str(1)  # lint:ok

    url = ('https://ajax.googleapis.com/ajax/services/search/'
           'images?v=1.0&q=%s&userip=%s&as_filetype=%s&%s&%s')
    url = url % (quote, ip, filetype, size, len)

    request = urllib2.Request(url, None, {'Referer': 'http://bobbelderbos.com'})
    result = json.loads(urllib2.urlopen(request))['responseData']['results']
    result = random.choice(result)

    irc.notice(other['target'], c5d + "\311" + result)


def search(irc, result, group, other):
    url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s"
    url = url % urllib.quote(result('text2find'))
    result = json.loads(urllib.urlopen(url)['responseData']['results'])

    for one in result:
        result.remove(one)
        result.append("%s \311%s" % (one['titleNoFormatting'], one['url']))

    max = 2
    str = []
    for it in max:
        if len(result) >= 1:
            one = random.choice(result)
            str.append(one)
            result.remove(one)

    irc.notice(other['target'], c5d + "\2" + "\00313|\3".join(str))
