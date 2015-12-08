# -*- coding: utf-8 -*-

import cPickle
import database
import time


class config(database.ownbot):

    def __init__(self):
        # Creamos la linda tabla que almacenara toda la configuracion <3
        time.sleep(2)
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
        t = 1
        while t < 2:
            try:
                return cPickle.loads(self.select('core', 'pick', 'id="%s"'
                % name)[0][0].encode('utf-8'))
            except IndexError:
                return
            except self.ProgrammingError:
                time.sleep(t)
                t += 1

    def upconfig(self, name, _object):
        self.update('core',
                    """ pick="%s" """ % cPickle.dumps(_object),
                    "id='%s'" % name)

core = config()
