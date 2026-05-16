from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _int_or_default(value: Any, default: int, *, minimum: int | None = None) -> int:
    try:
        if value in ("", None):
            result = int(default)
        else:
            result = int(value)
    except (TypeError, ValueError):
        result = int(default)
    if minimum is not None:
        result = max(minimum, result)
    return result


@dataclass(slots=True)
class AppConfig:
    source_path: str
    target_path: str
    state_file: Path
    export_file: Path
    temp_dir: Path
    openlist_mode: str = "external"
    managed_openlist_bin: str = ""
    managed_openlist_data_dir: Path = Path(".runtime/openlist")
    managed_openlist_port: int = 5244
    openlist_url: str = ""
    openlist_token: str = ""
    openlist_username: str = ""
    openlist_password: str = ""
    guangya_phone: str = ""
    guangya_authorization: str = ""
    guangya_access_token: str = ""
    guangya_refresh_token: str = ""
    guangya_device_id: str = ""
    delete_removed: bool = False
    openlist_page_size: int = 200
    openlist_request_interval_ms: int = 300
    queue_interval_ms: int = 3000
    auto_download_threshold_mb: int = 10
    rate_limit_mode: str = "safe"
    provider_captures: dict[str, Any] | None = None
    panel_open_states: dict[str, bool] | None = None
    bind_host: str = "127.0.0.1"
    bind_port: int = 8765
    log_file: Path = Path(".state/sync.log")

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_payload(payload)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AppConfig":
        return cls(
            source_path=payload["source_path"],
            target_path=payload["target_path"],
            state_file=Path(payload.get("state_file", ".state/sync-state.json")),
            export_file=Path(payload.get("export_file", ".work/source-export.jsonl")),
            temp_dir=Path(payload.get("temp_dir", ".work/download-cache")),
            openlist_mode=str(payload.get("openlist_mode", "external")),
            managed_openlist_bin=str(payload.get("managed_openlist_bin", "")),
            managed_openlist_data_dir=Path(payload.get("managed_openlist_data_dir", ".runtime/openlist")),
            managed_openlist_port=_int_or_default(payload.get("managed_openlist_port", 5244), 5244, minimum=1),
            openlist_url=payload.get("openlist_url", ""),
            openlist_token=payload.get("openlist_token", ""),
            openlist_username=payload.get("openlist_username", ""),
            openlist_password=payload.get("openlist_password", ""),
            guangya_phone=payload.get("guangya_phone", ""),
            guangya_authorization=payload.get("guangya_authorization", ""),
            guangya_access_token=payload.get("guangya_access_token", ""),
            guangya_refresh_token=payload.get("guangya_refresh_token", ""),
            guangya_device_id=payload.get("guangya_device_id", ""),
            delete_removed=bool(payload.get("delete_removed", False)),
            openlist_page_size=_int_or_default(payload.get("openlist_page_size", 200), 200, minimum=1),
            openlist_request_interval_ms=_int_or_default(payload.get("openlist_request_interval_ms", 300), 300, minimum=0),
            queue_interval_ms=_int_or_default(payload.get("queue_interval_ms", 3000), 3000, minimum=0),
            auto_download_threshold_mb=_int_or_default(payload.get("auto_download_threshold_mb", 10), 10, minimum=0),
            rate_limit_mode=str(payload.get("rate_limit_mode", "safe")),
            provider_captures=dict(payload.get("provider_captures", {}) or {}),
            panel_open_states=dict(payload.get("panel_open_states", {}) or {}),
            bind_host=str(payload.get("bind_host", "127.0.0.1")),
            bind_port=int(payload.get("bind_port", 8765)),
            log_file=Path(payload.get("log_file", ".state/sync.log")),
        )

    def ensure_parent_dirs(self) -> None:
        for target in (self.state_file, self.export_file, self.log_file):
            target.parent.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.managed_openlist_data_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "target_path": self.target_path,
            "state_file": str(self.state_file),
            "export_file": str(self.export_file),
            "temp_dir": str(self.temp_dir),
            "openlist_mode": self.openlist_mode,
            "managed_openlist_bin": self.managed_openlist_bin,
            "managed_openlist_data_dir": str(self.managed_openlist_data_dir),
            "managed_openlist_port": self.managed_openlist_port,
            "openlist_url": self.openlist_url,
            "openlist_token": self.openlist_token,
            "openlist_username": self.openlist_username,
            "openlist_password": self.openlist_password,
            "guangya_phone": self.guangya_phone,
            "guangya_authorization": self.guangya_authorization,
            "guangya_access_token": self.guangya_access_token,
            "guangya_refresh_token": self.guangya_refresh_token,
            "guangya_device_id": self.guangya_device_id,
            "delete_removed": self.delete_removed,
            "openlist_page_size": self.openlist_page_size,
            "openlist_request_interval_ms": self.openlist_request_interval_ms,
            "queue_interval_ms": self.queue_interval_ms,
            "auto_download_threshold_mb": self.auto_download_threshold_mb,
            "rate_limit_mode": self.rate_limit_mode,
            "provider_captures": dict(self.provider_captures or {}),
            "panel_open_states": dict(self.panel_open_states or {}),
            "bind_host": self.bind_host,
            "bind_port": self.bind_port,
            "log_file": str(self.log_file),
        }


def write_example_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "source_path": "/我的资源",
        "target_path": "/天翼同步",
        "state_file": ".state/sync-state.json",
        "export_file": ".work/source-export.jsonl",
        "temp_dir": ".work/download-cache",
        "openlist_mode": "external",
        "managed_openlist_bin": "",
        "managed_openlist_data_dir": ".runtime/openlist",
        "managed_openlist_port": 5244,
        "openlist_url": "http://127.0.0.1:5244",
        "openlist_token": "",
        "openlist_username": "admin",
        "openlist_password": "",
        "guangya_phone": "+86 13800138000",
        "guangya_authorization": "",
        "guangya_access_token": "",
        "guangya_refresh_token": "",
        "guangya_device_id": "",
        "delete_removed": False,
        "openlist_page_size": 200,
        "openlist_request_interval_ms": 300,
        "queue_interval_ms": 3000,
        "auto_download_threshold_mb": 10,
        "rate_limit_mode": "safe",
        "provider_captures": {},
        "panel_open_states": {},
        "bind_host": "127.0.0.1",
        "bind_port": 8765,
        "log_file": ".state/sync.log",
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
