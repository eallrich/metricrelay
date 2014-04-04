backends = (
    'backends.stdout',
)


flush_interval = 10000 # milliseconds


# stat names
# ----------
prefix_stats = "statsd"
bad_lines_seen          = prefix_stats + ".bad_lines_seen"
packets_received        = prefix_stats + ".packets_received"
timestamp_lag_namespace = prefix_stats + ".timestamp_lag"


logging = {
    'format':  '%(asctime)s | [%(levelname)s] %(message)s',
    'level':   'DEBUG',
    'datefmt': '%Y-%m-%dT%H:%M:%S',
}
