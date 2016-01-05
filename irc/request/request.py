# -*- coding: utf-8 -*-
import sys
import time


#==============================================================================#
#                                memoria cache                                 #
#==============================================================================#


class cache:

    def __init__(self, tlimit, ulimit):
        self.cache = {}
        self.time_limit = tlimit
        self.uses_limit = ulimit

    def add(self, server, name, target, result):
        server = server.lower()
        if not server in self.cache:
            self.cache[server] = {}

        if not name in self.cache[server]:
            self.cache[server][name] = {}

        self.cache[server][name][target] = {
            'time': time.time(),
            'uses': 0,
            'result': result}

    def verify(self, server, name, target):
        if not server in self.cache:
            self.cache[server] = {}

        if not name in self.cache[server]:
            self.cache[server][name] = {}

        if not target in self.cache[server][name]:
            return False
        else:
            epoch = (time.time() - self.cache[server][name][target]['time'])
            if epoch > self.time_limit:
                return False
            elif self.cache[server][name][target]['uses'] > self.uses_limit:
                return False
            else:
                return True

    def memory(self, func):
        def arguments(request):
            setattr(request, 'cache', False)
            server = request.irc.base.name
            target = request.target
            name = request.__class__.__name__

            if self.verify(server, name, target):
                self.cache[server][name][target]['uses'] += 1
                request.result = self.cache[server][name][target]['result']
                setattr(request, 'cache', True)

                def does_nothing(*args):
                    pass

                function = does_nothing
            else:
                for tar, res in self.cache[server][name].items():
                    if res['uses'] > self.uses_limit:
                        del res
                    elif (time.time() - res['time']) > self.time_limit:
                        del res

                request.irc.add_handler(request.func_reqs, 0, 'local')
                time.sleep(0.4)
                function = func

            return function(request)
        return arguments

    def set(self, tlimit, ulimit):
        self.time_limit = tlimit
        self.uses_limit = ulimit

cache = cache(120, 3)


class request(object):
    events = {}
    groups = {}

    def __init__(self, irc, target):
        self.queue = {}
        self.irc = irc
        if isinstance(target, str):
            target = target.lower()

        self.target = target
        self.result = {}
        self.execute()
        self.lock = True
        print 'bloqueado'
        while self.lock:
            if len(self.result) > 0:
                self.lock = False
            time.sleep(0.1)
            sys.stdout.write('.')
            sys.stdout.flush()

        else:
            sys.stdout.write('OK')
            sys.stdout.flush()
            if not self.cache:
                cache.add(irc.base.name, self.__class__.__name__, self.target, self.result)
                irc.remove_handler(self.func_reqs, 0, 'local')

    def __getitem__(self, item):
        try:
            return self.result[item]
        except KeyError:
            pass

    def __setitem__(self, name, item):
        self.result[name] = item

    def __repr__(self):
        return repr(self.result)

    def __len__(self):
        return len(self.result)

    def func_reqs(self, irc, event_name, group):
        for reqevent, func_name in self.events[self.__class__.__name__].items():
            if reqevent == event_name:
                if self.__class__.__name__ in self.groups:
                    for groupname in self.groups[self.__class__.__name__]:
                        try:
                            if group(groupname).lower() != self.target:
                                raise UnboundLocalError
                            else:
                                getattr(self, func_name)(group)
                                return True
                        except:
                            continue
                else:
                    if getattr(self, func_name)(group):
                        return True
        raise UnboundLocalError
