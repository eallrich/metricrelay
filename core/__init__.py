"""Core funtionality for the application.

During initialization, we're going to see whether the user has provided
any of their own configuration settings. If they have not, we'll use all of
the pre-set defaults. If they have, we'll leave those alone but use the
defaults to populate any settings they haven't specified. This enables users
to only override a subset of the settings while allowing defaults to be used
for the remainder.

We're also going to create and initialize the 'metrics' module which is the
global store for metrics data structures.

The method for dynamically generating the settings module (if it doesn't
exist) and the metrics module was derived from a StackOverflow answer:
http://stackoverflow.com/a/3799609/564584
"""
import imp
import importlib
import logging
import sys
import threading


def __init_metrics():
    """Dynamically generate the metrics module.

    This is the global namespace for metrics, but it doesn't need to be
    pre-defined in a .py module. Here we'll create the module, set up the
    default values for the data structures, and then export the module.
    """
    metrics = imp.new_module('metrics')
    sys.modules['metrics'] = metrics

    # When threads write to the dictionaries below, they should get this lock
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

    metrics.backends = [importlib.import_module(b) for b in settings.backends]

    # TODO Is metrics.stats used anywhere or can it be deleted?
    from . import util
    metrics.stats = {
        'messages': {
            'last_msg_seen': util.ts(),
            'bad_lines_seen': 0,
        },
    }

    # Return the module so that it can be set in the package's namespace
    return metrics


def __init_settings():
    """Initialize application settings.

    Will create an empty settings module and then copy default settings in
    if necessary, otherwise will only use defaults to fill in options not
    specified by the user in settings.py.
    """
    from . import defaults

    try:
        from . import settings
    except ImportError as exc:
        logging.basicConfig(**defaults.logging)
        log = logging.getLogger(__name__)
        log.warn("No local settings; proceeding with defaults")

        # Make the module since it doesn't already exist
        settings = imp.new_module('settings')
        sys.modules['settings'] = settings

    # If a setting has not been user-defined, use the default
    for k,v in defaults.__dict__.items():
        if k.startswith("__"):
            continue
        # Don't override a setting the user has specified
        if not hasattr(settings, k):
            settings.__dict__[k] = v

    return settings


# Prepare our modules
settings = __init_settings()
metrics  = __init_metrics()

