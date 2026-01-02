from pathlib import Path
import json, hashlib

ROOT = Path(__file__).resolve().parents[1]

def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sha3_id(o):
    return "sha3-256:" + hashlib.sha3_256(canon(o)).hexdigest()

# Load IDs and references
ids = json.loads((ROOT / "vendor/tritrpc/derived/ids.json").read_text(encoding="utf-8"))
av = json.loads((ROOT / ids["avro_ref"]).read_text(encoding="utf-8"))
ctx = json.loads((ROOT / ids["jsonld_ref"]).read_text(encoding="utf-8"))
assert ids["schema_id"] == sha3_id(av)
assert ids["context_id"] == sha3_id(ctx)

# Load wire profile for Path A
wire = json.loads((ROOT / "gaia/wire/tritrpc/hyper.v1.pathA.json").read_text(encoding="utf-8"))
assert wire["schema_bundle"]["schema_id"] == ids["schema_id"]
assert wire["schema_bundle"]["context_id"] == ids["context_id"]

# Check if Path B exists and is marked as "planned"
wireB = json.loads((ROOT / "gaia/wire/tritrpc/hyper.v1.pathB.json").read_text(encoding="utf-8"))
assert wireB["status"] == "planned"  # Ensuring Path B is planned, not enabled

# Final validation check
print("validate_registry: ok")

