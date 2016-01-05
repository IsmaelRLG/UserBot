# -*- coding: utf-8 -*-

from request import cache
from request import request


class ban(request):

    @cache.memory
    def execute(self):
        self.irc.mode(self.target, '+b')

    def list(self, group):
        if not 'list' in self.queue:
            self.queue['list'] = []

        self.queue['list'].append(group('channel', 'mask', 'from', 'date'))

    def endoflist(self, group):
        self.result.update(self.queue)

    # ERROR 442
    def notonchannel(self, group):
        self.result['error'] = "I'm not on that channel"

    # ERROR 482
    def chanoprivsneeded(self, group):
        self.result['error'] = "I'm not channel operator"


ban.events['ban'] = {
    "RPL_BANLIST": "list", "ERR_CHANOPRIVSNEEDED": "chanoprivsneeded",
    "RPL_ENDOFBANLIST": "endoflist", "ERR_NOTONCHANNEL": "notonchannel"}
ban.groups['ban'] = ('channel',)


class exception(request):

    @cache.memory
    def execute(self):
        self.irc.mode(self.target, '+e')

    def list(self, group):
        if not 'list' in self.queue:
            self.queue['list'] = []

        self.queue['list'].append(group('channel', 'mask', 'from', 'date'))

    def endoflist(self, group):
        self.result.update(self.queue)

    # ERROR 442
    def notonchannel(self, group):
        self.result['error'] = "I'm not on that channel"

    # ERROR 482
    def chanoprivsneeded(self, group):
        self.result['error'] = "I'm not channel operator"


exception.events['exception'] = {
    "RPL_EXCEPTLIST": "list", "ERR_CHANOPRIVSNEEDED": "chanoprivsneeded",
    "RPL_ENDOFEXCEPTLIST": "endoflist", "ERR_NOTONCHANNEL": "notonchannel"}
exception.groups['exception'] = ('channel',)


class invite(request):

    @cache.memory
    def execute(self):
        self.irc.mode(self.target, '+i')

    def list(self, group):
        if not 'list' in self.queue:
            self.queue['list'] = []

        self.queue['list'].append(group('channel', 'mask', 'from', 'date'))

    def endoflist(self, group):
        self.result.update(self.queue)

    # ERROR 442
    def notonchannel(self, group):
        self.result['error'] = "I'm not on that channel"

    # ERROR 482
    def chanoprivsneeded(self, group):
        self.result['error'] = "I'm not channel operator"


invite.events['invite'] = {
    "RPL_INVITELIST": "list", "ERR_CHANOPRIVSNEEDED": "chanoprivsneeded",
    "RPL_ENDOFINVITELIST": "endoflist", "ERR_NOTONCHANNEL": "notonchannel"}
invite.groups['invite'] = ('channel',)