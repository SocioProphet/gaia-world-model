#!/usr/bin/env python3
"""Deterministic v0 LiDAR rollback receipt proof.

Reads a LidarRuntimeRollbackPlan and emits a demotion/supersession receipt.
The receipt never mutates source observations or point-cloud artifacts; it only
records what should be preserved, demoted, and reviewed.

Usage:
  python3 navigation/lidar_rollback_receipt.py \
    fixtures/navigation/lidar-runtime-rollback-plan.sample.v1.json \
    /tmp/lidar-rollback-receipt.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REQUIRED_PLAN_FIELDS = [
    "plan_version",
    "plan_id",
    "runtime_ref",
    "trigger_conditions",
    "rollback_actions",
    "preserve_refs",
    "demote_refs",
    "post_rollback_state",
    "evidence_refs",
    "approval",
    "provenance",
    "classification",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected object: {path}")
    return value


def require_fields(doc: dict[str, Any], fields: Iterable[str], scope: str) -> None:
    missing = [field for field in fields if field not in doc]
    if missing:
        fail(f"{scope} missing fields: {', '.join(missing)}")


def rollback_receipt(plan: dict[str, Any]) -> dict[str, Any]:
    require_fields(plan, REQUIRED_PLAN_FIELDS, "rollback plan")
    if not plan.get("preserve_refs"):
        fail("rollback plan must preserve source refs")
    if not plan.get("demote_refs"):
        fail("rollback plan must include demote refs")
    if plan.get("approval", {}).get("approval_required") is not True:
        fail("rollback plan must require approval")

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "receipt_version": "v1",
        "receipt_type": "gaia.navigation.lidar_rollback_receipt",
        "created_at": created_at,
        "plan_id": plan["plan_id"],
        "runtime_ref": plan["runtime_ref"],
        "mutation_policy": {
            "source_observations_mutated": False,
            "point_cloud_artifacts_mutated": False,
            "derived_outputs_mutated": False,
            "notes": "Receipt records demotion/supersession intent only; source artifacts remain immutable."
        },
        "preserve_refs": plan["preserve_refs"],
        "demote_refs": plan["demote_refs"],
        "rollback_actions": plan["rollback_actions"],
        "post_rollback_state": plan["post_rollback_state"],
        "approval": plan["approval"],
        "evidence_refs": plan["evidence_refs"],
        "provenance": {
            "source_refs": [plan["plan_id"], *plan.get("provenance", {}).get("source_refs", [])],
            "runtime_refs": [plan["runtime_ref"]],
            "created_by": "navigation/lidar_rollback_receipt.py",
            "content_hash": "sha256:generated-at-runtime-placeholder"
        },
        "classification": plan.get("classification", {"data_class": "internal", "handling_tags": []}),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    receipt = rollback_receipt(load_json(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
