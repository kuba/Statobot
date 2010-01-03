from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory

from twisted.internet import reactor

import subprocess
import re

class StatobotProtocol(LineOnlyReceiver):
    MAX_LENGTH = 16
    delimiter = '\n'
    def lineReceived(self, line):
        if line == 'get':
            self.sendLine(self.factory.getGet())
        elif line == 'mem':
            self.sendLine(self.factory.getMem())
        elif line == 'both':
            self.sendLine(self.factory.getBoth())
        else:
            self.sendLine('Bad command, dying!')
            self.transport.loseConnection()

class StatobotServerFactory(ServerFactory):
    protocol = StatobotProtocol

    def getGet(self):
        f1 = open('/proc/loadavg').read().strip()
        f2 = open('/proc/uptime').read().strip()
        return "%s %s" % (f1, f2)

    def getMem(self):
        raw = subprocess.Popen("free", stdout=subprocess.PIPE).communicate()[0]
        return ' '.join(re.findall('\d+', raw))

    def getBoth(self):
        get = self.getGet()
        mem = self.getMem()
        return "%s %s" % (get, mem)

if __name__ == '__main__':
    reactor.listenTCP(65535, StatobotServerFactory())
    reactor.run()
