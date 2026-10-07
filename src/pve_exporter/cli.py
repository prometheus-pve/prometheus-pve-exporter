"""
Proxmox VE exporter for the Prometheus monitoring system.
"""

from argparse import ArgumentParser, BooleanOptionalAction
import os
import pathlib
import yaml
from pve_exporter import scrape_metrics
from pve_exporter.http import start_http_server
from pve_exporter.config import config_from_yaml
from pve_exporter.config import config_from_env
from pve_exporter.collector import COLLECTORS, CollectorsOptions


def main():
    """
    Main entry point.
    """

    parser = ArgumentParser()
    groups = {
        'cluster': parser.add_argument_group('cluster collectors', description=(
            'cluster collectors are run if the url parameter cluster=1 is set and '
            'skipped if the url parameter cluster=0 is set on a scrape url.'
        )),
        'node': parser.add_argument_group('node collectors', description=(
            'node collectors are run if the url parameter node=1 is set and '
            'skipped if the url parameter node=0 is set on a scrape url.'
        )),
    }

    for spec in COLLECTORS:
        groups[spec.scope].add_argument(
            f'--collector.{spec.name}', dest=f'collector_{spec.option}',
            action=BooleanOptionalAction, default=True,
            help=spec.description)

    scrapeflags = parser.add_argument_group('scrape collectors', description=(
        'metrics concerning the operation of the Prometheus PVE exporter itself.'
    ))
    scrapeflags.add_argument('--collector.pve-api-metrics', dest='api_metrics_enabled',
                              action=BooleanOptionalAction, default=False,
                              help='Exposes duration of PVE API calls')
    scrapeflags.add_argument('--collector.target-metrics', dest='target_metrics_enabled',
                              action=BooleanOptionalAction, default=False,
                              help='Exposes duration of scrapes by target')

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

    collectors = CollectorsOptions(**{
        spec.option: getattr(params, f'collector_{spec.option}')
        for spec in COLLECTORS
    })
    scrape_metrics.API_METRICS_ENABLED = params.api_metrics_enabled
    scrape_metrics.TARGET_METRICS_ENABLED = params.target_metrics_enabled

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
        'control_socket_disable': True,
    }

    if config.valid:
        start_http_server(config, gunicorn_options, collectors)
    else:
        parser.error(str(config))
