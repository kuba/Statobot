import re
import datetime

from twisted.internet import defer, task
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineOnlyReceiver

from prettytimedelta import PolishPrettyTimedelta


class Stats(object):
    get = """
          # `get`
          (?P<load_1>\d+\.\d+)\s
          (?P<load_5>\d+\.\d+)\s
          (?P<load_15>\d+\.\d+)\s
          (?P<executing_entities>\d+)/
          (?P<existing_entities>\d+)\s
          (?P<last_pid>\d+)\s
          (?P<uptime>\d+\.\d+)\s
          """
    mem = """
          # `mem`
          (?P<mem_total>\d+)\s
          (?P<mem_used>\d+)\s
          (?P<mem_free>\d+)\s
          (?P<shared>\d+)\s
          (?P<buffers>\d+)\s
          (?P<cached>\d+)\s
          (?P<cache_used>\d+)\s
          (?P<cache_free>\d+)\s
          (?P<swap_total>\d+)\s
          (?P<swap_used>\d+)\s
          (?P<swap_free>\d+)
          """
    both = re.compile(get + mem, re.VERBOSE)

    def __init__(self, raw_stats, time):
        self.time = time
        m = self.both.match(raw_stats).groupdict()
        for key, value in m.iteritems():
            self.__dict__[key] = float(value)
        dt = datetime.timedelta(seconds=self.uptime)
        self.uptime = PolishPrettyTimedelta(dt)

    @property
    def mem_percentage(self):
        return self.cache_used / self.mem_total * 100

    @property
    def pretty_uptime(self):
        return self.uptime.toWords()

    def formatShort(self):
        return '%s/%s/%d%%' % (self.load_1,
                self.uptime, self.mem_percentage)

    def formatLong(self):
        return '%s %s %s | %d/%d | %s | %d/%dMB (%d%%)' % \
               (self.load_1, self.load_5, self.load_15,
                self.executing_entities, self.existing_entities,
                self.pretty_uptime, self.cache_used/1024,
                self.mem_total/1024, self.mem_percentage)


class StatobotClient(LineOnlyReceiver):
    """
    Client which gets Rootnode's server status.
    
    """

    delimiter = '\n'
    def __init__(self):
        self.task = task.LoopingCall(self.requestStats)

    def connectionMade(self):
        self.task.start(self.factory._timer)

    def lineReceived(self, raw_stats):
        if not self.d.called:
            self.d.callback(raw_stats)

    def requestStats(self):
        """
        Get statisticts (load, uptime, memory usage, etc.)

        """
        self.d = defer.Deferred()
        self.d.addCallback(self.gotStats)
        # TODO timeout
        self.sendLine('both')
        return self.d

    def gotStats(self, raw_stats):
        stats_time = datetime.datetime.now()
        self.factory.stats = Stats(raw_stats, stats_time)


class StatobotClientFactory(ReconnectingClientFactory):
    protocol = StatobotClient

    def __init__(self, name, short, ip, timer, timeout):
        self.name = name
        self.short = short
        self.ip = ip
        self._timer = timer
        self._timeout = timeout
        self.stats = None

    def getStats(self):
        return self.stats

    def getCurrentStats(self):
        td = datetime.datetime.now() - self.stats.time
        if self.stats is not None and td.seconds > self._timeout:
            return None
        return self.stats
