# -*- coding: utf-8 -*-

import request


def who(irc, target):
    return request.who(irc, target).result


def whois(irc, target):
    return request.whois(irc, target).result


def list(irc, target, mode):
    request.list.mode = mode
    return request.list(irc, target).result