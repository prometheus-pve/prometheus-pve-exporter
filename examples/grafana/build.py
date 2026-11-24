#!/usr/bin/env python3
"""Build a portable native-panel dashboard for prometheus-pve-exporter."""
import json
from pathlib import Path

DS = {'type': 'prometheus', 'uid': '${datasource}'}
S = 'job="$job",instance="$instance"'
MATCH = 'job,instance'
ENTITY = 'job,instance,id'
HEALTH = f'(up{{{S}}} == 1) and on({MATCH}) (time() - timestamp(up{{{S}}}) < $freshness)'


def metric(name, extra=''):
    return f'{name}{{{S}' + (',' + extra if extra else '') + '}'


def node(name):
    return metric(name, 'id=~"node/${node:regex}"')


GI = metric('pve_guest_info', 'node=~"${node:regex}",template!="1"')
SI = metric('pve_storage_info', 'node=~"${node:regex}",storage=~"${storage:regex}"')


def guest(name):
    return f'{metric(name)} * on({ENTITY}) group_left(name,type,node) {GI}'


def storage(name):
    value = metric(name, 'id=~"storage/.+"')
    return f'{value} * on({ENTITY}) group_left(storage,node) {SI}'


panels = []


def panel(title, kind, x, y, w, h, queries=(), unit='short', legends=(), description=''):
    p = {'id': len(panels) + 1, 'title': title, 'type': kind,
         'gridPos': {'x': x, 'y': y, 'w': w, 'h': h}, 'datasource': DS,
         'description': description, 'fieldConfig': {'defaults': {
             'unit': unit, 'noValue': 'UNKNOWN', 'color': {'mode': 'palette-classic'},
             'thresholds': {'mode': 'absolute', 'steps': [{'color': 'blue', 'value': None}]},
             'mappings': []}, 'overrides': []}, 'options': {}}
    if queries:
        p['targets'] = [{'refId': chr(65+i), 'datasource': DS,
                         'expr': f'({q}) and on({MATCH}) ({HEALTH})',
                         'legendFormat': legends[i] if legends else title,
                         'range': kind == 'timeseries', 'instant': kind != 'timeseries',
                         'editorMode': 'code'} for i, q in enumerate(queries)]
    if kind == 'timeseries':
        p['fieldConfig']['defaults'].update(min=0, custom={
            'drawStyle': 'line', 'lineInterpolation': 'linear', 'lineWidth': 2,
            'fillOpacity': 10, 'showPoints': 'never', 'spanNulls': False,
            'axisCenteredZero': False, 'stacking': {'mode': 'none', 'group': 'A'}})
        p['options'] = {'legend': {'showLegend': True, 'displayMode': 'table',
                                   'placement': 'bottom', 'calcs': ['lastNotNull', 'max']},
                        'tooltip': {'mode': 'multi', 'sort': 'desc'}}
    if kind in ('stat', 'gauge', 'bargauge'):
        p['options'] = {'reduceOptions': {'calcs': ['lastNotNull'], 'fields': '', 'values': False},
                        'orientation': 'auto'}
    if kind == 'stat':
        p['options'].update(colorMode='value', graphMode='none', textMode='value_and_name')
    if kind == 'bargauge':
        p['options'].update(displayMode='gradient', orientation='horizontal', showUnfilled=True)
    if unit == 'percentunit':
        p['fieldConfig']['defaults'].update(min=0, max=1, decimals=1,
            thresholds={'mode': 'absolute', 'steps': [{'color': 'green', 'value': None},
                        {'color': 'orange', 'value': .75}, {'color': 'red', 'value': .9}]})
        if kind != 'timeseries':
            p['fieldConfig']['defaults']['color'] = {'mode': 'thresholds'}
    panels.append(p)
    return p


def row(title, y):
    p = panel(title, 'row', 0, y, 24, 1)
    p.update(collapsed=False, panels=[])


p = panel('Proxmox VE / Infrastructure', 'text', 0, 0, 24, 3)
p['options'] = {'mode': 'markdown', 'content':
    'Node capacity, QEMU and LXC guests, storage, and I/O. Select one cluster scrape target; '
    'then select nodes and storage pools. **UNKNOWN / gaps mean unavailable data.**'}
p = panel('Collection', 'stat', 0, 3, 4, 4, [f'up{{{S}}}'])
p['targets'][0]['expr'] = f'up{{{S}}} and on({MATCH}) (time() - timestamp(up{{{S}}}) < $freshness)'
p['fieldConfig']['defaults']['mappings'] = [{'type': 'value', 'options': {
    '1': {'text': 'UP', 'color': 'green'}, '0': {'text': 'FAILED', 'color': 'red'}}}]
p['description'] = 'Prometheus scrape success, not complete collector coverage or guest health. Missing or old samples show UNKNOWN.'
panel('Node uptime', 'stat', 4, 3, 4, 4, [node('pve_uptime_seconds')], 's', ['{{id}}'])
panel('Running guests', 'stat', 8, 3, 4, 4, [f'sum by({MATCH}) ({guest("pve_up")})'],
      description='Running QEMU and LXC guests, excluding templates. No guests yields UNKNOWN, not an invented zero.')
panel('Logical CPUs', 'stat', 12, 3, 4, 4, [node('pve_cpu_usage_limit')], legends=['{{id}}'])
panel('Configured guest RAM', 'stat', 16, 3, 4, 4,
      [f'sum by({MATCH}) ({guest("pve_memory_size_bytes")})'], 'bytes',
      description='Total configured RAM for selected non-template guests, including stopped guests.')
panel('Node sample age', 'stat', 20, 3, 4, 4,
      [f'time() - timestamp({node("pve_node_info")})'], 's', ['{{id}}'],
      'Prometheus sample age, not the age of Proxmox internal measurements.')
panel('Host CPU', 'gauge', 0, 7, 8, 7, [node('pve_cpu_usage_ratio')], 'percentunit', ['{{id}}'],
      'Already normalized by Proxmox; do not divide by CPU count again.')
panel('Host memory', 'gauge', 8, 7, 8, 7,
      [f'{node("pve_memory_usage_bytes")} / ({node("pve_memory_size_bytes")} > 0)'],
      'percentunit', ['{{id}}'], 'Proxmox-reported usage, not Linux available memory.')
panel('Storage utilization', 'bargauge', 16, 7, 8, 7,
      [f'{storage("pve_disk_usage_bytes")} / ({storage("pve_disk_size_bytes")} > 0)'],
      'percentunit', ['{{node}} / {{storage}}'],
      'Capacity per storage entry. Pools can share physical disks; capacity is not backup verification.')
row('Host capacity', 14)
panel('CPU utilization over time', 'timeseries', 0, 15, 12, 7,
      [node('pve_cpu_usage_ratio')], 'percentunit', ['{{id}}'])
panel('Host memory used / total', 'timeseries', 12, 15, 12, 7,
      [node('pve_memory_usage_bytes'), node('pve_memory_size_bytes')], 'bytes',
      ['{{id}} used', '{{id}} total'])
row('Guests / QEMU and LXC', 22)
panel('Guest CPU utilization', 'timeseries', 0, 23, 12, 8,
      [guest('pve_cpu_usage_ratio')], 'percentunit', ['{{name}} / {{id}}'],
      'Utilization relative to configured vCPU capacity, as reported by Proxmox.')
panel('Guest memory / hypervisor view', 'timeseries', 12, 23, 12, 8,
      [f'{guest("pve_memory_usage_bytes")} / ({guest("pve_memory_size_bytes")} > 0)'],
      'percentunit', ['{{name}} / {{id}}'],
      'Not guest available memory. Stopped guests or unsupported metrics may produce gaps.')
p = panel('Guest power state', 'stat', 0, 31, 12, 4,
          [guest('pve_up')], legends=['{{name}} / {{id}}'])
p['fieldConfig']['defaults']['mappings'] = [{'type': 'value', 'options': {
    '1': {'text': 'RUNNING', 'color': 'green'}, '0': {'text': 'STOPPED', 'color': 'orange'}}}]
panel('Assigned vCPUs', 'bargauge', 12, 31, 12, 4,
      [guest('pve_cpu_usage_limit')], legends=['{{name}} / {{id}}'],
      description='Scheduling allocations, not reserved physical cores.')
row('Storage', 35)
panel('Free capacity by pool', 'bargauge', 0, 36, 12, 7,
      [f'{storage("pve_disk_size_bytes")} - {storage("pve_disk_usage_bytes")}'],
      'bytes', ['{{node}} / {{storage}}'])
panel('Storage used over time', 'timeseries', 12, 36, 12, 7,
      [storage('pve_disk_usage_bytes')], 'bytes', ['{{node}} / {{storage}}'])
row('Guest network and disk I/O', 43)
for title, name, x, y in [
    ('Network receive', 'pve_network_receive_bytes_total', 0, 44),
    ('Network transmit', 'pve_network_transmit_bytes_total', 12, 44),
    ('Disk reads', 'pve_disk_read_bytes_total', 0, 51),
    ('Disk writes', 'pve_disk_written_bytes_total', 12, 51)]:
    q = f'rate({metric(name)}[$__rate_interval]) * on({ENTITY}) group_left(name,type,node) {GI}'
    panel(title, 'timeseries', x, y, 12, 7, [q], 'Bps', ['{{name}} / {{id}}'],
          'Counter rate; requires at least two samples. Availability depends on guest/storage support.')
p = panel('Interpretation', 'text', 0, 58, 24, 4)
p['options'] = {'mode': 'markdown', 'content':
    '**Collection:** read-only Proxmox API → prometheus-pve-exporter → Prometheus. '
    'Scrape success is not application health. Freshness follows the selected threshold. '
    'Historical graphs describe their evaluation time, not current health.\n\n'
    '**Storage:** pools may share disks. Free capacity is not backup freshness or restore proof. '
    'Guest memory is the hypervisor view. I/O rates use counter metrics.\n\n'
    'Inspired by the metric model of [Proxmox via Prometheus](https://github.com/mittelab/proxmox-via-prometheus-dashboard). '
    'Native Grafana panels only; no external panel plugins.'}


def query_var(name, label, query, multi=False):
    p = {'name': name, 'label': label, 'type': 'query', 'datasource': DS,
         'definition': query, 'query': {'query': query, 'refId': 'variable-'+name},
         'refresh': 1, 'sort': 1, 'multi': multi, 'includeAll': multi, 'options': []}
    if multi:
        p.update(allValue='.*', current={'text': 'All', 'value': '$__all'})
    return p


variables = [
    {'name': 'datasource', 'label': 'Prometheus', 'type': 'datasource', 'query': 'prometheus',
     'refresh': 1, 'options': []},
    query_var('job', 'Cluster scrape job', 'label_values(pve_node_info,job)'),
    query_var('instance', 'Cluster scrape target', 'label_values(pve_node_info{job="$job"},instance)'),
    query_var('node', 'Nodes', f'label_values(pve_guest_info{{{S}}},node)', True),
    query_var('storage', 'Storage', f'label_values(pve_storage_info{{{S},node=~"${{node:regex}}"}},storage)', True),
    {'name': 'freshness', 'label': 'Freshness (seconds)', 'type': 'custom', 'query': '90,180,300,600',
     'current': {'text': '90', 'value': '90'}, 'options': [
         {'text': str(v), 'value': str(v), 'selected': v == 90} for v in (90,180,300,600)]}]
# Node-info names include nodes without guests; derive node selector from those IDs.
variables[3] = query_var('node', 'Nodes', f'label_values(pve_node_info{{{S}}},id)', True)
variables[3]['regex'] = '/node\\/(.*)/'
dashboard = {'id': None, 'uid': 'pve-infrastructure', 'title': 'Proxmox VE / Infrastructure',
    'description': 'Node, QEMU, LXC, storage and guest I/O for prometheus-pve-exporter.',
    'tags': ['proxmox', 'prometheus-pve-exporter'], 'schemaVersion': 39, 'version': 1,
    'editable': True, 'graphTooltip': 1, 'timezone': 'browser', 'refresh': '30s',
    'time': {'from': 'now-1h', 'to': 'now'}, 'panels': panels,
    'templating': {'list': variables}, 'links': []}
if __name__ == '__main__':
    Path(__file__).with_name('proxmox-infrastructure.json').write_text(json.dumps(dashboard, indent=2)+'\n')
    print(f'Built {len(panels)} native panels')
