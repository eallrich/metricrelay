"""Statistics for metrics"""
import math
import time

from . import settings, util

def process_metrics(metrics, flush_interval, flush_callback):
    """Generates statistics on a metrics collection and calls the callback.

    This function is based on the equivalent function in Etsy's statsd. While
    some modifications have been made in an attempt to be more pythonic, I am
    indebted to Etsy for sharing their source code. All successful runs of
    this function are the work of Etsy and statsd contributors, and all
    errors in the translation are surely my own."""
    starttime = time.time() * 1000 # Using milliseconds for extra precision
    counter_rates = {}
    timer_data = {}
    statsd_metrics = {}
    timer_counters = metrics['timer_counters']
    percent_threshold = metrics['percent_threshold']
    histogram = metrics['histogram']

    for key in metrics['counters']:
        value = metrics['counters'][key]
        # calculate "per second" rate
        counter_rates[key] = value / (flush_interval / 1000.0)

    for key in metrics['timers']:
        if len(metrics['timers'][key]) == 0:
            continue

        timer_data[key] = {}
        current_timer_data = {}

        values = metrics['timers'][key]
        values.sort()
        count = len(values)
        min = values[0]
        max = values[count - 1]

        cumulative_values = [min,]
        for i in xrange(count):
            cumulative_values.append(values[i] + cumulative_values[i-1])

        sum = min
        mean = min
        threshold_boundary = max

        for percent in percent_threshold:
            if count > 1:
                number_in_threshold = round(abs(percent) / 100 * count)

                if number_in_threshold == 0:
                    continue

                if percent > 0:
                    threshold_boundary = values[number_in_threshold - 1]
                    sum = cumulative_values[number_in_threshold - 1]
                else:
                    threshold_boundary = values[count - number_in_threshold]
                    sum = cumulative_values[count - 1] - cumulative_values[count - number_in_threshold - 1]

                mean = sum / number_in_threshold

            clean_pct = str(percent)
            clean_pct = clean_pct.replace('.', '_').replace('-', 'top')
            current_timer_data["mean_" + clean_pct] = mean
            _prefix = "upper_" if percent > 0 else "lower_"
            current_timer_data[_prefix + clean_pct] = threshold_boundary
            current_timer_data["sum_" + clean_pct] = sum

        sum = cumulative_values[count-1]
        mean = sum / count

        sum_of_diffs = 0
        for i in xrange(count):
           sum_of_diffs += (values[i] - mean) * (values[i] - mean)

        mid = math.floor(count / 2)
        median = values[int(mid)] if count % 2 else (values[int(mid)-1] + values[int(mid)]) / 2

        stddev = math.sqrt(sum_of_diffs / count)
        current_timer_data["std"] = stddev
        current_timer_data["upper"] = max
        current_timer_data["lower"] = min
        current_timer_data["count"] = timer_counters[key]
        current_timer_data["count_ps"] = timer_counters[key] / (flush_interval / 1000.0)
        current_timer_data["sum"] = sum
        current_timer_data["mean"] = mean
        current_timer_data["median"] = median

        # By design, values bigger than the upper limit of the last bin are
        # ignored
        bins = []
        for i in xrange(len(histogram)):
            if histogram[i]['metric'] in key:
                bins = histogram[i]['bins']
                break

        if bins:
            current_timer_data['histogram'] = {}

        # The outer loop iterates bins; the inner loop iterates timer values
        # Within each run of the inner loop, we should only consider the timer
        # value range that's within the scope of the current bin. We'll
        # leverage the fact that the values are already sorted to end up with
        # only one full iteration of the entire values range.
        i = 0
        for bin_i in xrange(len(bins)):
            freq = 0
            while i < count and (bins[bin_i] == 'inf' or values[i] < bins[bin_i]):
                i += 1
                freq += 1

            bin_name = 'bin_' + bins[bin_i]
            current_timer_data['histogram'][bin_name] = freq

        timer_data[key] = current_timer_data

    metric_name = util.ns("processing_time", settings.suffix_stats)
    statsd_metrics[metric_name] = (time.time() * 1000) - starttime

    # Save the generated metrics data
    metrics['counter_rates'] = counter_rates
    metrics['timer_data'] = timer_data
    metrics['statsd_metrics'] = statsd_metrics

    flush_callback(metrics)

