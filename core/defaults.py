backends = (
    'backends.stdout',
)


flush_interval = 10000 # milliseconds


# Deleting metrics after flush
# ----------------------------
delete_idle_stats = False
delete_counters   = False
delete_timers     = False
delete_sets       = False
delete_gauges     = False


# Timer statistics
# ----------------
percent_threshold = [90,]
histogram = []


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
