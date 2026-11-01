"""
Test fixtures for the Proxmox VE exporter.

The collectors talk to a real PVE cluster through proxmoxer. To make them
testable, :class:`FakeProxmoxAPI` replays recorded API responses from a JSON
fixture instead. It reproduces the small part of the proxmoxer surface the
collectors actually use:

* attribute chaining, e.g. ``pve.cluster.status``
* call syntax appending path segments, e.g. ``pve.nodes('pve1').qemu(100)``
  and ``pve.cluster('backup-info/not-backed-up')``
* ``.get()`` with optional server side filters, e.g. ``.get(type='vm')``
"""

import copy
import json
import os
import pathlib
import time

import pytest
from proxmoxer import ResourceException

FIXTURE_DIR = pathlib.Path(__file__).parent / 'fixtures'
GOLDEN_DIR = pathlib.Path(__file__).parent / 'golden'


def pytest_addoption(parser):
    """Register --snapshot-update to rewrite the golden files in place."""
    parser.addoption(
        '--snapshot-update',
        action='store_true',
        default=False,
        help='Rewrite the golden exposition files instead of comparing against them.',
    )


@pytest.fixture(autouse=True, scope='session')
def _utc_timezone():
    """Pin the process timezone.

    SubscriptionCollector turns the subscription due date into a unix
    timestamp using local time, so the rendered metrics would otherwise
    differ depending on where the tests run.
    """
    previous = os.environ.get('TZ')
    os.environ['TZ'] = 'UTC'
    time.tzset()
    yield
    if previous is None:
        del os.environ['TZ']
    else:
        os.environ['TZ'] = previous
    time.tzset()


def _matches_type(entry, wanted):
    """Reproduce the server side ``type`` filter of /cluster/resources.

    The PVE API treats ``type=vm`` as "any guest", i.e. both qemu and lxc.
    Every other value matches the resource type verbatim.
    """
    if wanted == 'vm':
        return entry['type'] in ('qemu', 'lxc')
    return entry['type'] == wanted


class FakeProxmoxAPI:
    """Replays a recorded PVE API response set."""

    def __init__(self, responses, path=()):
        self._responses = responses
        self._path = path

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return FakeProxmoxAPI(self._responses, self._path + (name,))

    def __call__(self, *args):
        path = self._path
        for arg in args:
            path += tuple(str(arg).strip('/').split('/'))
        return FakeProxmoxAPI(self._responses, path)

    def get(self, **params):
        """Return a deep copy of the recorded response for the current path.

        A copy is returned because every real API call yields a fresh
        response, and collectors must not be able to affect each other by
        mutating what they got back.
        """
        path = '/'.join(self._path)
        if path not in self._responses:
            raise ResourceException(500, 'Internal Server Error', f'no such path: {path}')

        response = copy.deepcopy(self._responses[path])

        if 'type' in params:
            response = [entry for entry in response if _matches_type(entry, params['type'])]

        return response


def load_fixture(name):
    """Return a FakeProxmoxAPI factory for the named fixture file."""
    responses = json.loads((FIXTURE_DIR / f'{name}.json').read_text(encoding='utf-8'))
    responses.pop('_description', None)

    def factory(*_args, **_kwargs):
        return FakeProxmoxAPI(responses)

    return factory


@pytest.fixture(name='snapshot')
def snapshot_fixture(request):
    """Compare rendered exposition output against a golden file."""
    update = request.config.getoption('--snapshot-update')

    def compare(name, actual):
        path = GOLDEN_DIR / f'{name}.txt'
        if update or not path.exists():
            path.write_text(actual, encoding='utf-8')
            return
        expected = path.read_text(encoding='utf-8')
        assert actual == expected, (
            f'rendered metrics differ from {path}. '
            'Re-run with --snapshot-update if the change is intended.'
        )

    return compare
