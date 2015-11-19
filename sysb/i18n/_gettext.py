# -*- coding: utf-8 -*-

import main


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
        if not mod in self.get:
            self.get[mod] = {}

        if not lang in self.get[mod]:
            self.get[mod][lang] = {}

        self.get[mod][lang][str(hash(text.lower()))] = text
        main.logs.debug('text: ' + text)
