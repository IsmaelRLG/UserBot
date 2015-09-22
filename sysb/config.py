# -*- coding: utf-8 -*-

import os
import cPickle
import database
import traceback


class config(database.ownbot):

    def __init__(self):
        # Creamos la linda tabla que almacenara toda la configuracion <3
        self.create('core', 'id text key not null, pick text not null', True)

        if self.obtconfig('VERSION') is None:
            self.addconfig('VERSION', ('UserBot', 0, 7, 54))

    def addconfig(self, name, _object):
        """ Añade un objeto a la base de datos que sera serializado con Pickle
        para su uso posterior.
        Argumentos:
            _object -- Objeto equis a serializar."""
        self.insert('core', """ "%s", "%s" """ % (name, cPickle.dumps(_object)))

    def delconfig(self, name):
        self.delete('core', name)

    def obtconfig(self, name):
        try:
            return cPickle.loads(
            self.select('core', 'pick', 'id="%s"' % name)[0][0].encode('utf-8'))
        except IndexError:
            pass

    def upconfig(self, name, _object):
        self.update('core',
                    """ pick="%s" """ % cPickle.dumps(_object),
                    "id='%s'" % name)

core = config()
