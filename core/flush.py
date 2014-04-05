import logging
import threading

from . import defaults, metrics, util

logging.basicConfig(**defaults.logging)
log = logging.getLogger(__name__)


def _flush():
    """Called by _run when the flush timer expires, flushes metrics"""
    log.debug("Flushing metrics")


def _run():
    """Called by the flush timer, flushes and then restarts the timer"""
    try:
        _flush()
    except Exception as exc:
        logger.error("Exception during flush: %s" % exc)
    start()


def start():
    """Sets up and starts the flush timer"""
    metrics.timer = threading.Timer(defaults.flush_interval / 1000, _run)
    metrics.timer.start()


def stop():
    """Stops a running flush timer"""
    # TODO Run one final flush?
    metrics.timer.cancel()
