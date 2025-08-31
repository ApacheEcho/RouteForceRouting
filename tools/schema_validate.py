#!/usr/bin/env python3
"""
Lightweight JSON Schema validator CLI for RouteForce.

Usage:
  python tools/schema_validate.py --schema schemas/store.schema.json --data data/samples/cli_demo/stores_12_sf_compact.json

Behavior:
  - Tries to use 'jsonschema' if available.
  - Falls back to a minimal validator supporting a subset we use: type, properties, required, enum, minimum/maximum, oneOf, allOf, items, $ref (local).
  - Read-only; prints validation result and exits with 0/1.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def try_jsonschema_validate(instance: Any, schema: Dict) -> None:
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(instance=instance, schema=schema)
    except ImportError:
        raise
    except Exception as e:
        # Re-raise as ValueError for consistent handling
        raise ValueError(str(e))


def resolve_ref(schema: Dict, ref: str) -> Dict:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local refs supported, got: {ref}")
    parts = ref[2:].split("/")
    node: Any = schema
    for p in parts:
        if p not in node:
            raise ValueError(f"$ref path not found: {ref}")
        node = node[p]
    if not isinstance(node, dict):
        raise ValueError(f"$ref does not resolve to an object: {ref}")
    return node


def validate(instance: Any, schema: Dict, root: Dict | None = None, path: str = "$") -> List[str]:
    """Minimal JSON Schema validator. Returns a list of error strings (empty if valid)."""
    if root is None:
        root = schema

    errors: List[str] = []

    if "$ref" in schema:
        schema = resolve_ref(root, schema["$ref"])  # type: ignore

    # oneOf
    if "oneOf" in schema:
        opts = schema["oneOf"]
        matches = 0
        collected_errs: List[List[str]] = []
        for idx, sub in enumerate(opts):
            errs = validate(instance, sub, root, path)
            if not errs:
                matches += 1
            collected_errs.append(errs)
        if matches != 1:
            errors.append(f"{path}: oneOf failed (matched {matches} options)")
        return errors

    # allOf
    if "allOf" in schema:
        for sub in schema["allOf"]:
            errors.extend(validate(instance, sub, root, path))

    # type
    t = schema.get("type")
    if t:
        def _type_ok(val: Any, tname: str) -> bool:
            return (
                (tname == "object" and isinstance(val, dict)) or
                (tname == "array" and isinstance(val, list)) or
                (tname == "string" and isinstance(val, str)) or
                (tname == "integer" and isinstance(val, int) and not isinstance(val, bool)) or
                (tname == "number" and isinstance(val, (int, float)) and not isinstance(val, bool)) or
                (tname == "boolean" and isinstance(val, bool))
            )
        if isinstance(t, list):
            if not any(_type_ok(instance, tt) for tt in t):
                errors.append(f"{path}: type mismatch, expected one of {t}")
                return errors
        else:
            if not _type_ok(instance, t):
                errors.append(f"{path}: type mismatch, expected {t}")
                return errors

    # enum
    if "enum" in schema:
        if instance not in schema["enum"]:
            errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")
            return errors

    # numeric bounds
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value {instance} > maximum {schema['maximum']}")

    # object properties
    if isinstance(instance, dict) and schema.get("type") in (None, "object"):
        req = schema.get("required", [])
        for key in req:
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")

        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                errors.extend(validate(v, props[k], root, f"{path}.{k}"))
            else:
                addl = schema.get("additionalProperties", True)
                if addl is False:
                    errors.append(f"{path}: additional property '{k}' not allowed")
                # if addl is an object, could validate against it (skip for now)

    # array items
    if isinstance(instance, list) and schema.get("type") in (None, "array"):
        item_schema = schema.get("items")
        if item_schema:
            for i, it in enumerate(instance):
                errors.extend(validate(it, item_schema, root, f"{path}[{i}]"))

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate JSON data against a JSON Schema")
    ap.add_argument("--schema", required=True, help="Path to schema file")
    ap.add_argument("--data", required=True, help="Path to JSON data file")
    args = ap.parse_args()

    schema = load_json(args.schema)
    data = load_json(args.data)

    # Try jsonschema first
    try:
        try_jsonschema_validate(data, schema)
        print("✅ Valid (jsonschema)")
        return 0
    except ImportError:
        pass
    except ValueError as e:
        print(f"❌ Invalid: {e}")
        return 1

    # Fallback minimal validator
    errs = validate(data, schema)
    if errs:
        print("❌ Invalid:")
        for e in errs:
            print(" -", e)
        return 1
    print("✅ Valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())

