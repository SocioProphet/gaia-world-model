#!/usr/bin/env python3
"""detect adapter – sourceos.host-detect.v1

Detects host runtime facts for the GAIA bounded OSM ingest artifact.
Emits a host-facts JSON payload to stdout (or --out file).

This adapter is local-safe and produces deterministic output suitable
for fixture-mode runs. No privileged access required.

Usage:
  python3 adapters/detect.py [--out host-facts.json]
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def detect() -> dict:
    return {
        "host_facts_version": "v1",
        "artifact_type": "gaia.bounded_osm_ingest.host_facts",
        "detected_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "runtime": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "machine": platform.machine(),
            "mode": os.environ.get("GAIA_ARTIFACT_MODE", "fixture"),
            "network_posture": os.environ.get("GAIA_NETWORK_POSTURE", "allowlisted"),
        },
        "capabilities": {
            "fixture_mode": True,
            "live_network": False,
            "privileged": False,
        },
        "policy": {
            "safety_class": "bounded",
            "network_posture": "allowlisted",
            "requires_human_review": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect host runtime facts.")
    parser.add_argument("--out", help="Write output JSON to this file instead of stdout.")
    args = parser.parse_args(argv)

    facts = detect()
    payload = json.dumps(facts, indent=2, ensure_ascii=False) + "\n"

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        print(f"  OK  host facts written to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
