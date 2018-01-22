FROM python:alpine

RUN pip install --no-cache-dir prometheus-pve-exporter

CMD ["/usr/local/bin/pve_exporter", "/pve.yml", "9221"]
