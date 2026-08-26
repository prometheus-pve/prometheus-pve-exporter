"""
Prometheus collecters for Proxmox VE cluster.
"""

import collections
import typing

from proxmoxer import ProxmoxAPI

from prometheus_client import CollectorRegistry, generate_latest

from pve_exporter.collector.base import PveScrapeSession
from pve_exporter.collector.cluster import (
    StatusCollector,
    ClusterResourcesCollector,
    ClusterNodeCollector,
    VersionCollector,
    ClusterInfoCollector,
    BackupInfoCollector,
    QDeviceCollector
)
from pve_exporter.collector.node import (
    NodeConfigCollector,
    NodeReplicationCollector,
    SubscriptionCollector
)


class CollectorSpec(typing.NamedTuple):
    """Everything the exporter needs to know about one collector.

    Adding a collector means adding one entry to COLLECTORS below. The
    command line flag, its help text and the registration are all derived
    from it.
    """

    name: str
    """Flag suffix, exposed as --collector.<name>."""

    scope: str
    """Either 'cluster' or 'node', see the url parameters of the same name."""

    collector: type
    """The collector class, constructed with a PveScrapeSession."""

    description: str
    """Help text for the command line flag."""

    @property
    def option(self):
        """Attribute name of this collector on a CollectorsOptions."""
        return self.name.replace('-', '_')


# The order of this tuple is the order in which collectors are registered,
# which in turn is the order their metrics appear in the exposition output.
COLLECTORS = (
    CollectorSpec(
        'status', 'cluster', StatusCollector,
        'Exposes Node/VM/CT-Status'),
    CollectorSpec(
        'resources', 'cluster', ClusterResourcesCollector,
        'Exposes PVE resources info'),
    CollectorSpec(
        'node', 'cluster', ClusterNodeCollector,
        'Exposes PVE node info'),
    CollectorSpec(
        'cluster', 'cluster', ClusterInfoCollector,
        'Exposes PVE cluster info'),
    CollectorSpec(
        'version', 'cluster', VersionCollector,
        'Exposes PVE version info'),
    CollectorSpec(
        'backup-info', 'cluster', BackupInfoCollector,
        'Exposes information about guests which are not covered by any backup job'),
    CollectorSpec(
        'qdevice', 'cluster', QDeviceCollector,
        'Exposes PVE QDevice connection state'),
    CollectorSpec(
        'subscription', 'node', SubscriptionCollector,
        'Exposes PVE subscription info'),
    CollectorSpec(
        'config', 'node', NodeConfigCollector,
        'Exposes PVE onboot status'),
    CollectorSpec(
        'replication', 'node', NodeReplicationCollector,
        'Exposes PVE replication info'),
)

CollectorsOptions = collections.namedtuple(
    'CollectorsOptions', [spec.option for spec in COLLECTORS]
)


def collect_pve(config, host, cluster, node, options: CollectorsOptions):
    """Scrape a host and return prometheus text format for it"""

    pve = PveScrapeSession(ProxmoxAPI(host, **config))
    scope_enabled = {'cluster': cluster, 'node': node}

    registry = CollectorRegistry()
    for spec in COLLECTORS:
        if scope_enabled[spec.scope] and getattr(options, spec.option):
            registry.register(spec.collector(pve))

    return generate_latest(registry)
