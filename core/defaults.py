import platform
hostname = platform.node().replace('.', '_')

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


# Stat prefixes
# -------------
global_prefix = 'stats'
prefix_counter = 'counters'
prefix_timer = 'timers'
prefix_gauge = 'gauges'
prefix_set = 'sets'


# self-reported stat names
# ------------------------
prefix_stats = "statsd"
suffix_stats = ".%s" % hostname
bad_lines_seen          = prefix_stats + ".bad_lines_seen" + suffix_stats
packets_received        = prefix_stats + ".packets_received" + suffix_stats
timestamp_lag_namespace = prefix_stats + ".timestamp_lag" + suffix_stats


logging = {
    'format':  '%(asctime)s | [%(levelname)s] %(message)s',
    'level':   'INFO',
    'datefmt': '%Y-%m-%dT%H:%M:%S',
}
