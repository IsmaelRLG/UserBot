# -*- coding: utf-8 -*-

import main
import lc_all


class turn(main.i18n):

    def __init__(self, lang_o, tpk, module):
        self.lang_o = lang_o
        self.module = module

        if not self.load(tpk, 'tpk'):
            return

    def tr_aval(self, module, lang_code):
        assert not lang_code is 'info'
        return lang_code in self.json[module].keys()

    def _tr_aval(self):
        return self.json[self.module].keys()

    def turn_tr_str(self, string, lc=None):
        string = unicode(string.decode('utf-8')).lower()
        if lc is self.lang_o:
            return string

        if lc is None:
            lc = self.lang_o
        elif not self.tr_aval(self.module, lc):
            try:
                lc = lc.split('_')[0]  # ¿Un codigo de lenguaje regional?
            except IndexError:
                lc = self.lang_o
                if lc in lc_all.LC_ALL:  # Registrando lo sucedido...
                    main.logs.error('translation from "%s" is not available' %
                    lc_all.LC_ALL[lc])
            else:
                lc = self.lang_o

        try:
            s = string
            return self.json[self.module][lc][unicode(hash(s))]
        except KeyError:
            error = '[%s][%s][%s](%s)' % (self.module, lc, unicode(hash(s)), s)
            main.logs.error(error)
            return error