Prometheus Proxmox VE Exporter
==============================

|Build Status| |Package Version|

This is an exporter that exposes information gathered from Proxmox VE
node for use by the Prometheus monitoring system.

Installation
------------

Note: Python 2 is not supported anymore as of version 2.0.0. Instead use Python 3.6 or better.

Using pip:
==========

.. code:: shell

    python3 -m pip install prometheus-pve-exporter

Using docker:
=============

.. code:: shell

   docker pull prompve/prometheus-pve-exporter

Example: Display usage message:

.. code:: shell

   docker run -it --rm prompve/prometheus-pve-exporter --help


Example: Run the image with a mounted configuration file and published port:

.. code:: shell

   docker run --name prometheus-pve-exporter -d -p 127.0.0.1:9221:9221 -v /path/to/pve.yml:/etc/pve.yml prompve/prometheus-pve-exporter

Prometheus PVE Exporter will now be reachable at http://localhost:9221/.

Usage
-----

::

    usage: pve_exporter [-h] [--collector.status] [--collector.version]
                        [--collector.node] [--collector.cluster]
                        [--collector.resources] [--collector.config]
                        [config] [port] [address]

    positional arguments:
      config                Path to configuration file (pve.yml)
      port                  Port on which the exporter is listening (9221)
      address               Address to which the exporter will bind

    optional arguments:
      -h, --help            show this help message and exit
      --collector.status, --no-collector.status
                            Exposes Node/VM/CT-Status (default: True)
      --collector.version, --no-collector.version
                            Exposes PVE version info (default: True)
      --collector.node, --no-collector.node
                            Exposes PVE node info (default: True)
      --collector.cluster, --no-collector.cluster
                            Exposes PVE cluster info (default: True)
      --collector.resources, --no-collector.resources
                            Exposes PVE resources info (default: True)
      --collector.config, --no-collector.config
                            Exposes PVE onboot status (default: True)


Use `::` for the `address` argument in order to bind to both IPv6 and IPv4
sockets on dual stacked machines.

Visit http://localhost:9221/pve?target=1.2.3.4 where 1.2.3.4 is the IP
of the Proxmox VE node to get metrics from. Specify the ``module``
request parameter, to choose which module to use from the config file.

The ``target`` request parameter defaults to ``localhost``. Hence if
``pve_exporter`` is deployed directly on the proxmox host, ``target``
can be omitted.

Use the `--collector.X` / `--no-collector.X` flags to enable disable selected
collectors.

Note that that the config collector results in one API call per guest VM/CT.
It is therefore recommended to disable this collector using the
`--no-collector.config` flag on big deployments.

See the wiki_  for more examples and docs.

Authentication
--------------

**Using pve.yml config file**

Example ``pve.yml`` for password authentication:

.. code:: yaml

    default:
        user: prometheus@pve
        password: sEcr3T!
        # Optional: set to false to skip SSL/TLS verification
        verify_ssl: true

Example ``pve.yml`` for `token authentication`_:

.. code:: yaml

   default:
       user: prometheus@pve
       token_name: "..."
       token_value: "..."

**Using environment variables:**

If the ``PVE_USER`` environment variable exists, then configuration is taken from
the environment instead of from the ``pve.yml`` config file. The following
environment variables are respected:

* ``PVE_USER``: user name

Required for password authentication:

* ``PVE_PASSWORD``: user password

Required for `token authentication`_:

* ``PVE_TOKEN_NAME``: token name
* ``PVE_TOKEN_VALUE``: token value

Optional:

* ``PVE_VERIFY_SSL``: Either ``true`` or ``false``, whether or not to verify PVE tls
  certificate. Defaults to ``true``.
* ``PVE_MODULE``: Name of the configuration module. Defaults to ``default``.

The configuration is passed directly into `proxmoxer.ProxmoxAPI()`_.

**Note on verify_ssl and certificate trust store:**

When operating PVE with self-signed certificates, then it is necessary to
either import the certificate into the local trust store (see this `SE answer`_
for Debian/Ubuntu) or add ``verify_ssl: false`` to the config dict as a sibling
to the credentials. Note that PVE `supports Let's Encrypt`_ out ouf the box. In
many cases setting up trusted certificates is the better option than operating
with self-signed certs.

Proxmox VE Configuration
------------------------

For security reasons it is essential to add a user with read-only access
(PVEAuditor role) for the purpose of metrics collection.

Prometheus Configuration
------------------------

The PVE exporter can be deployed either directly on a Proxmox VE node or
onto a separate machine.

Example config for PVE exporter running on PVE node:

.. code:: yaml

    scrape_configs:
      - job_name: 'pve'
        static_configs:
          - targets:
            - 192.168.1.2:9221  # Proxmox VE node with PVE exporter.
            - 192.168.1.3:9221  # Proxmox VE node with PVE exporter.
        metrics_path: /pve
        params:
          module: [default]

Example config for PVE exporter running on Prometheus host:

.. code:: yaml

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

Grafana Dashboards
------------------

* `Proxmox via Prometheus by Pietro Saccardi`_

.. |Build Status| image:: https://github.com/prometheus-pve/prometheus-pve-exporter/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/prometheus-pve/prometheus-pve-exporter/actions/workflows/ci.yml
.. |Package Version| image:: https://img.shields.io/pypi/v/prometheus-pve-exporter.svg
   :target: https://pypi.python.org/pypi/prometheus-pve-exporter
.. _wiki: https://github.com/prometheus-pve/prometheus-pve-exporter/wiki
.. _`token authentication`: https://pve.proxmox.com/wiki/User_Management#pveum_tokens
.. _`proxmoxer.ProxmoxAPI()`: https://pypi.python.org/pypi/proxmoxer
.. _`SE answer`: https://askubuntu.com/a/1007236
.. _`supports Let's Encrypt`: https://pve.proxmox.com/pve-docs/pve-admin-guide.html#sysadmin_certificate_management
.. _`Proxmox via Prometheus by Pietro Saccardi`: https://grafana.com/dashboards/10347
