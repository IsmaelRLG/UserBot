# -*- coding: utf-8 -*-

from sysb.Thread import thread


class subproc:

    def __init__(self):
        self.queue = []
        self.drivers = []
        self.stop = False
        self.loop()

    def stop(self):
        self.stop = True

    @thread(init=True, n='loop')
    def loop(self):
        while not self.stop:
            try:
                get = self.queue.pop()
            except IndexError:
                continue

            for driver in self.drivers:
                try:
                    driver(get)
                except Exception:
                    pass

    def add(self, function):
        if not function in self.drivers:
            self.drivers.append(function)

    def remove(self, func_name):
        for function in self.drivers:
            if function.__name__ == func_name:
                self.drivers.remove(function)


subproc = subproc()