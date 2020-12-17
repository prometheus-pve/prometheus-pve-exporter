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

Prometheus PVE Exporter will now be reachable at http://localhost:9090/.

Usage
-----

::

    usage: pve_exporter [-h] [config] [port] [address]

    positional arguments:
      config      Path to configuration file (pve.yml)
      port        Port on which the exporter is listening (9221)
      address     Address to which the exporter will bind

    optional arguments:
      -h, --help  show this help message and exit

Use `::` for the `address` argument in order to bind to both IPv6 and IPv4
sockets on dual stacked machines.

Visit http://localhost:9221/pve?target=1.2.3.4 where 1.2.3.4 is the IP
of the Proxmox VE node to get metrics from. Specify the ``module``
request parameter, to choose which module to use from the config file.

The ``target`` request parameter defaults to ``localhost``. Hence if
``pve_exporter`` is deployed directly on the proxmox host, ``target``
can be omitted.

See the wiki_  for more examples and docs.

Authentication
--------------

Example ``pve.yml`` for password authentication:

.. code:: yaml

    default:
        user: prometheus@pve
        password: sEcr3T!

Example ``pve.yml`` for `token authentication`_:

.. code:: yaml

   default:
       user: prometheus@pve
       token_name: "..."
       token_value: "..."

The configuration is passed directly into `proxmoxer.ProxmoxAPI()`_.

Note: When operating PVE with self-signed certificates, then it is necessary to
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


.. |Build Status| image:: https://travis-ci.com/prometheus-pve/prometheus-pve-exporter.svg?branch=master
   :target: https://travis-ci.com/prometheus-pve/prometheus-pve-exporter
.. |Package Version| image:: https://img.shields.io/pypi/v/prometheus-pve-exporter.svg
   :target: https://pypi.python.org/pypi/prometheus-pve-exporter
.. _wiki: https://github.com/prometheus-pve/prometheus-pve-exporter/wiki
.. _`token authentication`: https://pve.proxmox.com/wiki/User_Management#pveum_tokens
.. _`proxmoxer.ProxmoxAPI()`: https://pypi.python.org/pypi/proxmoxer
.. _`SE answer`: https://askubuntu.com/a/1007236
.. _`supports Let's Encrypt`: https://pve.proxmox.com/pve-docs/pve-admin-guide.html#sysadmin_certificate_management
.. _`Proxmox via Prometheus by Pietro Saccardi`: https://grafana.com/dashboards/10347
