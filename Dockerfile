FROM alpine:3.19.0
RUN apk update && apk upgrade

RUN apk add --no-cache \
    ca-certificates \
    py3-pip \
    python3

ADD . /src/prometheus-pve-exporter
RUN python3 -m venv /opt/prometheus-pve-exporter && \
    /opt/prometheus-pve-exporter/bin/pip install -r /src/prometheus-pve-exporter/requirements.txt && \
    /opt/prometheus-pve-exporter/bin/pip install /src/prometheus-pve-exporter && \
    ln -s /opt/prometheus-pve-exporter/bin/pve_exporter /usr/bin/pve_exporter && \
    rm -rf /src/prometheus-pve-exporter /root/.cache

RUN addgroup -S -g 101 prometheus && \
    adduser -D -H -S -G prometheus -u 101 prometheus

USER prometheus
EXPOSE 9221

ENTRYPOINT [ "/opt/prometheus-pve-exporter/bin/pve_exporter" ]
