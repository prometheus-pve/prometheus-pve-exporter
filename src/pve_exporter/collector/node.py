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
