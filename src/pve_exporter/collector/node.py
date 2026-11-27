"""
Prometheus collecters for Proxmox VE cluster.
"""
# pylint: disable=too-few-public-methods

import itertools
import re
from datetime import datetime

from prometheus_client.core import GaugeMetricFamily

# Plain top-level config keys that map directly to a single metric value.
# To add another one of these: add an entry here, keyed by its config key name.
SIMPLE_METRICS = {
    'onboot': ('pve_onboot_status', 'Proxmox vm config onboot value'),
}

# Metrics embedded inside a device config string, e.g. "scsi0" or "net0":
# "local-lvm:vm-100-disk-0,mbps_rd=10,mbps_wr=10,size=32G" or "virtio=AA:BB,bridge=vmbr0,rate=10".
# To add another one of these: add an entry to a group's 'families' list (or a new group, if the
# metric lives on a device type not covered by an existing 'key_re').
DEVICE_METRIC_GROUPS = [
    {
        # QEMU disk devices support bandwidth/IOPS throttling; LXC mountpoints do not.
        'key_re': re.compile(r'^(ide|sata|scsi|virtio)\d+$'),
        'device_label': 'disk',
        'families': [
            {
                'name': 'pve_disk_bandwidth_limit_mbps',
                'help': (
                    "Configured disk bandwidth limit in megabytes per second, per disk device "
                    "and limit type (read, write, read_burst, write_burst). QEMU guests only."
                ),
                'limit_label': 'limit',
                'keys': {
                    'mbps_rd': 'read',
                    'mbps_wr': 'write',
                    'mbps_rd_max': 'read_burst',
                    'mbps_wr_max': 'write_burst',
                },
            },
            {
                'name': 'pve_disk_iops_limit',
                'help': (
                    "Configured disk IOPS limit in operations per second, per disk device "
                    "and limit type (read, write, read_burst, write_burst). QEMU guests only."
                ),
                'limit_label': 'limit',
                'keys': {
                    'iops_rd': 'read',
                    'iops_wr': 'write',
                    'iops_rd_max': 'read_burst',
                    'iops_wr_max': 'write_burst',
                },
            },
        ],
    },
    {
        # Both QEMU and LXC support a 'rate' limit on network devices.
        'key_re': re.compile(r'^net\d+$'),
        'device_label': 'iface',
        'families': [
            {
                'name': 'pve_network_rate_limit_mbps',
                'help': 'Configured network interface rate limit in megabytes per second.',
                'limit_label': None,
                'keys': {'rate': None},
            },
        ],
    },
]


def _parse_device_options(value):
    """Parse a Proxmox device config string (e.g. "local-lvm:vm-100-disk-0,mbps_rd=10,size=32G")
    into a dict of its key=value options, ignoring the leading volume/storage token."""
    options = {}
    for part in value.split(','):
        if '=' in part:
            key, val = part.split('=', 1)
            options[key] = val
    return options


class NodeConfigCollector:
    """
    Collects Proxmox VE VM information directly from config, i.e. boot, name, onboot, bandwidth
    and IOPS limits, network rate limits, etc.
    For manual test: "pvesh get /nodes/<node>/<type>/<vmid>/config"

    # HELP pve_onboot_status Proxmox vm config onboot value
    # TYPE pve_onboot_status gauge
    pve_onboot_status{id="qemu/113",node="XXXX",type="qemu"} 1.0
    """

    def __init__(self, pve):
        self._pve = pve

    def _build_metrics(self):
        simple_metrics = {
            key: GaugeMetricFamily(name, help_text, labels=['id', 'node', 'type'])
            for key, (name, help_text) in SIMPLE_METRICS.items()
        }

        device_metrics = {}
        for group in DEVICE_METRIC_GROUPS:
            for family in group['families']:
                labels = ['id', 'node', 'type', group['device_label']]
                if family['limit_label']:
                    labels.append(family['limit_label'])
                device_metrics[family['name']] = GaugeMetricFamily(
                    family['name'], family['help'], labels=labels)

        return simple_metrics, device_metrics

    def _collect_device_metrics(self, key, value, label_values, device_metrics):
        for group in DEVICE_METRIC_GROUPS:
            if not group['key_re'].match(key):
                continue
            options = _parse_device_options(value)
            for family in group['families']:
                metric = device_metrics[family['name']]
                for opt_key, limit_value in family['keys'].items():
                    if opt_key not in options:
                        continue
                    extra = [key] if limit_value is None else [key, limit_value]
                    metric.add_metric(label_values + extra, float(options[opt_key]))

    def collect(self):  # pylint: disable=missing-docstring
        simple_metrics, device_metrics = self._build_metrics()

        node = None
        for entry in self._pve.cluster.status.get():
            if entry['type'] == 'node' and entry['local']:
                node = entry['name']
                break

        for vmtype in ('qemu', 'lxc'):
            for vmdata in getattr(self._pve.nodes(node), vmtype).get():
                config = getattr(self._pve.nodes(node), vmtype)(
                    vmdata['vmid']).config.get().items()
                for key, metric_value in config:
                    label_values = [f"{vmtype}/{vmdata['vmid']}", node, vmtype]
                    if key in simple_metrics:
                        simple_metrics[key].add_metric(label_values, metric_value)
                    else:
                        self._collect_device_metrics(
                            key, metric_value, label_values, device_metrics)

        return itertools.chain(simple_metrics.values(), device_metrics.values())

class NodeReplicationCollector:
    """
    Collects Proxmox VE Replication information directly from status, i.e. replication duration,
    last_sync, last_try, next_sync, fail_count.
    For manual test: "pvesh get /nodes/<node>/replication/<id>/status"
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring

        info_metrics = {
            'info': GaugeMetricFamily(
            'pve_replication_info',
            'Proxmox vm replication info',
            labels=['id', 'type', 'source', 'target', 'guest'])
        }

        metrics = {
            'duration': GaugeMetricFamily(
                'pve_replication_duration_seconds',
                'Proxmox vm replication duration',
                labels=['id']),
            'last_sync': GaugeMetricFamily(
                'pve_replication_last_sync_timestamp_seconds',
                'Proxmox vm replication last_sync',
                labels=['id']),
            'last_try': GaugeMetricFamily(
                'pve_replication_last_try_timestamp_seconds',
                'Proxmox vm replication last_try',
                labels=['id']),
            'next_sync': GaugeMetricFamily(
                'pve_replication_next_sync_timestamp_seconds',
                'Proxmox vm replication next_sync',
                labels=['id']),
            'fail_count': GaugeMetricFamily(
                'pve_replication_failed_syncs',
                'Proxmox vm replication fail_count',
                labels=['id']),
        }

        node = None
        for entry in self._pve.cluster.status.get():
            if entry['type'] == 'node' and entry['local']:
                node = entry['name']
                break

        for jobdata in self._pve.nodes(node).replication.get():
            # Add info metric
            label_values = [
                str(jobdata['id']),
                str(jobdata['type']),
                f"node/{jobdata['source']}",
                f"node/{jobdata['target']}",
                f"{jobdata['vmtype']}/{jobdata['guest']}",
            ]
            info_metrics['info'].add_metric(label_values, 1)

            # Add metrics
            label_values = [str(jobdata['id'])]
            status = self._pve.nodes(node).replication(jobdata['id']).status.get()
            for key, metric_value in status.items():
                if key in metrics:
                    metrics[key].add_metric(label_values, metric_value)

        return itertools.chain(metrics.values(), info_metrics.values())

class SubscriptionCollector:
    """
    Collects Proxmox VE subscription information (node, subscription level, status, next due date).
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self):  # pylint: disable=missing-docstring
        info_metric = GaugeMetricFamily(
            "pve_subscription_info",
            "Proxmox VE subscription info (1 if present)",
            labels=["id", "level"],
        )

        possible_statuses = ["new", "notfound", "active", "invalid", "expired", "suspended"]
        status_metric = GaugeMetricFamily(
            "pve_subscription_status",
            "Proxmox VE subscription status (1 if matches status)",
            labels=["id", "status"],
        )

        next_due_metric = GaugeMetricFamily(
            "pve_subscription_next_due_timestamp_seconds",
            "Subscription next due date as Unix timestamp",
            labels=["id"],
        )

        node = None
        for entry in self._pve.cluster.status.get():
            if entry['type'] == 'node' and entry['local']:
                node = entry['name']
                break

        subscription = self._pve.nodes(node).subscription.get()

        level = subscription.get("level", "unknown")
        status = subscription.get("status", "unknown")

        info_metric.add_metric(
            [f"node/{node}", level],
            1,
        )

        for possible_status in possible_statuses:
            value = 1 if status == possible_status else 0
            status_metric.add_metric(
                [f"node/{node}", possible_status],
                value,
            )

        next_due_date = subscription.get("nextduedate")
        if next_due_date:
            timestamp = datetime.strptime(next_due_date, "%Y-%m-%d").timestamp()
            next_due_metric.add_metric(
                [f"node/{node}"],
                timestamp,
            )

        yield info_metric
        yield status_metric
        yield next_due_metric
