"""
Prometheus collecters for Proxmox VE cluster.
"""
# pylint: disable=too-few-public-methods

import collections
import itertools
import logging
from . import utils
from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException

from prometheus_client import CollectorRegistry, generate_latest
from prometheus_client.core import GaugeMetricFamily

CollectorsOptions = collections.namedtuple('CollectorsOptions', [
    'status',
    'version',
    'node',
    'cluster',
    'resources',
    'config',
])

class StatusCollector:
    """
    Collects Proxmox VE Node/VM/CT-Status

    # HELP pve_up Node/VM/CT-Status is online/running
    # TYPE pve_up gauge
    pve_up{id="node/proxmox-host"} 1.0
    pve_up{id="cluster/pvec"} 1.0
    pve_up{id="lxc/101"} 1.0
    pve_up{id="qemu/102"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring
        status_metrics = GaugeMetricFamily(
            'pve_up',
            'Node/VM/CT-Status is online/running',
            labels=['id', 'name'])

        for entry in self._pve.cluster.status.get():
            name = entry.get('name', '')
            if entry['type'] == 'node':
                label_values = [entry['id'], name]
                status_metrics.add_metric(label_values, entry['online'])
            elif entry['type'] == 'cluster':
                label_values = [f"cluster/{entry['name']}", name]
                status_metrics.add_metric(label_values, entry['quorate'])
            else:
                raise ValueError(f"Got unexpected status entry type {entry['type']}")

        for resource in self._pve.cluster.resources.get(type='vm'):
            name = resource.get('name', '')
            label_values = [resource['id'], name]
            status_metrics.add_metric(label_values, resource['status'] == 'running')

        yield status_metrics

class VersionCollector:
    """
    Collects Proxmox VE build information. E.g.:

    # HELP pve_version_info Proxmox VE version info
    # TYPE pve_version_info gauge
    pve_version_info{release="15",repoid="7599e35a",version="4.4"} 1.0
    """

    LABEL_WHITELIST = ['release', 'repoid', 'version']

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring
        version_items = self._pve.version.get().items()
        version = {key: value for key, value in version_items if key in self.LABEL_WHITELIST}

        labels, label_values = zip(*version.items())
        metric = GaugeMetricFamily(
            'pve_version_info',
            'Proxmox VE version info',
            labels=labels
        )
        metric.add_metric(label_values, 1)

        yield metric

class ClusterNodeCollector:
    """
    Collects Proxmox VE cluster node information. E.g.:

    # HELP pve_node_info Node info
    # TYPE pve_node_info gauge
    pve_node_info{id="node/proxmox-host", level="c", name="proxmox-host",
        nodeid="0"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring
        nodes = [entry for entry in self._pve.cluster.status.get() if entry['type'] == 'node']
        labels = ['id', 'level', 'name', 'nodeid']

        if nodes:
            info_metrics = GaugeMetricFamily(
                'pve_node_info',
                'Node info',
                labels=labels)

            for node in nodes:
                label_values = [str(node[key]) for key in labels]
                info_metrics.add_metric(label_values, 1)

            yield info_metrics

class ClusterInfoCollector:
    """
    Collects Proxmox VE cluster information. E.g.:

    # HELP pve_cluster_info Cluster info
    # TYPE pve_cluster_info gauge
    pve_cluster_info{id="cluster/pvec",nodes="2",quorate="1",version="2"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring
        clusters = [entry for entry in self._pve.cluster.status.get() if entry['type'] == 'cluster']

        if clusters:
            # Remove superflous keys.
            for cluster in clusters:
                del cluster['type']

            # Add cluster-prefix to id.
            for cluster in clusters:
                cluster['id'] = f"cluster/{cluster['name']}"
                del cluster['name']

            # Yield remaining data.
            labels = clusters[0].keys()
            info_metrics = GaugeMetricFamily(
                'pve_cluster_info',
                'Cluster info',
                labels=labels)

            for cluster in clusters:
                label_values = [str(cluster[key]) for key in labels]
                info_metrics.add_metric(label_values, 1)

            yield info_metrics

class ClusterResourcesCollector:
    """
    Collects Proxmox VE cluster resources information, i.e. memory, storage, cpu
    usage for cluster nodes and guests.
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring
        metrics = {
            'maxdisk': GaugeMetricFamily(
                'pve_disk_size_bytes',
                'Size of storage device',
                labels=['id', 'node', 'name', 'type']),
            'disk': GaugeMetricFamily(
                'pve_disk_usage_bytes',
                'Disk usage in bytes',
                labels=['id', 'node', 'name', 'type']),
            'maxmem': GaugeMetricFamily(
                'pve_memory_size_bytes',
                'Size of memory',
                labels=['id', 'node', 'name', 'type']),
            'mem': GaugeMetricFamily(
                'pve_memory_usage_bytes',
                'Memory usage in bytes',
                labels=['id', 'node', 'name', 'type']),
            'netout': GaugeMetricFamily(
                'pve_network_transmit_bytes',
                'Number of bytes transmitted over the network',
                labels=['id', 'node', 'name', 'type']),
            'netin': GaugeMetricFamily(
                'pve_network_receive_bytes',
                'Number of bytes received over the network',
                labels=['id', 'node', 'name', 'type']),
            'diskwrite': GaugeMetricFamily(
                'pve_disk_write_bytes',
                'Number of bytes written to storage',
                labels=['id', 'node', 'name', 'type']),
            'diskread': GaugeMetricFamily(
                'pve_disk_read_bytes',
                'Number of bytes read from storage',
                labels=['id', 'node', 'name', 'type']),
            'cpu': GaugeMetricFamily(
                'pve_cpu_usage_ratio',
                'CPU usage (value between 0.0 and pve_cpu_usage_limit)',
                labels=['id', 'node', 'name', 'type']),
            'maxcpu': GaugeMetricFamily(
                'pve_cpu_usage_limit',
                'Maximum allowed CPU usage',
                labels=['id', 'node', 'name', 'type']),
            'uptime': GaugeMetricFamily(
                'pve_uptime_seconds',
                'Number of seconds since the last boot',
                labels=['id', 'node', 'name', 'type']),
            'shared': GaugeMetricFamily(
                'pve_storage_shared',
                'Whether or not the storage is shared among cluster nodes',
                labels=['id', 'node', 'name', 'type']),
        }

        info_metrics = {
            'guest': GaugeMetricFamily(
                'pve_guest_info',
                'VM/CT info',
                labels=['id', 'node', 'name', 'type']),
            'storage': GaugeMetricFamily(
                'pve_storage_info',
                'Storage info',
                labels=['id', 'node', 'storage']),
        }

        info_lookup = {
            'lxc': {
                'labels': ['id', 'node', 'name', 'type'],
                'gauge': info_metrics['guest'],
            },
            'qemu': {
                'labels': ['id', 'node', 'name', 'type'],
                'gauge': info_metrics['guest'],
            },
            'storage': {
                'labels': ['id', 'node', 'storage'],
                'gauge': info_metrics['storage'],
            },
        }

        for resource in self._pve.cluster.resources.get():
            restype = resource['type']

            if restype in info_lookup:
                label_values = [resource.get(key, '') for key in info_lookup[restype]['labels']]
                info_lookup[restype]['gauge'].add_metric(label_values, 1)

            node = resource.get('node', '')
            restype = resource.get('type', '')
            resname = resource.get('name', '')
            label_values = [resource['id'], node, resname, restype]
            for key, metric_value in resource.items():
                if key in metrics:
                    metrics[key].add_metric(label_values, metric_value)

        return itertools.chain(metrics.values(), info_metrics.values())

class ClusterNodeConfigCollector:
    """
    Collects Proxmox VE VM information directly from config, i.e. boot, name, onboot, etc.
    For manual test: "pvesh get /nodes/<node>/<type>/<vmid>/config"

    # HELP pve_onboot_status Proxmox vm config onboot value
    # TYPE pve_onboot_status gauge
    pve_onboot_status{id="qemu/113",node="XXXX",type="qemu"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve
        self._log = logging.getLogger(__name__)

    def collect_net_metrics(self, config, metrics):
        pass

    def collect(self): # pylint: disable=missing-docstring
        metrics = {
            'onboot': GaugeMetricFamily(
                'pve_onboot_status',
                'Proxmox vm config onboot value',
                labels=['id', 'node', 'type', 'name']),
            'cores': GaugeMetricFamily(
                'pve_cores',
                'Proxmox vm config cores value',
                labels=['id', 'node', 'type', 'name']),
            'sockets': GaugeMetricFamily(
                'pve_sockets',
                'Proxmox vm config sockets value',
                labels=['id', 'node', 'type', 'name']),
            'memory': GaugeMetricFamily(
                'pve_memory',
                'Proxmox vm config memory value',
                labels=['id', 'node', 'type', 'name']),
            'netqueue': GaugeMetricFamily(
                'pve_netqueue_size',
                'Proxmox vm config netqueue value',
                labels=['id', 'node', 'type', 'net', 'name']),
            'vlan': GaugeMetricFamily(
                'pve_vlan_id',
                'Proxmox vm config vlan value',
                labels=['id', 'node', 'type', 'net', 'name']),
            'netrate': GaugeMetricFamily(
                'pve_netrate',
                'Proxmox vm config netrate value',
                labels=['id', 'node', 'type', 'net', 'name']),
            'rng': GaugeMetricFamily(
                'pve_rng',
                'Proxmox vm config random generator value',
                labels=['id', 'node', 'type', 'name']),
        }

        for node in self._pve.nodes.get():
            # The nodes/{node} api call will result in requests being forwarded
            # from the api node to the target node. Those calls can fail if the
            # target node is offline or otherwise unable to respond to the
            # request. In that case it is better to just skip scraping the
            # config for guests on that particular node and continue with the
            # next one in order to avoid failing the whole scrape.
            try:
                # Qemu
                vmtype = 'qemu'
                for vmdata in self._pve.nodes(node['node']).qemu.get():
                    config = self._pve.nodes(node['node']).qemu(vmdata['vmid']).config.get().items()
                    name = utils.get_key_tuple('name', config)
                    label_values = [f"{vmtype}/{vmdata['vmid']}", node['node'], vmtype, name]

                    rng = utils.get_key_tuple('rng0', config)
                    if rng != '':
                        metrics['rng'].add_metric(label_values, 1)
                    else:
                        metrics['rng'].add_metric(label_values, 0)
                    for key, metric_value in config:
                        if key in metrics:
                            metrics[key].add_metric(label_values, metric_value)
                        if key.startswith('net'):
                            label_values = [f"{vmtype}/{vmdata['vmid']}", node['node'], vmtype, key, name]
                            
                            # virtio=BA:0B:A4:09:8E:A1,bridge=vmbr0,queues=2,rate=125,tag=600
                            netinfo = dict(item.split("=") for item in metric_value.split(","))

                            if 'queues' in netinfo:
                                metrics['netqueue'].add_metric(label_values, int(netinfo['queues']))
                            else:
                                metrics['netqueue'].add_metric(label_values, -1)

                            if 'tag' in netinfo:
                                metrics['vlan'].add_metric(label_values, int(netinfo['tag']))
                            else:
                                metrics['vlan'].add_metric(label_values, -1)

                            if 'rate' in netinfo:
                                metrics['netrate'].add_metric(label_values, int(netinfo['rate']))
                            else:
                                metrics['netrate'].add_metric(label_values, -1)

                # LXC
                vmtype = 'lxc'
                for vmdata in self._pve.nodes(node['node']).lxc.get():
                    config = self._pve.nodes(node['node']).lxc(vmdata['vmid']).config.get().items()
                    name = utils.get_key_tuple('name', config)
                    for key, metric_value in config:
                        label_values = [f"{vmtype}/{vmdata['vmid']}", node['node'], vmtype, name]
                        if key in metrics:
                            metrics[key].add_metric(label_values, metric_value)

            except ResourceException:
                self._log.exception(
                    "Exception thrown while scraping quemu/lxc config from %s",
                    node['node']
                )
                continue

        return metrics.values()

def collect_pve(config, host, options: CollectorsOptions):
    """Scrape a host and return prometheus text format for it"""

    pve = ProxmoxAPI(host, **config)

    registry = CollectorRegistry()
    if options.status:
        registry.register(StatusCollector(pve))
    if options.resources:
        registry.register(ClusterResourcesCollector(pve))
    if options.node:
        registry.register(ClusterNodeCollector(pve))
    if options.cluster:
        registry.register(ClusterInfoCollector(pve))
    if options.config:
        registry.register(ClusterNodeConfigCollector(pve))
    if options.version:
        registry.register(VersionCollector(pve))

    return generate_latest(registry)
