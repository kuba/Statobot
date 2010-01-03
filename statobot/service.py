from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.application import internet

from statobot.server import StatobotServerFactory


class Options(usage.Options):
    optParameters = [['port', 'p', 65535, 'Port at which statobot should listen.']]


class StatobotServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = 'statobot'
    description = 'Run Statobot!'
    options = Options

    def makeService(self, options):
        port = int(options['port'])
        f = StatobotServerFactory()
        statobot = internet.TCPServer(port, f)
        return statobot
