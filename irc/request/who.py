# -*- coding: utf-8 -*-

from request import cache
from request import request


class who(request):

    @cache.memory
    def execute(self):
        self.irc.who(self.target)

    def whoreply(self, group):
        multi = group('line').split(' ', 7)
        channel, user, host, server, nick, s, hopcount, realname = multi

        chorni = channel.lower()
        if chorni[0] != '#':
            chorni = nick.lower()

        if chorni != self.target:
            raise UnboundLocalError

        if not 'list' in self.queue:
            self.queue['list'] = []

        self.queue['list'].append((nick, user, host, s))
        return True

    def endofwho(self, group):
        if group('name').lower() != self.target:
            raise UnboundLocalError
        if len(self.queue) == 0:
            self.queue['list'] = []

        self.result.update(self.queue)
        return True

who.events['who'] = {"RPL_WHOREPLY": "whoreply", "RPL_ENDOFWHO": "endofwho"}