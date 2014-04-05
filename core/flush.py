import logging
import threading

from . import defaults, metrics, statistics, util

logging.basicConfig(**defaults.logging)
log = logging.getLogger(__name__)


def _clear_metrics():
    """Resets metrics if config specifies to do so.

    Requires the caller to get the metrics.lock first."""
    for key in metrics.counters:
        if defaults.delete_counters:
            # Just reset built-in counters to zero
            if "packets_received" in key or "bad_lines_seen" in key:
                metrics.counters[key] = 0
            else:
                del metrics.counters[key]
        else:
            metrics.counters[key] = 0

    for key in metrics.timers:
        if defaults.delete_timers:
            del metrics.timers[key]
            del metrics.timer_counters[key]
        else:
            metrics.timers[key] = []
            metrics.timer_counters[key] = 0

    for key in metrics.sets:
        if defaults.delete_sets:
            del metrics.sets[key]
        else:
            metrics.sets[key] = set()

    # Gauges keep reporting previous values unless configured otherwise
    if defaults.delete_gauges:
        for key in metrics.gauges:
            del metrics.gauges[key]


def _processed(data):
    log.debug("Processed callback activated")
    log.debug(data)


def _flush():
    """Called by _run when the flush timer expires, flushes metrics"""
    log.debug("Flushing metrics")
    now = util.ts()
    if hasattr(metrics, 'old_timestamp'):
        lag = now - metrics.old_timestamp - (defaults.flush_interval / 1000)
        with metrics.lock:
            metrics.gauges[defaults.timestamp_lag_namespace] = lag
        # Only flush writes to 'old_timestamp' so we're not going to lock
        metrics.old_timestamp = now

    with metrics.lock:
        data = {
            'counters':          metrics.counters.copy(),
            'gauges':            metrics.gauges.copy(),
            'timers':            metrics.timers.copy(),
            'timer_counters':    metrics.timer_counters.copy(),
            'sets':              metrics.sets.copy(),
            'counter_rates':     metrics.counter_rates.copy(),
            'timer_data':        metrics.timer_data.copy(),
            'percent_threshold': defaults.percent_threshold,
            'histogram':         defaults.histogram,
        }

        _clear_metrics()

    statistics.process_metrics(data, defaults.flush_interval, _processed)


def _run():
    """Called by the flush timer, flushes and then restarts the timer"""
    try:
        _flush()
    except Exception as exc:
        log.exception("Exception during flush: %s" % exc)
    start()


def start():
    """Sets up and starts the flush timer"""
    metrics.timer = threading.Timer(defaults.flush_interval / 1000, _run)
    metrics.timer.start()


def stop():
    """Stops a running flush timer"""
    metrics.timer.cancel()
    # One final flush
    _flush()
