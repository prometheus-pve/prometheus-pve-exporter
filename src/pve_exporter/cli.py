"""
Proxmox VE exporter for the Prometheus monitoring system.
"""

from argparse import ArgumentParser, BooleanOptionalAction
import os
import pathlib
import yaml
from pve_exporter.http import start_http_server
from pve_exporter.config import config_from_yaml
from pve_exporter.config import config_from_env
from pve_exporter.collector import CollectorsOptions


def main():
    """
    Main entry point.
    """

    parser = ArgumentParser()
    clusterflags = parser.add_argument_group('cluster collectors', description=(
        'cluster collectors are run if the url parameter cluster=1 is set and '
        'skipped if the url parameter cluster=0 is set on a scrape url.'
    ))
    clusterflags.add_argument('--collector.status', dest='collector_status',
                              action=BooleanOptionalAction, default=True,
                              help='Exposes Node/VM/CT-Status')
    clusterflags.add_argument('--collector.version', dest='collector_version',
                              action=BooleanOptionalAction, default=True,
                              help='Exposes PVE version info')
    clusterflags.add_argument('--collector.node', dest='collector_node',
                              action=BooleanOptionalAction, default=True,
                              help='Exposes PVE node info')
    clusterflags.add_argument('--collector.cluster', dest='collector_cluster',
                              action=BooleanOptionalAction, default=True,
                              help='Exposes PVE cluster info')
    clusterflags.add_argument('--collector.resources', dest='collector_resources',
                              action=BooleanOptionalAction, default=True,
                              help='Exposes PVE resources info')

    nodeflags = parser.add_argument_group('node collectors', description=(
        'node collectors are run if the url parameter node=1 is set and '
        'skipped if the url parameter node=0 is set on a scrape url.'
    ))
    nodeflags.add_argument('--collector.config', dest='collector_config',
                           action=BooleanOptionalAction, default=True,
                           help='Exposes PVE onboot status')

    nodeflags.add_argument('--collector.replication', dest='collector_replication',
                           action=BooleanOptionalAction, default=True,
                           help='Exposes PVE replication info')

    parser.add_argument('--config.file', type=pathlib.Path,
                        dest="config_file", default='/etc/prometheus/pve.yml',
                        help='Path to config file (/etc/prometheus/pve.yml)')

    parser.add_argument('--web.listen-address',
                        dest="web_listen_address", default='[::]:9221',
                        help=(
                            'Address on which to expose metrics and web server. '
                            '([::]:9221)'
                        ))
    parser.add_argument('--server.keyfile', dest='server_keyfile',
                        help='SSL key for server')
    parser.add_argument('--server.certfile', dest='server_certfile',
                        help='SSL certificate for server')

    params = parser.parse_args()

    collectors = CollectorsOptions(
        status=params.collector_status,
        version=params.collector_version,
        node=params.collector_node,
        cluster=params.collector_cluster,
        resources=params.collector_resources,
        config=params.collector_config,
        replication=params.collector_replication
    )

    # Load configuration.
    if 'PVE_USER' in os.environ:
        config = config_from_env(os.environ)
    else:
        with open(params.config_file, encoding='utf-8') as handle:
            config = config_from_yaml(yaml.safe_load(handle))

    gunicorn_options = {
        'bind': f'{params.web_listen_address}',
        'threads': 2,
        'keyfile': params.server_keyfile,
        'certfile': params.server_certfile,
    }

    if config.valid:
        start_http_server(config, gunicorn_options, collectors)
    else:
        parser.error(str(config))
