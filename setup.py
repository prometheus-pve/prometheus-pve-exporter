from setuptools import find_packages
from setuptools import setup

setup(
    name="prometheus-pve-exporter",
    version="2.1.0",
    author="Lorenz Schori",
    author_email="lo@znerol.ch",
    description=("Proxmox VE exporter for the Prometheus monitoring system."),
    long_description=open('README.rst').read(),
    license="Apache Software License 2.0",
    keywords="prometheus exporter network monitoring proxmox",
    url="https://github.com/prometheus-pve/prometheus-pve-exporter",
    package_dir={"": "src"},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'pve_exporter=pve_exporter.cli:main',
        ],
    },
    test_suite="tests",
    python_requires=">=3.4",
    install_requires=[
        "prometheus_client>=0.0.11",
        "proxmoxer",
        "pyyaml",
        "requests",
        'Werkzeug',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
