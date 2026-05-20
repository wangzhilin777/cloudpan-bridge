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
    openlist_mode: str = "external_local"
    managed_openlist_bin: str = ""
    managed_openlist_data_dir: Path = Path(".runtime/openlist")
    managed_openlist_port: int = 5244
    openlist_url: str = ""
    openlist_token: str = ""
    openlist_username: str = ""
    openlist_password: str = ""
    external_local_openlist_url: str = ""
    external_local_openlist_token: str = ""
    external_local_openlist_username: str = ""
    external_local_openlist_password: str = ""
    external_remote_openlist_url: str = ""
    external_remote_openlist_token: str = ""
    external_remote_openlist_username: str = ""
    external_remote_openlist_password: str = ""
    managed_openlist_token: str = ""
    managed_openlist_username: str = ""
    managed_openlist_password: str = ""
    managed_openlist_init_username: str = "admin"
    managed_openlist_init_password: str = ""
    guangya_phone: str = ""
    target_key: str = "guangya"
    guangya_authorization: str = ""
    guangya_access_token: str = ""
    guangya_refresh_token: str = ""
    guangya_device_id: str = ""
    local_target_root: Path = Path(".exports/localfs")
    webdav_target_url: str = ""
    webdav_target_username: str = ""
    webdav_target_password: str = ""
    s3_target_endpoint: str = ""
    s3_target_bucket: str = ""
    s3_target_prefix: str = ""
    s3_target_access_key: str = ""
    s3_target_secret_key: str = ""
    s3_target_region: str = ""
    seafile_target_url: str = ""
    seafile_target_token: str = ""
    seafile_target_username: str = ""
    seafile_target_password: str = ""
    seafile_target_repo_id: str = ""
    seafile_target_repo_name: str = ""
    azureblob_target_account_url: str = ""
    azureblob_target_container: str = ""
    azureblob_target_prefix: str = ""
    azureblob_target_account_name: str = ""
    azureblob_target_account_key: str = ""
    smb_target_url: str = ""
    smb_target_username: str = ""
    smb_target_password: str = ""
    ftp_target_url: str = ""
    ftp_target_username: str = ""
    ftp_target_password: str = ""
    sftp_target_url: str = ""
    sftp_target_username: str = ""
    sftp_target_password: str = ""
    delete_removed: bool = False
    target_delete_removed: bool = False
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
    app_admin_username: str = ""
    app_admin_password: str = ""
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
        connections = dict(openlist.get("connections", {}) or {})
        external_local = dict(connections.get("external_local", {}) or {})
        external_remote = dict(connections.get("external_remote", {}) or {})
        managed_connection = dict(connections.get("managed_binary", {}) or {})
        managed_runtime = dict(openlist.get("managed_runtime", {}) or {})
        managed_init_admin = dict(openlist.get("managed_init_admin", {}) or {})
        targets = dict(payload.get("targets", {}) or {})
        guangya = dict(targets.get("guangya", {}) or {})
        localfs = dict(targets.get("localfs", {}) or {})
        sync = dict(payload.get("sync", {}) or {})
        state_cfg = dict(payload.get("state", {}) or {})
        legacy_mode = str(_pick(payload.get("openlist_mode"), openlist.get("mode"), default="external_local"))
        mode = cls.normalize_openlist_mode(legacy_mode)
        legacy_url = str(_pick(payload.get("openlist_url"), openlist.get("url"), default=""))
        legacy_token = str(_pick(payload.get("openlist_token"), openlist.get("token"), default=""))
        legacy_username = str(_pick(payload.get("openlist_username"), openlist.get("username"), default=""))
        legacy_password = str(_pick(payload.get("openlist_password"), openlist.get("password"), default=""))
        external_local_url = str(_pick(external_local.get("url"), legacy_url if mode == "external_local" else "", default=""))
        external_local_token = str(_pick(external_local.get("token"), legacy_token if mode == "external_local" else "", default=""))
        external_local_username = str(_pick(external_local.get("username"), legacy_username if mode == "external_local" else "admin", default="admin"))
        external_local_password = str(_pick(external_local.get("password"), legacy_password if mode == "external_local" else "", default=""))
        external_remote_url = str(_pick(external_remote.get("url"), legacy_url if mode == "external_remote" else "", default=""))
        external_remote_token = str(_pick(external_remote.get("token"), legacy_token if mode == "external_remote" else "", default=""))
        external_remote_username = str(_pick(external_remote.get("username"), legacy_username if mode == "external_remote" else "admin", default="admin"))
        external_remote_password = str(_pick(external_remote.get("password"), legacy_password if mode == "external_remote" else "", default=""))
        managed_token = str(_pick(managed_connection.get("token"), legacy_token if cls.is_managed_openlist_mode(mode) else "", default=""))
        managed_username = str(_pick(managed_connection.get("username"), legacy_username if cls.is_managed_openlist_mode(mode) else "admin", default="admin"))
        managed_password = str(_pick(managed_connection.get("password"), legacy_password if cls.is_managed_openlist_mode(mode) else "", default=""))
        if mode == "external_remote":
            effective_url = external_remote_url
            effective_token = external_remote_token
            effective_username = external_remote_username
            effective_password = external_remote_password
        elif cls.is_managed_openlist_mode(mode):
            effective_url = legacy_url or "http://127.0.0.1:5244"
            effective_token = managed_token
            effective_username = managed_username
            effective_password = managed_password
        else:
            effective_url = external_local_url or legacy_url or "http://127.0.0.1:5244"
            effective_token = external_local_token
            effective_username = external_local_username
            effective_password = external_local_password
        return cls(
            source_path=str(_pick(payload.get("source_path"), sync.get("source_path"), default="")),
            target_path=str(_pick(payload.get("target_path"), sync.get("target_path"), default="")),
            state_file=Path(_pick(payload.get("state_file"), state_cfg.get("state_file"), default=".state/sync-state.json")),
            export_file=Path(_pick(payload.get("export_file"), state_cfg.get("export_file"), default=".work/source-export.jsonl")),
            temp_dir=Path(_pick(payload.get("temp_dir"), state_cfg.get("temp_dir"), default=".work/download-cache")),
            openlist_mode=mode,
            managed_openlist_bin=str(_pick(payload.get("managed_openlist_bin"), managed_runtime.get("bin"), default="")),
            managed_openlist_data_dir=Path(_pick(payload.get("managed_openlist_data_dir"), managed_runtime.get("data_dir"), default=".runtime/openlist")),
            managed_openlist_port=_int_or_default(_pick(payload.get("managed_openlist_port"), managed_runtime.get("port"), default=5244), 5244, minimum=1),
            openlist_url=effective_url,
            openlist_token=effective_token,
            openlist_username=effective_username,
            openlist_password=effective_password,
            external_local_openlist_url=external_local_url or "http://127.0.0.1:5244",
            external_local_openlist_token=external_local_token,
            external_local_openlist_username=external_local_username,
            external_local_openlist_password=external_local_password,
            external_remote_openlist_url=external_remote_url,
            external_remote_openlist_token=external_remote_token,
            external_remote_openlist_username=external_remote_username,
            external_remote_openlist_password=external_remote_password,
            managed_openlist_token=managed_token,
            managed_openlist_username=managed_username,
            managed_openlist_password=managed_password,
            managed_openlist_init_username=str(_pick(managed_init_admin.get("username"), default="admin")) or "admin",
            managed_openlist_init_password=str(_pick(managed_init_admin.get("password"), default="")),
            guangya_phone=str(_pick(payload.get("guangya_phone"), guangya.get("phone"), default="")),
            target_key=str(_pick(payload.get("target_key"), targets.get("active_target"), default="guangya")),
            guangya_authorization=str(_pick(payload.get("guangya_authorization"), guangya.get("authorization"), default="")),
            guangya_access_token=str(_pick(payload.get("guangya_access_token"), guangya.get("access_token"), default="")),
            guangya_refresh_token=str(_pick(payload.get("guangya_refresh_token"), guangya.get("refresh_token"), default="")),
            guangya_device_id=str(_pick(payload.get("guangya_device_id"), guangya.get("device_id"), default="")),
            local_target_root=Path(_pick(payload.get("local_target_root"), localfs.get("root"), default=".exports/localfs")),
            webdav_target_url=str(_pick(payload.get("webdav_target_url"), targets.get("webdav", {}).get("url"), default="")),
            webdav_target_username=str(_pick(payload.get("webdav_target_username"), targets.get("webdav", {}).get("username"), default="")),
            webdav_target_password=str(_pick(payload.get("webdav_target_password"), targets.get("webdav", {}).get("password"), default="")),
            s3_target_endpoint=str(_pick(payload.get("s3_target_endpoint"), targets.get("s3", {}).get("endpoint"), default="")),
            s3_target_bucket=str(_pick(payload.get("s3_target_bucket"), targets.get("s3", {}).get("bucket"), default="")),
            s3_target_prefix=str(_pick(payload.get("s3_target_prefix"), targets.get("s3", {}).get("prefix"), default="")),
            s3_target_access_key=str(_pick(payload.get("s3_target_access_key"), targets.get("s3", {}).get("access_key"), default="")),
            s3_target_secret_key=str(_pick(payload.get("s3_target_secret_key"), targets.get("s3", {}).get("secret_key"), default="")),
            s3_target_region=str(_pick(payload.get("s3_target_region"), targets.get("s3", {}).get("region"), default="")),
            seafile_target_url=str(_pick(payload.get("seafile_target_url"), targets.get("seafile", {}).get("url"), default="")),
            seafile_target_token=str(_pick(payload.get("seafile_target_token"), targets.get("seafile", {}).get("token"), default="")),
            seafile_target_username=str(_pick(payload.get("seafile_target_username"), targets.get("seafile", {}).get("username"), default="")),
            seafile_target_password=str(_pick(payload.get("seafile_target_password"), targets.get("seafile", {}).get("password"), default="")),
            seafile_target_repo_id=str(_pick(payload.get("seafile_target_repo_id"), targets.get("seafile", {}).get("repo_id"), default="")),
            seafile_target_repo_name=str(_pick(payload.get("seafile_target_repo_name"), targets.get("seafile", {}).get("repo_name"), default="")),
            azureblob_target_account_url=str(_pick(payload.get("azureblob_target_account_url"), targets.get("azureblob", {}).get("account_url"), default="")),
            azureblob_target_container=str(_pick(payload.get("azureblob_target_container"), targets.get("azureblob", {}).get("container"), default="")),
            azureblob_target_prefix=str(_pick(payload.get("azureblob_target_prefix"), targets.get("azureblob", {}).get("prefix"), default="")),
            azureblob_target_account_name=str(_pick(payload.get("azureblob_target_account_name"), targets.get("azureblob", {}).get("account_name"), default="")),
            azureblob_target_account_key=str(_pick(payload.get("azureblob_target_account_key"), targets.get("azureblob", {}).get("account_key"), default="")),
            smb_target_url=str(_pick(payload.get("smb_target_url"), targets.get("smb", {}).get("url"), default="")),
            smb_target_username=str(_pick(payload.get("smb_target_username"), targets.get("smb", {}).get("username"), default="")),
            smb_target_password=str(_pick(payload.get("smb_target_password"), targets.get("smb", {}).get("password"), default="")),
            ftp_target_url=str(_pick(payload.get("ftp_target_url"), targets.get("ftp", {}).get("url"), default="")),
            ftp_target_username=str(_pick(payload.get("ftp_target_username"), targets.get("ftp", {}).get("username"), default="")),
            ftp_target_password=str(_pick(payload.get("ftp_target_password"), targets.get("ftp", {}).get("password"), default="")),
            sftp_target_url=str(_pick(payload.get("sftp_target_url"), targets.get("sftp", {}).get("url"), default="")),
            sftp_target_username=str(_pick(payload.get("sftp_target_username"), targets.get("sftp", {}).get("username"), default="")),
            sftp_target_password=str(_pick(payload.get("sftp_target_password"), targets.get("sftp", {}).get("password"), default="")),
            delete_removed=bool(_pick(payload.get("delete_removed"), sync.get("delete_removed"), default=False)),
            target_delete_removed=bool(_pick(payload.get("target_delete_removed"), sync.get("target_delete_removed"), default=False)),
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
            app_admin_username=str(_pick(payload.get("app_admin_username"), app.get("admin_username"), default="")),
            app_admin_password=str(_pick(payload.get("app_admin_password"), app.get("admin_password"), default="")),
            log_file=Path(_pick(payload.get("log_file"), state_cfg.get("log_file"), default=".state/sync.log")),
        )

    @staticmethod
    def normalize_openlist_mode(value: str) -> str:
        normalized = str(value or "").strip().lower()
        if normalized == "external":
            return "external_local"
        if normalized == "managed":
            return "managed_binary"
        allowed = {"external_local", "external_remote", "managed_binary", "managed_docker_placeholder"}
        return normalized if normalized in allowed else "external_local"

    @staticmethod
    def is_managed_openlist_mode(value: str) -> bool:
        return AppConfig.normalize_openlist_mode(value).startswith("managed_")

    def active_openlist_profile(self) -> str:
        return self.normalize_openlist_mode(self.openlist_mode)

    def ensure_parent_dirs(self) -> None:
        for target in (self.state_file, self.export_file, self.log_file):
            target.parent.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.managed_openlist_data_dir.mkdir(parents=True, exist_ok=True)
        self.local_target_root.mkdir(parents=True, exist_ok=True)

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
            "external_local_openlist_url": self.external_local_openlist_url,
            "external_local_openlist_token": self.external_local_openlist_token,
            "external_local_openlist_username": self.external_local_openlist_username,
            "external_local_openlist_password": self.external_local_openlist_password,
            "external_remote_openlist_url": self.external_remote_openlist_url,
            "external_remote_openlist_token": self.external_remote_openlist_token,
            "external_remote_openlist_username": self.external_remote_openlist_username,
            "external_remote_openlist_password": self.external_remote_openlist_password,
            "managed_openlist_token": self.managed_openlist_token,
            "managed_openlist_username": self.managed_openlist_username,
            "managed_openlist_password": self.managed_openlist_password,
            "managed_openlist_init_username": self.managed_openlist_init_username,
            "managed_openlist_init_password": self.managed_openlist_init_password,
            "guangya_phone": self.guangya_phone,
            "target_key": self.target_key,
            "guangya_authorization": self.guangya_authorization,
            "guangya_access_token": self.guangya_access_token,
            "guangya_refresh_token": self.guangya_refresh_token,
            "guangya_device_id": self.guangya_device_id,
            "local_target_root": str(self.local_target_root),
            "webdav_target_url": self.webdav_target_url,
            "webdav_target_username": self.webdav_target_username,
            "webdav_target_password": self.webdav_target_password,
            "s3_target_endpoint": self.s3_target_endpoint,
            "s3_target_bucket": self.s3_target_bucket,
            "s3_target_prefix": self.s3_target_prefix,
            "s3_target_access_key": self.s3_target_access_key,
            "s3_target_secret_key": self.s3_target_secret_key,
            "s3_target_region": self.s3_target_region,
            "seafile_target_url": self.seafile_target_url,
            "seafile_target_token": self.seafile_target_token,
            "seafile_target_username": self.seafile_target_username,
            "seafile_target_password": self.seafile_target_password,
            "seafile_target_repo_id": self.seafile_target_repo_id,
            "seafile_target_repo_name": self.seafile_target_repo_name,
            "azureblob_target_account_url": self.azureblob_target_account_url,
            "azureblob_target_container": self.azureblob_target_container,
            "azureblob_target_prefix": self.azureblob_target_prefix,
            "azureblob_target_account_name": self.azureblob_target_account_name,
            "azureblob_target_account_key": self.azureblob_target_account_key,
            "smb_target_url": self.smb_target_url,
            "smb_target_username": self.smb_target_username,
            "smb_target_password": self.smb_target_password,
            "ftp_target_url": self.ftp_target_url,
            "ftp_target_username": self.ftp_target_username,
            "ftp_target_password": self.ftp_target_password,
            "sftp_target_url": self.sftp_target_url,
            "sftp_target_username": self.sftp_target_username,
            "sftp_target_password": self.sftp_target_password,
            "delete_removed": self.delete_removed,
            "target_delete_removed": self.target_delete_removed,
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
            "app_admin_username": self.app_admin_username,
            "app_admin_password": self.app_admin_password,
            "log_file": str(self.log_file),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "app": {
                "name": "CloudPan Bridge",
                "bind_host": self.bind_host,
                "bind_port": self.bind_port,
                "admin_username": self.app_admin_username,
                "admin_password": self.app_admin_password,
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
                "connections": {
                    "external_local": {
                        "url": self.external_local_openlist_url,
                        "token": self.external_local_openlist_token,
                        "username": self.external_local_openlist_username,
                        "password": self.external_local_openlist_password,
                    },
                    "external_remote": {
                        "url": self.external_remote_openlist_url,
                        "token": self.external_remote_openlist_token,
                        "username": self.external_remote_openlist_username,
                        "password": self.external_remote_openlist_password,
                    },
                    "managed_binary": {
                        "token": self.managed_openlist_token,
                        "username": self.managed_openlist_username,
                        "password": self.managed_openlist_password,
                    },
                },
                "managed_runtime": {
                    "bin": self.managed_openlist_bin,
                    "data_dir": str(self.managed_openlist_data_dir),
                    "port": self.managed_openlist_port,
                },
                "managed_init_admin": {
                    "username": self.managed_openlist_init_username,
                    "password": self.managed_openlist_init_password,
                },
                "managed_docker": {
                    "enabled": self.openlist_mode == "managed_docker_placeholder",
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
                },
                "localfs": {
                    "root": str(self.local_target_root),
                },
                "webdav": {
                    "url": self.webdav_target_url,
                    "username": self.webdav_target_username,
                    "password": self.webdav_target_password,
                },
                "s3": {
                    "endpoint": self.s3_target_endpoint,
                    "bucket": self.s3_target_bucket,
                    "prefix": self.s3_target_prefix,
                    "access_key": self.s3_target_access_key,
                    "secret_key": self.s3_target_secret_key,
                    "region": self.s3_target_region,
                },
                "seafile": {
                    "url": self.seafile_target_url,
                    "token": self.seafile_target_token,
                    "username": self.seafile_target_username,
                    "password": self.seafile_target_password,
                    "repo_id": self.seafile_target_repo_id,
                    "repo_name": self.seafile_target_repo_name,
                },
                "azureblob": {
                    "account_url": self.azureblob_target_account_url,
                    "container": self.azureblob_target_container,
                    "prefix": self.azureblob_target_prefix,
                    "account_name": self.azureblob_target_account_name,
                    "account_key": self.azureblob_target_account_key,
                },
                "smb": {
                    "url": self.smb_target_url,
                    "username": self.smb_target_username,
                    "password": self.smb_target_password,
                },
                "ftp": {
                    "url": self.ftp_target_url,
                    "username": self.ftp_target_username,
                    "password": self.ftp_target_password,
                },
                "sftp": {
                    "url": self.sftp_target_url,
                    "username": self.sftp_target_username,
                    "password": self.sftp_target_password,
                }
            },
            "sync": {
                "source_path": self.source_path,
                "target_path": self.target_path,
                "delete_removed": self.delete_removed,
                "target_delete_removed": self.target_delete_removed,
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
        openlist_mode="external_local",
        managed_openlist_bin="",
        managed_openlist_data_dir=Path(".runtime/openlist"),
        managed_openlist_port=5244,
        openlist_url="http://127.0.0.1:5244",
        openlist_token="",
        openlist_username="admin",
        openlist_password="",
        external_local_openlist_url="http://127.0.0.1:5244",
        external_local_openlist_token="",
        external_local_openlist_username="admin",
        external_local_openlist_password="",
        external_remote_openlist_url="",
        external_remote_openlist_token="",
        external_remote_openlist_username="admin",
        external_remote_openlist_password="",
        managed_openlist_token="",
        managed_openlist_username="admin",
        managed_openlist_password="",
        managed_openlist_init_username="admin",
        managed_openlist_init_password="",
        guangya_phone="+86 13800138000",
        target_key="guangya",
        guangya_authorization="",
        guangya_access_token="",
        guangya_refresh_token="",
        guangya_device_id="",
        local_target_root=Path(".exports/localfs"),
        webdav_target_url="",
        webdav_target_username="",
        webdav_target_password="",
        s3_target_endpoint="",
        s3_target_bucket="",
        s3_target_prefix="",
        s3_target_access_key="",
        s3_target_secret_key="",
        s3_target_region="",
        azureblob_target_account_url="",
        azureblob_target_container="",
        azureblob_target_prefix="",
        azureblob_target_account_name="",
        azureblob_target_account_key="",
        smb_target_url="",
        smb_target_username="",
        smb_target_password="",
        ftp_target_url="",
        ftp_target_username="",
        ftp_target_password="",
        sftp_target_url="",
        sftp_target_username="",
        sftp_target_password="",
        delete_removed=False,
        target_delete_removed=False,
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
        app_admin_username="",
        app_admin_password="",
        log_file=Path(".state/sync.log"),
    ).to_dict()
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
