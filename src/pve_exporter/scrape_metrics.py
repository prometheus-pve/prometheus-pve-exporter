"""
Metrics concerning the operation of the Prometheus PVE exporter itself.
"""

import wrapt
from prometheus_client.metrics import Counter, Histogram

API_METRICS_ENABLED: bool = False
"""
Whether or not api metrics are enabled
"""

TARGET_METRICS_ENABLED: bool = False
"""
Whether or not target metrics are enabled
"""

API_DURATION = Histogram(
    'pve_scrape_api_duration_seconds',
    'Duration of PVE API calls',
    ['method', 'url']
)
API_ERRORS = Counter(
    'pve_scrape_api_errors_total',
    'Number of errors occured in PVE API calls',
    ['method', 'url']
)

TARGET_DURATION = Histogram(
    'pve_scrape_target_duration_seconds',
    'Duration of a scrape',
    ['target', 'cluster', 'node'],
    buckets=[val*10 for val in Histogram.DEFAULT_BUCKETS]
)
TARGET_ERRORS = Counter(
    'pve_scrape_target_errors_total',
    'Number of errors occured when scraping a target',
    ['target', 'cluster', 'node'],
)

@wrapt.patch_function_wrapper(
    'proxmoxer.core',
    'ProxmoxResource._request',
    lambda: API_METRICS_ENABLED
)
def _api_metrics(wrapped, instance, args, kwargs):
    # pylint: disable=protected-access
    errors = API_ERRORS.labels(args[0], instance._store["base_url"])
    duration = API_DURATION.labels(args[0], instance._store["base_url"])
    with errors.count_exceptions(), duration.time():
        return wrapped(*args, **kwargs)

@wrapt.patch_function_wrapper(
    'pve_exporter.collector',
    'collect_pve',
    lambda: TARGET_METRICS_ENABLED
)
def _target_metrics(wrapped, _, args, kwargs):
    # pylint: disable=protected-access
    errors = TARGET_ERRORS.labels(args[1], int(args[2]), int(args[3]))
    duration = TARGET_DURATION.labels(args[1], int(args[2]), int(args[3]))
    with errors.count_exceptions(), duration.time():
        return wrapped(*args, **kwargs)
