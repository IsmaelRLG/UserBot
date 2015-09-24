# -*- coding: utf-8 -*-

import time

__cache__ = {}


def cache(name):
    def tutu(func):
        if not name in __cache__:
            __cache__[name] = {}

        def baba(self):
            if not self.irc.base.name in __cache__[name]:
                __cache__[name][self.irc.base.name] = {}

            n = __cache__[name][self.irc.base.name]
            if self.target in n:
                tim = (time.time() - n[self.target]['time'])
                print tim
                if n[self.target]['uses'] >= 2 or tim >= 3:
                    print 'delete'
                    del __cache__[name][self.irc.base.name][self.target]

                else:
                    print 'cache: ' + str(n[self.target]['result'])
                    self.queue.put(n[self.target]['result'])
                    n[self.target]['uses'] += 1
                    setattr(self, 'cache', (True, name))

                    def does_nothing():
                        pass

                    return does_nothing()

                if len(__cache__[name][self.irc.base.name]) >= 5:
                    del __cache__[name][self.irc.base.name]

            setattr(self, 'cache', (False, name))
            return func(self)
        return baba
    return tutu
