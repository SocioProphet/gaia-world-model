#!/usr/bin/env python3
"""Build a v0 soil-intelligence fusion artifact.

This script fuses a GAIA artifact derived from an OFIF field observation with a
GAIA EO/reanalysis context fixture. It is intentionally simple and transparent:
world-class systems start with calibrated baselines before complex models.

Usage:
  python3 scripts/soil_intelligence_fusion.py \
    /tmp/gaia-ofif-output.json \
    fixtures/gaia/context/soil-eo-context.sample.v1.json \
    /tmp/gaia-soil-fusion-output.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


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


def require(obj: Dict[str, Any], key: str, scope: str) -> Any:
    if key not in obj:
        fail(f"{scope} missing {key}")
    return obj[key]


def find_source(context: Dict[str, Any], measurement: str) -> Optional[Dict[str, Any]]:
    sources = context.get("sources", [])
    if not isinstance(sources, list):
        fail("context.sources must be an array")
    for source in sources:
        if isinstance(source, dict) and source.get("measurement") == measurement:
            return source
    return None


def source_value(context: Dict[str, Any], measurement: str, default: Optional[float] = None) -> Optional[float]:
    source = find_source(context, measurement)
    if source is None:
        return default
    value = source.get("value", default)
    if isinstance(value, (int, float)):
        return float(value)
    return default


def source_confidence(context: Dict[str, Any], measurement: str, default: float = 0.5) -> float:
    source = find_source(context, measurement)
    if source is None:
        return default
    value = source.get("confidence", default)
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return default


def average(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def build_fusion(field_artifact: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    feature = require(field_artifact, "world_state_feature", "field artifact")
    spatial = require(feature, "spatial", "world_state_feature")
    temporal = require(feature, "temporal", "world_state_feature")
    observed_environment = feature.get("observed_environment", {})
    if not isinstance(observed_environment, dict):
        observed_environment = {}

    local_temp = observed_environment.get("temperature_c")
    if not isinstance(local_temp, (int, float)):
        local_temp = source_value(context, "air_temperature_2m_c", 0.0)
    local_temp = float(local_temp)

    lst = source_value(context, "land_surface_temperature_c", local_temp)
    air = source_value(context, "air_temperature_2m_c", local_temp)
    moisture = source_value(context, "surface_soil_moisture_volumetric_fraction", 0.30)
    ndvi = source_value(context, "ndvi", 0.50)
    slope = source_value(context, "slope_deg", 0.0)

    assert lst is not None and air is not None and moisture is not None and ndvi is not None and slope is not None

    # Transparent baseline fixture: weighted thermal estimate with small adjustments.
    # This is not agronomic advice. It creates a stable proof artifact for the fusion pipeline.
    soil_temperature = (
        0.42 * local_temp
        + 0.30 * float(lst)
        + 0.20 * float(air)
        - 1.10 * (float(moisture) - 0.30)
        - 0.80 * (float(ndvi) - 0.50)
        - 0.03 * float(slope)
    )

    bridge_confidence = field_artifact.get("derived_confidence", {}).get("bridge_confidence", 0.5)
    if not isinstance(bridge_confidence, (int, float)):
        bridge_confidence = 0.5

    context_confidence = average([
        source_confidence(context, "land_surface_temperature_c"),
        source_confidence(context, "surface_soil_moisture_volumetric_fraction"),
        source_confidence(context, "air_temperature_2m_c"),
        source_confidence(context, "ndvi"),
        source_confidence(context, "slope_deg"),
    ])
    fusion_confidence = clamp(0.55 * float(bridge_confidence) + 0.45 * context_confidence)

    source_event_ids = field_artifact.get("source_event_ids", [])
    if not isinstance(source_event_ids, list):
        source_event_ids = []

    evidence_refs = list(source_event_ids)
    evidence_refs.append(field_artifact.get("artifact_id", "unknown-field-artifact"))
    evidence_refs.append(context.get("context_id", "unknown-context"))

    return {
        "gaia_artifact_version": "v1",
        "artifact_type": "gaia.soil_intelligence.fusion.v0",
        "artifact_id": "gaia-soil-fusion-demo-0001",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "scope": {
            "spatial": spatial,
            "temporal": {
                "field_observed_at": temporal.get("observed_at"),
                "field_ingested_at": temporal.get("ingested_at"),
                "context_valid_from": context.get("temporal", {}).get("valid_from"),
                "context_valid_to": context.get("temporal", {}).get("valid_to"),
                "scenario_id": context.get("temporal", {}).get("scenario_id"),
            },
        },
        "soil_intelligence": {
            "estimate": {
                "soil_temperature_c": round(soil_temperature, 3),
                "depth_band": "surface_fixture",
                "model_version_id": context.get("model_context", {}).get("model_version_id", "gaia-soil-intelligence-baseline-demo-0.1.0"),
                "model_class": context.get("model_context", {}).get("model_class", "weighted_baseline_fixture"),
                "input_features": {
                    "local_temperature_c": local_temp,
                    "land_surface_temperature_c": lst,
                    "air_temperature_2m_c": air,
                    "surface_soil_moisture_volumetric_fraction": moisture,
                    "ndvi": ndvi,
                    "slope_deg": slope,
                },
                "formula_note": "Transparent baseline fixture; not agronomic advice."
            },
            "confidence": {
                "field_bridge_confidence": round(float(bridge_confidence), 3),
                "context_confidence": round(context_confidence, 3),
                "fusion_confidence": round(fusion_confidence, 3),
                "confidence_class": "high" if fusion_confidence >= 0.8 else "moderate" if fusion_confidence >= 0.6 else "low"
            },
            "uncertainty": {
                "status": "fixture_only",
                "note": "Uncertainty interval requires calibrated validation data; v0 emits confidence only."
            }
        },
        "evidence_refs": evidence_refs,
        "policy_constraints": [
            "No autonomous actuation from v0 soil-fusion artifact.",
            "Do not present fixture output as validated agronomic advice.",
            "Preserve OFIF raw event provenance and GAIA context provenance."
        ],
        "provenance": {
            "field_artifact_id": field_artifact.get("artifact_id"),
            "context_id": context.get("context_id"),
            "mapping_contract": "contracts/mappings/ofif-to-gaia.v1.json",
            "integration_contract": "docs/integrations/OFIF_INTEGRATION.md"
        }
    }


def main(argv: List[str]) -> int:
    if len(argv) != 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    field_artifact = load_json(Path(argv[1]))
    context = load_json(Path(argv[2]))
    target = Path(argv[3])
    fusion = build_fusion(field_artifact, context)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(fusion, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
