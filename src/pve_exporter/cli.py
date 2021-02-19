"""
Proxmox VE exporter for the Prometheus monitoring system.
"""

from argparse import ArgumentParser

import yaml
from pve_exporter.http import start_http_server
from pve_exporter.config import config_from_yaml
from pve_exporter.collector import CollectorsOptions

try:
    from argparse import BooleanOptionalAction
except ImportError:
    from argparse import Action
    # https://github.com/python/cpython/blob/master/Lib/argparse.py#L856
    # pylint: disable=all
    class BooleanOptionalAction(Action):
        def __init__(self,
                     option_strings,
                     dest,
                     default=None,
                     type=None,
                     choices=None,
                     required=False,
                     help=None,
                     metavar=None):

            _option_strings = []
            for option_string in option_strings:
                _option_strings.append(option_string)

                if option_string.startswith('--'):
                    option_string = '--no-' + option_string[2:]
                    _option_strings.append(option_string)

            if help is not None and default is not None:
                help += f" (default: {default})"

            super().__init__(
                option_strings=_option_strings,
                dest=dest,
                nargs=0,
                default=default,
                type=type,
                choices=choices,
                required=required,
                help=help,
                metavar=metavar)

        def __call__(self, parser, namespace, values, option_string=None):
            if option_string in self.option_strings:
                setattr(namespace, self.dest, not option_string.startswith('--no-'))

        def format_usage(self):
            return ' | '.join(self.option_strings)


def main():
    """
    Main entry point.
    """

    parser = ArgumentParser()
    parser.add_argument('--collector.status', dest='collector_status',
                        action=BooleanOptionalAction, default=True,
                        help='Exposes Node/VM/CT-Status')
    parser.add_argument('--collector.version', dest='collector_version',
                        action=BooleanOptionalAction, default=True,
                        help='Exposes PVE version info')
    parser.add_argument('--collector.node', dest='collector_node',
                        action=BooleanOptionalAction, default=True,
                        help='Exposes PVE node info')
    parser.add_argument('--collector.cluster', dest='collector_cluster',
                        action=BooleanOptionalAction, default=True,
                        help='Exposes PVE cluster info')
    parser.add_argument('--collector.resources', dest='collector_resources',
                        action=BooleanOptionalAction, default=True,
                        help='Exposes PVE resources info')
    parser.add_argument('--collector.config', dest='collector_config',
                        action=BooleanOptionalAction, default=True,
                        help='Exposes PVE onboot status')
    parser.add_argument('config', nargs='?', default='pve.yml',
                        help='Path to configuration file (pve.yml)')
    parser.add_argument('port', nargs='?', type=int, default='9221',
                        help='Port on which the exporter is listening (9221)')
    parser.add_argument('address', nargs='?', default='',
                        help='Address to which the exporter will bind')

    params = parser.parse_args()

    collectors = CollectorsOptions(
        status=params.collector_status,
        version=params.collector_version,
        node=params.collector_node,
        cluster=params.collector_cluster,
        resources=params.collector_resources,
        config=params.collector_config
    )

    # Load configuration.
    with open(params.config) as handle:
        config = config_from_yaml(yaml.safe_load(handle))

    if config.valid:
        start_http_server(config, params.port, params.address, collectors)
    else:
        parser.error(str(config))
