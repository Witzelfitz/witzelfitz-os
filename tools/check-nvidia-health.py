#!/usr/bin/env python3
"""Read GPU health without waking the GPU or changing system configuration."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


FAILURE = re.compile(
    r"NVRM:.*(?:Xid\s*\(|PMU has halted|NV_ERR_RESET_REQUIRED|"
    r"GSP RM heartbeat timed out|GPU has fallen off)|"
    r"(?:BUG:|Oops:|RIP:).*nvidia", re.IGNORECASE)
WARNING = re.compile(
    r"NVRM:.*(?:nvAssert(?:Ok)?FailedNoLog|nvCheckOkFailedNoLog|"
    r"NV_ERR_INVALID_LOCK_STATE)", re.IGNORECASE)


def failures(journal):
    return [line for line in journal.splitlines() if FAILURE.search(line)]


def warnings(journal):
    return [line for line in journal.splitlines()
            if WARNING.search(line) and not FAILURE.search(line)]


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def command(argv):
    result = subprocess.run(argv, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f"{argv[0]}: {result.stderr.strip()}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boot", default="0", help="journal boot index; default: current boot")
    parser.add_argument("--output", type=Path, help="optional local JSON report")
    args = parser.parse_args()
    try:
        journal = command(["journalctl", "-k", "-b", args.boot, "--no-pager", "-o", "short-iso", "--no-hostname"])
        if not journal.strip() or journal.strip() == "-- No entries --":
            raise RuntimeError("Keine Kernelmeldungen lesbar; keine Gesundheitsbewertung möglich.")
        deployments = json.loads(command(["rpm-ostree", "status", "--json"]))["deployments"]
        problems = failures(journal)
        notices = warnings(journal)
        report = {
            "journal_boot": args.boot,
            "current_kernel": read("/proc/sys/kernel/osrelease"),
            "current_nvidia": read("/proc/driver/nvidia/version"),
            "current_gpu_power": read("/sys/bus/pci/devices/0000:01:00.0/power/runtime_status"),
            "current_deployments": [{key: item.get(key) for key in
                ("booted", "staged", "pinned", "checksum", "container-image-reference", "version")} for item in deployments],
            "gpu_errors": problems,
            "gpu_warnings": notices,
            "suspend_events": [line for line in journal.splitlines() if re.search(r"PM: (suspend|resume)", line)],
            "assessment": ("GPU-Fehler im gewählten Boot" if problems else
                           "Interne NVIDIA-Treiberwarnungen; keine Fehlerfreiheit bestätigt" if notices else
                           "Keine bekannten GPU-Fehler oder Treiberwarnungen im gewählten Boot; kein Belastungsnachweis"),
        }
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content)
        print(content, end="")
        return 1 if problems else 3 if notices else 0
    except (RuntimeError, subprocess.SubprocessError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
