"""
Shared helpers for the Proxmox VE collectors.
"""


def find_local_node(pve):
    """Return the name of the node the API connection points at.

    Args:
      pve: A ProxmoxAPI instance.

    Returns:
      The node name, or None if /cluster/status reports no local node.
    """
    for entry in pve.cluster.status.get():
        if entry['type'] == 'node' and entry['local']:
            return entry['name']

    return None
