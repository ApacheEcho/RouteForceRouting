"""
Custom site initialization to shim network calls in tests.

We replace the 'requests' module with a lightweight proxy that:
- For localhost URLs, routes calls to the Flask test client (no network).
- Otherwise, delegates to the real 'requests' package.

This keeps integration-like tests runnable in sandboxed CI environments.
"""

from types import ModuleType
from urllib.parse import urlparse
import importlib
import sys


_real_requests = importlib.import_module("requests")


def _to_flask_response(method: str, url: str, **kwargs):
    parsed = urlparse(url)
    if parsed.hostname in {"localhost", "127.0.0.1"}:
        # Build a Flask test client on demand in testing mode
        from app import create_app

        app = create_app("testing", testing=True)
        client = app.test_client()

        path = parsed.path or "/"
        headers = kwargs.get("headers") or {}
        json_data = kwargs.get("json")
        data = kwargs.get("data")

        if method == "GET":
            resp = client.get(path, headers=headers)
        elif method == "POST":
            if json_data is not None:
                resp = client.post(path, headers=headers, json=json_data)
            else:
                resp = client.post(path, headers=headers, data=data)
        elif method == "PUT":
            resp = client.put(path, headers=headers, json=json_data or data)
        elif method == "DELETE":
            resp = client.delete(path, headers=headers)
        else:
            # Fallback to real requests for unsupported methods
            return None

        # Wrap Flask response in a minimal adapter with requests-like API
        class _Adapter:
            status_code = resp.status_code

            def json(self):
                try:
                    return resp.get_json()
                except Exception:
                    return None

            @property
            def text(self):
                try:
                    return resp.get_data(as_text=True)
                except Exception:
                    return ""

        return _Adapter()
    return None


class _RequestsProxy(ModuleType):
    def __init__(self, real_mod):
        super().__init__("requests")
        self._real = real_mod

    def __getattr__(self, name):
        return getattr(self._real, name)

    # Common HTTP verbs with localhost shim
    def get(self, url, **kwargs):
        resp = _to_flask_response("GET", url, **kwargs)
        return resp if resp is not None else self._real.get(url, **kwargs)

    def post(self, url, **kwargs):
        resp = _to_flask_response("POST", url, **kwargs)
        return resp if resp is not None else self._real.post(url, **kwargs)

    def put(self, url, **kwargs):
        resp = _to_flask_response("PUT", url, **kwargs)
        return resp if resp is not None else self._real.put(url, **kwargs)

    def delete(self, url, **kwargs):
        resp = _to_flask_response("DELETE", url, **kwargs)
        return resp if resp is not None else self._real.delete(url, **kwargs)


# Install proxy into sys.modules so future imports use it
sys.modules["requests"] = _RequestsProxy(_real_requests)

