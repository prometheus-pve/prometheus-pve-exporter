FROM        python:alpine

RUN         pip install --no-cache-dir prometheus-pve-exporter

EXPOSE      9221
USER        nobody

ENTRYPOINT  [ "/usr/local/bin/pve_exporter" ]
CMD         [ "/pve.yml", "9221" ]
