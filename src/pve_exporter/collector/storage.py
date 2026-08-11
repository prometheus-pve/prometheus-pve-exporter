"""
Prometheus collectors for Proxmox VE storage.
"""

import itertools
import logging

from prometheus_client.core import GaugeMetricFamily
from proxmoxer.core import ResourceException


def _content_id(node, volid):
    return f"content/{node}/{volid}"


def _guest_label(item):
    vmid = item.get('vmid', 0)
    if not vmid:
        return ''
    volid = item.get('volid', '')
    if 'vzdump-lxc-' in volid or item.get('content') == 'rootdir':
        return f"lxc/{vmid}"
    return f"qemu/{vmid}"


class StorageCollector:
    """
    Collects Proxmox VE storage content information.
    """

    def __init__(self, pve, node, storage):
        self._pve = pve
        self._node = node
        self._storage = storage

    def collect(self):  # pylint: disable=missing-docstring
        info_metric = GaugeMetricFamily(
            'pve_storage_contents_info',
            'Proxmox storage content info',
            labels=['id', 'node', 'storage', 'content', 'volid', 'guest', 'verification_state'],
        )

        metrics = {
            'ctime': GaugeMetricFamily(
                'pve_storage_contents_ctime_timestamp_seconds',
                'Proxmox storage content creation time',
                labels=['id']),
            'size': GaugeMetricFamily(
                'pve_storage_contents_bytes',
                'Proxmox storage content size in bytes',
                labels=['id']),
            'verification': GaugeMetricFamily(
                'pve_storage_contents_verification',
                'Proxmox storage content verification present',
                labels=['id']),
        }

        try:
            contents = self._pve.nodes(self._node).storage(self._storage).content.get()
            for item in contents:
                content_id = _content_id(self._node, item['volid'])
                verification = item.get('verification') or {}
                verification_state = verification.get('state', '')

                info_metric.add_metric(
                    [
                        content_id,
                        self._node,
                        self._storage,
                        item['content'],
                        item['volid'],
                        _guest_label(item),
                        verification_state,
                    ],
                    1,
                )

                label_values = [content_id]
                metrics['ctime'].add_metric(label_values, item['ctime'])
                metrics['size'].add_metric(label_values, item['size'])
                if verification_state:
                    metrics['verification'].add_metric(label_values, 1)
        except ResourceException as error:
            logging.error("Error fetching storage contents: %s", error)

        return itertools.chain(metrics.values(), [info_metric])
