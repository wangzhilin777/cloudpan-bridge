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


def _nested_get(payload: dict[str, Any], path: tuple[str, ...], default: Any = "") -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _pick(*values: Any, default: Any = "") -> Any:
    for value in values:
        if value is not None:
            return value
    return default


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
    target_key: str = "guangya"
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
    ui_language: str = "zh"
    coverage_filters: dict[str, Any] | None = None
    browser_state: dict[str, Any] | None = None
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
        app = dict(payload.get("app", {}) or {})
        ui = dict(payload.get("ui", {}) or {})
        openlist = dict(payload.get("openlist", {}) or {})
        managed_runtime = dict(openlist.get("managed_runtime", {}) or {})
        targets = dict(payload.get("targets", {}) or {})
        guangya = dict(targets.get("guangya", {}) or {})
        sync = dict(payload.get("sync", {}) or {})
        state_cfg = dict(payload.get("state", {}) or {})
        return cls(
            source_path=str(_pick(payload.get("source_path"), sync.get("source_path"), default="")),
            target_path=str(_pick(payload.get("target_path"), sync.get("target_path"), default="")),
            state_file=Path(_pick(payload.get("state_file"), state_cfg.get("state_file"), default=".state/sync-state.json")),
            export_file=Path(_pick(payload.get("export_file"), state_cfg.get("export_file"), default=".work/source-export.jsonl")),
            temp_dir=Path(_pick(payload.get("temp_dir"), state_cfg.get("temp_dir"), default=".work/download-cache")),
            openlist_mode=str(_pick(payload.get("openlist_mode"), openlist.get("mode"), default="external")),
            managed_openlist_bin=str(_pick(payload.get("managed_openlist_bin"), managed_runtime.get("bin"), default="")),
            managed_openlist_data_dir=Path(_pick(payload.get("managed_openlist_data_dir"), managed_runtime.get("data_dir"), default=".runtime/openlist")),
            managed_openlist_port=_int_or_default(_pick(payload.get("managed_openlist_port"), managed_runtime.get("port"), default=5244), 5244, minimum=1),
            openlist_url=str(_pick(payload.get("openlist_url"), openlist.get("url"), default="")),
            openlist_token=str(_pick(payload.get("openlist_token"), openlist.get("token"), default="")),
            openlist_username=str(_pick(payload.get("openlist_username"), openlist.get("username"), default="")),
            openlist_password=str(_pick(payload.get("openlist_password"), openlist.get("password"), default="")),
            guangya_phone=str(_pick(payload.get("guangya_phone"), guangya.get("phone"), default="")),
            target_key=str(_pick(payload.get("target_key"), targets.get("active_target"), default="guangya")),
            guangya_authorization=str(_pick(payload.get("guangya_authorization"), guangya.get("authorization"), default="")),
            guangya_access_token=str(_pick(payload.get("guangya_access_token"), guangya.get("access_token"), default="")),
            guangya_refresh_token=str(_pick(payload.get("guangya_refresh_token"), guangya.get("refresh_token"), default="")),
            guangya_device_id=str(_pick(payload.get("guangya_device_id"), guangya.get("device_id"), default="")),
            delete_removed=bool(_pick(payload.get("delete_removed"), sync.get("delete_removed"), default=False)),
            openlist_page_size=_int_or_default(_pick(payload.get("openlist_page_size"), sync.get("openlist_page_size"), default=200), 200, minimum=1),
            openlist_request_interval_ms=_int_or_default(_pick(payload.get("openlist_request_interval_ms"), sync.get("openlist_request_interval_ms"), default=300), 300, minimum=0),
            queue_interval_ms=_int_or_default(_pick(payload.get("queue_interval_ms"), sync.get("queue_interval_ms"), default=3000), 3000, minimum=0),
            auto_download_threshold_mb=_int_or_default(_pick(payload.get("auto_download_threshold_mb"), sync.get("auto_download_threshold_mb"), default=10), 10, minimum=0),
            rate_limit_mode=str(_pick(payload.get("rate_limit_mode"), sync.get("rate_limit_mode"), default="safe")),
            provider_captures=dict(_pick(payload.get("provider_captures"), payload.get("source_session", {}).get("provider_captures"), default={}) or {}),
            ui_language=str(_pick(payload.get("ui_language"), ui.get("language"), default="zh")),
            coverage_filters=dict(_pick(payload.get("coverage_filters"), ui.get("coverage_filters"), default={}) or {}),
            browser_state=dict(_pick(payload.get("browser_state"), ui.get("browser"), default={}) or {}),
            panel_open_states=dict(_pick(payload.get("panel_open_states"), ui.get("panel_open_states"), default={}) or {}),
            bind_host=str(_pick(payload.get("bind_host"), app.get("bind_host"), default="127.0.0.1")),
            bind_port=_int_or_default(_pick(payload.get("bind_port"), app.get("bind_port"), default=8765), 8765, minimum=1),
            log_file=Path(_pick(payload.get("log_file"), state_cfg.get("log_file"), default=".state/sync.log")),
        )

    def ensure_parent_dirs(self) -> None:
        for target in (self.state_file, self.export_file, self.log_file):
            target.parent.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.managed_openlist_data_dir.mkdir(parents=True, exist_ok=True)

    def to_flat_dict(self) -> dict[str, Any]:
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
            "target_key": self.target_key,
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
            "ui_language": self.ui_language,
            "coverage_filters": dict(self.coverage_filters or {}),
            "browser_state": dict(self.browser_state or {}),
            "panel_open_states": dict(self.panel_open_states or {}),
            "bind_host": self.bind_host,
            "bind_port": self.bind_port,
            "log_file": str(self.log_file),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "app": {
                "name": "CloudPan Bridge",
                "bind_host": self.bind_host,
                "bind_port": self.bind_port,
            },
            "ui": {
                "language": self.ui_language,
                "coverage_filters": dict(self.coverage_filters or {}),
                "browser": dict(self.browser_state or {}),
                "panel_open_states": dict(self.panel_open_states or {}),
            },
            "openlist": {
                "mode": self.openlist_mode,
                "url": self.openlist_url,
                "token": self.openlist_token,
                "username": self.openlist_username,
                "password": self.openlist_password,
                "managed_runtime": {
                    "bin": self.managed_openlist_bin,
                    "data_dir": str(self.managed_openlist_data_dir),
                    "port": self.managed_openlist_port,
                },
            },
            "source_session": {
                "provider_captures": dict(self.provider_captures or {}),
            },
            "targets": {
                "active_target": self.target_key,
                "guangya": {
                    "phone": self.guangya_phone,
                    "authorization": self.guangya_authorization,
                    "access_token": self.guangya_access_token,
                    "refresh_token": self.guangya_refresh_token,
                    "device_id": self.guangya_device_id,
                }
            },
            "sync": {
                "source_path": self.source_path,
                "target_path": self.target_path,
                "delete_removed": self.delete_removed,
                "openlist_page_size": self.openlist_page_size,
                "openlist_request_interval_ms": self.openlist_request_interval_ms,
                "queue_interval_ms": self.queue_interval_ms,
                "auto_download_threshold_mb": self.auto_download_threshold_mb,
                "rate_limit_mode": self.rate_limit_mode,
            },
            "state": {
                "state_file": str(self.state_file),
                "export_file": str(self.export_file),
                "temp_dir": str(self.temp_dir),
                "log_file": str(self.log_file),
            },
        }


def write_example_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = AppConfig(
        source_path="/我的资源",
        target_path="/天翼同步",
        state_file=Path(".state/sync-state.json"),
        export_file=Path(".work/source-export.jsonl"),
        temp_dir=Path(".work/download-cache"),
        openlist_mode="external",
        managed_openlist_bin="",
        managed_openlist_data_dir=Path(".runtime/openlist"),
        managed_openlist_port=5244,
        openlist_url="http://127.0.0.1:5244",
        openlist_token="",
        openlist_username="admin",
        openlist_password="",
        guangya_phone="+86 13800138000",
        target_key="guangya",
        guangya_authorization="",
        guangya_access_token="",
        guangya_refresh_token="",
        guangya_device_id="",
        delete_removed=False,
        openlist_page_size=200,
        openlist_request_interval_ms=300,
        queue_interval_ms=3000,
        auto_download_threshold_mb=10,
        rate_limit_mode="safe",
        provider_captures={},
        ui_language="zh",
        coverage_filters={},
        browser_state={},
        panel_open_states={},
        bind_host="127.0.0.1",
        bind_port=8765,
        log_file=Path(".state/sync.log"),
    ).to_dict()
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
