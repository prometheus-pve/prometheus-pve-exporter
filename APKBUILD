pkgname=pve-exporter
pkgver="3.1.0"
pkgrel=0
pkgdesc="Proxmox VE exporter for the Prometheus monitoring system."
url="https://github.com/prometheus-pve/prometheus-pve-exporter"
arch="noarch"
license="Apache Software License 2.0"
depends="python3 py3-proxmoxer"
subpackages="$pkgname-pyc"
options="!check" # no tests

srcdir="${startdir}/abuild/src"
pkgbasedir="${startdir}/abuild/pkg"
tmpdir="${startdir}/abuild/tmp"

unpack() {
	ln -v -s "$startdir" "$builddir"
}

build() {
	cd "$builddir"
	python3 setup.py build
}

package() {
	cd "$builddir"
	python3 setup.py install --skip-build --root="$pkgdir"
}
