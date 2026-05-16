from __future__ import annotations

import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass(slots=True)
class ManagedOpenListStatus:
    mode: str
    configured_url: str
    active_url: str
    port: int
    running: bool
    binary: str
    pid: int = 0
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "configured_url": self.configured_url,
            "active_url": self.active_url,
            "port": self.port,
            "running": self.running,
            "binary": self.binary,
            "pid": self.pid,
            "message": self.message,
        }


class ManagedOpenListRuntime:
    def __init__(
        self,
        *,
        mode: str,
        configured_url: str,
        data_dir: Path,
        binary_path: str = "",
        port: int = 0,
    ) -> None:
        self.mode = str(mode or "external")
        self.configured_url = str(configured_url or "").rstrip("/")
        self.data_dir = Path(data_dir)
        self.binary_path = str(binary_path or "").strip()
        self.port = int(port or 0)
        self.process: subprocess.Popen[str] | None = None
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _detect_binary(self) -> str:
        candidates = [
            self.binary_path,
            str((self.data_dir / "openlist.exe").resolve()),
            str((self.data_dir / "alist.exe").resolve()),
            "openlist.exe",
            "alist.exe",
            "openlist",
            "alist",
        ]
        for candidate in candidates:
            text = str(candidate or "").strip()
            if not text:
                continue
            if Path(text).exists():
                return text
            if "\\" not in text and "/" not in text:
                return text
        return ""

    def active_url(self) -> str:
        if self.mode == "external":
            return self.configured_url
        port = self.port or _pick_free_port()
        self.port = port
        return f"http://127.0.0.1:{port}"

    def status(self) -> ManagedOpenListStatus:
        binary = self._detect_binary()
        active_url = self.active_url()
        running = self._is_alive(active_url)
        pid = self.process.pid if self.process else 0
        message = ""
        if self.mode == "managed" and not binary:
            message = "未找到可用的 OpenList/Alist 可执行文件，请在配置里指定 managed_openlist_bin。"
        elif self.mode == "managed" and not running and self.process is None:
            message = "Managed OpenList 尚未启动。"
        elif self.mode == "external" and not running:
            message = "外部 OpenList 当前不可访问。"
        return ManagedOpenListStatus(
            mode=self.mode,
            configured_url=self.configured_url,
            active_url=active_url,
            port=self.port,
            running=running,
            binary=binary,
            pid=pid,
            message=message,
        )

    def start(self) -> ManagedOpenListStatus:
        if self.mode != "managed":
            return self.status()
        status = self.status()
        if status.running:
            return status
        binary = status.binary
        if not binary:
            return status
        active_url = self.active_url()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        command = [
            binary,
            "server",
            "--data",
            str(self.data_dir),
            "--force-bin-dir",
            str(self.data_dir),
            "--no-prefix",
        ]
        self.process = subprocess.Popen(
            command,
            cwd=str(self.data_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            if self._is_alive(active_url):
                return self.status()
            time.sleep(1)
        return self.status()

    def _is_alive(self, base_url: str) -> bool:
        if not base_url:
            return False
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{base_url}/api/public/settings")
                return response.status_code < 500
        except Exception:
            return False
