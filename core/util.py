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


def ns(*args):
    """Short for "namespace," returns a key composed of the given strings.

    Example: ns('foo', 'bar') yields 'foo.bar'
    """
    return '.'.join(args)


def ts():
    """Short for "timestamp," returns an integer unix epoch."""
    return int(time.time())
