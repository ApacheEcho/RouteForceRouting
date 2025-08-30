import json
import os
import re
from typing import Dict, List, Tuple

TITLE = "RouteForce Routing API"
VERSION = "1.0.0"
DESCRIPTION = "Auto-generated OpenAPI spec from Flask routes."
DEFAULT_SERVER = os.getenv("OPENAPI_SERVER_URL", "http://localhost:5000")
PUBLIC_PATHS = {"/api/login", "/health", "/healthz", "/metrics"}
METHODS_WITH_BODY = {"POST", "PUT", "PATCH"}


def get_app():
    """Create app with testing config to avoid background services."""
    from app import create_app

    return create_app("testing")


_conv_to_oapi_type = {
    "int": ("integer", None),
    "float": ("number", None),
    "path": ("string", None),
    "string": ("string", None),
    "uuid": ("string", "uuid"),
}

_path_var_re = re.compile(r"<(?:(?P<conv>[^:<>]+):)?(?P<name>[^<>]+)>")


def flask_rule_to_openapi_path(rule_str: str) -> str:
    return _path_var_re.sub(r"{\2}", rule_str)


def extract_path_params(rule_str: str) -> List[Tuple[str, str]]:
    return [
        (m.group("name"), m.group("conv") or "string")
        for m in _path_var_re.finditer(rule_str)
    ]


def method_is_documented(method: str) -> bool:
    return method.upper() not in {"HEAD", "OPTIONS"}


def endpoint_tag(endpoint: str) -> str:
    return endpoint.split(".", 1)[0] if "." in endpoint else "default"


def build_spec(app) -> Dict:
    spec: Dict = {
        "openapi": "3.1.0",
        "info": {"title": TITLE, "version": VERSION, "description": DESCRIPTION},
        "servers": [{"url": DEFAULT_SERVER}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "security": [{"bearerAuth": []}],
        "paths": {},
    }

    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        oapi_path = flask_rule_to_openapi_path(rule.rule)
        params = []
        for name, conv in extract_path_params(rule.rule):
            typ, fmt = _conv_to_oapi_type.get(conv, ("string", None))
            param_obj = {
                "name": name,
                "in": "path",
                "required": True,
                "schema": {"type": typ},
                "description": f"Path parameter: {name}",
            }
            if fmt:
                param_obj["schema"]["format"] = fmt
            params.append(param_obj)

        methods = [m for m in rule.methods or [] if method_is_documented(m)]
        if not methods:
            continue

        spec["paths"].setdefault(oapi_path, {})
        tag = endpoint_tag(rule.endpoint)

        for method in methods:
            func = app.view_functions.get(rule.endpoint)
            doc = (func.__doc__ or "").strip() if func else ""
            summary = doc.splitlines()[0].strip() if doc else f"{method.title()} {oapi_path}"
            description = doc if doc else f"Auto-generated operation for {rule.endpoint}"

            op: Dict = {
                "tags": [tag],
                "summary": summary,
                "description": description,
                "operationId": f"{rule.endpoint}.{method.lower()}",
                "parameters": list(params),
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "examples": {"ok": {"value": {"status": "ok"}}},
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                },
            }

            if method.upper() in METHODS_WITH_BODY:
                op["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                            "examples": {
                                "example": {"value": {"example": "replace-with-real-body"}}
                            },
                        }
                    },
                }

            # Document optional metrics token header for /metrics endpoints
            if oapi_path.startswith("/metrics"):
                op.setdefault("parameters", list(params))
                op["parameters"].append(
                    {
                        "name": "X-Metrics-Token",
                        "in": "header",
                        "required": False,
                        "schema": {"type": "string"},
                        "description": "Optional token header if METRICS_TOKEN is configured",
                    }
                )

            if oapi_path in PUBLIC_PATHS:
                op["security"] = []

            spec["paths"][oapi_path][method.lower()] = op

    return spec


def main():
    app = get_app()
    spec = build_spec(app)
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print("Wrote openapi.json")


if __name__ == "__main__":
    main()

