from prometheus_client.core import GaugeMetricFamily
import logging
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

class QgaFsCollector:
    """
    Collects per-filesystem disk usage from guests via QEMU Guest Agent (get-fsinfo).
    Optimized to run API calls concurrently and cache config.
    """

    def __init__(self, pve, max_workers: int = 16, timeout: float = 10.0):
        self.pve = pve
        self.logger = logging.getLogger("gunicorn.error")
        self.max_workers = max_workers
        self.timeout = timeout
        # Cache per (node, vmid) -> cfg (dict) to avoid repeated GET /config for same VM
        self._config_cache: Dict[Tuple[str, int], Dict] = {}

    def collect(self):
        size_metric = GaugeMetricFamily(
            "pve_qga_fs_size_bytes",
            "Filesystem size inside guest from QEMU guest agent (get-fsinfo)",
            labels=["id", "node", "vm", "disk", "mountpoint", "fstype"],
        )
        used_metric = GaugeMetricFamily(
            "pve_qga_fs_used_bytes",
            "Filesystem used bytes inside guest from QEMU guest agent (get-fsinfo)",
            labels=["id", "node", "vm", "disk", "mountpoint", "fstype"],
        )

        vms = list(self._iter_qemu_vms())
        if not vms:
            yield size_metric
            yield used_metric
            return

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            future_to_vm = {
                pool.submit(self._collect_vm_fs, vm, size_metric, used_metric): vm
                for vm in vms
            }

            for fut in as_completed(future_to_vm):
                vm = future_to_vm[fut]
                try:
                    fut.result(timeout=self.timeout)
                except Exception as exc:
                    self.logger.info(
                        "Failed to collect FS info for vmid=%s on node=%s: %s",
                        vm["vmid"], vm["node"], exc
                    )

        yield size_metric
        yield used_metric

    def _iter_qemu_vms(self):
        resources = self.pve.cluster.resources.get(type="vm")

        for res in resources:
            if res.get("type") != "qemu" or res.get("status") != "running":
                continue

            yield {
                "id":   res["id"],
                "vmid": int(res["vmid"]),
                "node": res["node"],
                "name": res.get("name", ""),
            }

    def _collect_vm_fs(self, vm, size_metric, used_metric):
        node = vm["node"]
        vmid = vm["vmid"]
        id_ = vm["id"]
        name = vm["name"]

        # Config (cached)
        cache_key = (node, vmid)
        cfg = self._config_cache.get(cache_key)
        if cfg is None:
            try:
                cfg = self.pve.nodes(node).qemu(vmid).config.get()
                self._config_cache[cache_key] = cfg
            except Exception as exc:
                self.logger.info("Failed to get config for vmid=%s on node=%s: %s", vmid, node, exc)
                return

        if not self._agent_enabled(cfg):
            self.logger.debug("QGA not enabled for vmid=%s on node=%s", vmid, node)
            return

        try:
            fsinfo = self.pve.nodes(node).qemu(vmid).agent("get-fsinfo").get()
        except Exception as exc:
            self.logger.info("QGA get-fsinfo failed for vmid=%s on node=%s: %s", vmid, node, exc)
            return

        fs_list = fsinfo.get("result") if isinstance(fsinfo, dict) else fsinfo
        if not fs_list:
            return

        for fs in fs_list:
            mount = fs.get("mountpoint")
            if not mount:
                continue

            total = fs.get("total-bytes")
            used = fs.get("used-bytes")
            fstype = fs.get("type", "")
            if total is None or used is None:
                continue

            disks = fs.get("disk") or []
            devs = [d.get("dev", "unknown") for d in disks] if disks else [fs.get("name", "unknown")]

            for dev in devs:
                labels = [id_, node, name, dev, mount, fstype]
                size_metric.add_metric(labels, float(total))
                used_metric.add_metric(labels, float(used))

    def _agent_enabled(self, cfg) -> bool:
        val = cfg.get("agent")
        if not isinstance(val, str):
            return False

        first = val.split(",", 1)[0].strip()
        if not first:
            return False

        if "=" in first:
            key, raw = first.split("=", 1)
            if key.strip() != "enabled":
                return False
            token = raw.strip()
        else:
            token = first

        return token.lower() in ("1", "true")