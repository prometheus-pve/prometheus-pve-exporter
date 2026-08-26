"""
Characterization tests for the PVE collectors.

These render the full exposition output for a recorded API response set and
compare it against a golden file. They exist so that refactorings can be
proven to leave the emitted metrics untouched: any diff against a golden file
is either a bug or a deliberate, reviewed behaviour change.
"""

import copy

import pytest

from pve_exporter import collector as collector_module
from pve_exporter.collector import CollectorsOptions, collect_pve

from conftest import load_fixture

ALL_COLLECTORS = CollectorsOptions(
    status=True,
    version=True,
    subscription=True,
    node=True,
    cluster=True,
    resources=True,
    backup_info=True,
    config=True,
    replication=True,
    qdevice=True,
)


@pytest.fixture(name='render')
def render_fixture(monkeypatch):
    """Render collect_pve() against a fixture instead of a real cluster."""

    def render(fixture, cluster=True, node=True, options=ALL_COLLECTORS):
        monkeypatch.setattr(collector_module, 'ProxmoxAPI', load_fixture(fixture))
        return collect_pve({}, 'pve.example.com', cluster, node, options).decode('utf-8')

    return render


@pytest.mark.parametrize('fixture', ['cluster', 'standalone'])
def test_all_collectors(render, snapshot, fixture):
    """Every collector enabled, for both a clustered and a standalone host."""
    snapshot(fixture, render(fixture))


@pytest.mark.parametrize('fixture', ['cluster', 'standalone'])
def test_cluster_collectors_only(render, snapshot, fixture):
    """Node collectors skipped, as with the url parameter node=0."""
    snapshot(f'{fixture}-cluster-only', render(fixture, node=False))


@pytest.mark.parametrize('fixture', ['cluster', 'standalone'])
def test_node_collectors_only(render, snapshot, fixture):
    """Cluster collectors skipped, as with the url parameter cluster=0."""
    snapshot(f'{fixture}-node-only', render(fixture, cluster=False))


def test_qdevice_absent_yields_no_metrics(render):
    """A cluster without a qdevice must not emit qdevice metrics.

    The PVE API answers /cluster/config/qdevice with an error in that case,
    which the fixture reproduces by not recording the path at all.
    """
    options = ALL_COLLECTORS._replace(
        status=False, version=False, node=False, cluster=False,
        resources=False, backup_info=False,
    )
    output = render('standalone', node=False, options=options)

    assert 'pve_qdevice_up' not in output
    assert 'pve_qdevice_info' not in output


def test_storage_content_label_is_sorted(render):
    """Proxmox returns the content list in random order.

    It is sorted before being used as a label value, otherwise every scrape
    would produce a different label set for the same storage.
    """
    output = render('cluster', node=False)

    assert 'content="backup,iso,vztmpl"' in output
    assert 'content="images,rootdir"' in output


def test_cluster_info_does_not_mutate_the_api_response():
    """Collectors must treat API responses as read-only.

    Responses are shared between collectors within one scrape, so a collector
    that edits what it got back would corrupt the ones that run after it.
    """
    from prometheus_client import CollectorRegistry, generate_latest
    from pve_exporter.collector.cluster import ClusterInfoCollector

    status = [{'type': 'cluster', 'id': 'cluster', 'name': 'pvec',
               'nodes': 2, 'quorate': 1, 'version': 2}]
    before = copy.deepcopy(status)

    class SharedResponseAPI:
        """Hands out the very same response object on every call."""

        def __init__(self, path=()):
            self._path = path

        def __getattr__(self, name):
            return SharedResponseAPI(self._path + (name,))

        def get(self):
            assert self._path == ('cluster', 'status')
            return status

    registry = CollectorRegistry()
    registry.register(ClusterInfoCollector(SharedResponseAPI()))

    first = generate_latest(registry)
    assert status == before, 'the API response was modified in place'
    assert generate_latest(registry) == first
