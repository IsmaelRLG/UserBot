# -*- coding: utf-8 -*-

import cPickle
import database
import time
import logg

log = logg.getLogger(__name__)


class config(database.ownbot):

    def __init__(self):
        # Creamos la linda tabla que almacenara toda la configuracion <3
        self.cache = {}
        time.sleep(2)
        self.create('core', 'id text key not null, pick text not null', True)

        if self.obtconfig('VERSION', cache=True) is None:
            self.addconfig('VERSION', ('UserBot', 0, 7, 54))

    def addconfig(self, name, _object):
        """ Añade un objeto a la base de datos que sera serializado con Pickle
        para su uso posterior.
        Argumentos:
            _object -- Objeto equis a serializar."""
        self.insert('core', """ "%s", "%s" """ % (name, cPickle.dumps(_object)))

    def delconfig(self, name):
        self.delete('core', name)

    def obtconfig(self, name, cache=False, up=False):
        relapse = [0]

        def get(name, relapse=relapse):
            if relapse[0] >= 4:
                return
            else:
                relapse[0] += 1

            #res = None
            try:
                res = self.select('core', 'pick', 'id="%s"' % name)[0]
                res = cPickle.loads(res.encode('utf-8'))
            except (IndexError, TypeError, self.ProgrammingError):
                log.warning(name + ': no exists')
                time.sleep(1)
                return get(name)
            else:
                log.debug(name + ': ' + str([res]))
                return res

        def __cache__(action, name, set=None):
            if action == 'get':
                try:
                    return self.cache[name]
                except KeyError:
                    return

            if action == 'set':
                self.cache[name] = set

        if cache:
            result = __cache__('get', name)
            if result:
                n = 'get ' + name
                if up:
                    result = get(name)
                    __cache__('set', name, result)
            else:
                n = 'set ' + name
                result = get(name)
                __cache__('set', name, result)

            log.debug('cache %s result: %s' % (n, str(result)))
            return result
        else:
            return get(name)

    def upconfig(self, name, _object):
        self.update('core',
                    """ pick="%s" """ % cPickle.dumps(_object),
                    "id='%s'" % name)

core = config()
