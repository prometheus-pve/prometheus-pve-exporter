"""
Prometheus collecters for Proxmox VE cluster.
"""

import collections

from prometheus_client import CollectorRegistry, generate_latest
from proxmoxer import ProxmoxAPI

from pve_exporter.collector.cluster import (
    ClusterInfoCollector,
    ClusterNodeCollector,
    ClusterResourcesCollector,
    StatusCollector,
    VersionCollector,
)
from pve_exporter.collector.node import (
    NodeConfigCollector,
    NodeReplicationCollector,
    SubscriptionCollector,
)
from pve_exporter.collector.qga import QgaFsCollector

CollectorsOptions = collections.namedtuple(
    "CollectorsOptions",
    [
        "status",
        "version",
        "subscription",
        "node",
        "cluster",
        "resources",
        "config",
        "replication",
        "qga_fs",
    ],
)


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
    if node and options.qga_fs:
        registry.register(QgaFsCollector(pve))
    if node and options.subscription:
        registry.register(SubscriptionCollector(pve))
    if node and options.config:
        registry.register(NodeConfigCollector(pve))
    if node and options.replication:
        registry.register(NodeReplicationCollector(pve))

    return generate_latest(registry)
