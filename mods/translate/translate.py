# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015, Ismael R. Lugo G.
"""

import urllib2
import json

from sysb import i18n
from sysb.config import core
from irc.request import whois
from irc.connection import servers as base

locale = i18n.turn(
    'es',
    core.obtconfig('package_translate', cache=True),
    'translate')
_ = locale.turn_tr_str
lang = core.obtconfig('lang', cache=True)

langcodes = {
    "el": "Greek",
    "eo": "Esperanto",
    "en": "English",
    "zh": "Chinese",
    "ro": "Romanian",
    "af": "Afrikaans",
    "tn": "Tswana",
    "mi": "Maori",
    "ca": "Catalan",
    "gu": "Gujarati",
    "nn": "Norwegian",
    "eu": "Basque",
    "cy": "Welsh",
    "ar": "Arabic",
    "zu": "Zulu",
    "cs": "Czech",
    "et": "Estonian",
    "xh": "Xhosa",
    "az": "Azeri",
    "id": "Indonesian",
    "es": "Español",
    "ps": "Pashto",
    "kok": "Konkani",
    "gl": "Galician",
    "nl": "Dutch",
    "pt": "Portuguese",
    "te": "Telugu",
    "nb": "Norwegian",
    "tr": "Turkish",
    "tl": "Tagalog",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "pa": "Punjabi",
    "th": "Thai",
    "vi": "Vietnamese",
    "it": "Italian",
    "sl": "Slovenian",
    "he": "Hebrew",
    "is": "Icelandic",
    "pl": "Polish",
    "ta": "Tamil",
    "be": "Belarusian",
    "fr": "French",
    "bg": "Bulgarian",
    "uk": "Ukrainian",
    "ru": "Russian",
    "hr": "Croatian",
    "sv": "Swedish",
    "de": "German",
    "ts": "Tsonga",
    "da": "Danish",
    "fa": "Farsi",
    "hi": "Hindi",
    "sa": "Sanskrit",
    "bs": "Bosnian",
    "dv": "Divehi",
    "fi": "Finnish",
    "hy": "Armenian",
    "hu": "Hungarian",
    "ja": "Japanese",
    "fo": "Faroese",
    "ka": "Georgian",
    "ns": "Northern",
    "qu": "Quechua",
    "uz": "Uzbek",
    "syr": "Syriac",
    "kk": "Kazakh",
    "sr": "Serbian",
    "sq": "Albanian",
    "mn": "Mongolian",
    "ko": "Korean",
    "kn": "Kannada",
    "mk": "FYRO",
    "ur": "Urdu",
    "sk": "Slovak",
    "mt": "Maltese",
    "tt": "Tatar",
    "ms": "Malay",
    "mr": "Marathi",
    "ky": "Kyrgyz",
    "sw": "Swahili",
    "se": "Sami"}


def translate(input, output, text, n=1):
    if input == output:  # ¿Quizas sea un subnormal?
        return text

    try:
        if not text is text.encode('UTF-8'):
            text = text.encode('UTF-8')
    except:
        pass
    finally:
        text = urllib2.quote(text, '')

    url = ("http://mymemory.translated.net/api/ge"
           "t?q={text}&langpair={input}|{output}").format(**vars())

    headers = {'User-Agent':
        ('Mozilla/5.0 '
        '(Macintosh; Intel Mac OS X 10_6_8)'
        ' AppleWebKit/535.19 '
        '(KHTML, like Gecko) '
        'Chrome/18.0.1025.168 Safari/535.19')}

    http_request = urllib2.Request(url, headers=headers)
    result = json.loads(urllib2.urlopen(http_request).read().decode('UTF-8'))
    if n == 1:
        return result['matches'][1]['translation'].encode('UTF-8')
    elif n == 2:
        return result['responseData']['translatedText'].encode('UTF-8')


def translate2_1(irc, result, group, other):
    input, output, text = result('in', 'out', 'text')
    rpl = whois(irc, group('nick'))
    lc = other['global_lang']
    user = None
    target = other['target']
    if rpl['is logged'] and base[irc.base.name][1][rpl['is logged']]:
        user = base[irc.base.name][1][rpl['is logged']]

    if user:
        lc = user['lang']

    if not output in langcodes:
        irc.err(target, _('codigo de lenguaje invalido: %s', lc) % output)
        return
    elif not input in langcodes:
        irc.err(target, _('codigo de lenguaje invalido: %s', lc) % input)
        return

    irc.notice(target, '(%s -> %s): %s' %
    (input, output, translate(input, output, text)))


def translate2_2(irc, result, group, other):
    input, output, text = result('in', 'out', 'text')
    rpl = whois(irc, group('nick'))
    lc = other['global_lang']
    user = None
    target = other['target']
    if rpl['is logged'] and base[irc.base.name][1][rpl['is logged']]:
        user = base[irc.base.name][1][rpl['is logged']]

    if user:
        lc = user['lang']

    if not output in langcodes:
        irc.err(target, _('codigo de lenguaje invalido: %s', lc) % output)
        return
    elif not input in langcodes:
        irc.err(target, _('codigo de lenguaje invalido: %s', lc) % input)
        return

    irc.notice(target, '(%s -> %s): %s' %
    (input, output, translate(input, output, text, 2)))
