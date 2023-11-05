ARG alpine_version=3.18.4

FROM alpine:${alpine_version} as base
RUN apk update && apk upgrade

RUN apk add --no-cache \
    ca-certificates \
    py3-gunicorn \
    py3-paramiko \
    py3-pip \
    py3-prometheus-client \
    py3-requests \
    py3-werkzeug \
    py3-wheel \
    py3-yaml \
    python3

FROM base as builder

ARG proxmoxer_version=2.0.1
ENV proxmoxer_version=${proxmoxer_version}

ADD . /src
WORKDIR /opt
RUN pip3 wheel --no-deps /src proxmoxer==${proxmoxer_version}

FROM base as runtime

COPY --from=builder /opt /opt

RUN pip3 install --no-cache-dir --no-index /opt/*py3-none-any.whl && \
    rm /opt/*py3-none-any.whl && \
    addgroup -S -g 101 prometheus && \
    adduser -D -H -S -G prometheus -u 101 prometheus

USER prometheus

EXPOSE 9221

ENTRYPOINT [ "/usr/bin/pve_exporter" ]
