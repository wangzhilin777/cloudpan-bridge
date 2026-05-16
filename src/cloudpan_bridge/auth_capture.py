from __future__ import annotations

from pathlib import Path
from typing import Any

from .provider_capture import GuangyaCaptureManager as _GuangyaCaptureManager


class GuangyaCaptureManager:
    def __init__(self, base_dir: Path):
        self._inner = _GuangyaCaptureManager(base_dir)

    def snapshot(self) -> dict[str, Any]:
        return self._inner.snapshot()

    def start(self) -> None:
        self._inner.start()
