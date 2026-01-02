#!/usr/bin/env python3
import json, sys

def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def load(path):
    try:
        return json.loads(open(path, "r", encoding="utf-8").read())
    except Exception as e:
        die(f"Failed to parse JSON: {path}: {e}")

def require(obj, key, path):
    if key not in obj:
        die(f"Missing required field: {path}.{key}")

def is_list(v, path):
    if not isinstance(v, list):
        die(f"Expected list at {path}")

def is_obj(v, path):
    if not isinstance(v, dict):
        die(f"Expected object at {path}")

def main():
    if len(sys.argv) != 2:
        die("Usage: scripts/validate_registry.py <manifest.json>")
    m = load(sys.argv[1])
    for k in ["id","version","kind","license","attribution","interfaces","provenance"]:
        require(m, k, "$")
    if not isinstance(m["id"], str) or len(m["id"]) < 3:
        die("id must be a non-empty string (>=3 chars)")
    is_list(m["license"], "$.license")
    is_obj(m["attribution"], "$.attribution")
    for k in ["source","authors"]:
        require(m["attribution"], k, "$.attribution")
    is_list(m["attribution"]["authors"], "$.attribution.authors")
    is_obj(m["interfaces"], "$.interfaces")
    for k in ["inputs","outputs"]:
        require(m["interfaces"], k, "$.interfaces")
        is_list(m["interfaces"][k], f"$.interfaces.{k}")
        for i, item in enumerate(m["interfaces"][k]):
            is_obj(item, f"$.interfaces.{k}[{i}]")
            for req in ["name","schema_ref"]:
                if req not in item:
                    die(f"Missing {req} at $.interfaces.{k}[{i}]")
    is_obj(m["provenance"], "$.provenance")
    require(m["provenance"], "origin", "$.provenance")
    is_obj(m["provenance"]["origin"], "$.provenance.origin")
    for k in ["url","pinned_ref","retrieved_at"]:
        require(m["provenance"]["origin"], k, "$.provenance.origin")
    print("OK: manifest passes minimal structural checks")

if __name__ == "__main__":
    main()

