# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import functools
import struct
import collections
import uuid as _uuid_
import six

from sysb import logg

# Encriptado, se usa en este caso: sha256. Cambiar al gusto.
__hash__ = __import__('hashlib').sha256
log = logg.getLogger(__name__)


def always_iterable(item):
    """
    Given an object, always return an iterable. If the item is not
    already iterable, return a tuple containing only the item.

    >>> always_iterable([1,2,3])
    [1, 2, 3]
    >>> always_iterable('foo')
    ('foo',)
    >>> always_iterable(None)
    (None,)
    >>> always_iterable(xrange(10))
    xrange(10)
    """
    if isinstance(item, basestring) or not hasattr(item, '__iter__'):
        item = item,
    return item


def total_seconds(td):
    """
    Python 2.7 adds a total_seconds method to timedelta objects.
    See http://docs.python.org/library/datetime.html#datetime.timedelta.total_seconds

    >>> import datetime
    >>> total_seconds(datetime.timedelta(hours=24))
    86400.0
    """
    try:
        result = td.total_seconds()
    except AttributeError:
        seconds = td.seconds + td.days * 24 * 3600
        result = (td.microseconds + seconds * 10**6) / 10**6
    return result


def hash(string):
    """Retorna cadena bajo el hash elegido previamente.
       Argumentos:
           string -- Cadena a convertir a hash."""

    return __hash__(string).hexdigest()


def uuid(string):
    """
    Retorna uuid.
    Argumentos:
        string -- Cadena a convertir a uuid.
    """
    return _uuid_.uuid5(_uuid_.NAMESPACE_DNS, string.lower())


def save_method_args(method):
    """
    Wrap a method such that when it is called, the args and kwargs are
    saved on the method.

    >>> class MyClass(object):
    ...     @save_method_args
    ...     def method(self, a, b):
    ...         print(a, b)
    >>> my_ob = MyClass()
    >>> my_ob.method(1, 2)
    1 2
    >>> my_ob._saved_method.args
    (1, 2)
    >>> my_ob._saved_method.kwargs
    {}
    >>> my_ob.method(a=3, b='foo')
    3 foo
    >>> my_ob._saved_method.args
    ()
    >>> my_ob._saved_method.kwargs == dict(a=3, b='foo')
    True

    The arguments are stored on the instance, allowing for
    different instance to save different args.

    >>> your_ob = MyClass()
    >>> your_ob.method({str('x'): 3}, b=[4])
    {'x': 3} [4]
    >>> your_ob._saved_method.args
    ({'x': 3},)
    >>> my_ob._saved_method.args
    ()
    """
    args_and_kwargs = collections.namedtuple('args_and_kwargs', 'args kwargs')
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        attr_name = '_saved_' + method.__name__
        attr = args_and_kwargs(args, kwargs)
        setattr(self, attr_name, attr)
        return method(self, *args, **kwargs)
    return wrapper


class NickMask(six.text_type):
    """
    A nickmask (the source of an Event)

    >>> nm = NickMask('pinky!username@example.com')
    >>> print(nm.nick)
    pinky

    >>> print(nm.host)
    example.com

    >>> print(nm.user)
    username

    >>> isinstance(nm, six.text_type)
    True

    >>> nm = 'красный!red@yahoo.ru'
    >>> if not six.PY3: nm = nm.decode('utf-8')
    >>> nm = NickMask(nm)

    >>> isinstance(nm.nick, six.text_type)
    True

    Some messages omit the userhost. In that case, None is returned.

    >>> nm = NickMask('irc.server.net')
    >>> print(nm.nick)
    irc.server.net
    >>> nm.userhost
    >>> nm.host
    >>> nm.user
    """
    @classmethod
    def from_params(cls, nick, user, host):
        return cls('{nick}!{user}@{host}'.format(**vars()))

    @property
    def nick(self):
        nick, sep, userhost = self.partition("!")
        return nick

    @property
    def userhost(self):
        nick, sep, userhost = self.partition("!")
        return userhost or None

    @property
    def host(self):
        nick, sep, userhost = self.partition("!")
        user, sep, host = userhost.partition('@')
        return host or None

    @property
    def user(self):
        nick, sep, userhost = self.partition("!")
        user, sep, host = userhost.partition('@')
        return user or None


def is_channel(string):
    """Check if a string is a channel name.

    Returns true if the argument is a channel name, otherwise false.
    """
    return string and string[0] in "#&+!"


def ip_numstr_to_quad(num):
    """
    Convert an IP number as an integer given in ASCII
    representation to an IP address string.

    >>> ip_numstr_to_quad('3232235521')
    '192.168.0.1'
    >>> ip_numstr_to_quad(3232235521)
    '192.168.0.1'
    """
    n = int(num)
    packed = struct.pack('>L', n)
    bytes = struct.unpack('BBBB', packed)
    return ".".join(map(str, bytes))


def ip_quad_to_numstr(quad):
    """
    Convert an IP address string (e.g. '192.168.0.1') to an IP
    number as a base-10 integer given in ASCII representation.

    >>> ip_quad_to_numstr('192.168.0.1')
    '3232235521'
    """
    bytes = map(int, quad.split("."))
    packed = struct.pack('BBBB', *bytes)
    return str(struct.unpack('>L', packed)[0])


import re
from irc.request import who
patt = re.compile('.{1,}!.{1,}@.{1,}')


def genls(ls, channel, irc, exc=False):
    res = []
    for target in ls:
        if patt.match(target):
            for pattern in who(irc, channel)['list']:
                print (target.replace('*', '.*'))
                print (pattern)
                if re.match(target.replace('*', '.*'), pattern[0], 2):
                    res.append(pattern[0].split('!')[0])
        elif exc:
            raise ValueError
        else:
            res.append(target)
    return res