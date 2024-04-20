"""
Prometheus collecters for Proxmox VE cluster.
"""

import collections
from proxmoxer import ProxmoxAPI

from prometheus_client import CollectorRegistry, generate_latest

from pve_exporter.collector.cluster import (
    StatusCollector,
    ClusterResourcesCollector,
    ClusterNodeCollector,
    VersionCollector,
    ClusterInfoCollector
)
from pve_exporter.collector.node import (
    NodeConfigCollector,
    NodeReplicationCollector
)

CollectorsOptions = collections.namedtuple('CollectorsOptions', [
    'status',
    'version',
    'node',
    'cluster',
    'resources',
    'config',
    'replication'
])


def collect_pve(config, host, cluster, node, options: CollectorsOptions):
    """Scrape a host and return prometheus text format for it"""

    pve = ProxmoxAPI(host, **config)

    registry = CollectorRegistry()
    if cluster and options.status:
        registry.register(StatusCollector(pve))
    if cluster and options.resources:
        registry.register(ClusterResourcesCollector(pve))
    if cluster and options.node:
        registry.register(ClusterNodeCollector(pve))
    if cluster and options.cluster:
        registry.register(ClusterInfoCollector(pve))
    if cluster and options.version:
        registry.register(VersionCollector(pve))
    if node and options.config:
        registry.register(NodeConfigCollector(pve))
    if node and options.replication:
        registry.register(NodeReplicationCollector(pve))

    return generate_latest(registry)
