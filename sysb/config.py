# -*- coding: utf-8 -*-

import cPickle
import database


class config(database.ownbot):

    def __init__(self):
        # Creamos la linda tabla que almacenara toda la configuracion <3
        self.create('core', 'id text key not null, pick text not null', True)
        try:
            self.obtconfig('VERSION')
        except IndexError:
            self.addconfig('VERSION', ('UserBot', 0, 7, 54))

    def addconfig(self, name, _object):
        """ Añade un objeto a la base de datos que sera serializado con Pickle
        para su uso posterior.
        Argumentos:
            _object -- Objeto equis a serializar."""
        self.insert('core', """ "%s", "%s" """ % (name, cPickle.dumps(_object)))

    def delconfig(self, nam):
        self.delete('core', nam)

    def obtconfig(self, nam):
        return cPickle.loads(
            self.select('core', 'pick', 'id="%s"' % nam)[0][0].encode('utf-8'))

    def upconfig(self, name, _object):
        self.update('core',
                    """ pick="%s" """ % cPickle.dumps(_object),
                    "id='%s'" % name)

# Feauture
core = config()