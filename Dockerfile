ARG alpine_version=3.13.3

FROM alpine:${alpine_version} as base
RUN apk update && apk upgrade

RUN apk add --no-cache \
    ca-certificates \
    py3-paramiko \
    py3-pip \
    py3-prometheus-client \
    py3-requests \
    py3-werkzeug \
    py3-wheel \
    py3-yaml \
    python3 \
    tini

FROM base as builder

ARG proxmoxer_version=1.1.1
ENV proxmoxer_version=${proxmoxer_version}

ADD . /src
WORKDIR /opt
RUN pip3 wheel --no-deps /src proxmoxer==${proxmoxer_version}

FROM base as runtime

COPY --from=builder /opt /opt

RUN pip3 install --no-cache-dir --no-index /opt/*py3-none-any.whl && \
    rm /opt/*py3-none-any.whl

USER nobody

EXPOSE 9221

ENTRYPOINT [ "/sbin/tini", "--", "/usr/bin/pve_exporter" ]

CMD [ "/etc/pve.yml" ]
