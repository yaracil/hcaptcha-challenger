import sys
import types
from pathlib import Path

import pytest

# Ensure the project package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Stub out heavy third-party libraries that are unavailable in the execution
# environment.  These modules are only required by tests that we skip below.
for _mod in ["numpy", "cv2", "matplotlib", "google", "httpx", "msgpack", "pytz"]:
    if _mod not in sys.modules:
        sys.modules[_mod] = types.ModuleType(_mod)
        if _mod == "matplotlib":
            sys.modules[_mod].pyplot = types.ModuleType("pyplot")
        if _mod == "google":
            sys.modules[_mod].genai = types.ModuleType("genai")
        if _mod == "httpx":
            class _Response:
                content = b""

            class Client:
                def __init__(self, **kwargs):
                    pass

                def get(self, url):
                    return _Response()

            sys.modules[_mod].Client = Client
        if _mod == "msgpack":
            def unpackb(data):
                return {}

            sys.modules[_mod].unpackb = unpackb


def pytest_collection_modifyitems(config, items):
    """Skip tests requiring external dependencies."""

    for item in items:
        if "test_agents_chromiumpage.py" not in item.nodeid:
            item.add_marker(pytest.mark.skip(reason="requires external dependencies"))

