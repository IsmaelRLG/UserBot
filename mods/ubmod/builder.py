# -*- coding: utf-8 -*-
"""
UserBot module
Copyright 2015-2016, Ismael R. Lugo G.
"""

import ConfigParser
import posixpath
import logging
import random
import imp

from sysb import commands

logs = logging.getLogger(__name__)


class sre_group:
    def __init__(self, group_func):
        self.group = group_func

    def __getitem__(self, item):
        result = self.group(item)
        if result is None or result == '':
            raise IndexError
        return result

    def __call__(self, name):
        return self.group(name)


class ubmodule:  # UserBot Module!

    def __init__(self, name):
        self.name = name
        self.conf = ConfigParser.ConfigParser()
        self.conf.read('mods/ubmod/ubmod/{module}'.format(module=name))
        logs.debug('Construyendo modulo [%s]' % name)

        kwargs = {}
        kwargs['module'] = 'ubmod'  # UserBot Virtual Module

        try:
            kwargs['regex'] = self.RegexParser(self.conf.get('config', 'regex'))
            kwargs['help'] = {}
            kwargs['help']['sintax'] = self.conf.get('config', 'sintax')
            kwargs['help']['example'] = self.conf.get('config', 'example')
            kwargs['help']['desc'] = self.conf.get('config', 'descrip')
        except ConfigParser.NoOptionError:
            logs.error('Archivo de configuracion invalido')
            return

        if self.conf.has_option('config', 'alias'):
            kwargs['help']['alias'] = self.conf.get('config', 'alias')

        if self.conf.has_option('config', 'oper'):
            kwargs['oper'] = tuple(self.conf.get('config', 'oper').split())

        if self.conf.has_option('config', 'chan_reqs'):
            kwargs['chan_reqs'] = self.conf.get('config', 'chan_reqs')

        if self.conf.has_option('config', 'privs'):
            kwargs['chan_reqs'] = self.conf.get('config', 'privs')

        try:
            step = 'null'
            if self.conf.has_option('config', 'anyuser'):
                step = 'anyuser'
                kwargs['anyuser'] = self.conf.getboolean('config', 'anyuser')
            if self.conf.has_option('config', 'registered'):
                step = 'registered'
                kwargs['registered'] =\
                self.conf.getboolean('config', 'registered')
            if self.conf.has_option('config', 'channels'):
                step = 'channels'
                kwargs['channels'] =\
                self.conf.getboolean('config', 'channels')
            if self.conf.has_option('config', 'chn_registered'):
                step = 'chn_registered'
                kwargs['chn_registered'] =\
                self.conf.getboolean('config', 'chn_registered')
            if self.conf.has_option('config', 'thread'):
                step = 'thread'
                kwargs['thread'] = self.conf.getboolean('config', 'thread')
            if self.conf.has_option('config', 'logged'):
                step = 'logged'
                kwargs['logged'] = self.conf.getboolean('config', 'logged')
            if self.conf.has_option('config', 'no_prefix'):
                step = 'no_prefix'
                kwargs['no_prefix'] =\
                self.conf.getboolean('config', 'no_prefix')
        except ValueError:
            logs.error('%s: no es "yes" o "no"' % step)
            return

        commands.addHandler(**kwargs)(self.func)
        logs.debug('modulo construido [%s]' % name)

        if True:
            for item, value in kwargs.items():
                if item == 'help':
                    for subitem, subvalue in value.items():
                        logs.debug('    [help][%s]: %s' % (subitem, subvalue))
                else:
                    logs.debug('    [%s]: %s' % (item, value))

    def func(self, irc, result, ev, core):
        result = sre_group(result)
        ev = sre_group(ev)
        if self.conf.has_option('program', 'target'):
            target = self.conf.get('program', 'target')
            target = target.format(ev=ev, core=core)

        else:
            logs.error('%s: target no indicado' % self.name)
            return

        if self.conf.has_section('python'):
            try:
                source = self.conf.get('python', 'source')
                object = self.conf.get('python', 'object')  # lint:ok
            except ConfigParser.NoOptionError:
                logs.debug('Opcion Python no existente')
                return

            source = source.replace('.pyc', '').replace('.py', '')
            module = imp.find_module(source)
            module = imp.load_module(posixpath.basename(source), module)
            if self.conf.has_option('python', 'handler') and\
                self.conf.getboolean('python', 'handler'):
                try:
                    message = eval(self.conf.get('object'))
                    message = message(irc, result, ev, core)
                except Exception as err:
                    logs.error(type(err) + ': ' + str(err))
                    return

            else:
                message = object.format(module=object)

        elif self.conf.has_option('program', 'random'):
            list = self.conf.get('program', 'random').split('|')  # lint:ok
            message = random.choice(list)
            try:
                message = message.format(result=result, ev=ev, core=core)
            except (IndexError, KeyError):
                logs.error('%s: fallo al generar respuesta' % self.name)
                logs.debug('%s: intentando con opcion secuandaria' % self.name)
                if self.conf.has_option('program', 'altern'):
                    list = self.conf.get('program', 'altern').split('|')  # lint:ok
                    message = random.choice(list)
                    try:
                        message = message.format(result=result, ev=ev, core=core)
                    except (IndexError, KeyError):
                        logs.error('%s: opcion secundaria fallida' % self.name)
                        return
                else:
                    logs.warning('%s: sin opcion secundaria, abortando' % self.name)
                    return

        elif self.conf.has_option('program', 'answer'):
            message = self.conf.get('program', 'answer')
            try:
                message = message.format(result=result, ev=ev, core=core)
            except (IndexError, KeyError):
                logs.error('%s: fallo al generar respuesta' % self.name)
                logs.debug('%s: intentando con opcion secuandaria' % self.name)
                if self.conf.has_option('program', 'altern'):
                    message = self.conf.get('program', 'altern')
                    try:
                        message = message.format(result=result, ev=ev, core=core)
                    except (IndexError, KeyError):
                        logs.error('%s: opcion secundaria fallida' % self.name)
                        return
                else:
                    logs.warning('%s: sin opcion secundaria, abortando' % self.name)
                    return
        else:
            logs.error('mala configuracion')
            return

        for line in message.splitlines():
            irc.notice(target, line)

    def RegexParser(self, regex):
        build = []
        for phrase in regex.split():
            phrase = self.PhraseParser(phrase)
            if not phrase.startswith('( (?P<'):
                phrase = ' ' + phrase
            build.append(phrase)
        return ''.join(build).replace(' ', '', 1)

    def PhraseParser(self, phrase):
        p12e = '.'  # Palabra Simple
        i22o = '~'  # Ignorar lineas en blanco
        t15e = '*'  # Todo lo que sigue
        v12l = '?'  # [OPCIONAL] Con espacio

        if phrase[0] == p12e:
            return phrase.replace(p12e, '', 1)
        elif phrase[0] == v12l:
            phrase = phrase.replace(v12l, '', 1)
            if phrase[0] == i22o:
                phrase = phrase.replace(i22o, '', 1)
                return "( (?P<{name}>[^ ]+))?".format(name=phrase)
            elif phrase[0] == t15e:
                phrase = phrase.replace(t15e, '', 1)
                return "( (?P<{name}>.*))?".format(name=phrase)
        elif phrase[0] == i22o:
            phrase = phrase.replace(i22o, '', 1)
            return "(?P<{name}>[^ ]+)".format(name=phrase)
        elif phrase[0] == t15e:
            phrase = phrase.replace(t15e, '', 1)
            return "(?P<{name}>.*)".format(name=phrase)

        raise SyntaxError('Invalid phrase: ' + phrase)

