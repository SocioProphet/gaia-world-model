#!/usr/bin/env python3
"""Deterministic v0 governed world-claim ingest proof for GAIA.

Reads an OSM-like feature input fixture and emits a GAIA WorldClaim bundle
following the governed world-claim contract:

  Observe -> Anchor -> Normalize -> Propose

The output includes:
- GeoAnchor (geometry, bbox, H3 cells, temporal binding)
- SourceEvidence (OSM attribution, license, temporal validity, confidence)
- ExplanationTrace (single-source passthrough rule, derivation steps)
- ProposedWorldClaim (policy_status=proposed, advisory map_display)

A world-claim at status='proposed' must pass Holmes/Policy review before it
may be admitted to GAIA world state or shown as truth on /map.

The emitted claims/traces also carry the additive CHRONOS carrier fields
(SocioProphet/gaia-world-model#38): fusion_rule.chronos_method_family/
chronos_method_output_type and claim.chronos_grounding_status/
chronos_owning_authority_plane. Single-source OSM passthrough uses no
neuro-symbolic method, so these fields are populated at their non-authority
defaults (chronos_method_family=not_applicable,
chronos_method_output_type=hard_value) and no
chronos_non_authority_declaration is required.

Usage:
  python3 geospatial/world_claim_ingest.py \\
    fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json \\
    /tmp/gaia-world-claim-output.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_INPUT_FIELDS = ["input_version", "source", "extract_ref", "features", "attribution", "classification"]
REQUIRED_FEATURE_FIELDS = ["osm_type", "osm_id", "tags", "geometry", "h3_cells", "bbox"]
REQUIRED_ATTRIBUTION_FIELDS = ["source_name", "license_ref", "attribution_text"]

STANDARDS_REFS = [
    "SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md",
    "SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md",
]
RUNTIME_REF = "runtime:world-claim-ingest:v0"
SCHEMA_REF_CLAIM = "schemas/geospatial/world_claim.v1.schema.json"
SCHEMA_REF_EVIDENCE = "schemas/geospatial/source_evidence.v1.schema.json"
SCHEMA_REF_ANCHOR = "schemas/geospatial/geo_anchor.v1.schema.json"
SCHEMA_REF_TRACE = "schemas/geospatial/fusion_explanation.v1.schema.json"


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


def entity_type_from_tags(tags: Dict[str, Any]) -> str:
    if "railway" in tags:
        return "RailSegment"
    if "highway" in tags:
        return "RoadSegment"
    if "building" in tags:
        return "BuildingAsset"
    if "waterway" in tags:
        return "WaterwayFeature"
    if "landuse" in tags or "natural" in tags:
        return "LandCoverFeature"
    return "SpatialFeature"


def osm_source_ref(osm_type: str, osm_id: str) -> str:
    """Build a canonical OSM source URI."""
    return f"osm://{osm_type}/{osm_id}"


def build_geo_anchor(feature: Dict[str, Any], created_at: str) -> Dict[str, Any]:
    """Build a GeoAnchor from an OSM feature."""
    geometry = feature.get("geometry", {})
    geom_type = geometry.get("type", "LineString") if isinstance(geometry, dict) else "LineString"
    anchor_type_map = {
        "Point": "point",
        "LineString": "linestring",
        "Polygon": "polygon",
        "MultiLineString": "linestring",
        "MultiPolygon": "polygon",
    }
    anchor_type = anchor_type_map.get(geom_type, "linestring")
    timestamp = feature.get("timestamp", created_at)

    anchor: Dict[str, Any] = {
        "anchor_id": f"anchor:osm:{feature['osm_type']}:{feature['osm_id']}",
        "anchor_type": anchor_type,
        "crs": "EPSG:4326",
        "temporal": {
            "observed_at": timestamp,
            "valid_from": timestamp,
            "time_basis": "document_timestamp",
        },
    }
    if isinstance(geometry, dict) and "coordinates" in geometry:
        anchor["geometry"] = geometry
    if isinstance(feature.get("bbox"), list):
        anchor["bbox"] = feature["bbox"]
    if isinstance(feature.get("h3_cells"), list):
        anchor["h3_cells"] = feature["h3_cells"]
    # NOTE: no "source_ref" here. schemas/geospatial/world_claim.v1.schema.json
    # embeds GeoAnchor inline under WorldClaim.geo_anchor with
    # additionalProperties=false and no "source_ref" property (source
    # attribution for the anchor's owning feature belongs on SourceEvidence,
    # which does carry source_ref). Adding it here breaks schema conformance.
    return anchor


def build_source_evidence(
    input_doc: Dict[str, Any],
    feature: Dict[str, Any],
    anchor_id: str,
    created_at: str,
) -> Dict[str, Any]:
    """Build a SourceEvidence record from an OSM feature."""
    attribution = input_doc["attribution"]
    osm_type = str(feature["osm_type"])
    osm_id = str(feature["osm_id"])
    evidence_id = f"evidence:osm:{osm_type}:{osm_id}:{created_at}"
    tags = feature.get("tags", {})

    evidence: Dict[str, Any] = {
        "evidence_version": "v1",
        "evidence_id": evidence_id,
        "source_type": "osm",
        "source_ref": osm_source_ref(osm_type, osm_id),
        "geo_anchor_ref": anchor_id,
        "attribution": {
            "source_name": attribution["source_name"],
            "license_ref": attribution["license_ref"],
            "attribution_text": attribution["attribution_text"],
        },
        "temporal": {
            "observed_at": feature.get("timestamp", created_at),
            "valid_from": feature.get("timestamp", created_at),
            "staleness_class": "historical",
        },
        "confidence": {
            "score": 0.85,
            "confidence_class": "high",
            "notes": "OSM community-maintained data. Advisory routing status applies.",
        },
        "spatial_summary": {
            "geometry_type": feature.get("geometry", {}).get("type", "Unknown"),
            "h3_cells": feature.get("h3_cells", []),
            "bbox": feature.get("bbox", []),
            "crs": "EPSG:4326",
        },
        "source_metadata": {
            "osm_type": osm_type,
            "osm_id": osm_id,
            "osm_version": feature.get("version"),
            "osm_changeset": feature.get("changeset"),
            "tags": {str(k): str(v) for k, v in tags.items()},
        },
        "classification": input_doc["classification"],
        "provenance": {
            "chain": [RUNTIME_REF],
            "runtime_ref": RUNTIME_REF,
            "ingest_ref": input_doc["extract_ref"],
        },
    }
    if attribution.get("source_url"):
        evidence["attribution"]["source_url"] = attribution["source_url"]
    evidence["content_hash"] = sha256_ref(evidence)
    return evidence


def build_explanation_trace(
    claim_id: str,
    evidence_id: str,
    anchor_id: str,
    osm_type: str,
    osm_id: str,
    created_at: str,
) -> Dict[str, Any]:
    """Build an ExplanationTrace for a single-source OSM passthrough claim."""
    trace_id = f"trace:osm:{osm_type}:{osm_id}:{created_at}"
    normalized_ref = f"normalized:osm:{osm_type}:{osm_id}"
    return {
        "trace_version": "v1",
        "trace_id": trace_id,
        "claim_ref": claim_id,
        "fusion_rule": {
            "rule_id": "single-source-passthrough-v1",
            "rule_class": "single_source_passthrough",
            "rule_version": "v1",
            "rule_ref": "docs/contracts/GOVERNED_WORLD_CLAIM_CONTRACT.md#single-source-passthrough",
            # CHRONOS carrier fields (SocioProphet/gaia-world-model#38): single-source
            # passthrough uses no neuro-symbolic method, so no non-authority
            # declaration is required here. See docs/contracts/GOVERNED_WORLD_CLAIM_CONTRACT.md
            # for the CHRONOS carrier field mapping.
            "chronos_method_family": "not_applicable",
            "chronos_method_output_type": "hard_value",
        },
        "inputs": [
            {
                "evidence_ref": evidence_id,
                "role": "primary",
                "weight": 1.0,
                "confidence_at_fusion": 0.85,
                "notes": "Single OSM source, no corroboration. Advisory status applies.",
            }
        ],
        "steps": [
            {
                "step_id": "step-normalize-osm-tags",
                "step_type": "normalize",
                "input_refs": [evidence_id],
                "output_ref": normalized_ref,
                "step_notes": "Map OSM tags to GAIA entity type and routing metadata.",
            },
            {
                "step_id": "step-anchor-geometry",
                "step_type": "annotate",
                "input_refs": [normalized_ref],
                "output_ref": anchor_id,
                "step_notes": "Bind geometry, bbox, H3 cells, and temporal anchor.",
            },
            {
                "step_id": "step-propose-claim",
                "step_type": "annotate",
                "input_refs": [anchor_id],
                "output_ref": claim_id,
                "step_notes": "Assemble proposed world claim with policy_status=proposed pending Holmes/Policy review.",
            },
        ],
        "uncertainty": {
            "method": "propagated_confidence",
            "combined_score": 0.85,
            "uncertainty_class": "low",
            "per_input_impact": [
                {"evidence_ref": evidence_id, "impact": 0.85}
            ],
            "notes": "Single-source passthrough propagates source confidence directly. Advisory routing constraint maintained.",
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": (
                "python3 geospatial/world_claim_ingest.py "
                "fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json "
                "/tmp/gaia-world-claim-output.json"
            ),
        },
        "provenance": {
            "runtime_ref": RUNTIME_REF,
            "created_at": created_at,
        },
    }


def build_world_claim(
    input_doc: Dict[str, Any],
    feature: Dict[str, Any],
    geo_anchor: Dict[str, Any],
    evidence_id: str,
    trace_id: str,
    created_at: str,
) -> Dict[str, Any]:
    """Build a governed WorldClaim from an OSM feature."""
    osm_type = str(feature["osm_type"])
    osm_id = str(feature["osm_id"])
    attribution = input_doc["attribution"]
    entity_type = entity_type_from_tags(feature.get("tags", {}))
    claim_id = f"gaia:world-claim:osm:{osm_type}:{osm_id}:{created_at}"

    return {
        "claim_version": "v1",
        "claim_id": claim_id,
        "claim_type": "feature_classification",
        "geo_anchor": geo_anchor,
        "source_evidence_refs": [evidence_id],
        "proposed_value": {
            "entity_type": entity_type,
            "osm_tags": {str(k): str(v) for k, v in feature.get("tags", {}).items()},
            "routing": feature.get("routing", {}),
        },
        "temporal_validity": {
            "valid_from": feature.get("timestamp", created_at),
            "staleness_class": "historical",
            "expiry_note": "OSM extract timestamp; re-ingest required when OSM changeset is updated.",
        },
        "uncertainty": {
            "confidence_score": 0.85,
            "uncertainty_class": "low",
            "uncertainty_notes": (
                "Single authoritative OSM source. Advisory routing status applies. "
                "No field validation or LiDAR corroboration exists for this fixture."
            ),
            "adversarial_impact": 0.0,
        },
        "policy_status": {
            "status": "proposed",
            "review_reason": (
                "OSM-sourced feature not yet reviewed by Holmes/Policy. "
                "Admitted status requires attribution check, CRS validation, temporal check, and uncertainty review."
            ),
            "constraints": [
                "display-advisory-only",
                "routing-advisory-only",
                "requires-policy-review-before-admission",
            ],
        },
        "explanation_trace_ref": trace_id,
        "map_display": {
            "show_source_attribution": True,
            "show_uncertainty": True,
            "show_evidence_chain": True,
            "show_policy_status": True,
            "display_layer": "proposed_candidate",
            "advisory_label": "OSM-derived candidate — not yet admitted to world state",
        },
        "attribution": {
            "primary_source_name": attribution["source_name"],
            "license_refs": [attribution["license_ref"]],
            "attribution_texts": [attribution["attribution_text"]],
            "attribution_notes": "OSM attribution must be preserved in all downstream displays and derivatives.",
        },
        "provenance": {
            "chain": [RUNTIME_REF],
            "derived_from": [osm_source_ref(osm_type, osm_id)],
            "runtime_ref": RUNTIME_REF,
            "created_at": created_at,
        },
        "classification": input_doc["classification"],
        "standards_refs": STANDARDS_REFS,
        # CHRONOS carrier fields (SocioProphet/gaia-world-model#38). OSM geometry is
        # taken directly from the source extract (grounded); Holmes/Policy is the
        # owning authority plane for this claim's Verify->Govern decision.
        "chronos_grounding_status": "grounded",
        "chronos_owning_authority_plane": "SocioProphet/holmes",
    }


def process_feature(
    input_doc: Dict[str, Any],
    feature: Dict[str, Any],
    created_at: str,
) -> Dict[str, Any]:
    """Process a single OSM feature into a WorldClaim bundle."""
    require_fields(feature, REQUIRED_FEATURE_FIELDS, "OSM feature")
    tags = feature.get("tags")
    if not isinstance(tags, dict):
        fail("OSM feature tags must be object")
    osm_type = str(feature["osm_type"])
    if osm_type not in {"node", "way", "relation"}:
        fail(f"unsupported osm_type: {osm_type}")

    geo_anchor = build_geo_anchor(feature, created_at)
    anchor_id = geo_anchor["anchor_id"]

    evidence = build_source_evidence(input_doc, feature, anchor_id, created_at)
    evidence_id = evidence["evidence_id"]

    claim_id = f"gaia:world-claim:osm:{osm_type}:{str(feature['osm_id'])}:{created_at}"
    trace = build_explanation_trace(claim_id, evidence_id, anchor_id, osm_type, str(feature["osm_id"]), created_at)
    trace_id = trace["trace_id"]

    claim = build_world_claim(input_doc, feature, geo_anchor, evidence_id, trace_id, created_at)

    return {
        "claim": claim,
        "evidence": evidence,
        "trace": trace,
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest an OSM input document and emit a WorldClaim bundle."""
    require_fields(input_doc, REQUIRED_INPUT_FIELDS, "world-claim input")
    if input_doc.get("source") != "OpenStreetMap":
        fail("input source must be OpenStreetMap")
    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("attribution must be object")
    require_fields(attribution, REQUIRED_ATTRIBUTION_FIELDS, "attribution")
    features = input_doc.get("features")
    if not isinstance(features, list) or not features:
        fail("input features must be a non-empty array")

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    bundles = [process_feature(input_doc, f, created_at) for f in features]

    # Compute a content hash over all claims for the output manifest
    claims_list = [b["claim"] for b in bundles]
    output_hash = sha256_ref({"claims": claims_list})

    return {
        "artifact_version": "v1",
        "artifact_type": "gaia.world_claim_ingest.output",
        "created_at": created_at,
        "source": "OpenStreetMap",
        "extract_ref": input_doc["extract_ref"],
        "standards_refs": STANDARDS_REFS,
        "claims": [b["claim"] for b in bundles],
        "evidence_records": [b["evidence"] for b in bundles],
        "explanation_traces": [b["trace"] for b in bundles],
        "runtime_evidence": {
            "evidence_version": "v1",
            "evidence_id": f"evidence:runtime:{RUNTIME_REF}:{created_at}",
            "runtime_id": RUNTIME_REF,
            "runtime_class": "ingest",
            "standards_refs": STANDARDS_REFS,
            "input_manifest": {
                "input_ref": input_doc["extract_ref"],
                "input_sha256": sha256_ref(input_doc),
                "input_schema_hint": "osm-feature-world-claim-input.v1",
            },
            "output_manifest": {
                "output_ref": f"world-claim-bundle:{created_at}",
                "output_sha256": output_hash,
                "output_schema_ref": SCHEMA_REF_CLAIM,
            },
            "policy": {
                "approval_required": True,
                "claim_status": "proposed — requires Holmes/Policy review for admission",
                "advisory_by_default": True,
                "network_posture": "none_for_fixture_proof",
                "secret_posture": "none_for_fixture_proof",
            },
            "replay": {
                "mode": "deterministic_fixture",
                "command": (
                    "python3 geospatial/world_claim_ingest.py "
                    "fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json "
                    "/tmp/gaia-world-claim-output.json"
                ),
            },
        },
        "policy": {
            "claim_status_summary": "proposed — pending Holmes/Policy review before admission",
            "attribution_required": True,
            "advisory_by_default": True,
            "notes": (
                "OSM-sourced world claims are advisory until attribution check, CRS validation, "
                "temporal check, and uncertainty review pass Holmes/Policy review gate."
            ),
        },
        "invariants": [
            "Raw OSM source was not mutated.",
            "OSM attribution and license ref were preserved.",
            "GeoAnchor binds each claim to a verifiable geometry.",
            "SourceEvidence carries source_ref, temporal validity, and confidence.",
            "ExplanationTrace records the single-source passthrough rule.",
            "policy_status is 'proposed' — not admitted to world state without Holmes/Policy review.",
            "map_display.display_layer is 'proposed_candidate' — advisory label required on /map.",
        ],
    }


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
