# -*- coding: utf-8 -*-

import urllib2
import lc_all
import main


class tr(main.i18n):

    def __init__(self, tpk):
        if not self.load(tpk, 'tpk'):
            return

        self.get = {}

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
        result =\
        main.json.loads(urllib2.urlopen(http_request).read().decode('UTF-8'))
        if n == 1:
            return result['matches'][1]['translation'].encode('UTF-8')
        elif n == 2:
            return result['responseData']['translatedText'].encode('UTF-8')

    def already_translated(self, mod, lc):
        assert lc != 'info'
        return mod in self.trn and lc in self.trn[mod]

    def tr_to(self, input, output):
        assert input in lc_all.LC_ALL and output in lc_all.LC_ALL

        for mod in self.trn:
            main.logs.debug('Trying to translate the module "%s"' % mod)
            if not self.already_translated(mod, input):
                main.logs.error("the language '%s' source it's not available" %
                lc_all.LC_ALL[input])
                main.logs.warning('languages available: ' +
                ', '.join(self.trn[mod].keys()))
                continue

            if self.already_translated(mod, output):
                lc_all.logs.error('The module "%s" is already translated' % mod)
                continue

            for id in self.trn[mod][input]:
                str = self.trn[mod][input][id]  # lint:ok
                main.logs.debug('translating of %s to %s: %s' % (input, output, str))
                try:
                    tr = self.translate(str, input, output, n=2)
                except:
                    main.logs.warning('used second option of translate!')
                    tr = self.translate(str, input, output)
                main.logs.debug('translation of %s to %s: %s' % (input, output, tr))

                if not output in self.trn[mod]:
                    self.trn[mod][output] = {}

                self.trn[mod][output][id] = tr
            main.logs.debug('The module %s has been translated' % mod)