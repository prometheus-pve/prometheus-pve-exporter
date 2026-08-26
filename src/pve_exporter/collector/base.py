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


def find_cluster_id(pve):
    """Return the prometheus id of the cluster the node belongs to.

    Args:
      pve: A ProxmoxAPI instance.

    Returns:
      An id of the form "cluster/<name>", or None if the node is not part of
      a cluster. A standalone node has no entry of type "cluster" in
      /cluster/status.
    """
    for entry in pve.cluster.status.get():
        if entry['type'] == 'cluster':
            return f"cluster/{entry['name']}"

    return None
