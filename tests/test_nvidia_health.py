"""Recognize observed NVIDIA failures without confusing CPU PMU boot messages."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "nvidia_health", Path(__file__).resolve().parents[1] / "tools/check-nvidia-health.py")
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


class NvidiaHealth(unittest.TestCase):
    def test_detects_pmu_halt_reset_and_resume_timeout(self):
        lines = [
            "NVRM: Xid (PCI:0000:01:00): 62, name=steamwebhelper",
            "NVRM: _kgspRpcGspEventPmuHalted: Received signal from GSP that PMU has halted.",
            "NVRM: GPU0 Reset required [NV_ERR_RESET_REQUIRED]",
            "NVRM: Xid (PCI:0000:01:00): 109, name=kwin_wayland",
            "RIP: 0010:nvEvoDisableVblankSemControl+0x34/0xd0 [nvidia_modeset]",
        ]
        self.assertEqual(health.failures("\n".join(lines)), lines)

    def test_cpu_pmu_and_normal_suspend_are_not_gpu_failures(self):
        self.assertEqual(health.failures(
            "Intel PMU driver.\nRAPL PMU: hw unit of domain core\n"
            "PM: suspend entry (deep)\nPM: suspend exit\n"
            "NVRM: loading NVIDIA UNIX Open Kernel Module"), [])

    def test_internal_assertions_and_lock_errors_are_reported_as_warnings(self):
        lines = [
            "NVRM: nvAssertFailedNoLog: Assertion failed: 0 @ alloc_free.c:263",
            "NVRM: nvAssertOkFailedNoLog: Requested lock state not valid [NV_ERR_INVALID_LOCK_STATE] @ kgraphics_tu102.c:395",
            "NVRM: nvCheckOkFailedNoLog: Check failed @ kgraphics_tu102.c:253",
            "NVRM: nvAssertFailedNoLog: Assertion failed: 0 @ gpu_suspend.c:321",
        ]
        journal = "\n".join(lines)
        self.assertEqual(health.warnings(journal), lines)
        self.assertEqual(health.failures(journal), [])

    def test_reset_error_is_not_downgraded_to_warning(self):
        line = "NVRM: nvAssertOkFailedNoLog: NV_ERR_RESET_REQUIRED"
        self.assertEqual(health.failures(line), [line])
        self.assertEqual(health.warnings(line), [])

    def test_normal_boot_and_cpu_pmu_do_not_generate_warnings(self):
        self.assertEqual(health.warnings(
            "Intel PMU driver\nRAPL PMU: hw unit of domain core\n"
            "NVRM: loading NVIDIA UNIX Open Kernel Module\n"
            "PM: suspend entry (deep)\nPM: suspend exit"), [])
