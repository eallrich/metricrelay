import logging
import SocketServer

from . import defaults

logging.basicConfig(**defaults.logging)
log = logging.getLogger(__name__)

try:
    from . import settings
except ImportError as exc:
    log.warn("No local settings; proceeding with defaults.")


class Statsd(SocketServer.BaseRequestHandler):
    def handle(self):
        pass


def start(host='127.0.0.1', port=8125):
    log.info("Listening at %s:%d" % (host, port))
    server = SocketServer.UDPServer((host, port), Statsd)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
