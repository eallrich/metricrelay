import importlib
import logging
import re
import SocketServer
import threading

from . import flush, metrics, settings, util

logging.basicConfig(**settings.logging)
log = logging.getLogger(__name__)


def _init():
    metrics.lock = threading.RLock()

    metrics.counters       = {}
    metrics.counter_rates  = {}
    metrics.gauges         = {}
    metrics.sets           = {}
    metrics.timers         = {}
    metrics.timer_counters = {}
    metrics.timer_data     = {}

    # Set to zero so we can increment
    metrics.counters[settings.bad_lines_seen] = 0
    metrics.counters[settings.packets_received] = 0

    metrics.stats = {
        'messages': {
            'last_msg_seen': util.ts(),
            'bad_lines_seen': 0,
        },
    }

    metrics.backends = []
    for backend in settings.backends:
        b = importlib.import_module(backend)
        metrics.backends.append(b)


class Statsd(SocketServer.BaseRequestHandler):
    def handle(self):
        # For convenience
        m = metrics

        with m.lock:
            m.counters[settings.packets_received] += 1

        data = self.request[0].rstrip('\n')

        for metric in data.split('\n'):
            if len(metric) == 0:
                continue
            log.debug(metric)

            # TODO If not valid packet, increment bad_lines_seen; continue

            key, rest = metric.split(':')
            key = util.clean(key)

            parts = rest.split('|')
            if len(parts) < 2 or len(parts) > 3:
                log.warning("Unexpected format: %s => %s" % (rest, parts))
                continue

            # For gauges, we'll want to know whether to (in|de)crement,
            # so we need to keep the sign (if it exists). Otherwise we
            # could just cast to float right here.
            value = parts[0]
            metric_type = parts[1]
            if len(parts) == 3:
                sample_rate = re.match(r'^@([\d\.]+)', fields[2]).group(1)
                sample_rate = float(sample_rate)
            else:
                sample_rate = 1

            log.debug("%s %s %s %f" % (key, value, metric_type, sample_rate))

            # TODO if key_flush_interval > 0, increment key_counter

            if metric_type == "ms":
                with m.lock:
                    m.timers.setdefault(key, [])
                    m.timers[key].append(float(value))

                    m.timer_counters.setdefault(key, 0)
                    m.timer_counters[key] += 1 / sample_rate
            elif metric_type == "g":
                with m.lock:
                    if key in m.gauges and re.match(r"[-+]", value):
                        log.debug("Changing gauge by %s" % value)
                        m.gauges[key] += float(value)
                    else:
                        log.debug("Setting gauge to %s" % value)
                        m.gauges[key] = float(value)
            elif metric_type == "s":
                with m.lock:
                    m.sets.setdefault(key, set())
                    m.sets[key].add(value)
            else:
                with m.lock:
                    m.counters.setdefault(key, 0)
                    m.counters[key] += float(value) * (1 / sample_rate)

        with m.lock:
            m.stats['messages']['last_msg_seen'] = util.ts()


def start(host='127.0.0.1', port=8125):
    _init()
    flush.start()
    log.info("Listening at %s:%d" % (host, port))
    server = SocketServer.UDPServer((host, port), Statsd)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
        server.shutdown()
        flush.stop()
