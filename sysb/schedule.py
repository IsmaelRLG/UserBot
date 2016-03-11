# -*- coding: utf-8 -*-

import re
import time

from config import core
from irc.connection import servers as base


class irc_schedule:

    def __init__(self, db_name):
        self.db_name = db_name
        self.jobs = core.obtconfig(self.db_name)
        if not self.jobs:
            self.jobs = {}
            core.addconfig(db_name, self.jobs)
        self.start = False

    def add(self, irc, rpl_ev, func_name, args, kwargs, exec_l, seconds, name=None):
        if irc in base and not irc in self.jobs:
            self.jobs[irc] = []

        self.jobs[irc].append({
            'rpl': rpl_ev if not rpl_ev else None,
            'func_name': getattr(base[irc][0], func_name).func_name,
            'args': args,
            'kwargs': kwargs,
            'exec_n': 0,
            'exec_l': exec_l,
            'seconds': time.time() + seconds if seconds >= 0 else seconds,
            'name': name})
        core.upconfig(self.db_name, self.jobs)

    def conv(self, year=None, month=None, day=None, hour=None, minute=None, second=None):
        total_seconds = 0
        if year:
            if year < 0:
                year = -1
            total_seconds += year * 31536000
        if month:
            if month < 0:
                month = -1
            total_seconds += month * 30.416
        if day:
            if day < 0:
                day = -1
            total_seconds += day *86400
        if hour:
            if hour < 0:
                hour = -1
            total_seconds += hour *3600
        if minute:
            if minute < 0:
                minute - 1
            total_seconds += minute * 60
        if second:
            if second < 0:
                second = -1
            total_seconds += second

        if total_seconds < 0:
            total_seconds = -1

        return total_seconds

    def conv_parse_txt(self, string):
        SRE = re.match('(?P<num>\d)(?P<alpha>[YMDHMS]{1})', string, 2)
        if SRE:
            alpha = SRE.group('alpha').upper()
            num = int(SRE.group('num'))
            to_conv = {}
            if alpha == 'y':
                to_conv['year'] = num
            elif alpha == 'm':
                to_conv['month'] = num
            elif alpha == 'd':
                to_conv['day'] = num
            elif alpha == 'hour':
                to_conv['hour'] = num
            elif alpha == 'minute':
                to_conv['minute'] = num
            elif alpha == 'second':
                to_conv['second'] = num

            return self.conv(**to_conv)
        else:
            raise ValueError

    def start_jobs(self):
        self.start = True
        while self.start:
            time.sleep(0.9)
            epoch = time.time()
            for ircname, jobls in self.jobs.items():
                self.process(base[ircname][0], jobls, epoch)

    def process(self, irc, jobls, epoch):
        try:
            if not irc.registered:
                time.sleep(4)
        except AttributeError:
            time.sleep(4)

        for job in jobls:
            remove = False
            if epoch >= job['seconds']:
                if job['exec_n'] >= job['exec_l']:
                    remove = True
                else:
                    job['exec_n'] += 1
                    getattr(irc, job['func_name'])(*job['args'], **job['kwargs'])
            else:
                continue

            if remove:
                jobls.remove(job)
                core.upconfig(self.db_name, self.jobs)