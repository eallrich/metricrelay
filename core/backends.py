from . import defaults

def flush(backends, data):
    for backend in backends:
        backend.flush(data)
