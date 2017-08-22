import os
from setuptools import setup

setup(
    name = "pve_exporter",
    version = "0.0.1",
    author = "Lorenz Schori",
    author_email = "lo@znerol.ch",
    description = ("Proxmox VE exporter for the Prometheus monitoring system."),
    long_description = ("See https://github.com/znerol/prometheus-pve-exporter/blob/master/README.md for documentation."),
    license = "Apache Software License 2.0",
    keywords = "prometheus exporter network monitoring proxmox",
    url = "https://github.com/znerol/prometheus-pve-exporter",
    scripts = ["scripts/pve_exporter"],
    packages=['pve_exporter'],
    test_suite="tests",
    install_requires=["prometheus_client>=0.0.11", "pyyaml", "proxmoxer", "requests"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
