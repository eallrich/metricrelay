"""Sends metrics in JSON format to one or more URLs

Expects the settings.http_servers attribute to be a list of servers (with
resource paths). E.g.:
http_servers = ('http://m1.example.com/publish','http://m2.example.com/new')
"""
import json
import logging

import requests
from statsd import StatsClient

from core import settings, util

logging.basicConfig(**settings.logging)
log = logging.getLogger(__name__)

# Restrict overly-verbose logging
logging.getLogger("requests").setLevel(logging.WARNING)

statsd = StatsClient('localhost', 48125, prefix=util.ns(settings.prefix_stats, 'backend', 'http'))

excluded = (
    'histogram',
    'percent_threshold',
    'timer_counters',
    'timers',
)
headers = {
    'content-type': 'application/json',
}


def _initialize():
    """Make sure the user has told us the servers to which to send metrics"""
    if not hasattr(settings, 'http_servers') or not settings.http_servers:
        log.error("Unable to find http_servers for %s" % __name__)
        raise RuntimeError("Unable to initialize: No servers found in settings")


def _format(key, value, timestamp):
    return {
        'metric':    key,
        'value':     value,
        'timestamp': timestamp,
    }


def flush(metrics):
    now = util.ts()

    # Ignore metrics we don't need to report
    metrics = {k:v for k,v in metrics.items() if k not in excluded}

    formatted = []
    for metric_type, data in metrics.items():
        if len(data) == 0:
            continue

        prefix = []
        suffix = []
        # Each metric type may get a special prefix and/or suffix
        if metric_type == "timer_data":
            prefix = [settings.global_prefix, settings.prefix_timer]
            for key, values in data.items():
                for subkey, value in values.items():
                    parts = prefix[:]
                    parts.extend([key, subkey])
                    m = _format(util.ns(*parts), value, now)
                    formatted.append(m)
            continue # Don't continue processing this metric type
        elif metric_type == "gauges":
            prefix = [settings.global_prefix, settings.prefix_gauge]
        elif metric_type == "counters":
            prefix = [settings.global_prefix, settings.prefix_counter]
            suffix = ['count']
        elif metric_type == "counter_rates":
            prefix = [settings.global_prefix, settings.prefix_counter]
            suffix = ['rate']
        elif metric_type == "sets":
            prefix = [settings.global_prefix, settings.prefix_set]
            suffix = ['count']
        elif metric_type == "statsd_metrics":
            prefix = [settings.global_prefix, settings.prefix_stats]

        for key, value in data.items():
            parts = prefix[:]
            parts.append(key)
            parts.extend(suffix[:])
            m = _format(util.ns(*parts), value, now)
            formatted.append(m)
    
    payload = json.dumps(formatted)

    with statsd.timer(util.ns('flush', 'transmit', settings.suffix_stats)):
        for url in settings.http_servers:
            try:
                r = requests.post(url, data=payload, headers=headers, timeout=10)
                if r.status_code != 201:
                    msg = "%s returned status %d" % (url, r.status_code)
                    log.error(msg + "; text:")
                    log.error(r.text)
                    statsd.incr(util.ns('flush', 'response_status', '%d' % r.status_code, settings.suffix_stats))
            except requests.exceptions.RequestException as exc:
                log.exception("RequestException against %s: %s" % (url, exc))
                statsd.incr(util.ns('flush', 'errors', settings.suffix_stats))


# Get ourselves set up
_initialize()
