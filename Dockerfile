FROM alpine:3.21.3 as base

FROM base as build
RUN apk update && apk add --no-cache \
    build-base \
    ca-certificates \
    libffi-dev \
    py3-build \
    py3-pip \
    python3 \
    python3-dev \
    yaml-dev

ADD . /src/prometheus-pve-exporter
WORKDIR /src/prometheus-pve-exporter
RUN python3 -m pip wheel -w dist --no-binary "cffi" --no-binary "pyyaml" -r requirements.txt && \
    python3 -m build .

FROM base
RUN apk update && apk add --no-cache \
    ca-certificates \
    py3-pip \
    python3

COPY --from=build /src/prometheus-pve-exporter/dist /src/prometheus-pve-exporter/dist
RUN python3 -m venv /opt/prometheus-pve-exporter && \
    /opt/prometheus-pve-exporter/bin/pip install /src/prometheus-pve-exporter/dist/*.whl && \
    ln -s /opt/prometheus-pve-exporter/bin/pve_exporter /usr/bin/pve_exporter && \
    rm -rf /src/prometheus-pve-exporter /root/.cache

RUN addgroup -S -g 101 prometheus && \
    adduser -D -H -S -G prometheus -u 101 prometheus

USER prometheus
EXPOSE 9221

ENTRYPOINT [ "/opt/prometheus-pve-exporter/bin/pve_exporter" ]
