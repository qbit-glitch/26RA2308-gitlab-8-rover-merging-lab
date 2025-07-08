#!/usr/bin/env python3
"""Check src/sensor_limits.h against what the rover needs. Exit 0 = every check passed, 1 = a check failed."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

LIMITS = Path(__file__).resolve().parents[1] / "src" / "sensor_limits.h"
FAR_ECHO_MS = 20   # an object about 3.4 m away must still be seen
NO_ECHO_MS = 60    # a reading this slow must be reported as "no echo"
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")
TIMEOUT_RE = re.compile(r"^#define SENSOR_TIMEOUT_MS (\d+)$")


def run_checks(text: str) -> List[Tuple[bool, str]]:
    """Return (passed, description) for every check on the text of sensor_limits.h."""
    lines = text.splitlines()
    timeouts = [int(m.group(1)) for m in (TIMEOUT_RE.match(line) for line in lines) if m]
    timeout = timeouts[0] if len(timeouts) == 1 else None
    return [
        (not any(line.startswith(MARKERS) for line in lines), "no merge markers left in src/sensor_limits.h"),
        (len(timeouts) == 1, "exactly one SENSOR_TIMEOUT_MS line"),
        (timeout is not None and timeout >= FAR_ECHO_MS, f"far object ({FAR_ECHO_MS} ms echo) is accepted"),
        (timeout is not None and timeout < NO_ECHO_MS, f"no echo ({NO_ECHO_MS} ms) is rejected"),
        ("#define SENSOR_MAX_CM 400" in lines and "#define SENSOR_MIN_CM 2" in lines,
         "SENSOR_MAX_CM and SENSOR_MIN_CM are unchanged"),
    ]


def main() -> int:
    """Print PASS or FAIL for each check and a summary line."""
    results = run_checks(LIMITS.read_text(encoding="utf-8"))
    for passed, description in results:
        print(f"{'PASS' if passed else 'FAIL'} {description}")
    failed = sum(1 for passed, _ in results if not passed)
    if failed == 0:
        print("ALL CHECKS PASSED")
        return 0
    print(f"{failed} of {len(results)} checks FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
