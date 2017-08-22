# Prometheus Proxmox VE Exporter

This is an exporter that exposes information gathered from Proxmox VE node for
use by the Prometheus monitoring system.

## Installation

```Shell
git clone https://github.com/znerol/prometheus-pve-exporter
cd prometheus-pve-exporter
pip install .
```

## Usage

```
pve_exporter [config_file] [port]
```

`config_file` contains authentication parameters.
`config_file` defaults to `pve.yml`. `port` defaults to 9221.

Visit http://localhost:9221/metrics?address=1.2.3.4 where 1.2.3.4 is the IP of
the Proxmox VE node to get metrics from. You can also specify a `module`
parameter, to choose which module to use from the config file.


## Authentication

Example `pve.yml`

```YAML
default:
    user: prometheus@pve
    password: sEcr3T!
    verify_ssl: false
```

The configuration is passed directly into [proxmoxer.ProxmoxAPI()](https://pypi.python.org/pypi/proxmoxer).


## Proxmox VE Configuration

For security reasons it is highly recommended to add a user with read-only
access (PVEAuditor role) for the purpose of metrics collection.


## Prometheus Configuration

The PVE exporter can be deployed either directly on a Proxmox VE node or onto a
separate machine.

Example config for PVE exporter running on PVE node:
```YAML
scrape_configs:
  - job_name: 'pve'
    static_configs:
      - targets:
        - 192.168.1.2:9221  # Proxmox VE node with PVE exporter.
        - 192.168.1.3:9221  # Proxmox VE node with PVE exporter.
    metrics_path: /pve
    params:
      module: [default]
```

Example config for PVE exporter running on Prometheus host:
```YAML
scrape_configs:
  - job_name: 'pve'
    static_configs:
      - targets:
        - 192.168.1.2  # Proxmox VE node.
        - 192.168.1.3  # Proxmox VE node.
    metrics_path: /pve
    params:
      module: [default]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9221  # PVE exporter.
```
