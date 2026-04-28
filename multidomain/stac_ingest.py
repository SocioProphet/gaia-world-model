#!/usr/bin/env python3
"""Deterministic v0 STAC ingestion proof for GAIA.

Reads a small STAC-like item fixture and emits a standards-bound
EarthObservationProductRecord with a runtime evidence bundle. This is a fixture
proof, not a network client.

Usage:
  python3 multidomain/stac_ingest.py \
    fixtures/multidomain/stac-item-input.sample.v1.json \
    /tmp/earth-observation-product.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_TOP = ["input_version", "source", "catalog_ref", "collection_ref", "item", "attribution", "classification"]
REQUIRED_ITEM = ["id", "type", "bbox", "geometry", "properties", "assets"]
REQUIRED_STANDARDS = [
    "SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md",
    "SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md",
]
AGENT_STANDARD_REF = "SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def canonical_bytes(value: Dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_ref(value: Dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected JSON object in {path}")
    return value


def require_fields(obj: Dict[str, Any], fields: Iterable[str], scope: str) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        fail(f"{scope} missing required fields: {', '.join(missing)}")


def asset_refs(assets: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    for name, asset in sorted(assets.items()):
        if not isinstance(asset, dict):
            fail(f"asset {name} must be object")
        href = asset.get("href")
        if not isinstance(href, str) or not href:
            fail(f"asset {name} missing href")
        refs.append(f"stac-asset:{name}:{href}")
    if not refs:
        fail("STAC assets must be non-empty")
    return refs


def build_runtime_evidence(input_doc: Dict[str, Any], output_record: Dict[str, Any]) -> Dict[str, Any]:
    input_hash = sha256_ref(input_doc)
    output_hash = sha256_ref(output_record)
    return {
        "evidence_version": "v1",
        "evidence_id": f"evidence:runtime:stac-ingest:{output_record['record_id']}",
        "runtime_id": "runtime:stac-ingest:v0",
        "runtime_class": "ingest",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "input_manifest": {
            "input_ref": f"stac:item:{input_doc['item']['id']}",
            "input_sha256": input_hash,
            "input_schema_hint": "stac-like-item-fixture.v1"
        },
        "output_manifest": {
            "output_ref": output_record["record_id"],
            "output_sha256": output_hash,
            "output_schema_ref": "schemas/multidomain/earth_observation_product_record.v1.schema.json"
        },
        "policy": {
            "approval_required": False,
            "sensitive_geo_handling": "preserve_policy_ref",
            "network_posture": "none_for_fixture_proof",
            "secret_posture": "none_for_fixture_proof"
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": "python3 multidomain/stac_ingest.py fixtures/multidomain/stac-item-input.sample.v1.json /tmp/gaia-stac-ingest-output.json"
        }
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(input_doc, REQUIRED_TOP, "STAC input")
    if input_doc.get("source") != "STAC":
        fail("input source must be STAC")
    item = input_doc["item"]
    if not isinstance(item, dict):
        fail("item must be object")
    require_fields(item, REQUIRED_ITEM, "STAC item")
    properties = item["properties"]
    if not isinstance(properties, dict):
        fail("item.properties must be object")
    assets = item["assets"]
    if not isinstance(assets, dict):
        fail("item.assets must be object")
    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("attribution must be object")
    require_fields(attribution, ["source_name", "license_ref", "attribution_text"], "attribution")
    classification = input_doc["classification"]
    if not isinstance(classification, dict):
        fail("classification must be object")

    item_id = str(item["id"])
    observed_start = properties.get("start_datetime") or properties.get("datetime")
    observed_end = properties.get("end_datetime") or properties.get("datetime")
    published_at = properties.get("datetime") or observed_end
    if not observed_start or not observed_end or not published_at:
        fail("STAC properties require datetime or start/end datetime")

    h3_refs = input_doc.get("h3_refs", [])
    if not isinstance(h3_refs, list):
        fail("h3_refs must be an array when present")

    output_record = {
        "record_version": "v1",
        "record_type": "EarthObservationProductRecord",
        "record_id": f"gaia:eo-product:{item_id}",
        "standards_refs": REQUIRED_STANDARDS,
        "product": {
            "product_id": f"eo-product:{item_id}",
            "product_type": "STAC_ITEM",
            "asset_refs": asset_refs(assets),
            "media_type": "application/geo+json",
            "derived_indices": input_doc.get("derived_indices", []),
            "catalog_ref": input_doc["catalog_ref"],
            "collection_ref": input_doc["collection_ref"],
        },
        "spatial": {
            "crs": "EPSG:4326",
            "geometry_encoding": "geojson",
            "bbox": item["bbox"],
            "geometry": item["geometry"],
            "h3_refs": h3_refs,
        },
        "temporal": {
            "observed_start": observed_start,
            "observed_end": observed_end,
            "published_at": published_at,
        },
        "source": {
            "source_id": input_doc["catalog_ref"],
            "source_type": "STAC",
            "license_ref": attribution["license_ref"],
            "access_tier": input_doc.get("access_tier", "open"),
            "attribution": attribution["attribution_text"],
        },
        "provenance": {
            "chain": ["runtime:stac-ingest:v0"],
            "derived_from": [f"stac:item:{item_id}"],
            "runtime_boundary_id": "runtime:stac-ingest:v0",
        },
        "governance": {
            "privacy_tier": input_doc.get("privacy_tier", "public"),
            "safety_tier": input_doc.get("safety_tier", "standard"),
            "retention_tier": input_doc.get("retention_tier", "sample"),
            "redistribution": input_doc.get("redistribution", "allowed"),
        },
        "classification": classification,
    }
    output_record["runtime_evidence"] = build_runtime_evidence(input_doc, output_record)
    return output_record


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    output = ingest(load_json(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
