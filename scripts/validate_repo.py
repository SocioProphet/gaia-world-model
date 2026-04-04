#!/usr/bin/env python3
from pathlib import Path
import json, sys

errors = []

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        errors.append(f"{path}: invalid JSON: {e}")
        return None

registry_path = Path("gaia/registry.json")
index_path = Path("schemas/index.json")

registry = load_json(registry_path) if registry_path.exists() else None
if registry is None:
    errors.append("gaia/registry.json missing or invalid")
else:
    for key in ("profiles", "domains", "core_contracts", "control_modes"):
        if key not in registry or not isinstance(registry[key], list) or not registry[key]:
            errors.append(f"gaia/registry.json: missing or empty '{key}'")

index = load_json(index_path) if index_path.exists() else None
schema_paths = []
if index is None:
    errors.append("schemas/index.json missing or invalid")
else:
    schema_map = index.get("schemas")
    if not isinstance(schema_map, dict) or not schema_map:
        errors.append("schemas/index.json: missing or empty 'schemas' map")
    else:
        for name, rel in sorted(schema_map.items()):
            p = Path(rel)
            if not p.exists():
                errors.append(f"schemas/index.json: listed schema missing: {rel}")
            else:
                schema_paths.append(p)

for p in schema_paths:
    data = load_json(p)
    if data is None:
        continue
    for key in ("$schema", "title", "type"):
        if key not in data:
            errors.append(f"{p}: missing required schema key '{key}'")
    if "required" in data and not isinstance(data["required"], list):
        errors.append(f"{p}: 'required' must be a list")

manifest_paths = sorted(Path("gaia").glob("profiles/*/manifest.json")) + sorted(Path("gaia").glob("domains/*/manifest.json"))
example_paths = sorted(Path("examples").rglob("*.json"))

for p in manifest_paths + example_paths:
    data = load_json(p)
    if data is None:
        continue
    if not isinstance(data, dict):
        errors.append(f"{p}: top-level JSON value must be an object")

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("[OK] GAIA canonical JSON validation passed")
