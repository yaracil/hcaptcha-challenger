import json
import time
from pathlib import Path


class DataPacket:
    """Lightweight representation of a network response used by tests."""

    def __init__(self, url: str = "", headers: dict | None = None, body: bytes | None = None):
        self.url = url
        self.headers = headers or {}
        self._body = body or b""

    # These helpers mimic the Playwright Response API used in the project
    def json(self):
        return json.loads(self._body.decode() or "{}")

    def text(self) -> str:
        return self._body.decode()

    def body(self) -> bytes:
        return self._body


class _DummyElement:
    def __init__(self):
        self.rect = {"x": 0, "y": 0, "width": 0, "height": 0}

    def click(self):
        return None

    def ele(self, _selector: str):
        return _DummyElement()

    @property
    def shadow_root(self):  # pragma: no cover - minimal stub
        return self

    def screenshot(self, path: str | Path | None = None):
        if path:
            Path(path).write_bytes(b"")
        return b""


class _DummyMouse:
    def move(self, _x: float, _y: float):
        return None

    def click(self, _x: float | None = None, _y: float | None = None):
        return None


class _Listener:
    def __init__(self):
        self._callback = None

    def start(self, callback):
        self._callback = callback

    def wait(self, _timeout: float | None = None):
        # This stub does not produce any packets automatically.
        return None


class ChromiumPage:
    """A tiny subset of the DrissionPage API used in the tests."""

    def __init__(self):
        self.mouse = _DummyMouse()
        self.listen = _Listener()
        self._url = ""

    def get(self, url: str):
        self._url = url

    def ele(self, _selector: str):  # pragma: no cover - simple stub
        return _DummyElement()

    def run_js(self, _script: str):  # pragma: no cover
        return None

    def wait(self, ms: int):  # pragma: no cover
        time.sleep(ms / 1000)


# re-export element type for type checkers
ChromiumElement = _DummyElement
