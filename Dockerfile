FROM python:alpine

ENV VERSION 1.1.2

COPY entrypoint.sh /

RUN pip install --no-cache-dir prometheus-pve-exporter==${VERSION} && \
    mkdir -p /config/pve_exporter && \
    chown -R nobody:nobody /config && \
    chmod +x /entrypoint.sh

EXPOSE 9221
USER nobody

VOLUME /config

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["/usr/local/bin/pve_exporter", "/config/pve.yml", "9221" ]
