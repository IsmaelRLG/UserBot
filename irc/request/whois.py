# -*- coding: utf-8 -*-

from request import cache
from request import request


class whois(request):

    @cache.memory
    def execute(self):
        self.irc.whois(self.target)

    def whoisuser(self, group):
        self.queue['mask'] = {
            'nick': group('nick'),
            'user': group('user'),
            'host': group('host'),
            'mask': '{}!{}@{}'.format(*group('nick', 'user', 'host')),
            'realname': group('realname')}

    def whoislogged(self, group):
        self.queue['is logged'] = group('account')

    def endofwhois(self, group):
        self.result.update(self.queue)

    def nosuchnick(self, group):
        self.result['error'] = 'No such nick/channel'


whois.events['whois'] = {
    "RPL_WHOISUSER": "whoisuser", "RPL_WHOISLOGGED": "whoislogged",
    "RPL_ENDOFWHOIS": "endofwhois", "ERR_NOSUCHNICK": "nosuchnick"}
whois.groups['whois'] = ('nick', 'username')