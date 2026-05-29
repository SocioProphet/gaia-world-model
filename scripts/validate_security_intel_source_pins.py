#!/usr/bin/env python3
"""Validate GAIA security-intel source pin examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "gaia" / "cv" / "security_intel_source_pins.schema.json"
EXAMPLE = ROOT / "gaia" / "cv" / "security_intel_source_pins.example.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(name: str, ok: bool, detail=None):
    return {"check": name, "passed": bool(ok), "detail": detail or []}


def main() -> int:
    schema = load(SCHEMA)
    example = load(EXAMPLE)
    out = []

    out.append(check("schema-version", example.get("schemaVersion") == "0.1.0"))
    out.append(check("kind", example.get("kind") == "SecurityIntelSourcePins"))
    pins = example.get("pins", [])
    out.append(check("pins-present", isinstance(pins, list) and len(pins) > 0))

    required = set(schema.get("properties", {}).get("pins", {}).get("items", {}).get("required", []))
    seen_ids = set()
    for idx, pin in enumerate(pins):
        prefix = f"pin-{idx}"
        out.append(check(f"{prefix}-required-covered", required <= set(pin.keys()), [sorted(required - set(pin.keys()))]))
        source_id = pin.get("sourceId", "")
        out.append(check(f"{prefix}-source-id", isinstance(source_id, str) and source_id.startswith("security-intel-source:")))
        out.append(check(f"{prefix}-source-id-unique", source_id not in seen_ids))
        seen_ids.add(source_id)
        out.append(check(f"{prefix}-url", str(pin.get("sourceUrl", "")).startswith("https://")))
        out.append(check(f"{prefix}-retrieved-at", str(pin.get("retrievedAt", "")).endswith("Z")))
        out.append(check(f"{prefix}-allowed-uses", isinstance(pin.get("allowedUses"), list) and len(pin["allowedUses"]) > 0))
        out.append(check(f"{prefix}-forbidden-uses", isinstance(pin.get("forbiddenUses"), list) and len(pin["forbiddenUses"]) > 0))
        forbidden = set(pin.get("forbiddenUses", []))
        for forbidden_use in [
            "local compromise proof",
            "attribution",
            "runtime authority",
            "engagement authorization",
            "claim promotion",
            "memory writeback approval",
        ]:
            out.append(check(f"{prefix}-forbid-{forbidden_use}", forbidden_use in forbidden))
        non_claims = set(pin.get("nonClaims", []))
        for non_claim in [
            "does_not_prove_local_compromise",
            "does_not_authorize_engagement",
            "does_not_claim_attribution",
            "does_not_promote_memory_writeback",
        ]:
            out.append(check(f"{prefix}-nonclaim-{non_claim}", non_claim in non_claims))
        if pin.get("hashStatus") == "not_copied_url_only":
            out.append(check(f"{prefix}-no-artifact-hash-for-url-only", pin.get("artifactHash") is None))
        out.append(check(f"{prefix}-not-authority-in-notes", "authority" in pin.get("provenanceNotes", "") or "taxonomy support" in pin.get("provenanceNotes", "")))

    passed = all(item["passed"] for item in out)
    result = {"validator": "gaia.security_intel_source_pins.v0.1", "passed": passed, "results": out}
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        print("FAIL: security-intel source pins", file=sys.stderr)
        return 1
    print("PASS: security-intel source pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
