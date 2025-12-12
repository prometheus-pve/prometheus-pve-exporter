"""
Proxmox VE exporter for the Prometheus monitoring system.
"""

import os
import pathlib
from argparse import ArgumentParser, BooleanOptionalAction

import yaml

from pve_exporter.collector import CollectorsOptions
from pve_exporter.config import config_from_env, config_from_yaml
from pve_exporter.http import start_http_server


## Settings helper
def env_bool(name: str):
    v = os.getenv(name)
    if v is None:
        return None
    return v.lower() in ("1", "true", "yes", "on")


def resolve_collector_flag(cli_value, env_name, default: bool) -> bool:
    # 1) CLI has highest priority if specified
    if cli_value is not None:
        return cli_value

    # 2) Environment variable if set
    env_val = env_bool(env_name)
    if env_val is not None:
        return env_val

    # 3) Hardcoded default
    return default


def main():
    """
    Main entry point.
    """

    parser = ArgumentParser()
    clusterflags = parser.add_argument_group(
        "cluster collectors",
        description=(
            "cluster collectors are run if the url parameter cluster=1 is set and "
            "skipped if the url parameter cluster=0 is set on a scrape url."
        ),
    )
    clusterflags.add_argument(
        "--collector.status",
        dest="collector_status",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes Node/VM/CT-Status",
    )
    clusterflags.add_argument(
        "--collector.version",
        dest="collector_version",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE version info",
    )
    clusterflags.add_argument(
        "--collector.node",
        dest="collector_node",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE node info",
    )
    clusterflags.add_argument(
        "--collector.cluster",
        dest="collector_cluster",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE cluster info",
    )
    clusterflags.add_argument(
        "--collector.resources",
        dest="collector_resources",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE resources info",
    )

    nodeflags = parser.add_argument_group(
        "node collectors",
        description=(
            "node collectors are run if the url parameter node=1 is set and "
            "skipped if the url parameter node=0 is set on a scrape url."
        ),
    )
    nodeflags.add_argument(
        "--collector.config",
        dest="collector_config",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE onboot status",
    )

    nodeflags.add_argument(
        "--collector.replication",
        dest="collector_replication",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE replication info",
    )
    nodeflags.add_argument(
        "--collector.subscription",
        dest="collector_subscription",
        action=BooleanOptionalAction,
        default=None,
        help="Exposes PVE subscription info",
    )

    parser.add_argument(
        "--config.file",
        type=pathlib.Path,
        dest="config_file",
        default="/etc/prometheus/pve.yml",
        help="Path to config file (/etc/prometheus/pve.yml)",
    )

    parser.add_argument(
        "--web.listen-address",
        dest="web_listen_address",
        default="[::]:9221",
        help=("Address on which to expose metrics and web server. ([::]:9221)"),
    )
    parser.add_argument(
        "--server.keyfile", dest="server_keyfile", help="SSL key for server"
    )
    parser.add_argument(
        "--server.certfile", dest="server_certfile", help="SSL certificate for server"
    )

    params = parser.parse_args()

    collectors = CollectorsOptions(
        status=resolve_collector_flag(
            params.collector_status, "PVE_COLLECTOR_STATUS", True
        ),
        version=resolve_collector_flag(
            params.collector_version, "PVE_COLLECTOR_VERSION", True
        ),
        subscription=resolve_collector_flag(
            params.collector_subscription, "PVE_COLLECTOR_SUBSCRIPTION", True
        ),
        node=resolve_collector_flag(params.collector_node, "PVE_COLLECTOR_NODE", True),
        cluster=resolve_collector_flag(
            params.collector_cluster, "PVE_COLLECTOR_CLUSTER", True
        ),
        resources=resolve_collector_flag(
            params.collector_resources, "PVE_COLLECTOR_RESOURCES", True
        ),
        config=resolve_collector_flag(
            params.collector_config, "PVE_COLLECTOR_CONFIG", True
        ),
        replication=resolve_collector_flag(
            params.collector_replication, "PVE_COLLECTOR_REPLICATION", True
        ),
    )

    # Load configuration.
    if "PVE_USER" in os.environ:
        config = config_from_env(os.environ)
    else:
        with open(params.config_file, encoding="utf-8") as handle:
            config = config_from_yaml(yaml.safe_load(handle))

    gunicorn_options = {
        "bind": f"{params.web_listen_address}",
        "threads": 2,
        "keyfile": params.server_keyfile,
        "certfile": params.server_certfile,
    }

    if config.valid:
        start_http_server(config, gunicorn_options, collectors)
    else:
        parser.error(str(config))
