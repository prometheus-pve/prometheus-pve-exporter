"""
Shared helpers for the Proxmox VE collectors.
"""

from collections.abc import Iterable
from functools import cached_property

from prometheus_client.core import Metric


def find_local_node(cluster_status):
    """Return the name of the node the API connection points at.

    Args:
      cluster_status: A /cluster/status response.

    Returns:
      The node name, or None if the status reports no local node.
    """
    for entry in cluster_status:
        if entry['type'] == 'node' and entry['local']:
            return entry['name']

    return None


def find_cluster_id(cluster_status):
    """Return the prometheus id of the cluster the node belongs to.

    Args:
      cluster_status: A /cluster/status response.

    Returns:
      An id of the form "cluster/<name>", or None if the node is not part of
      a cluster. A standalone node has no entry of type "cluster" in
      /cluster/status.
    """
    for entry in cluster_status:
        if entry['type'] == 'cluster':
            return f"cluster/{entry['name']}"

    return None


class PveScrapeSession:
    """One scrape of one Proxmox VE target.

    Most collectors need /cluster/status, and several need
    /cluster/resources. Fetching those once per collector meant a full scrape
    asked the same host for the same data up to eight times, each one a
    separate HTTPS round trip. This holds on to the responses for the
    duration of a single scrape instead.

    The cache lives on the instance and a fresh instance is built for every
    scrape, so a scrape never sees data collected for a previous one.

    Responses are shared between collectors, so a collector must treat what
    it gets back here as read-only.

    Endpoints that only a single collector needs are reached through the raw
    ProxmoxAPI instance exposed as ``api``.
    """

    def __init__(self, api):
        self.api = api

    @cached_property
    def version(self):
        """The /version response."""
        return self.api.version.get()

    @cached_property
    def cluster_status(self):
        """The /cluster/status response."""
        return self.api.cluster.status.get()

    @cached_property
    def cluster_resources(self):
        """The unfiltered /cluster/resources response.

        Callers that want a subset filter this list themselves rather than
        asking the API again with a type parameter.
        """
        return self.api.cluster.resources.get()

    @cached_property
    def local_node(self):
        """Name of the node the API connection points at, or None."""
        return find_local_node(self.cluster_status)

    @cached_property
    def cluster_id(self):
        """Prometheus id of the cluster, or None for a standalone node."""
        return find_cluster_id(self.cluster_status)


class BaseCollector:
    """Base class for the collectors of a single Proxmox VE target.

    Subclasses implement collect() and reach the API through ``self._pve``,
    a PveScrapeSession shared by every collector of the same scrape.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, pve: PveScrapeSession):
        self._pve = pve

    def collect(self) -> Iterable[Metric]:
        """Return the metrics this collector produces for one scrape."""
        raise NotImplementedError
