# -*- coding: utf-8 -*-

import os
import sys
import time

from signal import SIGTERM


"""
    This module is used to fork the current process into a daemon.
    Almost none of this is necessary (or advisable) if your daemon
    is being started by inetd. In that case, stdin, stdout and stderr are
    all set up for you to refer to the network connection, and the fork()s
    and session manipulation should not be done (to avoid confusing inetd).
    Only the chdir() and umask() steps remain as useful.
    References:
        UNIX Programming FAQ
            1.7 How do I get my program to act like a daemon?
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        Advanced Programming in the Unix Environment
            W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.

    History:
      2001/07/10 by Jürgen Hermann
      2002/08/28 by Noah Spurrier
      2003/02/24 by Clark Evans

      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
"""


def deamonize(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile=None, startmsg='UserBot started with PID: %s'):
    """
        This forks the current process into a daemon.
        The stdin, stdout, and stderr arguments are file names that
        will be opened and be used to replace the standard file descriptors
        in sys.stdin, sys.stdout, and sys.stderr.
        These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
        may not appear in the order that you expect.
    """
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    # Open file descriptors and print start message
    if not stderr:
        stderr = stdout
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())
    sys.stderr.write("%s\n" % startmsg % pid)
    sys.stderr.flush()
    if pidfile:
        file(pidfile, 'w+').write("%s\n" % pid)
        # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def startstop(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile='pid.txt', startmsg='started with PID: %s'):
    if len(sys.argv) > 1:
        action = sys.argv[1]
        try:
            pf = file(pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if action in ('--stop', '--restart'):
            if not pid:
                mess = "Could not stop, pid file '%s' missing.\n"
                sys.stderr.write(mess % pidfile)
                sys.exit(1)
            try:
                while 1:
                    os.kill(pid, SIGTERM)
                    time.sleep(1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    mess = "UserBot stoped PID: %s\n"
                    print mess % pid
                    os.remove(pidfile)
                    if 'stop' == action:
                        sys.exit(0)
                    action = 'start'
                    pid = None
                else:
                    print str(err)
                    sys.exit(1)

        if '--start' == action:
            if pid:
                mess = "UserBot start aborded since pid file '%s' exists.\n"
                sys.stderr.write(mess % pidfile)
                sys.exit(1)
            deamonize(stdout, stderr, stdin, pidfile, startmsg)
            return

    sys.exit(2)
