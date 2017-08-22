# Prometheus Proxmox VE Exporter

This is an exporter that exposes information gathered from Proxmox VE cluster
for use by the Prometheus monitoring system.

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

Visit http://localhost:9221/metrics?address=1.2.3.4 where 1.2.3.4 is the IP of the
Proxmox VE cluster to get metrics from. You can also specify a `module` parameter, to
choose which module to use from the config file.


## Authentication

Example `pve.yml`

```YAML
default:
    user: prometheus@pve
    password: sEcr3T!
    verify_ssl: false
```

The configuration is passed directly into [proxmoxer.ProxmoxAPI()](https://pypi.python.org/pypi/proxmoxer).


## Prometheus Configuration

The PVE exporter needs to be passed the address as a parameter, this can be
done with relabelling.

Example config:
```YAML
scrape_configs:
  - job_name: 'pve'
    target_groups:
      - targets:
        - 192.168.1.2  # Proxmox VE cluster.
    params:
      module: [default]
    relabel_configs:
      - source_labels: [__address__]
        regex: (.*?)(:80)?
        target_label: __param_address
        replacement: ${1}
      - source_labels: [__param_address]
        regex: (.*)
        target_label: instance
        replacement: ${1}
      - source_labels: []
        regex: .*
        target_label: __address__
        replacement: 127.0.0.1:9221  # PVE exporter.
```
