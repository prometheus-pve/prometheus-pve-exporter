#!/bin/bash

set -ex

TAG="${1:-SNAPSHOT}"

set -u

cd "$(dirname "$0")"

pip3 install pyinstaller
pip3 install -e .

pyinstaller pve.spec

(cd dist/ && tar -czf pve_exporter-"$TAG"-linux-i686.tgz pve_exporter/)
