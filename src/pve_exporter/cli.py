"""
Proxmox VE exporter for the Prometheus monitoring system.
"""

import sys
from argparse import ArgumentParser
from pve_exporter.http import start_http_server

def main(args=None):
    """
    Main entry point.
    """

    parser = ArgumentParser()
    parser.add_argument('config', nargs='?', default='pve.yml',
                        help='Path to configuration file (pve.yml)')
    parser.add_argument('port', nargs='?', type=int, default='9221',
                        help='Port on which the exporter is listening (9221)')
    parser.add_argument('address', nargs='?', default='',
                        help='Address to which the exporter will bind')

    params = parser.parse_args(args if args is None else sys.argv[1:])

    start_http_server(params.config, params.port, params.address)
