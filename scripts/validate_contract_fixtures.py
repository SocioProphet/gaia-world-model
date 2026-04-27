#!/usr/bin/env python3
"""Validate GAIA contract fixtures with dependency-light structural checks.

This is not a full JSON Schema implementation. It is an intentionally small
bootstrap validator that proves fixtures are valid JSON and satisfy the core
required fields declared by their matching v1 schemas.

A later pass can replace or augment this with jsonschema once dependency policy
is defined.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

CHECKS: List[Tuple[str, str, Iterable[str]]] = [
    (
        "schemas/control-tower/work_order_candidate.v1.schema.json",
        "fixtures/control-tower/work-order-candidate.rail-vegetation.sample.v1.json",
        ["candidate_version", "candidate_id", "created_at", "asset_refs", "issue_summary", "priority", "evidence_refs", "approval_state", "provenance", "classification"],
    ),
    (
        "schemas/control-tower/inventory_node_record.v1.schema.json",
        "fixtures/control-tower/inventory-node.rail-maintenance-depot.sample.v1.json",
        ["record_version", "node_id", "node_type", "authority_ref", "spatial_refs", "provenance", "classification"],
    ),
    (
        "schemas/control-tower/risk_exposure_record.v1.schema.json",
        "fixtures/control-tower/risk-exposure.rail-vegetation.sample.v1.json",
        ["record_version", "risk_id", "risk_type", "created_at", "scope", "score", "evidence_refs", "provenance", "classification"],
    ),
    (
        "schemas/control-tower/control_tower_decision_card.v1.schema.json",
        "fixtures/control-tower/navigation-asset-health-card.sample.v1.json",
        ["card_version", "card_id", "created_at", "situation_type", "summary", "scope", "evidence_refs", "recommendations", "policy", "provenance"],
    ),
    (
        "schemas/geospatial/osm_feature_binding.v1.schema.json",
        "fixtures/geospatial/osm-road-feature-binding.sample.v1.json",
        ["binding_version", "binding_id", "source", "osm_ref", "gaia_ref", "spatial", "attribution", "provenance", "classification"],
    ),
    (
        "schemas/geospatial/map_tile_layer_manifest.v1.schema.json",
        "fixtures/geospatial/osm-derived-map-tile-layer.sample.v1.json",
        ["manifest_version", "layer_id", "layer_type", "title", "sources", "tiles", "attribution", "provenance", "classification"],
    ),
    (
        "schemas/geospatial/osm_route_graph_manifest.v1.schema.json",
        "fixtures/geospatial/osm-route-graph.sample.v1.json",
        ["manifest_version", "graph_id", "source", "safety_status", "nodes", "edges", "attribution", "provenance", "classification"],
    ),
    (
        "schemas/navigation/lidar_corridor_observation.v1.schema.json",
        "fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json",
        ["observation_version", "observation_id", "observed_at", "platform", "sensor", "spatial", "assets_observed", "provenance", "integrity"],
    ),
    (
        "schemas/navigation/navigation_safety_case.v1.schema.json",
        "fixtures/navigation/navigation-safety-case.lidar-advisory.sample.v1.json",
        ["case_version", "case_id", "created_at", "scope", "claim", "safety_status", "evidence_refs", "validation", "approval", "limits", "provenance", "classification"],
    ),
    (
        "schemas/navigation/route_plan.v1.schema.json",
        "fixtures/navigation/multimodal-route-plan.sample.v1.json",
        ["route_plan_version", "route_plan_id", "created_at", "mode", "origin", "destination", "legs", "provenance", "policy"],
    ),
    (
        "schemas/mesh/mesh_node_record.v1.schema.json",
        "fixtures/mesh/mesh-node.local-host.sample.v1.json",
        ["record_version", "node_id", "node_type", "identity", "lifecycle", "capabilities", "provenance", "classification"],
    ),
    (
        "schemas/mesh/slice_allocation_record.v1.schema.json",
        "fixtures/mesh/slice-allocation.soil-intelligence.sample.v1.json",
        ["record_version", "slice_id", "owner_ref", "node_refs", "isolation_profile", "runtime_refs", "policy_bundle_ref", "resource_limits", "provenance", "classification"],
    ),
    (
        "schemas/mesh/mesh_telemetry_envelope.v1.schema.json",
        "fixtures/mesh/mesh-telemetry.local-host-health.sample.v1.json",
        ["envelope_version", "telemetry_id", "node_id", "observed_at", "metric_family", "measurements", "producer", "integrity", "provenance", "classification"],
    ),
    (
        "schemas/mesh/mesh_experiment_manifest.v1.schema.json",
        "fixtures/mesh/soil-intelligence-mesh-experiment.sample.v1.json",
        ["manifest_version", "experiment_id", "purpose", "node_selector", "runtime_refs", "expected_evidence_outputs", "rollback_strategy", "policy", "provenance", "classification"],
    ),
]

OUTPUT_CHECKS: List[Tuple[str, Iterable[str]]] = [
    (
        "fixtures/navigation/lidar-derived-infrastructure-assets.sample.v1.json",
        ["artifact_version", "artifact_type", "source_observation_id", "runtime_ref", "safety_status", "assets"],
    ),
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected top-level object in {path}")
    return value


def check_required(path: str, doc: Dict[str, Any], required: Iterable[str]) -> None:
    missing = [field for field in required if field not in doc]
    if missing:
        fail(f"{path} missing required fields: {', '.join(missing)}")


def check_lidar_output(path: str, doc: Dict[str, Any]) -> None:
    if doc.get("artifact_type") != "gaia.navigation.lidar_feature_extract.output":
        fail(f"{path} has unexpected artifact_type")
    if doc.get("safety_status") != "advisory":
        fail(f"{path} must remain advisory")
    assets = doc.get("assets")
    if not isinstance(assets, list) or not assets:
        fail(f"{path} assets must be non-empty")
    for asset in assets:
        if not isinstance(asset, dict):
            fail(f"{path} asset entries must be objects")
        check_required(path, asset, ["asset_version", "asset_id", "asset_type", "spatial", "condition", "provenance", "classification"])
        if not asset.get("provenance", {}).get("source_refs"):
            fail(f"{path} asset {asset.get('asset_id')} missing provenance.source_refs")
        if not asset.get("condition", {}).get("evidence_refs"):
            fail(f"{path} asset {asset.get('asset_id')} missing condition.evidence_refs")


def check_safety_case(path: str, doc: Dict[str, Any]) -> None:
    if doc.get("safety_status") == "validated" and doc.get("validation", {}).get("validation_status") != "validated":
        fail(f"{path} cannot be validated unless validation.validation_status is validated")
    if doc.get("safety_status") != "advisory":
        approval = doc.get("approval", {})
        if approval.get("approval_state") != "approved":
            fail(f"{path} non-advisory safety status requires approval_state=approved")
    if doc.get("safety_status") == "advisory" and "safety-critical navigation" not in doc.get("limits", {}).get("prohibited_uses", []):
        fail(f"{path} advisory safety case must prohibit safety-critical navigation")


def main() -> int:
    checked = 0
    for schema_path, fixture_path, required in CHECKS:
        schema = load_json(ROOT / schema_path)
        fixture = load_json(ROOT / fixture_path)
        declared_required = schema.get("required")
        if isinstance(declared_required, list):
            for field in required:
                if field not in declared_required:
                    fail(f"{schema_path} does not declare expected required field {field}")
        check_required(fixture_path, fixture, required)
        if fixture_path.endswith("navigation-safety-case.lidar-advisory.sample.v1.json"):
            check_safety_case(fixture_path, fixture)
        checked += 1

    for fixture_path, required in OUTPUT_CHECKS:
        fixture = load_json(ROOT / fixture_path)
        check_required(fixture_path, fixture, required)
        if fixture_path.endswith("lidar-derived-infrastructure-assets.sample.v1.json"):
            check_lidar_output(fixture_path, fixture)
        checked += 1

    print(f"validated {checked} contract fixture pairs and output fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
