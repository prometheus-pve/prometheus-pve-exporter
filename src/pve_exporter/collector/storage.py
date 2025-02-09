"""
Prometheus collectors for Proxmox VE storage.
"""

from prometheus_client.core import GaugeMetricFamily
from proxmoxer.core import ResourceException
import logging

class StorageCollector:
    """
    Collects Proxmox VE storage information.
    """

    def __init__(self, pve, node, storage):
        self._pve = pve
        self._node = node
        self._storage = storage

    def collect(self):
        metrics = {
            'ctime': GaugeMetricFamily(
                'pve_storage_contents_ctime',
                'Proxmox storage contents ctime',
                labels=['node', 'storage', 'vmid', 'content', 'volid']),
            'size': GaugeMetricFamily(
                'pve_storage_contents_bytes',
                'Proxmox storage contents size in bytes',
                labels=['node', 'storage', 'vmid', 'content', 'volid']),
            'verification': GaugeMetricFamily(
                'pve_storage_contents_verification',
                'Proxmox storage contents verification state',
                labels=['node', 'storage', 'vmid', 'content', 'volid', 'state']),
        }

        try:
            contents = self._pve.nodes(self._node).storage(self._storage).content.get()
            for item in contents:
                metrics['ctime'].add_metric(
                    [self._node, self._storage, str(item['vmid']), item['content'], item['volid']],
                    item['ctime']
                )

                metrics['size'].add_metric(
                    [self._node, self._storage, str(item['vmid']), item['content'], item['volid']],
                    item['size']
                )

                if 'verification' in item:
                    metrics['verification'].add_metric(
                        [self._node, self._storage, str(item['vmid']), item['content'], item['volid'], item['verification']['state']],
                        1
                    )
        except ResourceException as e:
            # Log the error and return an empty list of metrics
            logging.error(f"Error fetching storage contents: {e}")
            return metrics.values()

        return metrics.values()
