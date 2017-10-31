"""
Proxmox VE exporter for the Prometheus monitoring system.
"""

import sys
from pve_exporter.http import start_http_server

def main(args=None):
    """
    Main entry point.
    """

    if args is None:
        args = sys.argv

    if len(args) not in [1, 2, 3]:
        print("Usage: pve_exporter [config_file] [port]")
        sys.exit(1)

    if len(args) >= 2:
        config = args[1]
    else:
        config = "pve.yml"

    if len(args) >= 3:
        port = int(args[2])
    else:
        port = 9221

    start_http_server(config, port)
