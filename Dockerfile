FROM alpine:3.18.5 as base
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

RUN apk add --no-cache \
    alpine-sdk

RUN abuild-keygen -a -n -q && cp /root/.abuild/*.pub /etc/apk/keys/

ADD alpine/py3-openssh-wrapper /src/alpine/py3-openssh-wrapper
WORKDIR /src/alpine/py3-openssh-wrapper
RUN abuild -r -F && apk add --no-cache /root/packages/alpine/*/py3-openssh-wrapper-*.apk

ADD alpine/py3-proxmoxer /src/alpine/py3-proxmoxer
WORKDIR /src/alpine/py3-proxmoxer
RUN abuild -r -F && apk add --no-cache /root/packages/alpine/*/py3-proxmoxer-*.apk

ADD . /src/alpine/pve-exporter
WORKDIR /src/alpine/pve-exporter
RUN abuild -r -F && apk add --no-cache /root/packages/alpine/*/pve-exporter-*.apk

FROM base as runtime

COPY --from=builder /root/.abuild/*.pub /etc/apk/keys/
COPY --from=builder /root/packages/alpine/ /root/packages/alpine/

RUN apk add --no-cache /root/packages/alpine/*/*.apk && \
    rm -rf /root/packages && \
    addgroup -S -g 101 prometheus && \
    adduser -D -H -S -G prometheus -u 101 prometheus

USER prometheus

EXPOSE 9221

ENTRYPOINT [ "/usr/bin/pve_exporter" ]
