import platform
import re
import time


# TODO Test
# TODO Move to re patterns?
def clean(key):
    """Cleans received keys to ensure valid formatting"""
    re.sub(r'\s+', '_', key)
    key.replace('/', '-')
    re.sub(r'[^a-zA-Z_\-0-9\.]', '', key)
    return key


host = platform.node()
def ns(*args):
    """Short for "namespace," returns a key prefixed by the host's name.

    Example: ns('foo', 'bar') yields 'host.foo.bar'
    """
    parts = [host,]
    parts.extend(args)
    return '.'.join(parts)


def ts():
    """Short for "timestamp," returns an integer unix epoch."""
    return int(time.time())
