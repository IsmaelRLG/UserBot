# -*- coding: utf-8 -*-

from util import remove_from_dict as rm

# RFC 2812          Internet Relay Chat: Client Protocol
# Numeric Replies: Command responses

ALL = {}
NOT = ['ALL', 'NOT', 'BASE', '_', 'RPL_ALL', 'ERR_ALL', 'rm']

# Base of all, bueno, casi todo..
BASE = ':?(?P<machine>[^ ]+)'
_ = lambda code: ':?(?P<machine>[^ ]+) {} (?P<me>[^ ]+) '.format(code)


# The server sends Replies 001 to 004 to a user upon successful registration.
RPL_WELCOME = (_('001') + ':Welcome to the (?P<network>[^ ]+) '
    'Internet Relay Chat Network ((?(me)yes).+)')
RPL_YOURHOST = (_('002') +
    ':Your host is (?P<server>.+), running version (?P<version.*)')
RPL_CREATED = _('003') + ':This server was created (?P<data>.*)'
RPL_MYINFO = (_('004') + '(?P<servername>[^ ]+) (?P<version>[^ ]+)'
    ' (?P<aum>[^ ]+) (?P<acm>[^ ]+)')

# Sent by the server to a user to suggest an alternative
# server. This is often used when the connection is
# refused because the server is already full.
RPL_BOUNCE_RFC_2812 = (_('005') +
    ':Try server (?P<server>[^ ]+), port (?P<port>[^ ]+)')

# aksaksjas cambiar esto
RPL_FEATURELIST = (_('005') + '(?P<feature>.*)'
    '( :are supported by this server)')
RPL_STATSDLINE = (_('250') + ':Highest connection count: '
    '(?P<client>[^ ]+) \((?P<clients>[^ ]+) clients\)'
    ' \((?P<connections[^ ]+) connections received\)')
RPL_LUSERCLIENT = (_('251') + ':There are (?P<users>[^ ]+) users and '
    '(?P<integer>[^ ]+) (services|invisible) on (<servers>[^ ]+) servers')
RPL_LUSEROP = (_('252') + '(?P<num>[^ ]+) :'
    '(IRC )?[Oo]perator(s|\(s\) online')
RPL_LUSERCHANNELS = _('254') + '(?P<integer>[^ ]+) :channels formed'

RPL_AWAY = _('301') + '(?P<nick>[^ ]+) :(?P<message>.*)'
RPL_ISON = _('303') + ':(?P<nicks>.*)'
RPL_WHOISUSER = (_('311') + "(?P<nick>[^ ]+) (?P<user>[^ ]+) (?P<host>[^ ]+) \*"
    " :(?P<realname>[^ ]+)")
RPL_WHOISSERVER = (_('312') + "(?P<nick>[^ ]+) (?P<server>[^ ]+) "
    " :(?P<server_info>.*)")
RPL_WHOISOPERATOR = _('313') + "(?P<nick>[^ ]+) :is an IRC operator"
RPL_ENDOFWHO = _('315') + "(?P<name>[^ ]+) :End of /?WHO list(\.)?"
RPL_WHOISIDLE = (_('317') + "(?P<nick>[^ ]+) (?P<integer.*)"
    "( :seconds idle(, signon time)?)")
RPL_ENDOFWHOIS = _('318') + "(?P<nick>[^ ]+) :End of /?WHOIS list(\.)?"
RPL_LISTSTART = _('321') + "Channel :Users ( )?Name"  # Obsolete. Not used.
RPL_LIST = (_('322') + "(?P<channel>[^ ]+) (?P<total_user>[^ ]+) "
    ":(\[(?P<modes>.+)\] )?(?P<topic>.*)")
RPL_LISTEND = _('323') + ':End of /?LIST(\.)?'
RPL_CHANNELMODEIS = _('324') + '(?P<channel>[^ ]+) (?P<modes>.+)'
RPL_WHOISLOGGED = _('330') + '(?P<username>[^ ]+) (?P<account>[^ ]+) :is logged in as'
RPL_NOTOPIC = _('331') + '(?P<channel>[^ ]+) :No topic is set(\.)?'
RPL_TOPIC = _('332') + '(?P<channel>[^ ]+) :(?P<topic>.*)'
RPL_INVITING = _('341') + '(?P<nick>[^ ]+) (?P<channel>[^ ]+)'
RPL_INVITELIST = (_('346') + "(?P<channel>#[^ ]+) (?P<emask>[^ ]+) "
    "(?P<from>[^ ]+) (?P<date>[^ ]+)")
RPL_ENDOFINVITELIST = (_('347') + '(?P<channel>#[^ ]+) :'
    'End of [Cc]hannel [Ii]nvite [Ll]ist')
RPL_EXCEPTLIST = (_('348') + "(?P<channel>#[^ ]+) (?P<mask>[^ ]+) "
    "(?P<from>[^ ]+) (?P<date>[^ ]+)")
RPL_ENDOFEXCEPTLIST = (_('349') +
    "(?P<channel>#[^ ]+):End of [Cc]hannel [Ee]xception [Ll]ist")
RPL_WHOREPLY = (_('352') + "((?P<channel>#[^ ]+)|\*) (?P<user>[^ ]+) "
    "(?P<host>[^ ]+) (?P<server>[^ ]+) (?P<nick>[^ ]+) ([HG].+) "
    ":(?P<hopcount>.[0-9]) (?P<realname>.*)")
RPL_NAMREPLY = _('353') + "(=|\*|@) (?P<channel>#[^ ]+) :(?P<nicks>.*)"
RPL_LINKS = (_('364') + "(?P<mask>[^ ]+) (?P<server>[^ ]+) :"
    "(?P<hopcount>.[0-9]) (?P<server_info>.*)")
RPL_ENDOFLINKS = _('365') + "(?P<mask>[^ ]+) :End of /?LINKS list(\.)?"
RPL_ENDOFNAMES = _('366') + "(?P<channel>#[^ ]+) :End of /?NAMES list(\.)?"
RPL_BANLIST = (_('367') + "(?P<channel>#[^ ]+) (?P<mask>[^ ]+) "
    "(?P<from>[^ ]+) (?P<date>[^ ]+)")
RPL_ENDOFBANLIST = (_('368') + "(?P<channel>#[^ ]+) "
    ":End of channel [bB]an [lL]ist")
RPL_ENDOFWHOWAS = _('369') + "(?P<nick>[^ ]+) :End of /?WHOWAS(\.)?"
RPL_WHOISMODES = _('379') + "(?P<nick>[^ ]+) :is using modes (?P<modes>.+)"
RPL_STD = _('|'.join(['30[56]', '381', '39[245]', '242', ])) + ':(?P<text>.*)'

# When responding to the MOTD message and the MOTD file
# is found, the file is displayed line by line, with
# each line no longer than 80 characters, using

RPL_MOTDSTART = _('375') + ':- (?P<server>[^ ]+) Message of the day - '
RPL_MOTD = _('372') + ':- (?P<text>.*)'
RPL_ENDOFMOTD = (_('376') + ":(End of /?MOTD command(\.)?|"
    "End of message of the day(\.)?)")

RPL_ALL = rm(vars(), NOT)
ALL.update(RPL_ALL)

# Error Replies

ERR_NOSUCHNICK = _('401') + "(?P<nick>[^ ]+) :No such nick/channel"
ERR_NOSUCHSERVER = _('402') + '(?P<server>[^ ]+) :No such server'
ERR_NOSUCHCHANNEL = _('403') + '(?P<channel>[^ ]+) :No such channel'
ERR_CANNOTSENDTOCHAN = _('404') + "(?P<channel>[^ ]+) :Cannot send to channel"
#ERR_TOOMANYCHANNELS =
#ERR_WASNOSUCHNICK =
ERR_TOOMANYTARGETS = (_('407') +
    "(?P<target>[^ ]+) :(?P<error>.*)( recipients. )(?P<message>.*)")

# Returned to a client which is attempting to send a
# PRIVMSG/NOTICE using the user@host destination format
# and for a user@host which has several occurrences.
# Returned to a client which trying to send a
# PRIVMSG/NOTICE to too many recipients.
# Returned to a client which is attempting to JOIN a safe
# channel using the shortname when there are more than one
# such channel.
#ERR_TOOMANYTARGETS =

#ERR_NOSUCHSERVICE =

# 412 - 415 are returned by PRIVMSG to indicate that
# the message wasn't delivered for some reason.
# ERR_NOTOPLEVEL and ERR_WILDTOPLEVEL are errors that
# are returned when an invalid use of
# "PRIVMSG $<server>" or "PRIVMSG #<host>" is attempted.

ERR_NORECIPIENT = ":No recipient given (?P<command>[^ ]+)"
ERR_NOTOPLEVEL = "<mask> :No toplevel domain specified"
ERR_WILDTOPLEVEL = "<mask> :Wildcard in toplevel domain"
ERR_BADMASK = "<mask> :Bad Server/host mask"

# command sent is unknown by the server.? :O
ERR_UNKNOWNCOMMAND = _('422') + "(?P<command>[^ ]+) :Unknown command"

# Server's MOTD file could not be opened by the server? :O
ERR_NOMOTD = _('422') + ':(?P<text>.*)'

ERR_ERRONEUSNICKNAME = _('432') + '(?P<nick[^ ]+) :Erroneous Nickname'
ERR_NICKNAMEINUSE = _('433') + '(?P<nick[^ ]+) :Nickname is already in use'
ERR_NICKCOLLISION = (_('436') + '(?P<nick>[^ ]+) :Nickname collision KILL '
    'from (?P<user>.+)@(?P<host>.+)')
ERR_UNAVAILRESOURCE = (_('437') + '(?P<target>[^ ]+) '
    ':Nick/channel is temporarily unavailable')
ERR_USERNOTINCHANNEL = (_('441') + "(?P<nick>[^ ]+) (?P<channel>[^ ]+) "
    ":They aren't on that channel")
ERR_NOTONCHANNEL = _('442') + "(?P<channel>[^ ]+) :You're not on that channel"
ERR_USERONCHANNEL = (_('443') + "(?P<user>[^ ]+) (?P<channel>[^ ]+) :"
    "is already on channel")
ERR_NOLOGIN = _('444') + "(?P<user>[^ ]+) :User not logged in"
ERR_NEEDMOREPARAMS = _('461') + "(?P<command>[^ ]+) :Not enough parameters"
ERR_KEYSET = _('467') + "(?P<channel>[^ ]+) :Channel key already set"
ERR_CANNOTJOINCHANNEL = (_('47(1|[3-5])') + "(?P<channel>[^ ]+) "
    ":Cannot join channel \(\+(?P<mode>.)\)")
ERR_UNKNOWNMODE = (_('472') + "(?P<char>[^ ]+) :is unknown mode char to me for "
    "(?P<channel>[^ ]+)")
ERR_BADCHANMASK = _('476') + "(?P<channel>[^ ]+) :Bad Channel Mask"
ERR_NOCHANMODES = _('477') + "(?P<channel>[^ ]+) :Channel doesn't support modes"
ERR_BANLISTFULL = (_('478') + "(?P<channel>[^ ]+) (?P<char>[^ ]+) :"
    "Channel list is full")
ERR_CHANOPRIVSNEEDED = (_('482') +
    "(?P<channel>[^ ]+) :You're not channel operator")
ERR_STD = (_('|'.join(['409', '412', '424', '431', '44[56]', '451', '46[2-5]',
    '481', '48[3-5', '491', '50[12]'])) + ':(?P<text>.*)')

ERR_ALL = rm(rm(vars(), NOT), ALL.keys())
ALL.update(ERR_ALL)


def _(string):
    return (':((?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)|'
            '(?P<machine>[^ ]+)) %s ' % string)

# Operation messages

JOIN = _('JOIN') + '(?P<channel>[^ ]+)'
PART = _('PART') + '(?P<channel>[^ ]+)( :(?P<message>.*))?'
MODE = _('MODE') + '(?P<target>[^ ]+) (?P<mode>[^ ]+) (?P<victims>.*)'
KICK = _('KICK') + '(?P<channel>[^ ]+) (?P<victim>[^ ]+) :(?P<message>.*)'
QUIT = _('QUIT') + ':(?P<message>.*)'
NICK = _('NICK') + ':(?P<new_nick>.*)'
TOPIC = _('TOPIC') + '(?P<channel>[^ ]+) :(?P<text>.*)?'
INVITE = _('INVITE') + '(?P<me>[^ ]+) :(?P<channel>[^ ]+)'
NOTICE = _('NOTICE') + '(?P<target>[^ ]+) :(?P<message>.*)'
PRIVMSG = _('PRIVMSG') + '(?P<target>[^ ]+) :(?P<message>.*)'

OPMESS = rm(rm(vars(), NOT), ALL.keys())
ALL.update(OPMESS)

# Miscellaneous messages
KILL = ''
PING = 'PING (?P<server1>[^ ]+)( (?P<server2>[^ ]+))?'
PONG = ''
ERROR = 'ERROR (?P<message>.*)'

MIMESS = rm(rm(vars(), NOT), ALL.keys())
ALL.update(MIMESS)