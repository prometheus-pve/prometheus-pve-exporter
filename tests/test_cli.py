"""
Tests for the command line interface.

The --collector.* flags are generated from the COLLECTORS table, so these
tests pin down the resulting flag set and make sure a flag still switches off
the collector it names.
"""

import pytest

from pve_exporter import cli
from pve_exporter.collector import COLLECTORS

EXPECTED_COLLECTOR_FLAGS = {
    '--collector.status',
    '--collector.version',
    '--collector.node',
    '--collector.cluster',
    '--collector.resources',
    '--collector.backup-info',
    '--collector.qdevice',
    '--collector.subscription',
    '--collector.config',
    '--collector.replication',
}


def _run(monkeypatch, *argv):
    """Run main() with a config from the environment, return the options."""
    captured = {}

    def fake_start_http_server(config, gunicorn_options, collectors):
        captured['config'] = config
        captured['gunicorn_options'] = gunicorn_options
        captured['collectors'] = collectors

    monkeypatch.setattr(cli, 'start_http_server', fake_start_http_server)
    monkeypatch.setenv('PVE_USER', 'root@pam')
    monkeypatch.setenv('PVE_PASSWORD', 'secret')
    monkeypatch.setattr('sys.argv', ['pve_exporter', *argv])

    cli.main()

    return captured['collectors']


def test_help_lists_every_collector_flag(monkeypatch, capsys):
    """The generated flags must match the ones the exporter has always had."""
    monkeypatch.setattr('sys.argv', ['pve_exporter', '--help'])

    with pytest.raises(SystemExit):
        cli.main()

    out = capsys.readouterr().out
    for flag in EXPECTED_COLLECTOR_FLAGS:
        assert flag in out, f'{flag} is missing from --help'
        assert flag.replace('--', '--no-', 1) in out


def test_collector_flags_are_exactly_the_expected_set():
    """Guards against a collector being added without a matching flag name."""
    assert {f'--collector.{spec.name}' for spec in COLLECTORS} == EXPECTED_COLLECTOR_FLAGS


def test_collectors_default_to_enabled(monkeypatch):
    """Every collector is on unless explicitly switched off."""
    collectors = _run(monkeypatch)

    assert all(getattr(collectors, spec.option) for spec in COLLECTORS)


@pytest.mark.parametrize('spec', COLLECTORS, ids=lambda spec: spec.name)
def test_flag_disables_only_its_own_collector(monkeypatch, spec):
    """A --no-collector.<name> flag must not affect any other collector."""
    collectors = _run(monkeypatch, f'--no-collector.{spec.name}')

    assert getattr(collectors, spec.option) is False
    for other in COLLECTORS:
        if other.option != spec.option:
            assert getattr(collectors, other.option) is True
