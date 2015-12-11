# -*- coding: utf-8 -*-

import md5
import main
import crypt


class gettext(main.i18n):

    def __init__(self, path):
        if not self.load(path, 'path'):
            return

        self.get = {}
        self.read()

    def read(self):
        for mod, items in self.json.items():
            main.logs.debug('intentando leer: "%s"' % items['path'])
            with open(items['path']) as pyfile:
                lines = pyfile.readlines()

            main.logs.debug('buscando texto...')

            # linea por linea
            for lpl in lines:

                # parseando algunas cosas...
                lpl = lpl.rstrip('\n')
                if lpl.startswith(' ') or lpl.startswith('\t'):
                    lpl = lpl.strip(' ')
                    lpl = lpl.strip('\t')

                while True:

                    # Buscando coincidencias
                    posc = lpl.find(items['func'])
                    if posc == -1:
                        break
                    else:
                        lpl = lpl[posc:].lstrip(items['func'])

                        if lpl.startswith(' '):
                            lpl = lpl.strip(' ')

                        if lpl.startswith('('):
                            lpl = lpl.strip('(')
                            posc = lpl.find(')')
                            if posc != -1:
                                lpl = lpl[:posc]
                                if lpl in vars().keys():
                                    break

                                try:
                                    try:
                                        lpl = eval(lpl)[0].encode('utf-8')
                                    except UnicodeDecodeError:
                                        lpl = lpl.decode('utf-8')
                                        #line = line.encode('utf-8')
                                    except SyntaxError:
                                        pass

                                    self.add(mod, items['lc'], lpl)
                                    break
                                except NameError as name:
                                    name = eval(str(name).split()[1])
                                    lpl = lpl.replace(name, '')
                                    try:
                                        lpl = eval(lpl)[0]
                                        if not isinstance(lpl, str):
                                            break

                                    except SyntaxError:
                                        pass

                                    try:

                                        lpl = lpl.encode('utf-8')
                                    except UnicodeDecodeError:
                                        lpl = lpl.decode('utf-8')
                                        #line = line.encode('utf-8')

                                    self.add(mod, items['lc'], lpl)
                                    break

    def add(self, mod, lang, text):
        print [mod, lang, text]
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        if not mod in self.get:
            self.get[mod] = {}

        if not lang in self.get[mod]:
            self.get[mod][lang] = {}

        txt = md5.new(text.lower()).hexdigest()
        self.get[mod][lang][crypt.crypt(txt, txt)] = text
        main.logs.debug('text: ' + text)
