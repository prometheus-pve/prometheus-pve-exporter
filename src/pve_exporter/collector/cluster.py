"""
Prometheus collecters for Proxmox VE cluster.
"""
# pylint: disable=too-few-public-methods

import itertools
from typing import Any, Union

from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily


class StatusCollector:
    """
    Collects Proxmox VE Node/VM/CT-Status

    # HELP pve_up Node/VM/CT-Status is online/running
    # TYPE pve_up gauge
    pve_up{id="node/proxmox-host",name="proxmox-host"} 1.0
    pve_up{id="cluster/pvec",name="pvec"} 1.0
    pve_up{id="lxc/101",name="container-name"} 1.0
    pve_up{id="qemu/102",name="vm-name"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self):  # pylint: disable=missing-docstring
        status_metrics = GaugeMetricFamily(
            'pve_up',
            'Node/VM/CT-Status is online/running',
            labels=['id', 'name'])

        for entry in self._pve.cluster.status.get():
            if entry['type'] == 'node':
                label_values = [entry['id'], entry.get('name', '')]
                status_metrics.add_metric(label_values, entry['online'])
            elif entry['type'] == 'cluster':
                label_values = [f"cluster/{entry['name']}", entry.get('name', '')]
                status_metrics.add_metric(label_values, entry['quorate'])
            else:
                raise ValueError(f"Got unexpected status entry type {entry['type']}")

        for resource in self._pve.cluster.resources.get(type='vm'):
            label_values = [resource['id'], resource.get('name', '')]
            status_metrics.add_metric(label_values, resource['status'] == 'running')

        for resource in self._pve.cluster.resources.get(type='storage'):
            # Storage resources use 'storage' field for name, not 'name'
            label_values = [resource['id'], resource.get('storage', '')]
            status_metrics.add_metric(label_values, resource['status'] == 'available')

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

    def collect(self):  # pylint: disable=missing-docstring
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

    def collect(self):  # pylint: disable=missing-docstring
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

    def collect(self):  # pylint: disable=missing-docstring
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


class HighAvailabilityStateMetric(GaugeMetricFamily):
    """
    A single gauge representing PVE ha state.
    """

    GUEST_STATES = [
        'stopped',
        'request_stop',
        'request_start',
        'request_start_balance',
        'started',
        'fence',
        'recovery',
        'migrate',
        'relocate',
        'freeze',
        'error',
    ]

    NODE_STATES = ['online', 'maintenance', 'unknown', 'fence', 'gone']

    STATES = {
        'lxc': GUEST_STATES,
        'qemu': GUEST_STATES,
        'node': NODE_STATES,
    }

    def __init__(self):
        super().__init__(
            'pve_ha_state',
            'HA service status (for HA managed VMs).',
            labels=['id', 'state']
        )

    def add_metric_from_resource(self, resource: dict):
        """Inspect resource and add suitable metric- to the metric family.

        Args:
          resource: A PVE cluster resource
        """
        restype = resource['type']
        if restype in self.STATES:
            for state in self.STATES[restype]:
                value = resource.get('hastate', None) == state
                self.add_metric([resource['id'], state], value)


class LockStateMetric(GaugeMetricFamily):
    """
    A single gauge representing PVE guest lock state.
    """

    GUEST_STATES = [
        'backup',
        'clone',
        'create',
        'migrate',
        'rollback',
        'snapshot',
        'snapshot-delete',
        'suspended',
        'suspending',
    ]

    STATES = {
        'qemu': GUEST_STATES,
        'lxc': GUEST_STATES,
    }

    def __init__(self):
        super().__init__(
            'pve_lock_state',
            "The guest's current config lock (for types 'qemu' and 'lxc')",
            labels=['id', 'state']
        )

    def add_metric_from_resource(self, resource: dict):
        """Inspect resource and add suitable metric- to the metric family.

        Args:
          resource: A PVE cluster resource
        """
        restype = resource['type']
        if restype in self.STATES:
            for state in self.STATES[restype]:
                value = resource.get('lock', None) == state
                self.add_metric([resource['id'], state], value)


class ClusterResourcesCollector:
    """
    Collects Proxmox VE cluster resources information, i.e. memory, storage, cpu
    usage for cluster nodes and guests.
    """

    def __init__(self, pve):
        self._pve = pve
        # Resource type to name field mapping
        self._RESOURCE_NAME_FIELDS = {
            'qemu': 'name',
            'lxc': 'name',
            'node': 'name',
            'storage': 'storage',
        }

    def _get_resource_name(self, resource: dict[str, Any]) -> str:
        """Extract the name for a resource based on its type.
        
        Args:
            resource: Resource dictionary from PVE API
            
        Returns:
            Resource name string, or empty string if not available
        """
        restype = resource['type']
        name_field = self._RESOURCE_NAME_FIELDS.get(restype)
        if name_field:
            return resource.get(name_field, '')
        return ''

    def _build_label_values(self, resource: dict[str, Any], 
                           metric: Union[GaugeMetricFamily, CounterMetricFamily]) -> list[str]:
        """Build label values for a metric based on resource and metric labels.
        
        Args:
            resource: Resource dictionary from PVE API
            metric: Metric family object
            
        Returns:
            List of label values in the same order as metric._labelnames
        """
        label_values = [resource['id']]
        if 'name' in metric._labelnames:
            resource_name = self._get_resource_name(resource)
            label_values.append(resource_name)
        return label_values

    def collect(self):  # pylint: disable=missing-docstring
        # Metrics with 'name' label for VM, node, and storage metrics
        # Note: Prometheus requires all samples of the same metric to have the same label names.
        # For VM and node resources, the 'name' label will be populated from the 'name' field.
        # For storage resources, the 'name' label will be populated from the 'storage' field.
        metrics = {
            'maxdisk': GaugeMetricFamily(
                'pve_disk_size_bytes',
                (
                    "Storage size in bytes (for type 'storage'), root image size for VMs "
                    "(for types 'qemu' and 'lxc')."
                ),
                labels=['id', 'name']),
            'disk': GaugeMetricFamily(
                'pve_disk_usage_bytes',
                (
                    "Used disk space in bytes (for type 'storage'), used root image space for VMs "
                    "(for types 'qemu' and 'lxc')."
                ),
                labels=['id', 'name']),
            'maxmem': GaugeMetricFamily(
                'pve_memory_size_bytes',
                "Number of available memory in bytes (for types 'node', 'qemu' and 'lxc').",
                labels=['id', 'name']),
            'mem': GaugeMetricFamily(
                'pve_memory_usage_bytes',
                "Used memory in bytes (for types 'node', 'qemu' and 'lxc').",
                labels=['id', 'name']),
            'netout': GaugeMetricFamily(
                'pve_network_transmit_bytes',
                (
                    "The amount of traffic in bytes that was sent from the guest over the network "
                    "since it was started. (for types 'qemu' and 'lxc') "
                    "DEPRECATED: Use pve_network_transmit_bytes_total instead."
                ),
                labels=['id', 'name']),
            'netin': GaugeMetricFamily(
                'pve_network_receive_bytes',
                (
                    "The amount of traffic in bytes that was sent to the guest over the network "
                    "since it was started. (for types 'qemu' and 'lxc') "
                    "DEPRECATED: Use pve_network_receive_bytes_total instead."
                ),
                labels=['id', 'name']),
            'diskwrite': GaugeMetricFamily(
                'pve_disk_write_bytes',
                (
                    "The amount of bytes the guest wrote to its block devices since the guest was "
                    "started. This info is not available for all storage types. "
                    "(for types 'qemu' and 'lxc') "
                    "DEPRECATED: Use pve_disk_written_bytes_total instead."
                ),
                labels=['id', 'name']),
            'diskread': GaugeMetricFamily(
                'pve_disk_read_bytes',
                (
                    "The amount of bytes the guest read from its block devices since the guest was "
                    "started. This info is not available for all storage types. "
                    "(for types 'qemu' and 'lxc') "
                    "DEPRECATED: Use pve_disk_read_bytes_total instead."
                ),
                labels=['id', 'name']),
            'cpu': GaugeMetricFamily(
                'pve_cpu_usage_ratio',
                "CPU utilization (for types 'node', 'qemu' and 'lxc').",
                labels=['id', 'name']),
            'maxcpu': GaugeMetricFamily(
                'pve_cpu_usage_limit',
                "Number of available CPUs (for types 'node', 'qemu' and 'lxc').",
                labels=['id', 'name']),
            'uptime': GaugeMetricFamily(
                'pve_uptime_seconds',
                "Uptime of node or virtual guest in seconds (for types 'node', 'qemu' and 'lxc').",
                labels=['id', 'name']),
            'shared': GaugeMetricFamily(
                'pve_storage_shared',
                'Whether or not the storage is shared among cluster nodes',
                labels=['id']),
        }

        counter_metrics = {
            'netout': CounterMetricFamily(
                'pve_network_transmit_bytes_total',
                (
                    "The amount of traffic in bytes that was sent from the guest over the network "
                    "since it was started. (for types 'qemu' and 'lxc')"
                ),
                labels=['id', 'name']),
            'netin': CounterMetricFamily(
                'pve_network_receive_bytes_total',
                (
                    "The amount of traffic in bytes that was sent to the guest over the network "
                    "since it was started. (for types 'qemu' and 'lxc')"
                ),
                labels=['id', 'name']),
            'diskwrite': CounterMetricFamily(
                'pve_disk_written_bytes_total',
                (
                    "The amount of bytes the guest wrote to its block devices since the guest was "
                    "started. This info is not available for all storage types. "
                    "(for types 'qemu' and 'lxc')"
                ),
                labels=['id', 'name']),
            'diskread': CounterMetricFamily(
                'pve_disk_read_bytes_total',
                (
                    "The amount of bytes the guest read from its block devices since the guest was "
                    "started. This info is not available for all storage types. "
                    "(for types 'qemu' and 'lxc')"
                ),
                labels=['id', 'name']),
        }

        ha_metric = HighAvailabilityStateMetric()
        lock_metric = LockStateMetric()

        info_metrics = {
            'guest': GaugeMetricFamily(
                'pve_guest_info',
                'VM/CT info',
                labels=['id', 'node', 'name', 'type', 'template', 'tags']),
            'storage': GaugeMetricFamily(
                'pve_storage_info',
                'Storage info',
                labels=['id', 'node', 'storage', 'plugintype', 'content']),
        }

        info_lookup = {
            'lxc': {
                'labels': ['id', 'node', 'name', 'type', 'template', 'tags'],
                'gauge': info_metrics['guest'],
            },
            'qemu': {
                'labels': ['id', 'node', 'name', 'type', 'template', 'tags'],
                'gauge': info_metrics['guest'],
            },
            'storage': {
                'labels': ['id', 'node', 'storage', 'plugintype'],
                'csv_labels': ['content'],
                'gauge': info_metrics['storage'],
            },
        }

        for resource in self._pve.cluster.resources.get():
            restype = resource['type']

            if restype in info_lookup:
                all_labels = self._extract_resource_labels(info_lookup[restype], resource)
                info_lookup[restype]['gauge'].add_metric(all_labels, 1)

            ha_metric.add_metric_from_resource(resource)
            lock_metric.add_metric_from_resource(resource)

            # Process gauge metrics
            # Note: Prometheus requires all samples of the same metric to have the same label names
            for key, metric_value in resource.items():
                if key in metrics:
                    label_values = self._build_label_values(resource, metrics[key])
                    metrics[key].add_metric(label_values, metric_value)
                
                # Process counter metrics (all counter metrics are VM-only and have 'name' label)
                if key in counter_metrics:
                    label_values = self._build_label_values(resource, counter_metrics[key])
                    counter_metrics[key].add_metric(label_values, metric_value)

        return itertools.chain(
            metrics.values(),
            counter_metrics.values(),
            [ha_metric, lock_metric],
            info_metrics.values()
        )

    def _extract_resource_labels(self, resource_lookup_info: dict[str, Any],
                                 api_response_resource: dict[str, Any]) -> list[str]:
        """Extract resource labels from the PVE API response.

        Returns:
            list[str]: A list of labels.
        """
        labels = resource_lookup_info['labels']
        label_values = [str(api_response_resource.get(key, ''))
                        for key in labels]

        # Labels with comma-separated values are randomly ordered by
        # Proxmox. This causes different metrics on every scrape, which
        # results in both churn rate and cardinality to explode.
        # Split the list up, sort it, and rejoin to avoid this.
        csv_labels = resource_lookup_info.get('csv_labels') or []
        csv_label_values_unsorted = [
            str(api_response_resource.get(key, '')) for key in csv_labels
        ]

        csv_label_values = []
        for label_value in csv_label_values_unsorted:
            split_values = label_value.split(',')
            split_values.sort()
            sorted_values = ','.join(split_values)
            csv_label_values.append(sorted_values)

        return label_values + csv_label_values

class BackupInfoCollector:
    """
    Collects information on guests which are not covered by any backup job. E.g.:

    pve_not_backed_up_total{id="cluster/pvec"} 2.0
    pve_not_backed_up_info{id="qemu/102"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self):  # pylint: disable=missing-docstring
        not_enabled_total = GaugeMetricFamily(
            'pve_not_backed_up_total',
            'Total number of guests not covered by any backup job.',
            labels=['id']
        )
        not_enabled_info = GaugeMetricFamily(
            'pve_not_backed_up_info',
            'Present if guest is not covered by any backup job.',
            labels=['id']
        )

        not_enabled_data = self._pve.cluster("backup-info/not-backed-up").get()
        cluster_name = self._pve.cluster.status.get()[0]['name']

        for entry in not_enabled_data:
            label_values = [f"{entry['type']}/{entry['vmid']}"]
            not_enabled_info.add_metric(label_values, 1)

        not_enabled_total.add_metric(
            [f"cluster/{cluster_name}"],
            len(not_enabled_data)
        )

        yield not_enabled_total
        yield not_enabled_info
