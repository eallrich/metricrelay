"""Core funtionality for the application.

During initialization, we're going to see whether the user has provided
any of their own configuration settings. If they have not, we'll use all of
the preset defaults. If they have, we'll leave those alone but use the
defaults to populate any settings they haven't specified. This enables users
to only override a subset of the settings while allowing defaults to be used
for the remainder.

We're also going to create the 'metrics' module which is the global store for
metrics data structures.
"""
import imp
import logging
import sys

from . import defaults

logging.basicConfig(**defaults.logging)
log = logging.getLogger(__name__)

try:
    from . import settings
except ImportError as exc:
    log.warn("No local settings; proceeding with defaults")

    # The following approach is based on StackOverflow:
    # http://stackoverflow.com/a/3799609/564584

    # Create an empty module to store our settings
    settings = imp.new_module('settings')
    sys.modules['settings'] = settings

# If a setting has not been user-defined, use the default
for k,v in defaults.__dict__.items():
    if k.startswith("__"):
        continue
    # Don't override a setting the user has specified
    if not hasattr(settings, k):
        settings.__dict__[k] = v


# Dynamically generate the metrics module (the global namespace for metrics)
metrics = imp.new_module('metrics')
sys.modules['metrics'] = metrics
