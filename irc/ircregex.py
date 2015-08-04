# -*- coding: utf-8 -*-

import re

# Expresion regular para procesar la mayoria de los eventos del irc
SUPER_REGEX = (
":(?P<machine>(?P<nickname>.{1,}\D)!(?P<ident>.*)@(?P<host>.*)|(?P<server>[^ ]+"
")) (?P<event>(?P<int>.{1,3}\d)|(?P<str>.*[A-Z])) (:(?P<message0>.*)|(?P<from0>"
".*) :(?P<message1>.*)|(?P<from1>.*) (?P<for>.*) :(?P<message2>.*))|(?P<lol>.*)"
" :(?P<stupid>.*)|(?P<unprocessed>.*)")

# Compilando la super expresion xD
_irc_regex_base = re.compile(SUPER_REGEX)

_cmd_pat = "^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?"
_rfc_1459_command_regexp = re.compile(_cmd_pat)