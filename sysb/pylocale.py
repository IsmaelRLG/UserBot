# -*- coding: utf-8 -*-

import json
import logging
import urllib2
import re

from json import loads

log = logging.getLogger(__name__)

LC_ALL = {"el": "Greek",
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
            "es": "Spanish",
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


class pylocale(object):

    def load(self, filename):
        with open(filename) as e:
            conf = json.load(e)
        return conf

    def save(self, filename, obj):
        with file(filename, 'w') as f:
            json.dump(obj, f)


class turn(pylocale):

    def __init__(self, LC_O, FILEJSON, mod):
        """
        Argumentos:
        * LC_O -- Codigo de lenguaje del idioma original.
        * FILEJSON -- Archivo json con las traducciones.
        """
        self.LC_O = LC_O
        self.mod = mod

        self.trs = self.load(FILEJSON)

    def tr_aval(self, mod, lc):
        assert not lc is 'info'
        return lc in self.trs[mod].keys()

    def _tr_aval(self):
        return self.trs[self.mod].keys()

    def turn_tr_str(self, string, lc=None):
        string = unicode(string.decode('utf-8')).lower()
        if lc is self.LC_O:
            return string

        if lc is None:
            lc = self.LC_O
        elif not self.tr_aval(self.mod, lc):
            try:
                lc = lc.split('_')[0]  # ¿Un codigo de lenguaje regional?
            except IndexError:
                lc = self.LC_O
                if lc in LC_ALL:  # Registrando lo sucedido...
                    log.error('translation from "%s" is not available' %
                    LC_ALL[lc])
            else:
                lc = self.LC_O

        return self.trs[self.mod][lc][unicode(hash(string))].encode('utf-8')


class gettext(pylocale):

    def __init__(self, path_config):
        self.conf = self.load(path_config)
        self.obt = {}

    def read(self):
        __mod = {}
        for mod in self.conf:
            with open(self.conf[mod]['path']) as module:
                __mod[mod] = module.readlines()

        for mod, lines in __mod.items():
            for line in lines:
                line = line.rstrip('\n')
                if line.startswith(' ') or line.startswith('\t'):
                    line = line.strip(' ')
                    line = line.strip('\t')

                self.conf[mod]['func'] = self.conf[mod]['func'].encode('utf-8')

                while True:

                    posc = line.find(self.conf[mod]['func'])
                    if posc != -1:

                        line = line[posc:].lstrip(self.conf[mod]['func'])
                        if line.startswith(' '):
                            line = line.strip(' ')

                        if line.startswith('('):
                            line = line.strip('(')

                            posc_ = line.find(')')
                            if posc_ != -1:
                                line = line[:posc_]
                                if line in vars().keys():
                                    break

                                try:
                                    try:
                                        line = eval(line)[0].encode('utf-8')
                                    except UnicodeDecodeError:
                                        line = line.decode('utf-8')
                                        #line = line.encode('utf-8')
                                    except SyntaxError:
                                        pass

                                    self.add(mod, self.conf[mod]['lc'], line)
                                    break

                                except NameError as name:
                                    name = eval(str(name).split()[1])
                                    line = line.replace(name, '')
                                    try:
                                        line = eval(line)[0]
                                    except SyntaxError:
                                        pass

                                    try:
                                        line = line.encode('utf-8')
                                    except UnicodeDecodeError:
                                        line = line.decode('utf-8')
                                        #line = line.encode('utf-8')

                                    self.add(mod, self.conf[mod]['lc'], line)
                                    break
                    else:
                        break

    def add(self, mod, lc, string):
        print [string]
        if not mod in self.obt:
            self.obt[mod] = {}

        if not lc in self.obt[mod]:
            self.obt[mod][lc] = {}

        self.obt[mod][lc][hash(string.lower())] = string
        log.info('New string: mod="%s", str="%s" LC="%s"' % (mod, string, lc))

    def _save(self, name):
        self.save(name, self.obt)


class tr(pylocale):

    def __init__(self, FILEJSON):
        self.filename = FILEJSON
        self.trn = self.load(FILEJSON)

    def translate(self, text, input, output, n=1):
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
        result = loads(urllib2.urlopen(http_request).read().decode('UTF-8'))
        if n == 1:
            return result['matches'][1]['translation'].encode('UTF-8')
        elif n == 2:
            return result['responseData']['translatedText'].encode('UTF-8')

    def already_translated(self, mod, lc):
        assert lc != 'info'
        return mod in self.trn and lc in self.trn[mod]

    def tr_to(self, input, output):
        assert input in LC_ALL and output in LC_ALL

        for mod in self.trn:
            log.debug('Trying to translate the module "%s"' % mod)
            if not self.already_translated(mod, input):
                log.error("the language '%s' source it's not available" %
                LC_ALL[input])
                log.warning('languages available: ' +
                ', '.join(self.trn[mod].keys()))
                continue

            if self.already_translated(mod, output):
                log.error('The module "%s" is already translated' % mod)
                continue

            for id in self.trn[mod][input]:
                str = self.trn[mod][input][id]  # lint:ok
                log.debug('translating of %s to %s: %s' % (input, output, str))
                try:
                    tr = self.translate(str, input, output, n=2)
                except:
                    log.warning('used second option of translate!')
                    tr = self.translate(str, input, output)
                log.debug('translation of %s to %s: %s' % (input, output, tr))

                if not output in self.trn[mod]:
                    self.trn[mod][output] = {}

                self.trn[mod][output][id] = tr
            log.debug('The module %s has been translated' % mod)

    def _save(self):
        self.save(self.filename, self.trn)


def parsename(string):
    return string.split('.').pop()