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
    ClusterInfoCollector,
    BackupInfoCollector
)
from pve_exporter.collector.node import (
    NodeConfigCollector,
    NodeReplicationCollector,
    SubscriptionCollector
)
from pve_exporter.collector.storage import StorageCollector

CollectorsOptions = collections.namedtuple('CollectorsOptions', [
    'status',
    'version',
    'subscription',
    'node',
    'cluster',
    'resources',
    'backup_info',
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
    if cluster and options.backup_info:
        registry.register(BackupInfoCollector(pve))
    if node and options.subscription:
        registry.register(SubscriptionCollector(pve))
    if node and options.config:
        registry.register(NodeConfigCollector(pve))
    if node and options.replication:
        registry.register(NodeReplicationCollector(pve))

    return generate_latest(registry)


def collect_storage(config, host, node, storage):
    """Scrape storage metrics and return prometheus text format for it"""

    pve = ProxmoxAPI(host, **config)

    registry = CollectorRegistry()
    registry.register(StorageCollector(pve, node, storage))

    return generate_latest(registry)
