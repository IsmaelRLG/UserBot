# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
import os, json, logging

logs = logging.getLogger(__name__)


class i18n(object):

    def load(self, filename, type, name='json'):
        try:
            with open(filename) as file:  # lint:ok
                setattr(self, name, json.load(file))
        except Exception as error:
            return logs.error(error)

        if type.lower() == 'path':
            return self.path_val(getattr(self, name))
        elif type.lower() == 'tpk':
            return self.tpk_val(getattr(self, name))
        else:
            return logs.warning('tipo de fichero desconocido, solo: path tpk')

    def save(self, filename, obj):
        try:
            with file(filename, 'w') as filejson:
                json.dump(obj, filejson, indent=4)
        except Exception as error:
            return logs.error(error)
        else:
            logs.info('"%s" guardado correctamente' % filename)

    def path_val(self, dict):
        default = ('func', 'path', 'lc')
        for key, items in dict.items():

            for stuff in default:
                if not stuff in items:
                    logs.error('clave "%s" indefinida en "%s"' % (stuff, key))
                    return False

            if not os.path.exists(items['path']):
                logs.error('No existe el fichero: "%s"' % items['path'])
                return False

        logs.info('lista de modulos verificada')
        encode_dict(dict)
        return True

    def tpk_val(self, dict):
        for mod_name, items in dict.items():

            langs = []
            for lang, subitems in items.items():
                if not lang in langs:
                    langs.append(lang)
                else:
                    logs.warning('¿hay dos lenguajes iguales en un modulo? O_O')

                #for numkeys, text in subitems.items():
                    #try:
                        #int(numkeys)
                    #except ValueError:
                        #logs.error('[%s][%s][%s]: clave invalida' %
                        #(mod_name, lang, numkeys))
                        #return False

        logs.info('paquete de traducciones verificado')
        encode_dict(dict)
        return True


def parsename(string):
    return string.split('.').pop()


def encode_dict(dictionary):
    for key, items in dictionary.items():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(items, unicode):
            items = items.encode('utf-8')
        elif isinstance(items, dict):
            encode_dict(items)
        del dictionary[key]
        dictionary.update({key: items})