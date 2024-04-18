"""
Prometheus collecters for Proxmox VE cluster.
"""
# pylint: disable=too-few-public-methods

import logging

from prometheus_client.core import GaugeMetricFamily


class NodeConfigCollector:
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

    def collect(self):  # pylint: disable=missing-docstring
        metrics = {
            'onboot': GaugeMetricFamily(
                'pve_onboot_status',
                'Proxmox vm config onboot value',
                labels=['id', 'node', 'type']),
        }

        node = None
        for entry in self._pve.cluster.status.get():
            if entry['type'] == 'node' and entry['local']:
                node = entry['name']
                break

        # Scrape qemu config
        vmtype = 'qemu'
        for vmdata in self._pve.nodes(node).qemu.get():
            config = self._pve.nodes(node).qemu(
                vmdata['vmid']).config.get().items()
            for key, metric_value in config:
                label_values = [f"{vmtype}/{vmdata['vmid']}", node, vmtype]
                if key in metrics:
                    metrics[key].add_metric(label_values, metric_value)

        # Scrape LXC config
        vmtype = 'lxc'
        for vmdata in self._pve.nodes(node).lxc.get():
            config = self._pve.nodes(node).lxc(
                vmdata['vmid']).config.get().items()
            for key, metric_value in config:
                label_values = [f"{vmtype}/{vmdata['vmid']}", node, vmtype]
                if key in metrics:
                    metrics[key].add_metric(label_values, metric_value)

        return metrics.values()

class NodeReplicationCollector:
    """
    Collects Proxmox VE Replication information directly from status, i.e. replication time,last_time
    For manual test: "pvesh get /nodes/<node>/replication/<id>/status"
    # HELP pve_replication_duration Proxmox vm replication duration
    # TYPE pve_replication_duration gauge
    pve_replication_duration{id="101-0",type="local", vmtype="lxc", source="server1", target="server2", guest="101"} 47.56
    """

    def __init__(self, pve):
        self._pve = pve

    def collect(self): # pylint: disable=missing-docstring
        metrics = {
            'duration': GaugeMetricFamily(
                'pve_replication_duration',
                'Proxmox vm replication duration',
                labels=['id', 'type', 'vmtype', 'source', 'target', 'guest']),
            'last_sync': GaugeMetricFamily(
                'pve_replication_last_sync',
                'Proxmox vm replication last_sync',
                labels=['id', 'type', 'vmtype', 'source', 'target', 'guest']),
            'last_try': GaugeMetricFamily(
                'pve_replication_last_try',
                'Proxmox vm replication last_try',
                labels=['id', 'type', 'vmtype', 'source', 'target', 'guest']),
            'next_sync': GaugeMetricFamily(
                'pve_replication_next_sync',
                'Proxmox vm replication next_sync',
                labels=['id', 'type', 'vmtype', 'source', 'target', 'guest']),
            'fail_count': GaugeMetricFamily(
                'pve_replication_fail_count',
                'Proxmox vm replication fail_count',
                labels=['id', 'type', 'vmtype', 'source', 'target', 'guest']),
        }

        for entry in self._pve.cluster.status.get():
            if entry['type'] == 'node':
                node = entry['name']

                for vmdata in self._pve("nodes/{0}/replication/".format(node)).get():
                    for key, metric_value in self._pve("nodes/{0}/replication/{1}/status".format(node,vmdata['id'])).get().items():
                        label_values = [str(vmdata['id']), str(vmdata['type']), str(vmdata['vmtype']), str(vmdata['source']), str(vmdata['target']), str(vmdata['guest'])]
                        if key in metrics:
                            metrics[key].add_metric(label_values, metric_value)

        return metrics.values()