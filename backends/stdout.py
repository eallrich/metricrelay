import pprint

from core import util

def flush(metrics):
    print("Flushing stats at %d" % util.ts())
    pprint.pprint(metrics)
