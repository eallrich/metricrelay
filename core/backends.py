"""Simple backend thread.

Calls each backend's flush function with the processed metrics data
"""

def flush(backends, data):
    for backend in backends:
        backend.flush(data)
