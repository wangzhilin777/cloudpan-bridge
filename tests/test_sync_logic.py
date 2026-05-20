import json
from pathlib import Path, PurePosixPath

from fastapi.testclient import TestClient
import pytest

import cloudpan_bridge.provider_registry as provider_registry_module
from cloudpan_bridge.config import AppConfig
from cloudpan_bridge.cli import build_parser
from cloudpan_bridge.guangya_direct import GuangyaMiaochuanImporter
from cloudpan_bridge.guangya import GuangyaService
from cloudpan_bridge.fast_upload_decision import assess_directory_fast_upload
from cloudpan_bridge.provider_registry import build_source_mapping_context
from cloudpan_bridge.models import DirectImportResult, PendingFileState, QueueItemState, SourceEntry, SyncFileState, SyncPlanItem, SyncState, normalize_posix_path
from cloudpan_bridge.openlist_admin import OpenListDriverField, OpenListDriverInfo, build_storage_payload
from cloudpan_bridge.openlist import OpenListClient
from cloudpan_bridge.openlist_runtime import ManagedOpenListRuntime
from cloudpan_bridge.provider_capture import (
    build_capture_alias_to_spec_key_map,
    build_capture_supported_driver_aliases,
    build_driver_capture_spec,
    build_driver_prefill_values,
    default_provider_specs,
    derive_capture_requirements_from_fields,
    resolve_capture_spec_for_driver,
)
from cloudpan_bridge.source_adapter import OpenListSourceProvider, create_source_provider
from cloudpan_bridge.source_bridge_executor import execute_source_bridge
from cloudpan_bridge.source_bridge_registry import prepare_source_bridge
from cloudpan_bridge.source_enrich_bridge import build_bridge_runtime
from cloudpan_bridge.source_enrich import build_source_enrichment_runtime, enrich_batch, enrich_entry
from cloudpan_bridge.source_adapter import (
    build_source_provider_resolution,
    build_source_runtime_status,
    SourceProviderCompatMixin,
    build_source_provider_context,
    resolve_source_mount_path,
    source_download_stream,
    source_ensure_auth,
    source_get_file_fingerprints,
    source_get_runtime_context,
    source_walk_tree,
)
from cloudpan_bridge.transfer_planner import compute_fast_upload_hits, plan_transfer_mode, summarize_transfer_plan
from cloudpan_bridge.syncer import (
    SyncRunner,
    build_plan,
    build_source_miaochuan_payload,
    load_state,
    relative_target_path,
    render_tree,
    serialize_source_entry,
    summarize_source_entries,
)
from cloudpan_bridge.target_adapter import AzureBlobTargetAdapter, FtpTargetAdapter, GuangyaTargetAdapter, LocalFsTargetAdapter, OpenListTargetAdapter, S3TargetAdapter, SeafileTargetAdapter, SftpTargetAdapter, SmbTargetAdapter, WebDavTargetAdapter, target_delete_if_enabled, target_upload_stream
from cloudpan_bridge.web_runtime_utils import (
    build_pending_selected_execution_groups,
    compute_rate_limit_cooldown_ms,
    is_rate_limit_error_message,
)


def test_openlist_mode_snapshots_are_loaded_per_profile() -> None:
    cfg = AppConfig.from_payload(
        {
            "openlist": {
                "mode": "external_remote",
                "connections": {
                    "external_local": {
                        "url": "http://127.0.0.1:5244",
                        "username": "local-admin",
                    },
                    "external_remote": {
                        "url": "https://demo.example.com",
                        "token": "remote-token",
                        "username": "remote-admin",
                        "password": "remote-pass",
                    },
                    "managed_binary": {
                        "username": "managed-admin",
                        "password": "managed-pass",
                    },
                },
                "managed_init_admin": {
                    "username": "bootstrap-admin",
                    "password": "bootstrap-pass",
                },
            }
        }
    )
    assert cfg.openlist_mode == "external_remote"
    assert cfg.openlist_url == "https://demo.example.com"
    assert cfg.openlist_token == "remote-token"
    assert cfg.openlist_username == "remote-admin"
    assert cfg.external_local_openlist_username == "local-admin"
    assert cfg.managed_openlist_username == "managed-admin"
    assert cfg.managed_openlist_init_username == "bootstrap-admin"


def test_managed_runtime_status_requires_install_when_binary_missing(tmp_path: Path) -> None:
    runtime = ManagedOpenListRuntime(
        mode="managed_binary",
        configured_url="http://127.0.0.1:5244",
        data_dir=tmp_path / "runtime",
        binary_path="",
        port=5244,
    )
    status = runtime.status()
    assert status.mode == "managed_binary"
    assert status.install_required is True
    assert status.binary_exists is False
    assert "拉取" in status.message


def test_managed_docker_reports_missing_docker_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cloudpan_bridge.openlist_runtime.shutil.which", lambda _name: "")
    runtime = ManagedOpenListRuntime(
        mode="managed_docker",
        configured_url="http://127.0.0.1:5244",
        data_dir=tmp_path / "runtime",
        binary_path="",
        port=5244,
    )
    status = runtime.status()
    assert status.mode == "managed_docker"
    assert status.install_required is False
    assert status.can_start is False
    assert status.docker_available is False
    assert "Docker CLI" in status.message


def test_managed_docker_reports_detected_docker_without_daemon(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cloudpan_bridge.openlist_runtime.shutil.which", lambda _name: r"C:\Program Files\Docker\docker.exe")
    runtime = ManagedOpenListRuntime(
        mode="managed_docker",
        configured_url="http://127.0.0.1:5244",
        data_dir=tmp_path / "runtime",
        binary_path="",
        port=5244,
    )
    monkeypatch.setattr(runtime, "_docker_daemon_available", lambda: False)
    status = runtime.status()
    assert status.docker_available is True
    assert status.docker_cli.endswith("docker.exe")
    assert status.docker_daemon_available is False
    assert "daemon 不可用" in status.message


def test_managed_docker_start_runs_container_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = ManagedOpenListRuntime(
        mode="managed_docker",
        configured_url="http://127.0.0.1:5244",
        data_dir=tmp_path / "runtime",
        binary_path="",
        port=5244,
    )
    monkeypatch.setattr("cloudpan_bridge.openlist_runtime.shutil.which", lambda _name: r"C:\Program Files\Docker\docker.exe")
    monkeypatch.setattr(runtime, "_docker_daemon_available", lambda: True)
    inspect_state: dict[str, object | None] = {"value": None}
    calls: list[tuple[str, ...]] = []

    def fake_inspect() -> dict[str, object] | None:
        value = inspect_state["value"]
        return value if isinstance(value, dict) else None

    def fake_run_docker(*args: str, check: bool = False):  # noqa: ANN001
        calls.append(tuple(args))
        if args and args[0] == "run":
            inspect_state["value"] = {
                "Config": {"Image": runtime.docker_image},
                "HostConfig": {
                    "Binds": [runtime._docker_volume_spec()],
                    "PortBindings": {runtime._docker_port_key(): [{"HostPort": str(runtime.port)}]},
                },
                "State": {"Running": True},
            }

        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Result()

    monkeypatch.setattr(runtime, "_docker_inspect", fake_inspect)
    monkeypatch.setattr(runtime, "_run_docker", fake_run_docker)
    monkeypatch.setattr(runtime, "_is_alive", lambda _base_url: True)
    monkeypatch.setattr("cloudpan_bridge.openlist_runtime.time.sleep", lambda _seconds: None)
    status = runtime.start()
    assert any(item and item[0] == "run" for item in calls)
    assert status.mode == "managed_docker"
    assert status.running is True
    assert status.docker_container_exists is True


def test_normalize_posix_path() -> None:
    assert normalize_posix_path("abc/def.txt") == "/abc/def.txt"
    assert normalize_posix_path("/abc/../abc/def.txt") == "/abc/def.txt"


def test_cli_serve_parser_accepts_host_and_port() -> None:
    parser = build_parser()
    args = parser.parse_args(["serve", "--config", ".work/openlist-config.json", "--host", "0.0.0.0", "--port", "8765"])
    assert args.command == "serve"
    assert args.host == "0.0.0.0"
    assert args.port == 8765


def test_build_plan_marks_new_and_changed_entries() -> None:
    state = SyncState(
        files={
            "/root/a.txt": SyncFileState(path="/root/a.txt", md5="AAA", size=1, last_op_time="1"),
            "/root/old.txt": SyncFileState(path="/root/old.txt", md5="OLD", size=2, last_op_time="1"),
        }
    )
    entries = [
        SourceEntry(path="/root/a.txt", md5="BBB", size=1, last_op_time="2"),
        SourceEntry(path="/root/new.bin", md5="CCC", size=1024 * 1024, last_op_time="3"),
    ]

    plan, removed = build_plan(entries, state)

    assert [item.action for item in plan] == ["update", "create"]
    assert [item.requires_download for item in plan] == [False, False]
    assert removed == ["/root/old.txt"]


def test_relative_target_path_preserves_directory_structure() -> None:
    actual = relative_target_path("/我的资源", "/我的资源/照片/1.jpg", "/天翼同步")
    assert PurePosixPath(actual) == PurePosixPath("/天翼同步/照片/1.jpg")


def test_relative_target_path_keeps_leaf_stream_parent_hierarchy() -> None:
    actual = relative_target_path(
        "/2-天翼云盘",
        "/2-天翼云盘/我的图片/22081212C相册/0/2024年08月/1.jpg",
        "/",
    )
    assert PurePosixPath(actual) == PurePosixPath("/我的图片/22081212C相册/0/2024年08月/1.jpg")


def test_render_tree_contains_nested_indentation() -> None:
    text = render_tree(["/根/文件1.txt", "/根/子目录/文件2.txt"])
    assert "- 文件1.txt" in text
    assert "    - 文件2.txt" in text


def test_openlist_directory_helpers() -> None:
    assert OpenListClient._normalize_dir("\\挂载1\\相册\\") == "/挂载1/相册"
    assert OpenListClient._parent("/挂载1/相册") == "/挂载1"
    assert OpenListClient._parent("/") is None


def test_config_has_scan_throttle_defaults(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    assert cfg.openlist_page_size == 200
    assert cfg.openlist_request_interval_ms == 300
    assert cfg.queue_interval_ms == 3000
    assert cfg.auto_download_threshold_mb == 10
    assert cfg.source_provider_preference == "auto"
    assert cfg.to_flat_dict()["openlist_page_size"] == 200
    assert cfg.to_flat_dict()["queue_interval_ms"] == 3000
    assert cfg.to_flat_dict()["provider_captures"] == {}


def test_config_supports_nested_structure_roundtrip(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "app": {
    "bind_host": "127.0.0.1",
    "bind_port": 9876
  },
  "openlist": {
    "mode": "external",
    "url": "http://127.0.0.1:5244",
    "username": "admin",
    "password": "demo",
    "managed_runtime": {
      "bin": "openlist.exe",
      "data_dir": ".runtime/openlist",
      "port": 5244
    }
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {
      "phone": "+86 13800138000",
      "authorization": "Bearer abc",
      "access_token": "tok",
      "refresh_token": "refresh",
      "device_id": "device"
    },
    "webdav": {
      "url": "https://dav.example.com/root",
      "username": "dav-user",
      "password": "dav-pass"
    },
    "s3": {
      "endpoint": "https://s3.example.com",
      "bucket": "archive-bucket",
      "prefix": "cloudpan-bridge/archive",
      "access_key": "AKIA_TEST",
      "secret_key": "SECRET_TEST",
      "region": "ap-southeast-1"
    },
    "seafile": {
      "url": "https://seafile.example.com",
      "token": "seafile-token",
      "username": "seafile-user",
      "password": "seafile-pass",
      "repo_id": "repo-1",
      "repo_name": "Archive"
    },
    "azureblob": {
      "account_url": "https://demo.blob.core.windows.net",
      "container": "archive-container",
      "prefix": "cloudpan-bridge/archive",
      "account_name": "demo-account",
      "account_key": "azure-key"
    },
    "smb": {
      "url": "smb://nas/share/archive",
      "username": "smb-user",
      "password": "smb-pass"
    },
    "ftp": {
      "url": "ftp://ftp.example.com:21/root",
      "username": "ftp-user",
      "password": "ftp-pass"
    },
    "sftp": {
      "url": "sftp://sftp.example.com:22/root",
      "username": "sftp-user",
      "password": "sftp-pass"
    }
  },
  "sync": {
    "source_path": "/src",
    "target_path": "/dst",
    "openlist_page_size": 120,
    "openlist_request_interval_ms": 600,
    "queue_interval_ms": 2500,
    "auto_download_threshold_mb": 8,
    "rate_limit_mode": "balanced"
  },
  "source_session": {
    "provider_preference": "direct_preferred",
    "provider_captures": {
      "quark": {
        "status": "captured",
        "captured": {
          "cookie_header": "k=v"
        }
      }
    }
  },
  "ui": {
    "language": "mix",
    "coverage_filters": {
      "onlyGaps": true
    },
    "browser": {
      "current_path": "/browse",
      "mounted_source": "/mount"
    },
    "panel_open_states": {
      "basic_config": true
    }
  },
  "state": {
    "state_file": ".state/sync-state.json",
    "export_file": ".work/source-export.jsonl",
    "temp_dir": ".work/download-cache",
    "log_file": ".state/sync.log"
  }
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    assert cfg.source_path == "/src"
    assert cfg.target_path == "/dst"
    assert cfg.openlist_password == "demo"
    assert cfg.target_key == "guangya"
    assert cfg.guangya_refresh_token == "refresh"
    assert cfg.local_target_root == Path(".exports/localfs")
    assert cfg.webdav_target_url == "https://dav.example.com/root"
    assert cfg.webdav_target_username == "dav-user"
    assert cfg.webdav_target_password == "dav-pass"
    assert cfg.s3_target_endpoint == "https://s3.example.com"
    assert cfg.s3_target_bucket == "archive-bucket"
    assert cfg.s3_target_prefix == "cloudpan-bridge/archive"
    assert cfg.s3_target_access_key == "AKIA_TEST"
    assert cfg.s3_target_secret_key == "SECRET_TEST"
    assert cfg.s3_target_region == "ap-southeast-1"
    assert cfg.seafile_target_url == "https://seafile.example.com"
    assert cfg.seafile_target_token == "seafile-token"
    assert cfg.seafile_target_username == "seafile-user"
    assert cfg.seafile_target_password == "seafile-pass"
    assert cfg.seafile_target_repo_id == "repo-1"
    assert cfg.seafile_target_repo_name == "Archive"
    assert cfg.azureblob_target_account_url == "https://demo.blob.core.windows.net"
    assert cfg.azureblob_target_container == "archive-container"
    assert cfg.azureblob_target_prefix == "cloudpan-bridge/archive"
    assert cfg.azureblob_target_account_name == "demo-account"
    assert cfg.azureblob_target_account_key == "azure-key"
    assert cfg.smb_target_url == "smb://nas/share/archive"
    assert cfg.smb_target_username == "smb-user"
    assert cfg.smb_target_password == "smb-pass"
    assert cfg.ftp_target_url == "ftp://ftp.example.com:21/root"
    assert cfg.ftp_target_username == "ftp-user"
    assert cfg.ftp_target_password == "ftp-pass"
    assert cfg.sftp_target_url == "sftp://sftp.example.com:22/root"
    assert cfg.sftp_target_username == "sftp-user"
    assert cfg.sftp_target_password == "sftp-pass"
    assert cfg.target_delete_removed is False
    assert cfg.source_provider_preference == "direct_preferred"
    assert cfg.provider_captures["quark"]["captured"]["cookie_header"] == "k=v"
    assert cfg.ui_language == "mix"
    assert cfg.coverage_filters["onlyGaps"] is True
    assert cfg.browser_state["current_path"] == "/browse"
    nested = cfg.to_dict()
    assert nested["sync"]["source_path"] == "/src"
    assert nested["targets"]["guangya"]["device_id"] == "device"
    assert nested["targets"]["webdav"]["url"] == "https://dav.example.com/root"
    assert nested["targets"]["s3"]["endpoint"] == "https://s3.example.com"
    assert nested["targets"]["s3"]["bucket"] == "archive-bucket"
    assert nested["targets"]["seafile"]["url"] == "https://seafile.example.com"
    assert nested["targets"]["seafile"]["repo_id"] == "repo-1"
    assert nested["targets"]["azureblob"]["account_url"] == "https://demo.blob.core.windows.net"
    assert nested["targets"]["azureblob"]["container"] == "archive-container"
    assert nested["targets"]["smb"]["url"] == "smb://nas/share/archive"
    assert nested["targets"]["ftp"]["url"] == "ftp://ftp.example.com:21/root"
    assert nested["targets"]["sftp"]["url"] == "sftp://sftp.example.com:22/root"
    assert nested["source_session"]["provider_captures"]["quark"]["captured"]["cookie_header"] == "k=v"
    assert nested["source_session"]["provider_preference"] == "direct_preferred"
    assert nested["ui"]["language"] == "mix"
    assert nested["ui"]["browser"]["mounted_source"] == "/mount"
    flat = cfg.to_flat_dict()
    assert flat["bind_port"] == 9876
    assert flat["openlist_password"] == "demo"
    assert flat["ui_language"] == "mix"


def test_config_supports_flat_legacy_structure_and_writes_nested(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "target_key": "guangya",
  "openlist_password": "legacy-pass",
  "guangya_refresh_token": "legacy-refresh",
  "webdav_target_url": "https://dav.example.com/legacy",
  "webdav_target_username": "legacy-dav",
  "webdav_target_password": "legacy-pass",
  "s3_target_endpoint": "https://legacy-s3.example.com",
  "s3_target_bucket": "legacy-bucket",
  "s3_target_prefix": "legacy-prefix",
  "s3_target_access_key": "legacy-ak",
  "s3_target_secret_key": "legacy-sk",
  "s3_target_region": "cn-test-1",
  "seafile_target_url": "https://legacy-seafile.example.com",
  "seafile_target_token": "legacy-seafile-token",
  "seafile_target_username": "legacy-seafile",
  "seafile_target_password": "legacy-seafile-pass",
  "seafile_target_repo_id": "legacy-repo-id",
  "seafile_target_repo_name": "Legacy Repo",
  "azureblob_target_account_url": "https://legacy.blob.core.windows.net",
  "azureblob_target_container": "legacy-container",
  "azureblob_target_prefix": "legacy-prefix",
  "azureblob_target_account_name": "legacy-azure",
  "azureblob_target_account_key": "legacy-azure-key",
  "smb_target_url": "smb://legacy-nas/share/root",
  "smb_target_username": "legacy-smb",
  "smb_target_password": "legacy-smb-pass",
  "ftp_target_url": "ftp://legacy.example.com/root",
  "ftp_target_username": "legacy-ftp",
  "ftp_target_password": "legacy-ftp-pass",
  "sftp_target_url": "sftp://legacy.example.com/root",
  "sftp_target_username": "legacy-sftp",
  "sftp_target_password": "legacy-sftp-pass"
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    serialized = cfg.to_dict()
    assert serialized["sync"]["source_path"] == "/src"
    assert serialized["targets"]["active_target"] == "guangya"
    assert serialized["targets"]["guangya"]["refresh_token"] == "legacy-refresh"
    assert serialized["targets"]["localfs"]["root"] == str(Path(".exports/localfs"))
    assert serialized["targets"]["webdav"]["url"] == "https://dav.example.com/legacy"
    assert serialized["targets"]["webdav"]["username"] == "legacy-dav"
    assert serialized["targets"]["s3"]["endpoint"] == "https://legacy-s3.example.com"
    assert serialized["targets"]["s3"]["bucket"] == "legacy-bucket"
    assert serialized["targets"]["s3"]["access_key"] == "legacy-ak"
    assert serialized["targets"]["seafile"]["url"] == "https://legacy-seafile.example.com"
    assert serialized["targets"]["seafile"]["token"] == "legacy-seafile-token"
    assert serialized["targets"]["seafile"]["repo_id"] == "legacy-repo-id"
    assert serialized["targets"]["azureblob"]["account_url"] == "https://legacy.blob.core.windows.net"
    assert serialized["targets"]["azureblob"]["container"] == "legacy-container"
    assert serialized["targets"]["azureblob"]["account_name"] == "legacy-azure"
    assert serialized["targets"]["smb"]["url"] == "smb://legacy-nas/share/root"
    assert serialized["targets"]["smb"]["username"] == "legacy-smb"
    assert serialized["targets"]["ftp"]["url"] == "ftp://legacy.example.com/root"
    assert serialized["targets"]["ftp"]["username"] == "legacy-ftp"
    assert serialized["targets"]["sftp"]["url"] == "sftp://legacy.example.com/root"
    assert serialized["targets"]["sftp"]["username"] == "legacy-sftp"
    assert serialized["sync"]["target_delete_removed"] is False
    assert "source_path" not in serialized


def test_config_roundtrip_provider_captures(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "provider_captures": {
    "quark": {
      "status": "captured",
      "captured": {
        "cookie_header": "k=v"
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    assert cfg.provider_captures == {
        "quark": {
            "status": "captured",
            "captured": {
                "cookie_header": "k=v",
            },
        }
    }
    assert cfg.to_flat_dict()["provider_captures"]["quark"]["captured"]["cookie_header"] == "k=v"


def test_config_roundtrip_source_provider_preference(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "source_session": {
    "provider_preference": "openlist_only"
  }
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    assert cfg.source_provider_preference == "openlist_only"
    assert cfg.to_flat_dict()["source_provider_preference"] == "openlist_only"
    assert cfg.to_dict()["source_session"]["provider_preference"] == "openlist_only"


def test_config_roundtrip_mount_provider_mapping(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "source_session": {
    "mount_provider_mapping": {
      "/alist/quark": "quark",
      "/alist/mystery": "generic"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    assert cfg.mount_provider_mapping == {
        "/alist/quark": "quark",
        "/alist/mystery": "generic",
    }
    assert cfg.to_flat_dict()["mount_provider_mapping"]["/alist/quark"] == "quark"
    assert cfg.to_dict()["source_session"]["mount_provider_mapping"]["/alist/mystery"] == "generic"


def test_sync_state_supports_generic_target_states_and_legacy_guangya_tokens() -> None:
    restored = SyncState.from_dict(
        {
            "guangya_tokens": {
                "access_token": "legacy-token",
                "refresh_token": "legacy-refresh",
            },
            "target_states": {
                "demo": {
                    "token": "demo-token",
                }
            },
        }
    )
    assert restored.get_target_state("guangya")["access_token"] == "legacy-token"
    assert restored.get_target_state("demo")["token"] == "demo-token"
    restored.set_target_state("guangya", {"access_token": "new-token"})
    dumped = restored.to_dict()
    assert dumped["guangya_tokens"]["access_token"] == "new-token"
    assert dumped["target_states"]["guangya"]["access_token"] == "new-token"


def test_auto_download_threshold_zero_disables_fallback(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "auto_download_threshold_mb": 0
}
""".strip(),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    item = build_plan([SourceEntry(path="/src/a.txt", md5="ABC", size=1024, last_op_time="1")], SyncState())[0][0]
    assert runner._should_auto_download(item) is False


def test_auto_download_threshold_accepts_small_file(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "auto_download_threshold_mb": 10
}
""".strip(),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)


def test_openlist_source_provider_reports_provider_key_and_auth_state() -> None:
    provider = OpenListSourceProvider(
        base_url="http://127.0.0.1:5244",
        token="demo-token",
        username="admin",
        password="demo-pass",
    )
    try:
        assert provider.get_provider_key() == "openlist"
        assert provider.get_auth_state()["base_url"] == "http://127.0.0.1:5244"
        assert provider.get_auth_state()["token"] == "demo-token"
        assert provider.get_auth_state()["username"] == "admin"
    finally:
        provider.close()


def test_create_source_provider_returns_openlist_provider(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "openlist": {
    "url": "http://127.0.0.1:5244",
    "token": "token-1",
    "username": "admin",
    "password": "demo"
  }
}
""".strip(),
        encoding="utf-8",
    )
    provider = create_source_provider(AppConfig.load(path))
    try:
        assert provider.get_provider_key() == "openlist"
        assert provider.get_auth_state()["token"] == "token-1"
        assert provider.get_runtime_context()["source_mode"] == "openlist_mount"
    finally:
        provider.close()


def test_source_provider_context_uses_longest_mount_prefix_and_override(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/quark/photos/2026",
                    "target_path": "/dst",
                    "target_key": "guangya",
                },
                "source_session": {
                    "mount_provider_mapping": {
                        "/alist": "generic",
                        "/alist/quark": "quark",
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    assert resolve_source_mount_path("/alist/quark/photos/2026", cfg.mount_provider_mapping or {}, "") == "/alist/quark"
    context = build_source_provider_context(cfg)
    assert context["mount_path"] == "/alist/quark"
    assert context["provider_key"] == "quark"
    assert context["source_mode"] == "openlist_mount"
    assert context["target_mode"] == "metadata_import"


def test_source_runtime_context_helper_reads_real_provider_context(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/quark/demo",
                    "target_path": "/dst",
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                    "token": "token-1",
                },
                "source_session": {
                    "mount_provider_mapping": {
                        "/alist/quark": "quark",
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    provider = create_source_provider(AppConfig.load(path))
    try:
        context = source_get_runtime_context(provider)
        assert context["provider_key"] == "quark"
        assert context["effective_driver"] == "quark"
        assert context["supports_fast_upload"] is True
    finally:
        provider.close()


def test_build_source_runtime_status_exposes_provider_runtime_shape(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/quark/demo",
                    "target_path": "/dst",
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                    "token": "token-1",
                    "username": "admin",
                },
                "source_session": {
                    "mount_provider_mapping": {
                        "/alist/quark": "quark",
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_runtime_status(AppConfig.load(path))
    assert runtime["provider_class"] == "OpenListSourceProvider"
    assert runtime["provider_factory"] == "create_source_provider"
    assert runtime["execution_provider_class"] == "OpenListSourceProvider"
    assert runtime["execution_provider_factory"] == "create_source_provider"
    assert runtime["provider_key"] == "quark"
    assert runtime["requested_provider_preference"] == "auto"
    assert runtime["selected_source_mode"] == "openlist_with_capture_gap_candidate"
    assert runtime["auth_state"]["base_url"] == "http://127.0.0.1:5244"
    assert runtime["auth_state"]["username"] == "admin"
    assert runtime["auth_state"]["has_token"] is True
    assert runtime["direct_provider_candidate"] is True
    assert runtime["source_enrichment"]["provider_key"] == "quark"
    assert runtime["source_enrichment"]["capture_ready"] is False
    assert runtime["bridge_preparation"]["hook_registered"] is True
    assert runtime["bridge_preparation"]["execution_state"] == "missing_capture"
    assert runtime["source_target_route"]["decision_bucket"] == "capture_gap_before_fast"
    assert runtime["source_target_route"]["bridge_recoverable_fast_hashes"] == ["md5"]
    assert runtime["source_target_route"]["route_honesty"] == "capture_missing_before_fast_upload"
    assert runtime["source_target_route"]["preferred_execution_mode"] == "record_pending_only"


def test_source_provider_resolution_prefers_direct_candidate_but_falls_back_honestly(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/quark/demo",
                    "target_path": "/dst",
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                    "token": "token-1",
                    "username": "admin",
                },
                "source_session": {
                    "provider_preference": "direct_preferred",
                    "mount_provider_mapping": {
                        "/alist/quark": "quark",
                    },
                    "provider_captures": {
                        "quark": {
                            "status": "captured",
                            "captured": {
                                "cookie_header": "sid=1; token=2",
                            },
                        }
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    context = build_source_provider_context(cfg)
    resolution = build_source_provider_resolution(cfg, context)
    assert resolution["requested_provider_preference"] == "direct_preferred"
    assert resolution["direct_provider_candidate"] is True
    assert resolution["direct_provider_ready"] is True
    assert resolution["source_enrichment"]["provider_key"] == "quark"
    assert resolution["source_enrichment"]["capture_ready"] is True
    assert resolution["bridge_preparation"]["transport_hint"] == "cookie_snapshot"
    assert resolution["bridge_preparation"]["selected_field_names"] == ["cookie_header"]
    assert resolution["selected_source_mode"] == "direct_provider_bridge_ready"
    assert resolution["selected_provider_key"] == "quark"
    assert resolution["source_target_route"]["decision_bucket"] == "session_bridge_fast_candidate"
    assert resolution["source_target_route"]["next_focus"] == "validate_fast_hash_hit_rate"
    assert resolution["source_target_route"]["route_honesty"] == "session_bridge_ready_but_transport_not_direct"
    assert resolution["source_target_route"]["preferred_execution_mode"] == "fast_upload"
    assert "回退 OpenList" in resolution["fallback_reason"]


def test_create_source_provider_runtime_context_includes_resolution(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/quark/demo",
                    "target_path": "/dst",
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                    "token": "token-1",
                    "username": "admin",
                },
                "source_session": {
                    "provider_preference": "direct_preferred",
                    "mount_provider_mapping": {
                        "/alist/quark": "quark",
                    },
                    "provider_captures": {
                        "quark": {
                            "status": "captured",
                            "captured": {
                                "cookie_header": "sid=1; token=2",
                            },
                        }
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    provider = create_source_provider(AppConfig.load(path))
    runtime = provider.get_runtime_context()
    assert runtime["selected_source_mode"] == "direct_provider_bridge_ready"
    assert runtime["selected_provider_key"] == "quark"
    assert runtime["source_target_route"]["decision_bucket"] == "session_bridge_fast_candidate"
    assert runtime["execution_provider_class"] == "OpenListSourceProvider"
    assert "回退 OpenList" in runtime["fallback_reason"]
    provider.close()


def test_source_provider_resolution_marks_api_pending_candidate_honestly(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/onedrive/demo",
                    "target_path": "/dst",
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                    "token": "token-1",
                    "username": "admin",
                },
                "source_session": {
                    "provider_preference": "direct_preferred",
                    "mount_provider_mapping": {
                        "/alist/onedrive": "onedrive",
                    },
                    "provider_captures": {
                        "onedrive": {
                            "status": "captured",
                            "captured": {
                                "refresh_token": "demo-refresh",
                            },
                        }
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    context = build_source_provider_context(cfg)
    resolution = build_source_provider_resolution(cfg, context)
    assert resolution["direct_provider_candidate"] is True
    assert resolution["direct_provider_ready"] is False
    assert resolution["direct_provider_api_pending"] is True
    assert resolution["direct_provider_capture_missing"] is False
    assert resolution["selected_source_mode"] == "direct_provider_api_pending"
    assert "API 型直连 provider 候选" in resolution["fallback_reason"]


def test_source_enrichment_runtime_reports_mainstream_provider_capture_state(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "thunder": {
                            "status": "captured",
                            "captured": {
                                "authorization": "Bearer demo",
                                "device_id": "dev-1",
                            },
                        }
                    },
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "thunder")
    assert runtime["supported"] is True
    assert runtime["capture_ready"] is True
    assert "gcid" in runtime["preferred_hashes"]
    assert runtime["bridge_runtime"]["status"] == "bridge_ready_but_api_pending"
    assert runtime["bridge_runtime"]["matched_groups"] == [["authorization", "device_id"]]
    assert runtime["bridge_preparation_summary"]["transport_hint"] == "authorization_plus_device_id"
    assert runtime["bridge_preparation_summary"]["fingerprint_expectation"] == ["gcid", "md5", "sha1"]
    assert runtime["bridge_preparation_summary"]["preferred_hashes"] == ["gcid", "md5"]
    assert runtime["bridge_preparation_summary"]["selected_field_names"] == ["authorization", "device_id"]
    assert runtime["bridge_preparation_summary"]["throttle_defaults"]["rate_mode"] == "strict"
    assert runtime["bridge_preparation_summary"]["fallback_policy"]["pending_only_when_hash_missing"] is True
    assert runtime["bridge_maturity_summary"]["level"] == "api_capture_ready_pending_provider_enrich"


def test_source_enrichment_runtime_marks_session_bridge_ready_when_capture_available(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "quark": {
                            "status": "captured",
                            "captured": {
                                "cookie_header": "sid=1; token=2",
                            },
                        }
                    },
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "quark")
    assert runtime["capture_ready"] is True
    assert runtime["bridge_status"] == "bridge_ready"
    assert runtime["bridge_runtime"]["status"] == "bridge_ready"
    assert runtime["bridge_runtime"]["next_action"] == "prepare_quark_session_bridge"
    assert runtime["bridge_maturity_summary"]["level"] == "session_snapshot_ready"


def test_source_enrichment_runtime_reports_189cloud_session_bridge_summary(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "189cloud": {
                            "status": "captured",
                            "captured": {
                                "cookie_header": "sid=1",
                            },
                        }
                    },
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "189Cloud")
    assert runtime["capture_ready"] is True
    assert runtime["bridge_preparation_summary"]["transport_hint"] == "cookie_or_session_snapshot"
    assert runtime["bridge_preparation_summary"]["fingerprint_expectation"] == ["md5"]
    assert runtime["bridge_preparation_summary"]["preferred_hashes"] == ["md5"]
    assert runtime["bridge_preparation_summary"]["throttle_defaults"]["request_interval_ms"] == 900
    assert runtime["bridge_preparation_summary"]["fallback_policy"]["allow_auto_download"] is True
    assert runtime["bridge_maturity_summary"]["level"] == "session_snapshot_ready"


def test_source_enrichment_runtime_reports_123pan_session_bridge_summary(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "123pan": {
                            "status": "captured",
                            "captured": {
                                "access_token": "token-123",
                                "refresh_token": "refresh-123",
                            },
                        }
                    },
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "123Pan")
    assert runtime["capture_ready"] is True
    assert runtime["bridge_preparation_summary"]["selected_field_names"] == ["access_token", "refresh_token"]
    assert runtime["bridge_preparation_summary"]["fingerprint_expectation"] == ["md5", "sha1"]
    assert runtime["bridge_maturity_summary"]["level"] == "session_snapshot_ready"


def test_source_enrichment_promotes_hashes_from_existing_raw_fields(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/a.bin",
        md5="",
        size=10,
        provider="thunder",
        raw_hash_info={"file_gcid": "GCID-123", "md5": "md5-abc"},
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.gcid == "GCID-123"
    assert enriched.md5 == "MD5-ABC"
    assert report["changed"] is True


def test_source_enrichment_keeps_onedrive_etag_outside_md5(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/onedrive.docx",
        md5="",
        size=10,
        provider="OneDrive",
        raw_hash_info={"etag": "not-md5-etag-value"},
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.md5 == ""
    assert report["changed"] is False


def test_source_enrichment_allows_baidu_etag_as_md5(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/baidu.bin",
        md5="",
        size=10,
        provider="Baidu",
        raw_hash_info={"etag": "abcdef0123456789abcdef0123456789"},
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert report["changed"] is True
    assert report["bridge_execution_state"] == "session_snapshot_normalized"
    assert report["bridge_executor"] == "prepare_baidu_session_bridge"
    assert report["candidate_hashes"][0] == "md5"
    assert report["fast_upload_ready_after_bridge"] is True


def test_source_enrichment_derives_sha1_from_tagged_content_hash(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/onedrive-tagged.bin",
        md5="",
        size=10,
        provider="OneDrive",
        raw_hash_info={"content_hash": "sha1:abcdef0123456789abcdef0123456789abcdef01"},
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.sha1 == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert report["candidate_hashes"] == ["sha1", "content_hash"]
    assert report["changed"] is True


def test_source_enrichment_derives_md5_from_tagged_content_hash(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/provider-tagged.bin",
        md5="",
        size=10,
        provider="123Pan",
        raw_hash_info={"content_hash": "md5=abcdef0123456789abcdef0123456789"},
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert report["fast_upload_ready_after_bridge"] is True
    assert report["changed"] is True


def test_source_enrichment_reads_nested_hash_info_payloads(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/nested-thunder.bin",
        md5="",
        size=10,
        provider="Thunder",
        raw_hash_info={
            "metadata": {
                "hash_info": {
                    "file_gcid": "G" * 40,
                    "md5": "abcdef0123456789abcdef0123456789",
                }
            }
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.gcid == "G" * 40
    assert enriched.md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert report["candidate_hashes"][:2] == ["md5", "gcid"]
    assert report["fast_upload_ready_after_bridge"] is True


def test_source_enrichment_reads_nested_content_hash_from_provider_specific(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/nested-onedrive.bin",
        md5="",
        size=10,
        provider="OneDrive",
        provider_specific={
            "metadata": "{\"content_hash\":\"sha1:abcdef0123456789abcdef0123456789abcdef01\"}"
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.sha1 == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert "sha1" in report["candidate_hashes"]


def test_source_enrichment_reads_stringified_nested_hash_info_payloads(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/stringified-quark.bin",
        md5="",
        size=10,
        provider="Quark",
        provider_specific={
            "metadata": "{\"hash_info\":{\"sha1\":\"abcdef0123456789abcdef0123456789abcdef01\",\"slice_md5\":\"abcdef0123456789abcdef0123456789\"}}"
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.sha1 == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert enriched.slice_md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert "sha1" in report["candidate_hashes"]
    assert "slice_md5" in report["candidate_hashes"]


def test_source_enrichment_derives_gcid_from_tagged_digest_string(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/gcid-digest.bin",
        md5="",
        size=10,
        provider="Thunder",
        raw_hash_info={
            "digest": "gcid=abcdef0123456789abcdef0123456789abcdef01; md5=abcdef0123456789abcdef0123456789"
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.gcid == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert enriched.md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert "gcid" in report["candidate_hashes"]


def test_source_enrichment_derives_slice_md5_from_tagged_hash_string(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/slice-md5-hash.bin",
        md5="",
        size=10,
        provider="Quark",
        raw_hash_info={
            "hash": "slice_md5=abcdef0123456789abcdef0123456789&sha1=abcdef0123456789abcdef0123456789abcdef01"
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.slice_md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert enriched.sha1 == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert "slice_md5" in report["candidate_hashes"]


def test_source_enrichment_reads_algorithm_list_hash_payloads(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/quark-hash-list.bin",
        md5="",
        size=10,
        provider="Quark",
        raw_hash_info={
            "hashes": [
                {"algorithm": "sha1", "value": "abcdef0123456789abcdef0123456789abcdef01"},
                {"algorithm": "slice_md5", "value": "abcdef0123456789abcdef0123456789"},
            ]
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.sha1 == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert enriched.slice_md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert "sha1" in report["candidate_hashes"]
    assert "slice_md5" in report["candidate_hashes"]


def test_source_enrichment_reads_stringified_algorithm_list_hash_payloads(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    entry = SourceEntry(
        path="/src/thunder-stringified-hash-list.bin",
        md5="",
        size=10,
        provider="Thunder",
        provider_specific={
            "metadata": "{\"hashes\":[{\"name\":\"gcid\",\"hash\":\"abcdef0123456789abcdef0123456789abcdef01\"},{\"name\":\"md5\",\"hash\":\"abcdef0123456789abcdef0123456789\"}]}"
        },
    )
    enriched, report = enrich_entry(entry, AppConfig.load(path))
    assert enriched.gcid == "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    assert enriched.md5 == "ABCDEF0123456789ABCDEF0123456789"
    assert "gcid" in report["candidate_hashes"]
    assert "md5" in report["candidate_hashes"]


def test_source_enrichment_runtime_reports_bridge_status_for_aliyundriveopen(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "aliyundriveopen": {
                            "status": "captured",
                            "captured": {
                                "refresh_token": "refresh-demo",
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "AliyunDriveOpen")
    assert runtime["capture_ready"] is True
    assert runtime["bridge_status"] == "bridge_ready_but_api_pending"
    assert runtime["strategy_level"] == "provider_normalization"
    assert "etag" not in runtime["hash_aliases"]["md5"]
    assert runtime["bridge_runtime"]["next_action"] == "prepare_aliyundriveopen_api_bridge"
    assert runtime["bridge_preparation_summary"]["transport_hint"] == "refresh_token_or_authorization"
    assert runtime["bridge_preparation_summary"]["fingerprint_expectation"] == ["sha1", "md5", "crc64"]
    assert runtime["bridge_preparation_summary"]["selected_field_names"] == ["refresh_token"]


def test_source_runtime_status_exposes_bridge_preparation_summary(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/alist/onedrive/demo",
                    "target_path": "/dst"
                },
                "source_session": {
                    "mount_provider_mapping": {
                        "/alist/onedrive": "onedrive",
                    },
                    "provider_captures": {
                        "onedrive": {
                            "status": "captured",
                            "captured": {
                                "refresh_token": "demo-refresh"
                            }
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runtime = build_source_runtime_status(AppConfig.load(path))
    summary = runtime["source_enrichment"]["bridge_preparation_summary"]
    assert summary["transport_hint"] == "refresh_token_or_authorization"
    assert summary["fingerprint_expectation"] == ["sha1", "md5", "content_hash"]
    assert summary["preferred_hashes"] == ["sha1", "md5"]
    assert summary["selected_field_names"] == ["refresh_token"]
    assert summary["throttle_defaults"]["page_size"] == 120
    assert summary["fallback_policy"]["download_selected_only"] is True


def test_bridge_runtime_reports_missing_keys_for_baidu_capture() -> None:
    runtime = build_bridge_runtime("baidu", {"cookie_header": "sid=1"})
    assert runtime["ready"] is False
    assert runtime["status"] == "bridge_capture_missing"
    assert "bdstoken" in runtime["missing_keys"]


def test_source_enrichment_runtime_reports_capture_missing_maturity(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "baidu")
    assert runtime["capture_ready"] is False
    assert runtime["bridge_maturity_summary"]["level"] == "capture_missing"


def test_bridge_runtime_accepts_refresh_token_for_onedrive() -> None:
    runtime = build_bridge_runtime("onedrive", {"refresh_token": "demo-refresh"})
    assert runtime["ready"] is True
    assert runtime["status"] == "bridge_ready_but_api_pending"
    assert runtime["matched_groups"] == [["refresh_token"]]


def test_prepare_source_bridge_reports_transport_hint_for_quark() -> None:
    prepared = prepare_source_bridge("quark", {"cookie_header": "sid=1; token=2"})
    assert prepared["hook_registered"] is True
    assert prepared["available"] is True
    assert prepared["transport_hint"] == "cookie_snapshot"
    assert prepared["selected_field_names"] == ["cookie_header"]
    assert "md5" in prepared["fingerprint_expectation"]
    assert prepared["preferred_hashes"] == ["md5"]
    assert prepared["throttle_defaults"]["small_batch_only"] is True
    assert prepared["fallback_policy"]["pending_only_when_hash_missing"] is True


def test_enrich_batch_reports_bridge_candidate_and_pending_counts(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "quark": {
                            "status": "captured",
                            "captured": {
                                "cookie_header": "sid=1; token=2",
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    entries = [
        SourceEntry(path="/src/a.bin", md5="", size=10, provider="Quark", raw_hash_info={"sha1": "b" * 40, "slice_md5": "c" * 32}),
        SourceEntry(path="/src/b.bin", md5="ABCDEF0123456789ABCDEF0123456789", size=10, provider="Quark", raw_hash_info={}),
    ]
    enriched, report = enrich_batch(entries, AppConfig.load(path))
    assert enriched[0].sha1 == "B" * 40
    assert report["candidate_hash_counts"]["sha1"] == 1
    assert report["candidate_hash_counts"]["slice_md5"] == 1
    assert report["pending_reason_counts"]["non_fast_hashes_only_after_session_snapshot"] == 1
    assert report["bridge_execution_state_counts"]["session_snapshot_normalized"] == 2
    assert report["fast_ready_after_bridge"] == 1


def test_execute_source_bridge_marks_api_bridge_placeholder_for_onedrive(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "onedrive": {
                            "status": "captured",
                            "captured": {
                                "refresh_token": "demo-refresh",
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    entry = SourceEntry(path="/src/a.docx", md5="", size=10, provider="OneDrive", raw_hash_info={"sha1": "a" * 40})
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "onedrive")
    enriched, report = execute_source_bridge(entry, runtime)
    assert enriched.sha1 == "A" * 40
    assert report["bridge_execution_state"] == "api_bridge_prepared_but_not_executed"
    assert report["bridge_executor"] == "prepare_onedrive_api_bridge"
    assert report["bridge_transport_hint"] == "refresh_token_or_authorization"
    assert report["candidate_hashes"] == ["sha1"]
    assert report["bridge_expected_hashes"] == ["sha1", "md5", "content_hash"]
    assert report["bridge_missing_expected_hashes"] == ["md5", "content_hash"]
    assert report["pending_reason"] == "provider_api_bridge_not_executed_yet"
    assert report["fast_upload_ready_after_bridge"] is False


def test_execute_source_bridge_skips_api_pending_reason_when_fast_hash_already_present(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "thunder": {
                            "status": "captured",
                            "captured": {
                                "authorization": "Bearer demo",
                                "device_id": "dev-1",
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    entry = SourceEntry(path="/src/a.bin", md5="", size=10, provider="Thunder", raw_hash_info={"file_gcid": "GCID-123"})
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "thunder")
    enriched, report = execute_source_bridge(entry, runtime)
    assert enriched.gcid == "GCID-123"
    assert report["candidate_hashes"] == ["gcid"]
    assert report["pending_reason"] == ""
    assert report["fast_upload_ready_after_bridge"] is True


def test_execute_source_bridge_reads_api_capture_cache_by_path_for_aliyundriveopen(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "aliyundriveopen": {
                            "status": "captured",
                            "captured": {
                                "refresh_token": "demo-refresh",
                                "file_hashes_by_path": {
                                    "/src/demo.bin": {
                                        "sha1": "a" * 40,
                                        "md5": "b" * 32,
                                        "crc64": "c" * 16,
                                    }
                                },
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    entry = SourceEntry(path="/src/demo.bin", md5="", size=10, provider="AliyunDriveOpen")
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "aliyundriveopen")
    enriched, report = execute_source_bridge(entry, runtime)
    assert enriched.sha1 == "A" * 40
    assert enriched.md5 == "B" * 32
    assert enriched.crc64 == "C" * 16
    assert report["bridge_execution_state"] == "api_capture_cache_normalized"
    assert report["provider_stage"] == "api_capture_cache"
    assert report["pending_reason"] == ""
    assert report["fast_upload_ready_after_bridge"] is True


def test_execute_source_bridge_reads_api_capture_cache_list_for_onedrive(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "onedrive": {
                            "status": "captured",
                            "captured": {
                                "refresh_token": "demo-refresh",
                                "entries": [
                                    {
                                        "path": "/src/a.docx",
                                        "sha1": "a" * 40,
                                        "content_hash": "sha1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                    }
                                ],
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    entry = SourceEntry(path="/src/a.docx", md5="", size=10, provider="OneDrive")
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "onedrive")
    enriched, report = execute_source_bridge(entry, runtime)
    assert enriched.sha1 == "A" * 40
    assert enriched.content_hash == "SHA1:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    assert report["bridge_execution_state"] == "api_capture_cache_normalized"
    assert report["provider_stage"] == "api_capture_cache"
    assert report["bridge_missing_expected_hashes"] == ["md5"]
    assert report["pending_reason"] == "provider_api_bridge_not_executed_yet"


def test_execute_source_bridge_marks_non_fast_candidates_for_quark(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "source_session": {
                    "provider_captures": {
                        "quark": {
                            "status": "captured",
                            "captured": {
                                "cookie_header": "sid=1; token=2",
                            },
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    entry = SourceEntry(path="/src/q.bin", md5="", size=10, provider="Quark", raw_hash_info={"sha1": "b" * 40, "slice_md5": "c" * 32})
    runtime = build_source_enrichment_runtime(AppConfig.load(path), "quark")
    enriched, report = execute_source_bridge(entry, runtime)
    assert enriched.sha1 == "B" * 40
    assert enriched.slice_md5 == "C" * 32
    assert report["candidate_hashes"] == ["sha1", "slice_md5"]
    assert report["pending_reason"] == "non_fast_hashes_only_after_session_snapshot"
    assert report["fast_upload_ready_after_bridge"] is False


def test_transfer_planner_prefers_fast_upload_when_target_hash_matches() -> None:
    entry = SourceEntry(path="/src/a.txt", md5="abc", size=10)
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=0,
    )
    assert plan["mode"] == "fast_upload"
    assert plan["fast_hash_hits"] == ["md5"]
    assert plan["next_action_hint"] == "direct_fast_upload_ready"


def test_transfer_planner_prefers_download_for_small_file_when_no_fast_hash_hit() -> None:
    entry = SourceEntry(path="/src/a.txt", md5="", size=2 * 1024 * 1024, sha1="sha1-only")
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5", "gcid"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=10,
    )
    assert plan["mode"] == "download_upload"
    assert plan["next_action_hint"] == "fallback_download_upload_ready"


def test_transfer_planner_explains_api_bridge_pending_with_candidate_hashes() -> None:
    entry = SourceEntry(
        path="/src/a.docx",
        md5="",
        size=10,
        provider="OneDrive",
        sha1="A" * 40,
        provider_specific={
            "__bridge_candidate_hashes": "sha1",
            "__bridge_pending_reason": "provider_api_bridge_not_executed_yet",
            "__bridge_execution_state": "api_bridge_prepared_but_not_executed",
            "__bridge_expected_hashes": "sha1,md5,content_hash",
            "__bridge_missing_expected_hashes": "md5,content_hash",
        },
    )
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5", "gcid"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=0,
    )
    assert plan["mode"] == "record_pending_only"
    assert plan["bridge_candidate_hashes"] == ["sha1"]
    assert plan["bridge_pending_reason"] == "provider_api_bridge_not_executed_yet"
    assert "理论预期哈希" in plan["reason"]
    assert "目标端当前最关键的是 md5" in plan["reason"]
    assert plan["bridge_missing_expected_hashes"] == ["md5", "content_hash"]
    assert plan["target_fast_hashes"] == ["md5", "gcid"]
    assert plan["missing_target_fast_hashes"] == ["md5", "gcid"]
    assert plan["bridge_recoverable_fast_hashes"] == ["md5"]
    assert plan["bridge_missing_recoverable_fast_hashes"] == ["md5"]
    assert plan["next_action_hint"] == "execute_provider_api_for_fast_hashes"


def test_transfer_planner_marks_api_bridge_pending_without_fast_hash_gap() -> None:
    entry = SourceEntry(
        path="/src/api-only.bin",
        md5="",
        size=10,
        provider="OneDrive",
        sha1="A" * 40,
        provider_specific={
            "__bridge_candidate_hashes": "sha1",
            "__bridge_pending_reason": "provider_api_bridge_not_executed_yet",
            "__bridge_execution_state": "api_bridge_prepared_but_not_executed",
            "__bridge_expected_hashes": "sha1,content_hash",
            "__bridge_missing_expected_hashes": "content_hash",
        },
    )
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5", "gcid"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=0,
    )
    assert plan["reason_code"] == "provider_api_bridge_not_executed_yet"
    assert plan["next_action_hint"] == "execute_provider_api_enrich"


def test_transfer_planner_explains_non_fast_session_snapshot_candidates() -> None:
    entry = SourceEntry(
        path="/src/q.bin",
        md5="",
        size=10,
        provider="Quark",
        sha1="B" * 40,
        slice_md5="C" * 32,
        provider_specific={
            "__bridge_candidate_hashes": "sha1,slice_md5",
            "__bridge_pending_reason": "non_fast_hashes_only_after_session_snapshot",
            "__bridge_execution_state": "session_snapshot_normalized",
        },
    )
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5", "gcid"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=0,
    )
    assert plan["bridge_candidate_hashes"] == ["sha1", "slice_md5"]
    assert plan["bridge_pending_reason"] == "non_fast_hashes_only_after_session_snapshot"
    assert "session snapshot" in plan["reason"]
    assert "目标端仍缺=md5, gcid" in plan["reason"]
    assert plan["missing_target_fast_hashes"] == ["md5", "gcid"]
    assert plan["next_action_hint"] == "wait_for_fast_hash_or_fallback"


def test_transfer_planner_marks_target_without_fast_capability_for_fallback() -> None:
    entry = SourceEntry(path="/src/no-fast.txt", md5="abc", size=10)
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": False, "fast_upload_hashes": [], "fallback_modes": ["stream_upload"]},
        auto_download_threshold_mb=0,
        allow_full_fallback=False,
    )
    assert plan["mode"] == "record_pending_only"
    assert plan["reason_code"] == "target_no_fast_capability"
    assert plan["next_action_hint"] == "fallback_target_has_no_fast_upload"


def test_transfer_planner_marks_target_hash_not_supported_for_fallback() -> None:
    entry = SourceEntry(
        path="/src/sha1-only.bin",
        md5="",
        size=10,
        sha1="B" * 40,
        provider_specific={
            "__bridge_candidate_hashes": "sha1",
            "__bridge_pending_reason": "bridge_not_registered",
        },
    )
    plan = plan_transfer_mode(
        entry,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=0,
    )
    assert plan["reason_code"] == "target_hash_not_supported"
    assert plan["next_action_hint"] == "fallback_target_does_not_accept_hashes"


def test_transfer_planner_summarizes_mode_counts() -> None:
    entries = [
        SourceEntry(path="/src/1.txt", md5="abc", size=10),
        SourceEntry(path="/src/2.txt", md5="", size=2 * 1024 * 1024),
    ]
    summary = summarize_transfer_plan(
        entries,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=10,
    )
    assert summary["mode_counts"]["fast_upload"] == 1
    assert summary["mode_counts"]["download_upload"] == 1
    assert compute_fast_upload_hits(entries[0], {"fast_upload_hashes": ["md5"]}) == ["md5"]


def test_transfer_planner_summary_collects_bridge_candidate_counts() -> None:
    entries = [
        SourceEntry(
            path="/src/a.docx",
            md5="",
            size=10,
            sha1="A" * 40,
            provider_specific={
                "__bridge_candidate_hashes": "sha1",
                "__bridge_pending_reason": "provider_api_bridge_not_executed_yet",
                "__bridge_execution_state": "api_bridge_prepared_but_not_executed",
                "__bridge_provider_stage": "api_placeholder",
                "__bridge_transport_hint": "refresh_token_or_authorization",
                "__bridge_maturity_level": "api_capture_ready_pending_provider_enrich",
                "__bridge_maturity_honesty": "api_prepared_not_executed",
                "__bridge_expected_hashes": "sha1,md5,content_hash",
                "__bridge_missing_expected_hashes": "md5,content_hash",
            },
        ),
        SourceEntry(
            path="/src/b.bin",
            md5="",
            size=20,
            sha1="B" * 40,
            slice_md5="C" * 32,
            provider_specific={
                "__bridge_candidate_hashes": "sha1,slice_md5",
                "__bridge_pending_reason": "non_fast_hashes_only_after_session_snapshot",
                "__bridge_execution_state": "session_snapshot_normalized",
                "__bridge_provider_stage": "session_snapshot",
                "__bridge_transport_hint": "cookie_snapshot",
                "__bridge_maturity_level": "session_snapshot_ready",
                "__bridge_maturity_honesty": "capture_ready_normalization_only",
            },
        ),
    ]
    summary = summarize_transfer_plan(
        entries,
        {"supports_fast_upload": True, "fast_upload_hashes": ["md5", "gcid"], "fallback_modes": ["download_upload"]},
        auto_download_threshold_mb=0,
    )
    assert summary["bridge_candidate_counts"]["sha1"] == 2
    assert summary["bridge_candidate_counts"]["slice_md5"] == 1
    assert summary["bridge_pending_reason_counts"]["provider_api_bridge_not_executed_yet"] == 1
    assert summary["reason_code_counts"]["provider_api_bridge_not_executed_yet"] == 1
    assert summary["reason_code_counts"]["non_fast_hashes_only_after_session_snapshot"] == 1
    assert summary["bridge_execution_state_counts"]["api_bridge_prepared_but_not_executed"] == 1
    assert summary["bridge_provider_stage_counts"]["api_placeholder"] == 1
    assert summary["bridge_transport_hint_counts"]["refresh_token_or_authorization"] == 1
    assert summary["bridge_maturity_level_counts"]["api_capture_ready_pending_provider_enrich"] == 1
    assert summary["bridge_maturity_honesty_counts"]["api_prepared_not_executed"] == 1
    assert summary["bridge_missing_expected_hash_counts"]["md5"] == 1
    assert summary["bridge_missing_expected_hash_counts"]["content_hash"] == 1
    assert summary["missing_target_fast_hash_counts"]["md5"] == 2
    assert summary["missing_target_fast_hash_counts"]["gcid"] == 2
    assert summary["bridge_missing_recoverable_fast_hash_counts"]["md5"] == 1
    assert summary["next_action_hint_counts"]["execute_provider_api_for_fast_hashes"] == 1
    assert summary["next_action_hint_counts"]["wait_for_fast_hash_or_fallback"] == 1


def test_sync_runner_uses_source_provider_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  }
}
""".strip(),
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    class FakeSourceProvider:
        def ensure_auth(self) -> None:
            captured["ensure_auth"] = True

        def close(self) -> None:
            captured["closed"] = True

        def list_roots(self) -> list[str]:
            return ["/"]

        def list_dir(self, path: str) -> dict[str, object]:
            return {"path": path, "directories": []}

        def walk_tree(self, source_root: str) -> list[SourceEntry]:
            captured["walk_tree"] = source_root
            return []

        def walk_leaf_dirs(self, root_path: str):
            if False:
                yield root_path
            return

        def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
            return []

        def download_stream(self, source_path: str, temp_dir: Path) -> Path:
            raise AssertionError("download_stream should not be called in analyze test")

        def get_auth_state(self) -> dict[str, str]:
            return {"token": "demo"}

        def get_provider_key(self) -> str:
            return "openlist"

    monkeypatch.setattr("cloudpan_bridge.syncer.create_source_provider", lambda config, on_progress=None: FakeSourceProvider())
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    entries, plan, removed = runner.analyze()
    assert entries == []
    assert plan == []
    assert removed == []
    assert captured["ensure_auth"] is True
    assert captured["walk_tree"] == "/src"
    assert captured.get("closed") is not True
    runner.source.close()
    item = build_plan([SourceEntry(path="/src/a.txt", md5="ABC", size=5 * 1024 * 1024, last_op_time="1")], SyncState())[0][0]
    assert runner._should_auto_download(item) is True


def test_sync_runner_enriches_missing_fast_upload_fingerprint_before_direct_sync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "config.json"
    state_path = tmp_path / "state.json"
    export_path = tmp_path / "export.jsonl"
    temp_dir = tmp_path / "tmp"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                    "auto_download_threshold_mb": 0,
                },
                "state": {
                    "state_file": str(state_path),
                    "export_file": str(export_path),
                    "temp_dir": str(temp_dir),
                },
                "targets": {
                    "active_target": "guangya"
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    captured: dict[str, object] = {"fingerprint_paths": []}

    class FakeSourceProvider:
        def ensure_auth(self) -> None:
            return None

        def close(self) -> None:
            return None

        def list_roots(self) -> list[str]:
            return ["/"]

        def list_dir(self, path: str) -> dict[str, object]:
            return {"path": path, "directories": []}

        def walk_tree(self, source_root: str) -> list[SourceEntry]:
            return [SourceEntry(path="/src/a.bin", md5="", size=123, last_op_time="1", provider="quark", sha256="A" * 64)]

        def walk_leaf_dirs(self, root_path: str):
            if False:
                yield root_path
            return

        def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
            cast_list = captured["fingerprint_paths"]
            assert isinstance(cast_list, list)
            cast_list.append(path)
            return [SourceEntry(path="/src/a.bin", md5="ABCDEF0123456789ABCDEF0123456789", size=123, last_op_time="1", provider="quark")]

        def download_stream(self, source_path: str, temp_dir: Path) -> Path:
            raise AssertionError("download_stream should not be called when enrichment unlocks direct sync")

        def get_auth_state(self) -> dict[str, str]:
            return {"token": "demo"}

        def get_provider_key(self) -> str:
            return "openlist"

    class FakeTarget:
        def ensure_auth(self) -> None:
            return None

        def export_state(self) -> dict[str, str]:
            return {}

        def close(self) -> None:
            return None

        def ensure_target_dir(self, path: str) -> str:
            return "parent-id"

        def delete_if_exists(self, parent_id: str, name: str) -> bool:
            return False

        def remove_target_path(self, path: str) -> bool:
            return False

        def try_fast_upload(self, file_name: str, file_size: int, parent_id: str, md5_hex: str = "", gcid: str = "") -> DirectImportResult:
            captured["md5_hex"] = md5_hex
            captured["gcid"] = gcid
            return DirectImportResult(True, "mocked-import", used_hash="md5")

        def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, object]:
            raise AssertionError("upload_local_file should not be called when direct sync succeeds")

        def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
            return None

    monkeypatch.setattr("cloudpan_bridge.syncer.create_source_provider", lambda config, on_progress=None: FakeSourceProvider())
    monkeypatch.setattr("cloudpan_bridge.syncer.create_target_adapter", lambda config, state, target_key="": FakeTarget())
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    summary = runner.run_direct_phase()
    assert summary.direct_success == 1
    assert summary.downloaded_success == 0
    assert summary.failed == 0
    assert summary.pending_downloads == []
    assert captured["fingerprint_paths"] == ["/src/a.bin"]
    assert captured["md5_hex"] == "ABCDEF0123456789ABCDEF0123456789"
    state = load_state(state_path)
    assert state.files["/src/a.bin"].md5 == "ABCDEF0123456789ABCDEF0123456789"


def test_sync_runner_marks_pending_when_enrichment_still_lacks_fast_upload_fingerprint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "config.json"
    state_path = tmp_path / "state.json"
    export_path = tmp_path / "export.jsonl"
    temp_dir = tmp_path / "tmp"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                    "auto_download_threshold_mb": 0,
                },
                "state": {
                    "state_file": str(state_path),
                    "export_file": str(export_path),
                    "temp_dir": str(temp_dir),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    class FakeSourceProvider:
        def ensure_auth(self) -> None:
            return None

        def close(self) -> None:
            return None

        def list_roots(self) -> list[str]:
            return ["/"]

        def list_dir(self, path: str) -> dict[str, object]:
            return {"path": path, "directories": []}

        def walk_tree(self, source_root: str) -> list[SourceEntry]:
            return [SourceEntry(path="/src/a.bin", md5="", size=123, last_op_time="1", provider="thunder", pickcode="pc-1")]

        def walk_leaf_dirs(self, root_path: str):
            if False:
                yield root_path
            return

        def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
            return [SourceEntry(path="/src/a.bin", md5="", size=123, last_op_time="1", provider="thunder", pickcode="pc-1")]

        def download_stream(self, source_path: str, temp_dir: Path) -> Path:
            raise AssertionError("download_stream should not be called when threshold is disabled")

        def get_auth_state(self) -> dict[str, str]:
            return {"token": "demo"}

        def get_provider_key(self) -> str:
            return "openlist"

    class FakeTarget:
        def ensure_auth(self) -> None:
            return None

        def export_state(self) -> dict[str, str]:
            return {}

        def close(self) -> None:
            return None

        def ensure_target_dir(self, path: str) -> str:
            return "parent-id"

        def delete_if_exists(self, parent_id: str, name: str) -> bool:
            return False

        def remove_target_path(self, path: str) -> bool:
            return False

        def try_fast_upload(self, file_name: str, file_size: int, parent_id: str, md5_hex: str = "", gcid: str = "") -> DirectImportResult:
            raise AssertionError("try_fast_upload should not be called without enriched fast-upload fingerprints")

        def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, object]:
            raise AssertionError("upload_local_file should not be called when threshold is disabled")

        def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
            return None

    monkeypatch.setattr("cloudpan_bridge.syncer.create_source_provider", lambda config, on_progress=None: FakeSourceProvider())
    monkeypatch.setattr("cloudpan_bridge.syncer.create_target_adapter", lambda config, state, target_key="": FakeTarget())
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    summary = runner.run_direct_phase()
    assert summary.direct_success == 0
    assert summary.pending_downloads == ["/src/a.bin"]
    state = load_state(state_path)
    assert state.pending_files["/src/a.bin"].pickcode == "pc-1"
    assert state.pending_files["/src/a.bin"].reason == "未命中秒传库存"


def test_auto_download_threshold_accepts_small_file_without_md5(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "auto_download_threshold_mb": 10
}
""".strip(),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    item = build_plan([SourceEntry(path="/src/a.txt", md5="", size=5 * 1024 * 1024, last_op_time="1", hash_type="none")], SyncState())[0][0]
    assert runner._should_auto_download(item) is True


def test_target_adapter_upload_stream_helper_falls_back_to_legacy_upload_method(tmp_path: Path) -> None:
    local_file = tmp_path / "demo.bin"
    local_file.write_bytes(b"demo")
    seen: dict[str, object] = {}

    class LegacyTarget:
        def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, object]:
            seen["legacy"] = (local_path.name, target_parent_id, target_name)
            return {"ok": True}

    result = target_upload_stream(LegacyTarget(), local_file, "parent-1", "demo.bin")  # type: ignore[arg-type]
    assert result == {"ok": True}
    assert seen["legacy"] == ("demo.bin", "parent-1", "demo.bin")


def test_target_adapter_delete_helper_prefers_new_delete_if_enabled_method() -> None:
    seen: list[str] = []

    class NewTarget:
        def delete_if_enabled(self, parent_id: str, name: str) -> bool:
            seen.append(f"new:{parent_id}:{name}")
            return True

        def delete_if_exists(self, parent_id: str, name: str) -> bool:
            seen.append(f"legacy:{parent_id}:{name}")
            return False

    result = target_delete_if_enabled(NewTarget(), "parent-1", "demo.bin")  # type: ignore[arg-type]
    assert result is True
    assert seen == ["new:parent-1:demo.bin"]


def test_target_adapter_compat_mixin_exposes_unified_methods_on_real_adapter(tmp_path: Path) -> None:
    root_dir = tmp_path / "target-root"
    adapter = LocalFsTargetAdapter(root_dir)
    adapter.ensure_auth()
    target_parent = adapter.ensure_target_dir("/demo")
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")
    uploaded = adapter.upload_stream(local_file, target_parent, "demo.txt")
    assert uploaded["path"].endswith("demo.txt")
    assert adapter.delete_if_enabled(target_parent, "demo.txt") is True


def test_source_provider_helpers_fall_back_to_legacy_methods(tmp_path: Path) -> None:
    local_file = tmp_path / "legacy.txt"
    local_file.write_text("legacy", encoding="utf-8")
    seen: dict[str, object] = {}

    class LegacySource:
        def ensure_login(self) -> None:
            seen["ensure"] = True

        def export_tree(self, source_root: str) -> list[SourceEntry]:
            seen["walk"] = source_root
            return [SourceEntry(path=f"{source_root}/a.bin", md5="abc", size=1, last_op_time="1")]

        def download_file(self, source_path: str, temp_dir: Path) -> Path:
            seen["download"] = (source_path, temp_dir)
            return local_file

    source_ensure_auth(LegacySource())  # type: ignore[arg-type]
    walked = source_walk_tree(LegacySource(), "/demo")  # type: ignore[arg-type]
    downloaded = source_download_stream(LegacySource(), "/demo/a.bin", tmp_path)  # type: ignore[arg-type]
    fingerprints = source_get_file_fingerprints(LegacySource(), "/demo/a.bin")  # type: ignore[arg-type]

    assert seen["ensure"] is True
    assert seen["walk"] == "/demo"
    assert seen["download"] == ("/demo/a.bin", tmp_path)
    assert walked[0].path == "/demo/a.bin"
    assert downloaded == local_file
    assert fingerprints == []


def test_source_provider_compat_mixin_exposes_unified_methods_on_real_provider(tmp_path: Path) -> None:
    fake_download = tmp_path / "downloaded.bin"
    fake_download.write_bytes(b"demo")

    class DemoSourceProvider(SourceProviderCompatMixin):
        def ensure_login(self) -> None:
            return None

        def close(self) -> None:
            return None

        def list_roots(self) -> list[str]:
            return ["/"]

        def list_dir(self, path: str) -> dict[str, object]:
            return {"path": path, "directories": []}

        def export_tree(self, source_root: str) -> list[SourceEntry]:
            return [SourceEntry(path=f"{source_root}/a.bin", md5="abc", size=1, last_op_time="1")]

        def walk_leaf_dirs(self, root_path: str):
            yield root_path

        def download_file(self, source_path: str, temp_dir: Path) -> Path:
            return fake_download

        def get_auth_state(self) -> dict[str, str]:
            return {"token": "demo"}

        def get_provider_key(self) -> str:
            return "demo"

    provider = DemoSourceProvider()
    provider.ensure_auth()
    walked = provider.walk_tree("/demo")
    downloaded = provider.download_stream("/demo/a.bin", tmp_path)
    fingerprints = provider.get_file_fingerprints("/demo/a.bin")

    assert walked[0].path == "/demo/a.bin"
    assert downloaded == fake_download
    assert fingerprints == []


def test_sync_runner_builds_guangya_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "guangya_phone": "+86 13800138000"
}
""".strip(),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, GuangyaTargetAdapter)
    assert adapter.phone_number == "+86 13800138000"
    adapter.close()


def test_sync_runner_builds_guangya_target_adapter_from_generic_target_state(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "guangya_phone": "+86 13800138000"
}
""".strip(),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    state = SyncState(target_states={"guangya": {"access_token": "new-token", "refresh_token": "new-refresh", "device_id": "new-device"}})
    adapter = runner._build_target_adapter(state)
    assert isinstance(adapter, GuangyaTargetAdapter)
    exported = adapter.export_state()
    assert exported["access_token"] == "new-token"
    assert exported["refresh_token"] == "new-refresh"
    assert exported["device_id"] == "new-device"
    adapter.close()


def test_sync_runner_builds_openlist_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "openlist": {
    "url": "http://127.0.0.1:5244",
    "username": "admin",
    "password": "demo",
    "token": "cfg-token"
  },
  "targets": {
    "active_target": "openlist"
  }
}
""".strip(),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    state = SyncState(target_states={"openlist": {"token": "state-token"}})
    adapter = runner._build_target_adapter(state)
    assert isinstance(adapter, OpenListTargetAdapter)
    assert adapter.export_state()["token"] == "state-token"
    adapter.close()


def test_sync_runner_builds_localfs_target_adapter(tmp_path) -> None:
    local_root = tmp_path / "exports"
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "localfs",
                    "localfs": {
                        "root": str(local_root),
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, LocalFsTargetAdapter)
    adapter.ensure_auth()
    exported = adapter.export_state()
    assert exported["root"] == str(local_root)
    adapter.close()


def test_sync_runner_builds_webdav_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "webdav",
                    "webdav": {
                        "url": "https://dav.example.com/root",
                        "username": "dav-user",
                        "password": "dav-pass",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, WebDavTargetAdapter)
    exported = adapter.export_state()
    assert exported["url"] == "https://dav.example.com/root"
    assert exported["username"] == "dav-user"
    adapter.close()


def test_sync_runner_builds_s3_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "s3",
                    "s3": {
                        "endpoint": "https://s3.example.com",
                        "bucket": "archive-bucket",
                        "prefix": "cloudpan-bridge/archive",
                        "access_key": "AKIA_TEST",
                        "secret_key": "SECRET_TEST",
                        "region": "ap-southeast-1",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, S3TargetAdapter)
    exported = adapter.export_state()
    assert exported["endpoint"] == "https://s3.example.com"
    assert exported["bucket"] == "archive-bucket"
    assert exported["prefix"] == "cloudpan-bridge/archive"
    adapter.close()


def test_sync_runner_builds_azureblob_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "azureblob",
                    "azureblob": {
                        "account_url": "https://demo.blob.core.windows.net",
                        "container": "archive-container",
                        "prefix": "cloudpan-bridge/archive",
                        "account_name": "demo-account",
                        "account_key": "azure-key",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, AzureBlobTargetAdapter)
    exported = adapter.export_state()
    assert exported["account_url"] == "https://demo.blob.core.windows.net"
    assert exported["container"] == "archive-container"
    assert exported["prefix"] == "cloudpan-bridge/archive"
    adapter.close()


def test_sync_runner_builds_seafile_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "seafile",
                    "seafile": {
                        "url": "https://seafile.example.com",
                        "token": "seafile-token",
                        "username": "seafile-user",
                        "password": "seafile-pass",
                        "repo_id": "repo-1",
                        "repo_name": "Archive",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, SeafileTargetAdapter)
    exported = adapter.export_state()
    assert exported["url"] == "https://seafile.example.com"
    assert exported["token"] == "seafile-token"
    assert exported["repo_id"] == "repo-1"
    adapter.close()


def test_sync_runner_builds_smb_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "smb",
                    "smb": {
                        "url": "smb://nas/share/archive",
                        "username": "smb-user",
                        "password": "smb-pass",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, SmbTargetAdapter)
    exported = adapter.export_state()
    assert exported["url"] == "smb://nas/share/archive"
    assert exported["username"] == "smb-user"
    adapter.close()


def test_sync_runner_builds_ftp_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "ftp",
                    "ftp": {
                        "url": "ftp://ftp.example.com:21/root",
                        "username": "ftp-user",
                        "password": "ftp-pass",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, FtpTargetAdapter)
    exported = adapter.export_state()
    assert exported["url"] == "ftp://ftp.example.com:21/root"
    assert exported["username"] == "ftp-user"
    adapter.close()


def test_sync_runner_builds_sftp_target_adapter(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "targets": {
                    "active_target": "sftp",
                    "sftp": {
                        "url": "sftp://sftp.example.com:22/root",
                        "username": "sftp-user",
                        "password": "sftp-pass",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    runner = SyncRunner(AppConfig.load(path), log=lambda _message: None)
    adapter = runner._build_target_adapter(SyncState())
    assert isinstance(adapter, SftpTargetAdapter)
    exported = adapter.export_state()
    assert exported["url"] == "sftp://sftp.example.com:22/root"
    assert exported["username"] == "sftp-user"
    adapter.close()


def test_localfs_target_adapter_can_remove_target_path(tmp_path) -> None:
    root = tmp_path / "exports"
    adapter = LocalFsTargetAdapter(root)
    adapter.ensure_auth()
    nested = root / "a" / "b.txt"
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_text("demo", encoding="utf-8")
    assert adapter.remove_target_path("/a/b.txt") is True
    assert not nested.exists()
    assert adapter.remove_target_path("/a/missing.txt") is False


def test_webdav_target_adapter_uses_basic_webdav_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeResponse:
        def __init__(self, status_code: int, text: str = "") -> None:
            self.status_code = status_code
            self.text = text

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str, bytes | None]] = []

        def request(self, method: str, url: str, auth=None, headers=None, content=None):  # type: ignore[no-untyped-def]
            self.calls.append((method, url, content))
            if method == "DELETE":
                return FakeResponse(204)
            if method == "PUT":
                return FakeResponse(201)
            return FakeResponse(201)

        def close(self) -> None:
            return None

    fake_client = FakeClient()
    adapter = WebDavTargetAdapter(
        base_url="https://dav.example.com/root",
        username="demo",
        password="secret",
        client=fake_client,  # type: ignore[arg-type]
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    methods = [item[0] for item in fake_client.calls]
    assert methods[:2] == ["MKCOL", "MKCOL"]
    assert "PUT" in methods
    assert "DELETE" in methods
    adapter.close()


def test_s3_target_adapter_uses_basic_s3_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeS3Client:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str, str]] = []
            self.closed = False

        def upload_file(self, local_path: str, bucket: str, key: str) -> None:
            _ = Path(local_path).read_bytes()
            self.calls.append(("upload_file", bucket, key))

        def delete_object(self, Bucket: str, Key: str) -> None:  # noqa: N803
            self.calls.append(("delete_object", Bucket, Key))

        def close(self) -> None:
            self.closed = True

    fake_client = FakeS3Client()
    adapter = S3TargetAdapter(
        endpoint="https://s3.example.com",
        bucket="archive-bucket",
        access_key="AKIA_TEST",
        secret_key="SECRET_TEST",
        region="ap-southeast-1",
        prefix="cloudpan-bridge/archive",
        client_factory=lambda **kwargs: fake_client,
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert result["bucket"] == "archive-bucket"
    assert result["key"] == "cloudpan-bridge/archive/photos/2026/demo.txt"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    assert ("upload_file", "archive-bucket", "cloudpan-bridge/archive/photos/2026/demo.txt") in fake_client.calls
    assert ("delete_object", "archive-bucket", "cloudpan-bridge/archive/photos/2026/demo.txt") in fake_client.calls
    adapter.close()
    assert fake_client.closed is True


def test_azureblob_target_adapter_uses_basic_blob_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeContainerClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def upload_blob(self, blob_name: str, handle, overwrite: bool = False) -> None:  # type: ignore[no-untyped-def]
            _ = handle.read()
            self.calls.append(("upload_blob", f"{blob_name}|{overwrite}"))

        def delete_blob(self, blob_name: str) -> None:
            self.calls.append(("delete_blob", blob_name))

    class FakeServiceClient:
        def __init__(self) -> None:
            self.container = FakeContainerClient()

        def get_container_client(self, name: str) -> FakeContainerClient:
            self.container.calls.append(("get_container_client", name))
            return self.container

    fake_service = FakeServiceClient()
    adapter = AzureBlobTargetAdapter(
        account_url="https://demo.blob.core.windows.net",
        container="archive-container",
        account_name="demo-account",
        account_key="azure-key",
        prefix="cloudpan-bridge/archive",
        service_factory=lambda **kwargs: fake_service,
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert result["container"] == "archive-container"
    assert result["blob_name"] == "cloudpan-bridge/archive/photos/2026/demo.txt"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    assert ("get_container_client", "archive-container") in fake_service.container.calls
    assert ("upload_blob", "cloudpan-bridge/archive/photos/2026/demo.txt|True") in fake_service.container.calls
    assert ("delete_blob", "cloudpan-bridge/archive/photos/2026/demo.txt") in fake_service.container.calls
    adapter.close()


def test_seafile_target_adapter_uses_basic_http_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeResponse:
        def __init__(self, status_code: int, payload=None, text: str = "") -> None:  # type: ignore[no-untyped-def]
            self.status_code = status_code
            self._payload = payload
            self.text = text

        def json(self):  # type: ignore[no-untyped-def]
            if self._payload is None:
                raise ValueError("no json")
            return self._payload

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def post(self, url: str, data=None, headers=None, files=None):  # type: ignore[no-untyped-def]
            self.calls.append(("POST", url))
            if url.endswith("/api2/auth-token/"):
                return FakeResponse(200, {"token": "token-1"})
            if "/api2/repos/repo-1/dir/" in url:
                return FakeResponse(201, {"success": True})
            if url == "https://upload.seafile.example.com/upload-api":
                uploaded_name = files["file"][0] if files else ""
                return FakeResponse(200, [{"name": uploaded_name}])
            return FakeResponse(500, text="unexpected post")

        def get(self, url: str, params=None, headers=None):  # type: ignore[no-untyped-def]
            self.calls.append(("GET", url))
            if url.endswith("/api2/repos/"):
                return FakeResponse(200, [{"repo_id": "repo-1", "name": "Archive"}])
            if url.endswith("/api/v2.1/repos/repo-1/dir/detail/"):
                path = str((params or {}).get("path") or "")
                if path == "/photos":
                    return FakeResponse(404, text="missing")
                if path == "/photos/2026":
                    return FakeResponse(404, text="missing")
                return FakeResponse(200, {"path": path})
            if url.endswith("/api2/repos/repo-1/upload-link/"):
                return FakeResponse(200, "https://upload.seafile.example.com/upload-api")
            return FakeResponse(500, text="unexpected get")

        def delete(self, url: str, params=None, headers=None):  # type: ignore[no-untyped-def]
            self.calls.append(("DELETE", url))
            return FakeResponse(200, {"success": True})

        def close(self) -> None:
            return None

    fake_client = FakeClient()
    adapter = SeafileTargetAdapter(
        base_url="https://seafile.example.com",
        username="demo",
        password="secret",
        repo_name="Archive",
        client=fake_client,  # type: ignore[arg-type]
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert result["repo_id"] == "repo-1"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    assert ("POST", "https://seafile.example.com/api2/auth-token/") in fake_client.calls
    assert ("GET", "https://seafile.example.com/api2/repos/") in fake_client.calls
    assert ("POST", "https://seafile.example.com/api2/repos/repo-1/dir/?p=/photos") in fake_client.calls
    assert ("POST", "https://seafile.example.com/api2/repos/repo-1/dir/?p=/photos/2026") in fake_client.calls
    assert ("GET", "https://seafile.example.com/api2/repos/repo-1/upload-link/") in fake_client.calls
    assert ("POST", "https://upload.seafile.example.com/upload-api") in fake_client.calls
    assert ("DELETE", "https://seafile.example.com/api2/repos/repo-1/file/") in fake_client.calls
    adapter.close()


def test_smb_target_adapter_uses_basic_smb_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeRemoteFile:
        def __init__(self) -> None:
            self.buffer = bytearray()

        def write(self, data: bytes) -> int:
            self.buffer.extend(data)
            return len(data)

        def __enter__(self) -> "FakeRemoteFile":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    class FakeSmbClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def register_session(self, host: str, username: str = "", password: str = "") -> None:
            self.calls.append(("register_session", f"{host}|{username}|{password}"))

        def mkdir(self, path: str) -> None:
            self.calls.append(("mkdir", path))

        def open_file(self, path: str, mode: str = "rb") -> FakeRemoteFile:
            self.calls.append(("open_file", f"{path}|{mode}"))
            return FakeRemoteFile()

        def remove(self, path: str) -> None:
            self.calls.append(("remove", path))

        def rmdir(self, path: str) -> None:
            self.calls.append(("rmdir", path))

    fake_client = FakeSmbClient()
    adapter = SmbTargetAdapter(
        base_url="smb://nas/share/archive",
        username="demo",
        password="secret",
        client_module=fake_client,
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    assert ("register_session", "nas|demo|secret") in fake_client.calls
    assert ("mkdir", "\\\\nas\\share\\archive\\photos") in fake_client.calls
    assert ("mkdir", "\\\\nas\\share\\archive\\photos\\2026") in fake_client.calls
    assert ("open_file", "\\\\nas\\share\\archive\\photos\\2026\\demo.txt|wb") in fake_client.calls
    assert ("remove", "\\\\nas\\share\\archive\\photos\\2026\\demo.txt") in fake_client.calls
    adapter.close()


def test_ftp_target_adapter_uses_basic_ftp_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeFtp:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def connect(self, host: str, port: int) -> None:
            self.calls.append(("connect", f"{host}:{port}"))

        def login(self, username: str, password: str) -> None:
            self.calls.append(("login", username))

        def mkd(self, path: str) -> None:
            self.calls.append(("mkd", path))

        def storbinary(self, command: str, handle) -> None:  # type: ignore[no-untyped-def]
            _ = handle.read()
            self.calls.append(("storbinary", command))

        def delete(self, path: str) -> None:
            self.calls.append(("delete", path))

        def rmd(self, path: str) -> None:
            self.calls.append(("rmd", path))

        def quit(self) -> None:
            self.calls.append(("quit", ""))

    fake_ftp = FakeFtp()
    adapter = FtpTargetAdapter(
        base_url="ftp://ftp.example.com:21/root",
        username="demo",
        password="secret",
        ftp_factory=lambda: fake_ftp,  # type: ignore[arg-type]
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    assert ("connect", "ftp.example.com:21") in fake_ftp.calls
    assert ("login", "demo") in fake_ftp.calls
    assert ("mkd", "/root/photos") in fake_ftp.calls
    assert ("mkd", "/root/photos/2026") in fake_ftp.calls
    assert ("storbinary", "STOR /root/photos/2026/demo.txt") in fake_ftp.calls
    assert ("delete", "/root/photos/2026/demo.txt") in fake_ftp.calls
    adapter.close()


def test_sftp_target_adapter_uses_basic_sftp_calls(tmp_path) -> None:
    local_file = tmp_path / "demo.txt"
    local_file.write_text("hello", encoding="utf-8")

    class FakeTransport:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    class FakeSftp:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []
            self.closed = False

        def mkdir(self, path: str) -> None:
            self.calls.append(("mkdir", path))

        def put(self, local_path: str, remote_path: str) -> None:
            _ = Path(local_path).read_bytes()
            self.calls.append(("put", remote_path))

        def remove(self, path: str) -> None:
            self.calls.append(("remove", path))

        def rmdir(self, path: str) -> None:
            self.calls.append(("rmdir", path))

        def close(self) -> None:
            self.closed = True

    fake_transport = FakeTransport()
    fake_sftp = FakeSftp()
    adapter = SftpTargetAdapter(
        base_url="sftp://sftp.example.com:22/root",
        username="demo",
        password="secret",
        connect_factory=lambda host, port, username, password: (fake_transport, fake_sftp),
    )
    adapter.ensure_auth()
    parent_id = adapter.ensure_target_dir("/photos/2026")
    assert parent_id == "/photos/2026"
    result = adapter.upload_local_file(local_file, parent_id, "demo.txt")
    assert result["path"] == "/photos/2026/demo.txt"
    assert adapter.remove_target_path("/photos/2026/demo.txt") is True
    assert ("mkdir", "/root/photos") in fake_sftp.calls
    assert ("mkdir", "/root/photos/2026") in fake_sftp.calls
    assert ("put", "/root/photos/2026/demo.txt") in fake_sftp.calls
    assert ("remove", "/root/photos/2026/demo.txt") in fake_sftp.calls
    adapter.close()
    assert fake_transport.closed is True
    assert fake_sftp.closed is True


def test_delete_removed_does_not_touch_target_when_target_delete_removed_disabled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    state_path = tmp_path / "state.json"
    export_path = tmp_path / "export.jsonl"
    temp_dir = tmp_path / "tmp"
    config_path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                    "delete_removed": True,
                    "target_delete_removed": False,
                },
                "state": {
                    "state_file": str(state_path),
                    "export_file": str(export_path),
                    "temp_dir": str(temp_dir),
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    state_path.write_text(
        json.dumps(
            {
                "files": {
                    "/src/old.txt": {
                        "path": "/src/old.txt",
                        "md5": "ABC",
                        "size": 1,
                        "last_op_time": "1",
                        "target_path": "/dst/old.txt",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    from cloudpan_bridge import syncer as syncer_module

    class FakeSource:
        def ensure_login(self) -> None:
            return None

        def export_tree(self, _path: str) -> list[SourceEntry]:
            return []

        def close(self) -> None:
            return None

    class FakeTarget:
        removed: list[str]

        def __init__(self) -> None:
            self.removed = []

        def ensure_auth(self) -> None:
            return None

        def export_state(self) -> dict[str, str]:
            return {}

        def close(self) -> None:
            return None

        def ensure_target_dir(self, path: str) -> str:
            return path

        def delete_if_exists(self, parent_id: str, name: str) -> bool:
            return False

        def remove_target_path(self, path: str) -> bool:
            self.removed.append(path)
            return True

        def try_fast_upload(self, file_name: str, file_size: int, parent_id: str, md5_hex: str = "", gcid: str = "") -> DirectImportResult:
            return DirectImportResult(False, "disabled")

        def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, object]:
            return {}

        def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
            return None

    fake_target = FakeTarget()
    monkeypatch.setattr(syncer_module, "create_target_adapter", lambda config, state, target_key="": fake_target)
    runner = SyncRunner(AppConfig.load(config_path), log=lambda _message: None)
    runner.source = FakeSource()  # type: ignore[assignment]
    summary = runner.run(dry_run=False)
    assert summary.total == 0
    assert fake_target.removed == []


def test_delete_removed_can_remove_target_when_target_delete_removed_enabled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    state_path = tmp_path / "state.json"
    export_path = tmp_path / "export.jsonl"
    temp_dir = tmp_path / "tmp"
    config_path.write_text(
        json.dumps(
            {
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                    "delete_removed": True,
                    "target_delete_removed": True,
                },
                "state": {
                    "state_file": str(state_path),
                    "export_file": str(export_path),
                    "temp_dir": str(temp_dir),
                },
                "openlist": {
                    "url": "http://127.0.0.1:5244",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    state_path.write_text(
        json.dumps(
            {
                "files": {
                    "/src/old.txt": {
                        "path": "/src/old.txt",
                        "md5": "ABC",
                        "size": 1,
                        "last_op_time": "1",
                        "target_path": "/dst/old.txt",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    from cloudpan_bridge import syncer as syncer_module

    class FakeSource:
        def ensure_login(self) -> None:
            return None

        def export_tree(self, _path: str) -> list[SourceEntry]:
            return []

        def close(self) -> None:
            return None

    class FakeTarget:
        removed: list[str]

        def __init__(self) -> None:
            self.removed = []

        def ensure_auth(self) -> None:
            return None

        def export_state(self) -> dict[str, str]:
            return {}

        def close(self) -> None:
            return None

        def ensure_target_dir(self, path: str) -> str:
            return path

        def delete_if_exists(self, parent_id: str, name: str) -> bool:
            return False

        def remove_target_path(self, path: str) -> bool:
            self.removed.append(path)
            return True

        def try_fast_upload(self, file_name: str, file_size: int, parent_id: str, md5_hex: str = "", gcid: str = "") -> DirectImportResult:
            return DirectImportResult(False, "disabled")

        def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, object]:
            return {}

        def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
            return None

    fake_target = FakeTarget()
    monkeypatch.setattr(syncer_module, "create_target_adapter", lambda config, state, target_key="": fake_target)
    runner = SyncRunner(AppConfig.load(config_path), log=lambda _message: None)
    runner.source = FakeSource()  # type: ignore[assignment]
    summary = runner.run(dry_run=False)
    assert summary.total == 0
    assert fake_target.removed == ["/dst/old.txt"]


def test_provider_registry_endpoint_returns_active_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "target_key": "guangya"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/registry")
    assert response.status_code == 200
    payload = response.json()
    assert payload["active_target"] == "guangya"
    assert payload["driver_matrix"]["thunder"]["targetProfile"]["key"] == "guangya"
    assert payload["implemented_targets"] == ["guangya", "openlist", "localfs", "webdav", "s3", "seafile", "azureblob", "ftp", "sftp", "smb"]
    assert payload["target_implementation_status"]["guangya"]["known_profile"] is True
    assert payload["target_implementation_status"]["guangya"]["implemented"] is True
    assert payload["target_implementation_status"]["guangya"]["selectable"] is True
    assert payload["target_implementation_status"]["openlist"]["known_profile"] is True
    assert payload["target_implementation_status"]["openlist"]["implemented"] is True
    assert payload["target_implementation_status"]["openlist"]["selectable"] is True
    assert payload["target_implementation_status"]["localfs"]["known_profile"] is True
    assert payload["target_implementation_status"]["localfs"]["implemented"] is True
    assert payload["target_implementation_status"]["localfs"]["selectable"] is True
    assert payload["target_implementation_status"]["s3"]["known_profile"] is True
    assert payload["target_implementation_status"]["s3"]["implemented"] is True
    assert payload["target_implementation_status"]["s3"]["selectable"] is True
    assert payload["target_implementation_status"]["seafile"]["known_profile"] is True
    assert payload["target_implementation_status"]["seafile"]["implemented"] is True
    assert payload["target_implementation_status"]["seafile"]["selectable"] is True
    assert payload["target_implementation_status"]["azureblob"]["known_profile"] is True
    assert payload["target_implementation_status"]["azureblob"]["implemented"] is True
    assert payload["target_implementation_status"]["azureblob"]["selectable"] is True
    assert payload["target_implementation_status"]["smb"]["known_profile"] is True
    assert payload["target_implementation_status"]["smb"]["implemented"] is True
    assert payload["target_implementation_status"]["smb"]["selectable"] is True


def test_provider_registry_endpoint_returns_current_source_mapping_context(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "source_session": {
    "mount_provider_mapping": {
      "/alist/quark": "quark"
    }
  },
  "grouped_config": {
    "ui": {
      "browser": {
        "mounted_source": "/alist/quark"
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/registry")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source_mapping"]["/alist/quark"] == "quark"
    assert any(item["key"] == "quark" for item in payload["provider_catalog"])
    assert payload["current_source_context"]["mount_path"] == "/alist/quark"
    assert payload["current_source_context"]["source_profile_override"] == "quark"
    assert payload["current_source_context"]["effective_driver"] == "quark"
    assert payload["current_source_context"]["provider_key"] == "quark"
    assert payload["current_source_context"]["source_mode"] == "openlist_mount"
    assert payload["current_source_context"]["target_mode"] == "metadata_import"
    assert payload["current_source_context"]["supports_fingerprint_enrichment"] is True
    assert payload["current_source_context"]["supports_direct_target_write"] is True
    assert payload["current_source_context"]["supports_fast_upload"] is True
    assert payload["current_source_context"]["fallback_strategy"] == "metadata_then_pending"
    assert payload["current_source_context"]["current_capability"]["driver"] == "quark"


def test_provider_source_mapping_endpoint_roundtrip(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "source_session": {
    "mount_provider_mapping": {
      "/alist/quark": "quark"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/source_mapping")
    assert response.status_code == 200
    assert response.json()["items"]["/alist/quark"] == "quark"

    update = client.post(
        "/api/provider/source_mapping",
        json={"mount_path": "/alist/quark", "profile_key": "generic"},
    )
    assert update.status_code == 200
    assert update.json()["items"]["/alist/quark"] == "generic"

    clear_response = client.post(
        "/api/provider/source_mapping",
        json={"mount_path": "/alist/quark", "profile_key": ""},
    )
    assert clear_response.status_code == 200
    assert clear_response.json()["items"] == {}


def test_provider_capability_assess_uses_mount_override_context(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "source_session": {
    "mount_provider_mapping": {
      "/alist/quark": "quark"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "generic",
            "mount_path": "/alist/quark",
            "target": "guangya",
            "analysis_summary": {},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["driver"] == "quark"
    assert payload["sourceMappingContext"]["mount_path"] == "/alist/quark"
    assert payload["sourceMappingContext"]["requested_driver"] == "generic"
    assert payload["sourceMappingContext"]["source_profile_override"] == "quark"
    assert payload["sourceMappingContext"]["effective_driver"] == "quark"
    assert payload["sourceMappingContext"]["provider_key"] == "quark"
    assert payload["sourceMappingContext"]["supports_fast_upload"] is True
    assert payload["sourceMappingContext"]["target_mode"] == "metadata_import"


def test_provider_registry_resolves_source_mapping_by_longest_prefix(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/alist/quark/photos/2026",
  "target_path": "/dst",
  "source_session": {
    "mount_provider_mapping": {
      "/alist": "generic",
      "/alist/quark": "quark"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/registry")
    assert response.status_code == 200
    payload = response.json()
    assert payload["current_source_context"]["mount_path"] == "/alist/quark"
    assert payload["current_source_context"]["source_path"] == "/alist/quark/photos/2026"
    assert payload["current_source_context"]["effective_driver"] == "quark"


def test_build_source_mapping_context_normalizes_generic_driver_into_conservative_provider() -> None:
    payload = build_source_mapping_context(
        mount_path="/alist/mystery",
        requested_driver="mystery",
        effective_driver="generic",
        source_profile_override="generic",
        source_path="/alist/mystery/a",
        target="openlist",
    )
    assert payload["provider_key"] == "generic_openlist_driver"
    assert payload["source_profile_key"] == "generic"
    assert payload["source_mode"] == "openlist_mount"
    assert payload["target_key"] == "openlist"
    assert payload["target_mode"] == "direct_write"
    assert payload["supports_direct_target_write"] is True
    assert payload["supports_fast_upload"] is False
    assert payload["fallback_strategy"] == "download_upload_only"


def test_start_sync_writes_source_mapping_context_into_runtime_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/alist/quark/photos/2026",
    "target_path": "/archive"
  },
  "source_session": {
    "mount_provider_mapping": {
      "/alist/quark": "quark"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    class FakeSummary:
        pending_downloads: list[str] = []

        def to_dict(self) -> dict[str, object]:
            return {
                "source_path": "/alist/quark/photos/2026",
                "total": 0,
                "direct_success": 0,
                "downloaded_success": 0,
                "skipped": 0,
                "failed": 0,
                "pending_downloads": [],
            }

    class FakeSyncRunner:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

        @staticmethod
        def _update_queue_item(*_args: object, **_kwargs: object) -> None:
            return None

        def run(self, *_args: object, **_kwargs: object) -> FakeSummary:
            return FakeSummary()

        def run_direct_phase(self) -> FakeSummary:
            return FakeSummary()

        def run_selected_downloads(self, _selected_paths: list[str]) -> FakeSummary:
            return FakeSummary()

    class ImmediateThread:
        def __init__(self, *, target, args=(), kwargs=None, daemon=None):  # type: ignore[no-untyped-def]
            self._target = target
            self._args = args
            self._kwargs = kwargs or {}

        def start(self) -> None:
            self._target(*self._args, **self._kwargs)

    monkeypatch.setattr(webapp_module, "SyncRunner", FakeSyncRunner)
    monkeypatch.setattr(webapp_module, "Thread", ImmediateThread)

    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/sync/start",
        json={
            "mode": "dry_run",
            "source_path": "/alist/quark/photos/2026",
        },
    )
    assert response.status_code == 200
    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    payload = status_response.json()
    assert payload["sync"]["current_task"] == {}
    assert payload["sync"]["current_source_context"]["mount_path"] == "/alist/quark"
    assert payload["sync"]["current_source_context"]["source_profile_override"] == "quark"
    assert payload["sync"]["current_source_context"]["effective_driver"] == "quark"
    assert payload["sync"]["last_summary"]["source_path"] == "/alist/quark/photos/2026"


def test_target_preflight_endpoint_reports_supported_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "target_key": "guangya"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/target/preflight")
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_key"] == "guangya"
    assert payload["known_profile"] is True
    assert payload["implemented"] is True
    assert payload["selectable"] is True
    assert payload["configured"] is False
    assert payload["adapter_capability"]["supports_fast_upload"] is True
    assert payload["adapter_capability"]["fast_upload_hashes"] == ["md5", "gcid"]
    assert "access_token_or_refresh_token" in payload["missing_fields"]


def test_target_preflight_endpoint_reports_openlist_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "openlist": {
    "url": "http://127.0.0.1:5244",
    "username": "admin",
    "password": "demo"
  },
  "targets": {
    "active_target": "openlist"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/target/preflight?target=openlist")
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_key"] == "openlist"
    assert payload["known_profile"] is True
    assert payload["implemented"] is True
    assert payload["selectable"] is True
    assert payload["configured"] is True
    assert payload["adapter_capability"]["supports_fast_upload"] is False
    assert payload["adapter_capability"]["write_mode"] == "upload_overwrite"


def test_target_preflight_endpoint_reports_webdav_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "webdav",
    "webdav": {
      "url": "https://dav.example.com/root",
      "username": "dav-user",
      "password": "dav-pass"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/target/preflight?target=webdav")
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_key"] == "webdav"
    assert payload["known_profile"] is True
    assert payload["implemented"] is True
    assert payload["selectable"] is True
    assert payload["configured"] is True
    assert payload["adapter_capability"]["fallback_modes"] == ["download_upload", "stream_upload"]


def test_target_preflight_endpoint_reports_ftp_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "ftp",
    "ftp": {
      "url": "ftp://ftp.example.com:21/root",
      "username": "ftp-user",
      "password": "ftp-pass"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/target/preflight?target=ftp")
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_key"] == "ftp"
    assert payload["known_profile"] is True
    assert payload["implemented"] is True
    assert payload["selectable"] is True
    assert payload["configured"] is True
    assert payload["adapter_capability"]["write_mode"] == "stream_upload"


def test_target_preflight_endpoint_rejects_unknown_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "target_key": "quark"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/target/preflight")
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_key"] == "quark"
    assert payload["known_profile"] is False
    assert payload["implemented"] is False
    assert payload["selectable"] is False
    assert payload["configured"] is False
    assert payload["adapter_capability"]["write_mode"] == "unavailable"

    sync_response = client.post("/api/sync/start", json={"mode": "dry_run"})
    assert sync_response.status_code == 400
    assert "目标端 quark 当前既没有内置档案，也没有实现可写入适配器" in sync_response.json()["detail"]


def test_sync_start_accepts_grouped_source_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/from-config",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {}
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    seen: dict[str, object] = {}

    class FakeSummary:
        pending_downloads: list[str] = []

        def to_dict(self) -> dict[str, object]:
            return {"total": 0, "direct_success": 0, "downloaded_success": 0, "failed": 0}

    class DummySource:
        def close(self) -> None:
            return None

    class FakeRunner:
        def __init__(self, config: AppConfig, log: object | None = None, source_root_for_target: str = "") -> None:
            seen["source_path"] = config.source_path
            seen["source_root_for_target"] = source_root_for_target
            self.source = DummySource()

        def run(self, allow_download_upload: bool = False, dry_run: bool = False) -> FakeSummary:
            seen["allow_download_upload"] = allow_download_upload
            seen["dry_run"] = dry_run
            return FakeSummary()

    class ImmediateThread:
        def __init__(self, target: object, args: tuple[object, ...] = (), daemon: bool = False) -> None:
            self._target = target
            self._args = args

        def start(self) -> None:
            self._target(*self._args)

    monkeypatch.setattr(webapp_module, "SyncRunner", FakeRunner)
    monkeypatch.setattr(webapp_module, "Thread", ImmediateThread)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/sync/start",
        json={
            "mode": "dry_run",
            "grouped_config": {
                "sync": {
                    "source_path": "/grouped-sync"
                }
            }
        },
    )
    assert response.status_code == 200
    assert seen["source_path"] == "/grouped-sync"
    assert seen["source_root_for_target"] == "/grouped-sync"
    assert seen["dry_run"] is True
    assert seen["allow_download_upload"] is False


def test_config_endpoint_returns_flat_and_grouped_views(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "app": {
    "bind_port": 9999
  },
  "openlist": {
    "url": "http://127.0.0.1:5244",
    "username": "admin"
  },
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {
      "phone": "+86 13800138000"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source_path"] == "/src"
    assert payload["target_path"] == "/dst"
    assert payload["grouped_config"]["sync"]["source_path"] == "/src"
    assert payload["grouped_config"]["targets"]["guangya"]["phone"] == "+86 13800138000"
    assert "source_path" not in payload["grouped_config"]
    assert "target_path" not in payload["grouped_config"]
    assert payload["config_meta"]["storage"] == "nested_with_flat_compat"
    assert payload["config_meta"]["active_target"] == "guangya"


def test_config_endpoint_grouped_view_preserves_unknown_nested_sections(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src"
  },
  "extra_runtime": {
    "feature_flag": true,
    "notes": {
      "owner": "demo"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["grouped_config"]["extra_runtime"]["feature_flag"] is True
    assert payload["grouped_config"]["extra_runtime"]["notes"]["owner"] == "demo"
    assert "extra_runtime" not in payload


def test_config_endpoint_grouped_update_preserves_unknown_nested_sections(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "extra_runtime": {
    "feature_flag": true,
    "notes": {
      "owner": "demo"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/config",
        json={
            "grouped_config": {
                "ui": {
                    "language": "mix",
                }
            }
        },
    )
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["ui"]["language"] == "mix"
    assert saved["extra_runtime"]["feature_flag"] is True
    assert saved["extra_runtime"]["notes"]["owner"] == "demo"


def test_config_endpoint_grouped_view_preserves_unknown_scalar_and_list_sections(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src"
  },
  "feature_switch": true,
  "provider_order": ["quark", "189cloud"]
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["grouped_config"]["feature_switch"] is True
    assert payload["grouped_config"]["provider_order"] == ["quark", "189cloud"]
    assert "feature_switch" not in payload
    assert "provider_order" not in payload


def test_config_endpoint_flat_update_preserves_unknown_scalar_and_list_sections(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "feature_switch": true,
  "provider_order": ["quark", "189cloud"]
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/config",
        json={
            "source_path": "/src-2",
            "target_path": "/dst-2",
        },
    )
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["sync"]["source_path"] == "/src-2"
    assert saved["sync"]["target_path"] == "/dst-2"
    assert saved["feature_switch"] is True
    assert saved["provider_order"] == ["quark", "189cloud"]


def test_config_endpoint_accepts_grouped_partial_update(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {
      "phone": "+86 13800138000",
      "refresh_token": "old-refresh"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/config",
        json={
            "grouped_config": {
                "targets": {
                    "guangya": {
                        "refresh_token": "new-refresh",
                    }
                },
                "sync": {
                    "target_path": "/dst-2",
                },
            }
        },
    )
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["targets"]["guangya"]["phone"] == "+86 13800138000"
    assert saved["targets"]["guangya"]["refresh_token"] == "new-refresh"
    assert saved["sync"]["source_path"] == "/src"
    assert saved["sync"]["target_path"] == "/dst-2"


def test_queue_add_accepts_grouped_source_path(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/from-config"
  },
  "state": {
    "state_file": ".state/test-state.json"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/queue/add",
        json={
            "grouped_config": {
                "sync": {
                    "source_path": "/grouped-source"
                }
            }
        },
    )
    assert response.status_code == 200
    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    source_queue = status_response.json()["sync"]["source_queue"]
    assert source_queue[0]["source_path"] == "/grouped-source"


def test_queue_remove_accepts_grouped_source_path(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/from-config"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    add_response = client.post(
        "/api/queue/add",
        json={
            "grouped_config": {
                "sync": {
                    "source_path": "/grouped-source"
                }
            }
        },
    )
    assert add_response.status_code == 200
    remove_response = client.post(
        "/api/queue/remove",
        json={
            "grouped_config": {
                "sync": {
                    "source_path": "/grouped-source"
                }
            }
        },
    )
    assert remove_response.status_code == 200
    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    source_queue = status_response.json()["sync"]["source_queue"]
    assert source_queue == []


def test_config_endpoint_preserves_and_updates_ui_grouped_state(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "ui": {
    "language": "zh",
    "coverage_filters": {
      "onlyGaps": true,
      "nextAction": "add_guide"
    },
    "browser": {
      "current_path": "/old-browser",
      "mounted_source": "/old-mount"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/config",
        json={
            "grouped_config": {
                "ui": {
                    "language": "mix",
                    "coverage_filters": {
                        "onlyGaps": False,
                        "profileKey": "aliyundriveopen",
                    },
                    "browser": {
                        "current_path": "/new-browser",
                        "mounted_source": "/new-mount",
                    },
                }
            }
        },
    )
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["ui"]["language"] == "mix"
    assert saved["ui"]["coverage_filters"]["onlyGaps"] is False
    assert saved["ui"]["coverage_filters"]["profileKey"] == "aliyundriveopen"
    assert saved["ui"]["browser"]["current_path"] == "/new-browser"
    assert saved["ui"]["browser"]["mounted_source"] == "/new-mount"


def test_openlist_login_accepts_grouped_openlist_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "openlist": {
    "url": "http://127.0.0.1:5244",
    "username": "admin",
    "password": ""
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    captured: dict[str, str] = {}

    class FakeOpenListClient:
        def __init__(self, base_url: str, username: str, password: str, token: str, **_: object) -> None:
            captured["base_url"] = base_url
            captured["username"] = username
            captured["password"] = password
            captured["token"] = token
            self.base_url = base_url.rstrip("/")
            self.username = username
            self.password = password
            self.token = "grouped-token"

        def ensure_login(self) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr(webapp_module, "OpenListClient", FakeOpenListClient)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/openlist/login",
        json={
            "grouped_config": {
                "openlist": {
                    "url": "http://127.0.0.1:5245",
                    "username": "grouped-admin",
                    "password": "grouped-pass"
                }
            }
        },
    )
    assert response.status_code == 200
    assert captured["base_url"] == "http://127.0.0.1:5245"
    assert captured["username"] == "grouped-admin"
    assert captured["password"] == "grouped-pass"
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["openlist"]["url"] == "http://127.0.0.1:5245"
    assert saved["openlist"]["username"] == "grouped-admin"
    assert saved["openlist"]["token"] == "grouped-token"
    assert "openlist_url" not in saved
    assert "openlist_token" not in saved


def test_status_persists_grouped_capture_updates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    state_path = tmp_path / "sync-state.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "state": {
    "state_file": "__STATE_FILE__"
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {}
  }
}
""".replace("__STATE_FILE__", str(state_path).replace("\\", "\\\\")).strip(),
        encoding="utf-8",
    )
    state_path.write_text(json.dumps({"target_states": {}}, ensure_ascii=False), encoding="utf-8")
    from cloudpan_bridge import webapp as webapp_module

    class FakeProviderCaptureManager:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

        def snapshots(self) -> dict[str, dict[str, object]]:
            return {
                "quark": {
                    "provider": "quark",
                    "status": "captured",
                    "message": "from live snapshot",
                    "captured": {
                        "cookie_header": "sid=1; token=2",
                    },
                }
            }

        def snapshot(self, provider: str) -> dict[str, object]:
            if provider == "guangya":
                return {
                    "provider": "guangya",
                    "status": "captured",
                    "message": "guangya live",
                    "captured": {
                        "authorization": "Bearer live-auth",
                        "access_token": "live-token",
                        "refresh_token": "live-refresh",
                        "device_id": "live-device",
                    },
                }
            return {}

        def definitions_payload(self) -> list[dict[str, object]]:
            return []

    monkeypatch.setattr(webapp_module, "ProviderCaptureManager", FakeProviderCaptureManager)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.get("/api/status")
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["targets"]["guangya"]["authorization"] == "Bearer live-auth"
    assert saved["targets"]["guangya"]["access_token"] == "live-token"
    assert saved["targets"]["guangya"]["refresh_token"] == "live-refresh"
    assert saved["targets"]["guangya"]["device_id"] == "live-device"
    assert saved["source_session"]["provider_captures"]["quark"]["captured"]["cookie_header"] == "sid=1; token=2"
    assert "guangya_authorization" not in saved
    assert "provider_captures" not in saved


def test_status_persists_explicit_empty_guangya_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    state_path = tmp_path / "sync-state.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "state": {
    "state_file": "__STATE_FILE__"
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {
      "authorization": "Bearer stale-auth",
      "access_token": "stale-token",
      "refresh_token": "stale-refresh",
      "device_id": "stale-device"
    }
  }
}
""".replace("__STATE_FILE__", str(state_path).replace("\\", "\\\\")).strip(),
        encoding="utf-8",
    )
    state_path.write_text(json.dumps({"target_states": {}}, ensure_ascii=False), encoding="utf-8")
    from cloudpan_bridge import webapp as webapp_module

    class FakeProviderCaptureManager:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

        def snapshots(self) -> dict[str, dict[str, object]]:
            return {}

        def snapshot(self, provider: str) -> dict[str, object]:
            if provider == "guangya":
                return {
                    "provider": "guangya",
                    "status": "captured",
                    "message": "guangya live",
                    "captured": {
                        "authorization": "Bearer refreshed-auth",
                        "access_token": "",
                        "refresh_token": "fresh-refresh",
                        "device_id": "fresh-device",
                    },
                }
            return {}

        def definitions_payload(self) -> list[dict[str, object]]:
            return []

    monkeypatch.setattr(webapp_module, "ProviderCaptureManager", FakeProviderCaptureManager)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.get("/api/status")
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["targets"]["guangya"]["authorization"] == "Bearer refreshed-auth"
    assert saved["targets"]["guangya"]["access_token"] == ""
    assert saved["targets"]["guangya"]["refresh_token"] == "fresh-refresh"
    assert saved["targets"]["guangya"]["device_id"] == "fresh-device"


def test_openlist_list_dirs_accepts_grouped_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "openlist": {
    "url": "http://127.0.0.1:5244",
    "username": "admin",
    "password": ""
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    captured: dict[str, str] = {}

    class FakeClient:
        def __init__(self, *, base_url: str, token: str, username: str, password: str, **_: object) -> None:
            captured["base_url"] = base_url
            captured["token"] = token
            captured["username"] = username
            captured["password"] = password

        def list_directories(self, path: str) -> dict[str, object]:
            captured["path"] = path
            return {"path": path, "items": [], "parent_path": "/"}

        def close(self) -> None:
            return None

    monkeypatch.setattr(webapp_module, "OpenListClient", FakeClient)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/openlist/list_dirs",
        json={
            "grouped_config": {
                "openlist": {
                    "url": "http://127.0.0.1:5245",
                    "username": "grouped-admin",
                    "password": "grouped-pass",
                    "token": "grouped-token"
                },
                "ui": {
                    "browser": {
                        "current_path": "/photos/2026"
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    assert captured["base_url"] == "http://127.0.0.1:5245"
    assert captured["username"] == "grouped-admin"
    assert captured["password"] == "grouped-pass"
    assert captured["token"] == "grouped-token"
    assert captured["path"] == "/photos/2026"


def test_source_analyze_accepts_grouped_source_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/from-config"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    seen: dict[str, object] = {}

    class DummySource:
        def close(self) -> None:
            seen["closed"] = True

    class FakeRunner:
        def __init__(self, config: AppConfig, log: object | None = None, source_root_for_target: str = "") -> None:
            seen["source_path"] = config.source_path
            self.source = DummySource()

        def analyze(self) -> tuple[list[SourceEntry], list[object], list[str]]:
            return (
                [SourceEntry(path="/grouped/file.txt", md5="ABC", size=1, provider="openlist", hash_type="md5")],
                [],
                [],
            )

    monkeypatch.setattr(webapp_module, "SyncRunner", FakeRunner)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/source/analyze",
        json={
            "grouped_config": {
                "sync": {
                    "source_path": "/grouped"
                }
            }
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert seen["source_path"] == "/grouped"
    assert seen["closed"] is True
    assert payload["source_path"] == "/grouped"
    assert payload["summary"]["total"] == 1


def test_config_endpoint_updates_grouped_panel_open_states(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "ui": {
    "panel_open_states": {
      "activeTab": "overview",
      "logsVisible": true
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/config",
        json={
            "grouped_config": {
                "ui": {
                    "panel_open_states": {
                        "activeTab": "sync",
                        "logsVisible": False,
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["ui"]["panel_open_states"]["activeTab"] == "sync"
    assert saved["ui"]["panel_open_states"]["logsVisible"] is False


def test_state_supports_pending_and_queue_roundtrip() -> None:
    state = SyncState(
        pending_files={
            "/a.txt": PendingFileState(path="/a.txt", md5="ABC", size=1, source_root="/src", reason="miss")
        },
        source_queue=[
            QueueItemState(source_path="/src1", source_root_for_target="/src1"),
            QueueItemState(source_path="/src2", source_root_for_target="/root", last_status="completed"),
        ],
    )
    restored = SyncState.from_dict(state.to_dict())
    assert "/a.txt" in restored.pending_files
    assert restored.pending_files["/a.txt"].reason == "miss"
    assert [item.source_path for item in restored.source_queue] == ["/src1", "/src2"]
    assert [item.source_root_for_target for item in restored.source_queue] == ["/src1", "/root"]


def test_guangya_upload_uses_string_parent_id(tmp_path: Path) -> None:
    local_file = tmp_path / "demo.bin"
    local_file.write_bytes(b"demo")
    captured: dict[str, object] = {}

    class DummyClient:
        token = ""
        refresh_token_value = ""
        device_id = ""

        def file_upload(self, path: str, name: str, parent_id: str | None = None) -> dict[str, str]:
            captured["path"] = path
            captured["name"] = name
            captured["parent_id"] = parent_id
            return {"ok": "1"}

    service = GuangyaService()
    service.client = DummyClient()  # type: ignore[assignment]

    result = service.upload_local_file(local_file, "1902430028220756040", "demo.bin")

    assert result == {"ok": "1"}
    assert captured["name"] == "demo.bin"
    assert captured["parent_id"] == "1902430028220756040"
    assert isinstance(captured["parent_id"], str)


def test_pending_selected_execution_groups_run_deepest_directories_first() -> None:
    pending_files = {
        "/root/a/1.txt": PendingFileState(path="/root/a/1.txt", md5="A", size=1),
        "/root/a/b/2.txt": PendingFileState(path="/root/a/b/2.txt", md5="B", size=1),
        "/root/a/b/c/3.txt": PendingFileState(path="/root/a/b/c/3.txt", md5="C", size=1),
        "/root/d/4.txt": PendingFileState(path="/root/d/4.txt", md5="D", size=1),
    }

    groups = build_pending_selected_execution_groups(
        [
            "/root/a/1.txt",
            "/root/a/b/2.txt",
            "/root/a/b/c/3.txt",
            "/root/d/4.txt",
        ],
        pending_files,
    )

    assert groups == [
        ("/root/a/b/c", ["/root/a/b/c/3.txt"]),
        ("/root/a/b", ["/root/a/b/2.txt"]),
        ("/root/a", ["/root/a/1.txt"]),
        ("/root/d", ["/root/d/4.txt"]),
    ]


def test_rate_limit_detection_and_cooldown() -> None:
    assert is_rate_limit_error_message("429 Too Many Requests")
    assert is_rate_limit_error_message("检测到风控，请稍后再试")
    cfg = AppConfig.from_payload(
        {
            "source_path": "/baidu-root",
            "target_path": "/dst",
            "queue_interval_ms": 3000,
            "rate_limit_mode": "safe",
        }
    )
    assert compute_rate_limit_cooldown_ms(cfg, "/baidu-root/demo") == 270000


def test_build_storage_payload_serializes_addition_and_types() -> None:
    info = OpenListDriverInfo(
        name="Demo",
        common=[
            OpenListDriverField(name="mount_path", required=True),
            OpenListDriverField(name="cache_expiration", type="number", default="30"),
        ],
        additional=[
            OpenListDriverField(name="cookie", required=True),
            OpenListDriverField(name="rapid_upload", type="bool", default="true"),
        ],
        config={},
    )

    payload = build_storage_payload(
        info,
        {
            "mount_path": "/demo",
            "cache_expiration": "60",
            "cookie": "abc",
            "rapid_upload": "false",
        },
    )

    assert payload["mount_path"] == "/demo"
    assert payload["cache_expiration"] == 60
    assert payload["addition"] == '{"cookie": "abc", "rapid_upload": false}'


def test_default_provider_specs_cover_major_sources() -> None:
    specs = default_provider_specs()
    assert {"guangya", "quark", "123pan", "p123", "189cloud", "baidu", "thunder", "aliyundriveopen", "onedrive", "googledrive", "dropbox", "openlist", "cloudreve", "github", "alias", "terabox", "yandexdisk", "webdav", "s3", "ftp", "sftp", "seafile", "smb", "azureblob", "mega", "pikpak", "115", "139yun"} <= set(specs)
    assert "cookie_header" in specs["quark"].required_keys
    assert "bdstoken" in specs["baidu"].required_keys
    assert "authorization" in specs["thunder"].required_keys
    assert "refresh_token" in specs["aliyundriveopen"].required_keys
    assert "refresh_token" in specs["onedrive"].required_keys
    assert "refresh_token" in specs["googledrive"].required_keys
    assert "refresh_token" in specs["dropbox"].required_keys
    assert specs["p123"].capture_mode == "manual"
    assert specs["openlist"].capture_mode == "manual"
    assert "refresh_token" in specs["cloudreve"].required_keys
    assert specs["github"].capture_mode == "manual"
    assert specs["alias"].capture_mode == "manual"
    assert "cookie_header" in specs["terabox"].required_keys
    assert "refresh_token" in specs["yandexdisk"].required_keys
    assert specs["webdav"].capture_mode == "manual"
    assert specs["s3"].capture_mode == "manual"
    assert specs["ftp"].capture_mode == "manual"
    assert specs["sftp"].capture_mode == "manual"
    assert specs["seafile"].capture_mode == "manual"
    assert specs["smb"].capture_mode == "manual"
    assert specs["azureblob"].capture_mode == "manual"
    assert specs["mega"].capture_mode == "manual"
    assert "refresh_token" in specs["pikpak"].required_keys
    assert "cookie_header" in specs["115"].required_keys
    assert "authorization" in specs["139yun"].required_keys


def test_capture_alias_registry_resolves_real_spec_keys() -> None:
    alias_map = build_capture_alias_to_spec_key_map()
    supported = build_capture_supported_driver_aliases()
    assert alias_map["aliyundriveopen"] == "aliyundriveopen"
    assert alias_map["alipan"] == "aliyundriveopen"
    assert alias_map["baidunetdisk"] == "baidu"
    assert alias_map["123open"] == "123pan"
    assert alias_map["p123"] == "p123"
    assert alias_map["googledrive"] == "googledrive"
    assert alias_map["dropbox"] == "dropbox"
    assert alias_map["sharepoint"] == "onedrive"
    assert alias_map["alistv3"] == "openlist"
    assert alias_map["cloudreve"] == "cloudreve"
    assert alias_map["github"] == "github"
    assert alias_map["alias"] == "alias"
    assert alias_map["terabox"] == "terabox"
    assert alias_map["yandexdisk"] == "yandexdisk"
    assert alias_map["115share"] == "115"
    assert alias_map["webdav"] == "webdav"
    assert alias_map["s3"] == "s3"
    assert alias_map["ftp"] == "ftp"
    assert alias_map["sftp"] == "sftp"
    assert alias_map["seafile"] == "seafile"
    assert alias_map["smb"] == "smb"
    assert alias_map["azureblob"] == "azureblob"
    assert alias_map["mega"] == "mega"
    assert "quarkopen" in supported
    assert "googlephotos" in supported

    resolved = resolve_capture_spec_for_driver("AliyunDriveOpen")
    assert resolved["specKey"] == "aliyundriveopen"
    assert resolved["matchedAlias"] == "aliyundriveopen"
    assert resolved["loginUrl"].startswith("https://")

    google_resolved = resolve_capture_spec_for_driver("GoogleDrive")
    assert google_resolved["specKey"] == "googledrive"
    assert google_resolved["matchedAlias"] == "googledrive"
    assert google_resolved["loginUrl"].startswith("https://")

    missing = resolve_capture_spec_for_driver("UnknownDrive")
    assert missing["specKey"] == ""
    assert missing["matchedAlias"] == ""


def test_driver_guide_supports_profile_and_alias_resolution() -> None:
    guide_123 = provider_registry_module.get_driver_guide("123Pan")
    assert guide_123 is not None
    assert guide_123["docUrl"].endswith("/123_open")
    assert guide_123["isGenericFallback"] is False
    assert guide_123["docUrlCandidates"][0].endswith("/123_open")

    guide_baidu = provider_registry_module.get_driver_guide("BaiduNetdisk")
    assert guide_baidu is not None
    assert guide_baidu["docUrl"].endswith("/baidu")

    guide_189 = provider_registry_module.get_driver_guide("189Cloud")
    assert guide_189 is not None
    assert guide_189["docUrl"].endswith("/189")
    assert any(item.endswith("/189") for item in guide_189["docUrlCandidates"])

    guide_google = provider_registry_module.get_driver_guide("GoogleDrive")
    assert guide_google is not None
    assert guide_google["docUrl"].endswith("/google_drive")

    guide_p123 = provider_registry_module.get_driver_guide("P123")
    assert guide_p123 is not None
    assert guide_p123["docUrl"].endswith("/123.html")

    guide_115 = provider_registry_module.get_driver_guide("115Share")
    assert guide_115 is not None
    assert guide_115["docUrl"].endswith("/115")

    guide_webdav = provider_registry_module.get_driver_guide("WebDav")
    assert guide_webdav is not None
    assert guide_webdav["docUrl"].endswith("/webdav")

    guide_s3 = provider_registry_module.get_driver_guide("S3")
    assert guide_s3 is not None
    assert guide_s3["docUrl"].endswith("/s3")

    guide_smb = provider_registry_module.get_driver_guide("SMB")
    assert guide_smb is not None
    assert guide_smb["docUrl"].endswith("/smb")

    guide_openlist = provider_registry_module.get_driver_guide("AListV3")
    assert guide_openlist is not None
    assert guide_openlist["docUrl"].endswith("/openlist")

    guide_terabox = provider_registry_module.get_driver_guide("TeraBox")
    assert guide_terabox is not None
    assert guide_terabox["docUrl"].endswith("/terabox")

    guide_alias = provider_registry_module.get_driver_guide("Alias")
    assert guide_alias is not None
    assert guide_alias["docUrl"].endswith("/advanced/alias")


def test_unknown_driver_guide_returns_generic_fallback_without_claiming_full_coverage() -> None:
    guide = provider_registry_module.get_driver_guide("UnknownDrive")
    assert guide is not None
    assert guide["docUrl"] == "https://doc.oplist.org/guide/drivers/"
    assert guide["isGenericFallback"] is True
    assert "https://doc.oplist.org/guide/drivers/" in guide["docUrlCandidates"]

    audit = provider_registry_module.build_driver_coverage_audit(["UnknownDrive"], target="guangya")
    row = audit["rows"][0]
    assert row["guideDocUrl"] == "https://doc.oplist.org/guide/drivers/"
    assert row["hasGuide"] is False
    assert row["matchedGuideKey"] == ""


def test_openlist_extract_hash_fields_supports_md5_and_gcid() -> None:
    result = OpenListClient._extract_hash_fields(
        {
            "name": "demo.bin",
            "hash_info": {"md5": "abc123", "gcid": "A" * 40},
            "fileId": "123",
            "provider": "Thunder",
        }
    )
    assert result["md5"] == "ABC123"
    assert result["etag"] == "ABC123"
    assert result["gcid"] == "A" * 40
    assert result["hash_type"] == "md5"
    assert OpenListClient._extract_source_id({"fileId": 123}) == "123"
    assert OpenListClient._extract_provider({"provider": "Thunder"}) == "Thunder"


def test_openlist_extract_hash_fields_supports_gcid_only() -> None:
    result = OpenListClient._extract_hash_fields(
        {
            "name": "demo.bin",
            "hash_info": {"gcid": "B" * 40},
        }
    )
    assert result["md5"] == ""
    assert result["gcid"] == "B" * 40
    assert result["hash_type"] == "gcid"


def test_openlist_extract_hash_fields_allows_non_fast_upload_fingerprint_only() -> None:
    result = OpenListClient._extract_hash_fields(
        {
            "name": "demo.bin",
            "hash_info": {"sha1": "C" * 40, "pickcode": "pc-1"},
        }
    )
    assert result["md5"] == ""
    assert result["gcid"] == ""
    assert result["sha1"] == "C" * 40
    assert result["pickcode"] == "pc-1"
    assert result["hash_type"] == "sha1"


def test_openlist_extract_hash_fields_supports_extended_fingerprint_fields() -> None:
    result = OpenListClient._extract_hash_fields(
        {
            "name": "demo.bin",
            "hash_info": {
                "sha256": "E" * 64,
                "pre_hash": "F" * 32,
                "slice_md5": "1" * 32,
                "content_hash": "2" * 64,
            },
            "contenthash": "3" * 64,
        }
    )
    assert result["sha256"] == "E" * 64
    assert result["pre_hash"] == "F" * 32
    assert result["slice_md5"] == "1" * 32
    assert result["content_hash"] == "2" * 64
    assert result["provider_specific"]["contenthash"] == "3333333333333333333333333333333333333333333333333333333333333333"


def test_build_driver_prefill_values_matches_common_tokens() -> None:
    fields = [
        OpenListDriverField(name="cookie"),
        OpenListDriverField(name="authorization"),
        OpenListDriverField(name="refresh_token"),
        OpenListDriverField(name="bdstoken"),
        OpenListDriverField(name="device_id"),
    ]
    values = build_driver_prefill_values(
        fields,
        {
            "cookie_header": "sid=1; token=2",
            "authorization": "Bearer abc",
            "refresh_token": "refresh-demo",
            "bdstoken": "bd-demo",
            "device_id": "dev-demo",
        },
        "baidu",
    )
    assert values == {
        "cookie": "sid=1; token=2",
        "authorization": "Bearer abc",
        "refresh_token": "refresh-demo",
        "bdstoken": "bd-demo",
        "device_id": "dev-demo",
    }


def test_build_driver_capture_spec_derives_generic_requirements() -> None:
    fields = [
        OpenListDriverField(name="cookie"),
        OpenListDriverField(name="refresh_token"),
        OpenListDriverField(name="sessionKey"),
    ]
    derived = derive_capture_requirements_from_fields(fields)
    assert derived["required_keys"] == ["cookie_header", "refresh_token", "session_key"]
    spec = build_driver_capture_spec("AliyundriveOpen", fields)
    assert spec.key == "driver::aliyundriveopen"
    assert spec.login_url == "https://www.alipan.com/"
    assert "cookie" in spec.description


def test_status_restores_provider_captures_from_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    state_path = tmp_path / "sync-state.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "state": {
    "state_file": "__STATE_FILE__"
  },
  "provider_captures": {
    "quark": {
      "provider": "quark",
      "status": "captured",
      "message": "from config",
      "captured": {
        "cookie_header": "sid=1; token=2"
      }
    }
  }
}
""".replace("__STATE_FILE__", str(state_path).replace("\\", "\\\\")).strip(),
        encoding="utf-8",
    )
    state_path.write_text(
        json.dumps(
            {
                "target_states": {
                    "guangya": {
                        "access_token": "tok",
                        "refresh_token": "refresh",
                        "device_id": "device",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    app = create_app(config_path)
    client = TestClient(app)
    status = client.get("/api/status")
    assert status.status_code == 200
    body = status.json()
    assert body["provider_captures"]["quark"]["captured"]["cookie_header"] == "sid=1; token=2"
    assert body["source_runtime"]["provider_class"] == "OpenListSourceProvider"
    assert body["source_runtime"]["requested_provider_preference"] == "auto"
    assert body["sourceEnrichment"]["provider_key"] == "generic_openlist_driver"
    assert body["sourceEnrichment"]["supported"] is False
    assert body["active_target"] == "guangya"
    assert body["active_target_state"]["has_state"] is True
    assert body["active_target_state"]["field_count"] == 3
    assert "access_token" in body["active_target_state"]["fields"]
    assert body["target_preflight"]["target_key"] == "guangya"
    assert body["target_preflight"]["adapter_capability"]["supports_fast_upload"] is True
    assert body["source_runtime"]["source_target_route"]["decision_bucket"] == "openlist_upload_path"


def test_provider_driver_blueprint_endpoint_returns_dynamic_capture_spec(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from unittest.mock import patch
    from cloudpan_bridge.webapp import create_app

    app = create_app(config_path)
    client = TestClient(app)
    info = OpenListDriverInfo(
        name="AliyundriveOpen",
        common=[OpenListDriverField(name="mount_path", required=True)],
        additional=[OpenListDriverField(name="refresh_token"), OpenListDriverField(name="device_id")],
        config={},
    )
    with patch("cloudpan_bridge.webapp.OpenListAdminClient.driver_info", return_value=info):
        response = client.get("/api/provider/driver_blueprint", params={"driver": "AliyundriveOpen"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["key"] == "driver::aliyundriveopen"
    assert payload["login_url"] == "https://www.alipan.com/"
    assert payload["required_keys"] == ["refresh_token", "device_id"]
    assert payload["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/aliyundrive_open"
    assert payload["guide"]["defaults"]["root_folder_id"] == "root"


def test_provider_registry_endpoint_returns_serialized_guides(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/registry")
    assert response.status_code == 200
    payload = response.json()
    assert payload["guides"]["aliyundriveopen"]["docUrl"] == "https://doc.oplist.org/guide/drivers/aliyundrive_open"
    assert payload["guides"]["p123"]["docUrl"] == "https://doc.oplist.org/guide/drivers/123.html"
    assert payload["guides"]["googledrive"]["docUrl"] == "https://doc.oplist.org/guide/drivers/google_drive"
    assert payload["guides"]["webdav"]["docUrl"] == "https://doc.oplist.org/guide/drivers/webdav"
    assert payload["guides"]["s3"]["docUrl"] == "https://doc.oplist.org/guide/drivers/s3"
    assert payload["guides"]["openlist"]["docUrl"] == "https://doc.oplist.org/guide/drivers/openlist"
    assert payload["guides"]["cloudreve"]["docUrl"] == "https://doc.oplist.org/guide/drivers/cloudreve_v4"
    assert payload["guides"]["github"]["docUrl"] == "https://doc.oplist.org/guide/drivers/github"
    assert payload["guides"]["alias"]["docUrl"] == "https://doc.oplist.org/guide/advanced/alias"
    assert payload["guides"]["terabox"]["docUrl"] == "https://doc.oplist.org/guide/drivers/terabox"
    assert payload["guides"]["yandexdisk"]["docUrl"] == "https://doc.oplist.org/guide/drivers/yandex"
    assert payload["guides"]["smb"]["docUrl"] == "https://doc.oplist.org/guide/drivers/smb"
    assert payload["guides"]["azureblob"]["docUrl"] == "https://doc.oplist.org/guide/drivers/azure_blob"
    assert payload["guides"]["mega"]["docUrl"] == "https://doc.oplist.org/guide/drivers/mega"
    assert payload["guides"]["quark"]["defaults"]["web_proxy"] == "true"
    assert payload["source_profiles"]["189cloud"]["recommendedRateProfile"] == "safe"
    assert payload["source_profiles"]["p123"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/123.html"
    assert payload["source_profiles"]["189cloud"]["loginMode"] == "cookie + sessionKey style fields"
    assert payload["source_profiles"]["googledrive"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/google_drive"
    assert payload["source_profiles"]["dropbox"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/dropbox"
    assert payload["source_profiles"]["openlist"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/openlist"
    assert payload["source_profiles"]["cloudreve"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/cloudreve_v4"
    assert payload["source_profiles"]["github"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/github"
    assert payload["source_profiles"]["alias"]["docLinks"][0] == "https://doc.oplist.org/guide/advanced/alias"
    assert payload["source_profiles"]["terabox"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/terabox"
    assert payload["source_profiles"]["yandexdisk"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/yandex"
    assert payload["source_profiles"]["115"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/115"
    assert payload["source_profiles"]["webdav"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/webdav"
    assert payload["source_profiles"]["s3"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/s3"
    assert payload["source_profiles"]["smb"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/smb"
    assert payload["source_profiles"]["azureblob"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/azure_blob"
    assert payload["source_profiles"]["mega"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/mega"
    assert payload["source_profiles"]["quark"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/quark.html"
    assert payload["source_profiles"]["thunder"]["hashFieldsSupported"] == ["gcid"]
    assert payload["target_profiles"]["guangya"]["fastUploadHashes"] == ["md5", "gcid"]
    assert payload["target_profiles"]["guangya"]["authMode"] == "authorization + access_token + refresh_token + device_id"
    assert payload["target_profiles"]["guangya"]["autoCreateDir"] is True
    assert payload["target_profiles"]["localfs"]["authMode"] == "local filesystem path"
    assert payload["target_profiles"]["localfs"]["autoCreateDir"] is True
    assert payload["target_profiles"]["webdav"]["authMode"] == "webdav url + username/password"
    assert payload["target_profiles"]["webdav"]["autoCreateDir"] is True
    assert payload["target_profiles"]["s3"]["authMode"] == "endpoint + bucket + access key/secret"
    assert payload["target_profiles"]["s3"]["autoCreateDir"] is True
    assert payload["target_profiles"]["seafile"]["authMode"] == "seafile url + token or username/password + repo"
    assert payload["target_profiles"]["seafile"]["autoCreateDir"] is True
    assert payload["target_profiles"]["azureblob"]["authMode"] == "account url + container + account key"
    assert payload["target_profiles"]["azureblob"]["autoCreateDir"] is True
    assert payload["target_profiles"]["smb"]["authMode"] == "smb url + username/password"
    assert payload["target_profiles"]["smb"]["autoCreateDir"] is True
    assert payload["target_profiles"]["ftp"]["authMode"] == "ftp url + username/password"
    assert payload["target_profiles"]["ftp"]["autoCreateDir"] is True
    assert payload["target_profiles"]["sftp"]["authMode"] == "sftp url + username/password"
    assert payload["target_profiles"]["sftp"]["autoCreateDir"] is True
    assert payload["driver_matrix"]["thunder"]["level"] == "fast_upload_partial"


def test_provider_captures_endpoint_includes_complex_driver_specs(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/captures")
    assert response.status_code == 200
    payload = response.json()
    providers = {item["key"]: item for item in payload["providers"]}
    assert providers["aliyundriveopen"]["recommended_drivers"] == ["AliyundriveOpen", "AliyunDrive", "Alipan"]
    assert providers["aliyundriveopen"]["provider_key"] == "aliyundriveopen"
    assert providers["aliyundriveopen"]["auth_mode"] == "refresh token + online api or own open platform app"
    assert providers["aliyundriveopen"]["auth_interface"]["browser_capture"]["supported"] is True
    assert providers["aliyundriveopen"]["auth_interface"]["manual_fields"]["supported"] is True
    assert providers["aliyundriveopen"]["auth_interface"]["openlist_mount"]["supported"] is True
    assert providers["aliyundriveopen"]["auth_interface"]["direct_api"]["supported"] is True
    assert providers["aliyundriveopen"]["auth_interface"]["docs"]["doc_url"] == "https://doc.oplist.org/guide/drivers/aliyundrive_open"
    assert providers["aliyundriveopen"]["auth_interface"]["recommended_defaults"]["rate_profile"] == "balanced"
    assert providers["p123"]["capture_mode"] == "manual"
    assert providers["p123"]["auth_interface"]["browser_capture"]["supported"] is False
    assert providers["p123"]["auth_interface"]["manual_fields"]["required_keys"] == ["username", "password"]
    assert providers["p123"]["auth_interface"]["direct_api"]["supported"] is True
    assert providers["onedrive"]["required_keys"] == ["refresh_token"]
    assert providers["googledrive"]["required_keys"] == ["refresh_token"]
    assert providers["dropbox"]["required_keys"] == ["refresh_token"]
    assert providers["openlist"]["capture_mode"] == "manual"
    assert providers["cloudreve"]["required_keys"] == ["refresh_token"]
    assert providers["github"]["capture_mode"] == "manual"
    assert providers["alias"]["capture_mode"] == "manual"
    assert providers["terabox"]["required_keys"] == ["cookie_header"]
    assert providers["yandexdisk"]["required_keys"] == ["refresh_token"]
    assert providers["webdav"]["capture_mode"] == "manual"
    assert providers["s3"]["capture_mode"] == "manual"
    assert providers["ftp"]["capture_mode"] == "manual"
    assert providers["sftp"]["capture_mode"] == "manual"
    assert providers["seafile"]["capture_mode"] == "manual"
    assert providers["smb"]["capture_mode"] == "manual"
    assert providers["azureblob"]["capture_mode"] == "manual"
    assert providers["mega"]["capture_mode"] == "manual"
    assert providers["115"]["required_keys"] == ["cookie_header"]
    assert providers["pikpak"]["login_url"] == "https://mypikpak.com/drive/all"
    assert providers["139yun"]["required_keys"] == ["authorization"]
    assert providers["aliyundriveopen"]["source_profile"]["key"] == "aliyundriveopen"
    assert providers["p123"]["source_profile"]["key"] == "p123"
    assert providers["googledrive"]["source_profile"]["key"] == "googledrive"
    assert providers["onedrive"]["source_profile"]["recommendedRateProfile"] == "balanced"
    assert providers["139yun"]["source_profile"]["docLinks"] == ["https://doc.oplist.org/guide/drivers/139.html"]
    assert providers["aliyundriveopen"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/aliyundrive_open"
    assert providers["p123"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/123.html"
    assert providers["googledrive"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/google_drive"
    assert providers["openlist"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/openlist"
    assert providers["openlist"]["auth_interface"]["direct_api"]["supported"] is True
    assert providers["cloudreve"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/cloudreve_v4"
    assert providers["github"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/github"
    assert providers["alias"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/advanced/alias"
    assert providers["terabox"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/terabox"
    assert providers["yandexdisk"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/yandex"
    assert providers["115"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/115"
    assert providers["139yun"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/139.html"


def test_manual_provider_capture_switches_to_manual_snapshot(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capture/start",
        json={
            "provider": "webdav",
            "driver": "WebDav",
        },
    )
    assert response.status_code == 200
    captures = client.get("/api/provider/captures")
    assert captures.status_code == 200
    providers = {item["key"]: item for item in captures.json()["providers"]}
    snapshots = captures.json()["snapshots"]
    assert providers["webdav"]["capture_mode"] == "manual"
    assert snapshots["webdav"]["status"] == "manual"
    assert "url" in snapshots["webdav"]["message"]


def test_manual_provider_capture_start_accepts_grouped_payload(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capture/start",
        json={
            "grouped_config": {
                "ui": {
                    "provider_capture": {
                        "provider": "webdav",
                        "driver": "WebDav",
                        "login_url": "https://dav.example.com/login"
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    captures = client.get("/api/provider/captures")
    assert captures.status_code == 200
    snapshots = captures.json()["snapshots"]
    assert snapshots["webdav"]["status"] == "manual"


def test_provider_capability_endpoint_returns_driver_to_guangya_matrix(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/capability", params={"driver": "AliyundriveOpen"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["driver"] == "AliyundriveOpen"
    assert payload["sourceProfile"]["key"] == "aliyundriveopen"
    assert payload["targetProfile"]["key"] == "guangya"
    assert payload["level"] == "download_upload_only"


def test_provider_capability_endpoint_supports_webdav_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "webdav",
    "webdav": {
      "url": "https://dav.example.com/root",
      "username": "dav-user",
      "password": "dav-pass"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/capability", params={"driver": "Quark", "target": "webdav"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["targetProfile"]["key"] == "webdav"
    assert payload["level"] == "download_upload_only"
    assert "WebDAV" in payload["recommendedFlow"]


def test_provider_capability_endpoint_supports_ftp_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "ftp",
    "ftp": {
      "url": "ftp://ftp.example.com:21/root",
      "username": "ftp-user",
      "password": "ftp-pass"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/capability", params={"driver": "Quark", "target": "ftp"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["targetProfile"]["key"] == "ftp"
    assert payload["level"] == "download_upload_only"
    assert "FTP" in payload["recommendedFlow"]


def test_provider_coverage_audit_endpoint_reports_registry_and_capture_coverage(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["AliyundriveOpen", "OneDrive", "UnknownDrive", "Thunder"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    backlog = payload["backlog"]
    execution_plan = payload["executionPlan"]
    assert payload["totals"]["total"] == 4
    assert payload["gapBuckets"]["fullyCovered"] >= 1
    assert backlog[0]["normalized"] == "unknowndrive"
    assert backlog[0]["priorityRank"] == 1
    assert execution_plan["totalBacklog"] == len(backlog)
    assert execution_plan["waveCount"] >= 1
    assert execution_plan["waves"][0]["nextAction"] == "add_profile_first"
    assert "UnknownDrive" in execution_plan["waves"][0]["drivers"]
    assert rows["aliyundriveopen"]["hasProfile"] is True
    assert rows["aliyundriveopen"]["hasGuide"] is True
    assert rows["aliyundriveopen"]["canonicalDriverKey"] == "aliyundriveopen"
    assert rows["aliyundriveopen"]["matchedGuideKey"] == "aliyundriveopen"
    assert rows["aliyundriveopen"]["hasCapture"] is True
    assert rows["aliyundriveopen"]["guideDocUrl"].endswith("/aliyundrive_open")
    assert rows["aliyundriveopen"]["captureSpecKey"] == "aliyundriveopen"
    assert rows["aliyundriveopen"]["captureMatchedAlias"] == "aliyundriveopen"
    assert rows["aliyundriveopen"]["captureLoginUrl"].startswith("https://")
    assert rows["aliyundriveopen"]["capabilityLevel"] == "download_upload_only"
    assert rows["aliyundriveopen"]["nextAction"] == "covered"
    assert rows["thunder"]["hasCapability"] is True
    assert rows["thunder"]["captureSpecKey"] == "thunder"
    assert rows["unknowndrive"]["hasProfile"] is False
    assert rows["unknowndrive"]["hasGuide"] is False
    assert rows["unknowndrive"]["canonicalDriverKey"] == "generic"
    assert rows["unknowndrive"]["matchedGuideKey"] == ""
    assert rows["unknowndrive"]["hasCapture"] is False
    assert rows["unknowndrive"]["captureSpecKey"] == ""
    assert rows["unknowndrive"]["missingItems"] == ["profile", "guide", "capture", "capability"]


def test_provider_coverage_audit_marks_google_dropbox_115_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["GoogleDrive", "Dropbox", "115Share"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    assert rows["googledrive"]["hasProfile"] is True
    assert rows["googledrive"]["hasGuide"] is True
    assert rows["googledrive"]["hasCapture"] is True
    assert rows["googledrive"]["hasCapability"] is True
    assert rows["googledrive"]["nextAction"] == "covered"
    assert rows["dropbox"]["hasProfile"] is True
    assert rows["dropbox"]["hasGuide"] is True
    assert rows["dropbox"]["hasCapture"] is True
    assert rows["dropbox"]["hasCapability"] is True
    assert rows["dropbox"]["capabilityLevel"] == "download_upload_only"
    assert rows["115share"]["hasProfile"] is True
    assert rows["115share"]["hasGuide"] is True
    assert rows["115share"]["hasCapture"] is True
    assert rows["115share"]["hasCapability"] is True


def test_provider_coverage_audit_marks_manual_protocol_drivers_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["WebDav", "S3", "FTP", "SFTP", "Seafile"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    assert rows["webdav"]["hasProfile"] is True
    assert rows["webdav"]["hasGuide"] is True
    assert rows["webdav"]["hasCapture"] is True
    assert rows["webdav"]["hasCapability"] is True
    assert rows["webdav"]["capabilityLevel"] == "download_upload_only"
    assert rows["s3"]["hasProfile"] is True
    assert rows["s3"]["hasGuide"] is True
    assert rows["s3"]["hasCapture"] is True
    assert rows["s3"]["hasCapability"] is True
    assert rows["ftp"]["hasProfile"] is True
    assert rows["sftp"]["hasProfile"] is True
    assert rows["seafile"]["hasProfile"] is True
    assert rows["seafile"]["capabilityLevel"] == "fast_upload_partial"


def test_provider_coverage_audit_marks_smb_azureblob_mega_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["SMB", "AzureBlob", "Mega"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    assert rows["smb"]["hasProfile"] is True
    assert rows["smb"]["hasGuide"] is True
    assert rows["smb"]["hasCapture"] is True
    assert rows["smb"]["hasCapability"] is True
    assert rows["azureblob"]["hasProfile"] is True
    assert rows["azureblob"]["hasGuide"] is True
    assert rows["azureblob"]["hasCapture"] is True
    assert rows["azureblob"]["hasCapability"] is True
    assert rows["mega"]["hasProfile"] is True
    assert rows["mega"]["hasGuide"] is True
    assert rows["mega"]["hasCapture"] is True
    assert rows["mega"]["hasCapability"] is True


def test_provider_coverage_audit_marks_openlist_cloudreve_terabox_yandex_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["OpenList", "AListV3", "Cloudreve", "TeraBox", "YandexDisk", "Sharepoint", "Github"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    assert rows["openlist"]["hasProfile"] is True
    assert rows["openlist"]["hasGuide"] is True
    assert rows["openlist"]["hasCapture"] is True
    assert rows["openlist"]["hasCapability"] is True
    assert rows["alistv3"]["hasProfile"] is True
    assert rows["alistv3"]["canonicalDriverKey"] == "openlist"
    assert rows["cloudreve"]["hasProfile"] is True
    assert rows["cloudreve"]["hasGuide"] is True
    assert rows["cloudreve"]["hasCapture"] is True
    assert rows["cloudreve"]["hasCapability"] is True
    assert rows["terabox"]["hasProfile"] is True
    assert rows["terabox"]["hasGuide"] is True
    assert rows["terabox"]["hasCapture"] is True
    assert rows["terabox"]["hasCapability"] is True
    assert rows["yandexdisk"]["hasProfile"] is True
    assert rows["yandexdisk"]["hasGuide"] is True
    assert rows["yandexdisk"]["hasCapture"] is True
    assert rows["yandexdisk"]["hasCapability"] is True
    assert rows["sharepoint"]["hasProfile"] is True
    assert rows["sharepoint"]["canonicalDriverKey"] == "onedrive"
    assert rows["sharepoint"]["captureSpecKey"] == "onedrive"
    assert rows["github"]["hasProfile"] is True
    assert rows["github"]["hasGuide"] is True
    assert rows["github"]["hasCapture"] is True
    assert rows["github"]["hasCapability"] is True


def test_provider_coverage_audit_marks_alias_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["Alias"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    assert rows["alias"]["hasProfile"] is True
    assert rows["alias"]["hasGuide"] is True
    assert rows["alias"]["hasCapture"] is True
    assert rows["alias"]["hasCapability"] is True
    assert rows["alias"]["capabilityLevel"] == "download_upload_only"


def test_provider_coverage_audit_marks_p123_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["P123"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["normalized"]: item for item in payload["rows"]}
    assert rows["p123"]["hasProfile"] is True
    assert rows["p123"]["hasGuide"] is True
    assert rows["p123"]["hasCapture"] is True
    assert rows["p123"]["hasCapability"] is True
    assert rows["p123"]["capabilityLevel"] == "download_upload_only"


def test_provider_coverage_audit_can_infer_dynamic_profile_capture_and_capability() -> None:
    live_fields = {
        "unknowndrive": [
            OpenListDriverField(name="refresh_token", required=True),
            OpenListDriverField(name="root_folder_id", default="root"),
            OpenListDriverField(name="use_online_api", default="true"),
        ]
    }
    audit = provider_registry_module.build_driver_coverage_audit(
        ["UnknownDrive"],
        target="guangya",
        live_driver_fields_map=live_fields,
    )
    row = audit["rows"][0]
    assert row["canonicalDriverKey"] == "dynamic_unknowndrive"
    assert row["hasProfile"] is True
    assert row["profileIsDynamic"] is True
    assert row["hasCapture"] is True
    assert row["captureIsDynamic"] is True
    assert row["hasCapability"] is True
    assert row["capabilityIsDynamic"] is True
    assert row["capabilityLevel"] == "download_upload_only"
    assert row["dynamicRequiredKeys"] == ["refresh_token"]
    assert row["nextAction"] == "add_guide"
    assert row["missingItems"] == ["guide"]


def test_provider_coverage_audit_uses_real_capture_specs_instead_of_profile_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    original_profiles = provider_registry_module.SOURCE_PROVIDER_PROFILES
    fake_profiles = {
        **original_profiles,
        "fakecapturegap": {
            **dict(original_profiles["generic"]),
            "key": "fakecapturegap",
            "label": "Fake Capture Gap",
            "label_zh": "假驱动抓取缺口",
            "driver_aliases": ["FakeCaptureGap"],
            "doc_links": [],
            "capability_to_targets": {
                "guangya": {
                    "level": "download_upload_only",
                    "recommended_flow": "仅用于测试覆盖审计。",
                    "recommended_flow_en": "For coverage audit regression testing only.",
                }
            },
        },
    }
    monkeypatch.setattr(provider_registry_module, "SOURCE_PROVIDER_PROFILES", fake_profiles)

    audit = provider_registry_module.build_driver_coverage_audit(["FakeCaptureGap"], target="guangya")
    row = audit["rows"][0]
    assert row["normalized"] == "fakecapturegap"
    assert row["hasProfile"] is True
    assert row["hasGuide"] is False
    assert row["hasCapture"] is False
    assert row["captureSpecKey"] == ""
    assert row["hasCapability"] is True
    assert row["onboardingReady"] is True
    assert row["onboardingStage"] == "ready_for_guide"
    assert row["missingItems"] == ["guide", "capture"]
    assert row["nextAction"] == "add_guide"
    assert audit["gapBuckets"]["missingCapture"] == 1


def test_provider_coverage_audit_endpoint_supports_filtered_view_export(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["AliyundriveOpen", "UnknownDrive", "Thunder"],
            "target": "guangya",
            "only_gaps": True,
            "next_action": "add_profile_first",
            "missing_item": "profile",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["filters"]["onlyGaps"] is True
    assert payload["filters"]["nextAction"] == "add_profile_first"
    assert payload["filters"]["missingItem"] == "profile"
    assert payload["totals"]["total"] == 1
    assert payload["rows"][0]["normalized"] == "unknowndrive"
    assert payload["backlog"][0]["normalized"] == "unknowndrive"
    assert payload["executionPlan"]["waves"][0]["nextAction"] == "add_profile_first"
    assert payload["rows"][0]["onboardingReady"] is False
    assert payload["rows"][0]["onboardingStage"] == "needs_profile_bootstrap"


def test_provider_coverage_audit_endpoint_supports_capability_and_profile_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["AliyundriveOpen", "OneDrive", "UnknownDrive", "Thunder"],
            "target": "guangya",
            "capability_level": "download_upload_only",
            "profile_key": "aliyundriveopen",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["filters"]["capabilityLevel"] == "download_upload_only"
    assert payload["filters"]["profileKey"] == "aliyundriveopen"
    assert payload["totals"]["total"] == 1
    assert payload["rows"][0]["normalized"] == "aliyundriveopen"
    assert payload["rows"][0]["profileKey"] == "aliyundriveopen"
    assert payload["rows"][0]["capabilityLevel"] == "download_upload_only"
    assert payload["rows"][0]["onboardingStage"] == "covered"
    assert payload["backlog"] == []


def test_provider_coverage_audit_filtered_backlog_keeps_capability_and_profile_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_profiles = provider_registry_module.SOURCE_PROVIDER_PROFILES
    fake_profiles = {
        **original_profiles,
        "fakecapturegap": {
            **dict(original_profiles["generic"]),
            "key": "fakecapturegap",
            "label": "Fake Capture Gap",
            "label_zh": "假驱动抓取缺口",
            "driver_aliases": ["FakeCaptureGap"],
            "doc_links": [],
            "capability_to_targets": {
                "guangya": {
                    "level": "download_upload_only",
                    "recommended_flow": "仅用于测试 backlog 过滤。",
                    "recommended_flow_en": "For backlog filtering regression testing only.",
                }
            },
        },
    }
    monkeypatch.setattr(provider_registry_module, "SOURCE_PROVIDER_PROFILES", fake_profiles)
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["AliyundriveOpen", "OneDrive", "UnknownDrive", "FakeCaptureGap"],
            "target": "guangya",
            "only_gaps": True,
            "capability_level": "download_upload_only",
            "profile_key": "fakecapturegap",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["totals"]["total"] == 1
    assert payload["rows"][0]["normalized"] == "fakecapturegap"
    assert payload["backlog"][0]["normalized"] == "fakecapturegap"
    assert payload["backlog"][0]["profileKey"] == "fakecapturegap"
    assert payload["backlog"][0]["capabilityLevel"] == "download_upload_only"
    assert payload["executionPlan"]["waves"][0]["profileKeys"] == ["fakecapturegap"]


def test_provider_coverage_audit_marks_123open_capture_as_covered(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["123Open"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    row = response.json()["rows"][0]
    assert row["normalized"] == "123open"
    assert row["profileKey"] == "123pan"
    assert row["hasCapture"] is True
    assert row["captureSpecKey"] == "123pan"
    assert row["captureMatchedAlias"] == "123open"
    assert row["onboardingReady"] is False
    assert row["onboardingStage"] == "covered"
    assert "capture" not in row["missingItems"]


def test_provider_coverage_audit_supports_onboarding_ready_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    original_profiles = provider_registry_module.SOURCE_PROVIDER_PROFILES
    fake_profiles = {
        **original_profiles,
        "fakecapturegap": {
            **dict(original_profiles["generic"]),
            "key": "fakecapturegap",
            "label": "Fake Capture Gap",
            "label_zh": "假驱动抓取缺口",
            "driver_aliases": ["FakeCaptureGap"],
            "doc_links": [],
            "capability_to_targets": {
                "guangya": {
                    "level": "download_upload_only",
                    "recommended_flow": "仅用于测试 onboarding-ready 过滤。",
                    "recommended_flow_en": "For onboarding-ready filter regression testing only.",
                }
            },
        },
    }
    monkeypatch.setattr(provider_registry_module, "SOURCE_PROVIDER_PROFILES", fake_profiles)
    audit = provider_registry_module.build_driver_coverage_audit(["UnknownDrive", "FakeCaptureGap"], target="guangya")
    filtered = provider_registry_module.filter_driver_coverage_audit(
        audit,
        only_onboarding_ready=True,
        onboarding_stage="ready_for_guide",
    )
    assert filtered["filters"]["onlyOnboardingReady"] is True
    assert filtered["filters"]["onboardingStage"] == "ready_for_guide"
    assert filtered["totals"]["total"] == 1
    assert filtered["rows"][0]["normalized"] == "fakecapturegap"
    assert filtered["rows"][0]["onboardingReady"] is True
    assert filtered["backlog"][0]["normalized"] == "fakecapturegap"
    assert filtered["executionPlan"]["waves"][0]["onboardingStage"] == "ready_for_guide"


def test_provider_coverage_audit_markdown_endpoint_renders_backlog_report(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit_markdown",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "# CloudPan Bridge 驱动覆盖审计" in text
    assert "`UnknownDrive` | P1 | add_profile_first" in text
    assert "## 执行波次建议" in text
    assert "Wave P1 | `add_profile_first` | `needs_profile_bootstrap`" in text
    assert "| `AliyundriveOpen` | yes | yes | yes | yes | `download_upload_only` | 4/4 | `covered` | `aliyundriveopen` | - |" in text


def test_provider_coverage_audit_markdown_endpoint_renders_filtered_view(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit_markdown",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen"],
            "target": "guangya",
            "only_gaps": True,
            "next_action": "add_profile_first",
            "missing_item": "profile",
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "- 只看缺口: `True`" in text
    assert "- 只看可直接接入: `False`" in text
    assert "- 下一步动作: `add_profile_first`" in text
    assert "- 缺口类型: `profile`" in text
    assert "- 能力等级: `-`" in text
    assert "- Profile Key: `-`" in text
    assert "- 接入阶段: `-`" in text
    assert "`UnknownDrive` | P1 | add_profile_first" in text
    assert "`AliyundriveOpen` | P99" not in text


def test_provider_coverage_audit_markdown_endpoint_renders_capability_and_profile_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit_markdown",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen", "Thunder"],
            "target": "guangya",
            "capability_level": "download_upload_only",
            "profile_key": "aliyundriveopen",
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "- 能力等级: `download_upload_only`" in text
    assert "- Profile Key: `aliyundriveopen`" in text
    assert "| `AliyundriveOpen` | yes | yes | yes | yes | `download_upload_only` | 4/4 | `covered` | `aliyundriveopen` | - |" in text
    assert "| `Thunder` |" not in text


def test_provider_coverage_audit_markdown_filtered_backlog_still_renders_after_profile_filter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_profiles = provider_registry_module.SOURCE_PROVIDER_PROFILES
    fake_profiles = {
        **original_profiles,
        "fakecapturegap": {
            **dict(original_profiles["generic"]),
            "key": "fakecapturegap",
            "label": "Fake Capture Gap",
            "label_zh": "假驱动抓取缺口",
            "driver_aliases": ["FakeCaptureGap"],
            "doc_links": [],
            "capability_to_targets": {
                "guangya": {
                    "level": "download_upload_only",
                    "recommended_flow": "仅用于测试 backlog 过滤。",
                    "recommended_flow_en": "For backlog filtering regression testing only.",
                }
            },
        },
    }
    monkeypatch.setattr(provider_registry_module, "SOURCE_PROVIDER_PROFILES", fake_profiles)
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit_markdown",
        json={
            "drivers": ["AliyundriveOpen", "OneDrive", "UnknownDrive", "FakeCaptureGap"],
            "target": "guangya",
            "only_gaps": True,
            "capability_level": "download_upload_only",
            "profile_key": "fakecapturegap",
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "- Profile Key: `fakecapturegap`" in text
    assert "- 能力等级: `download_upload_only`" in text
    assert "`FakeCaptureGap` | P2 | add_guide" in text


def test_provider_coverage_audit_markdown_supports_onboarding_ready_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    original_profiles = provider_registry_module.SOURCE_PROVIDER_PROFILES
    fake_profiles = {
        **original_profiles,
        "fakecapturegap": {
            **dict(original_profiles["generic"]),
            "key": "fakecapturegap",
            "label": "Fake Capture Gap",
            "label_zh": "假驱动抓取缺口",
            "driver_aliases": ["FakeCaptureGap"],
            "doc_links": [],
            "capability_to_targets": {
                "guangya": {
                    "level": "download_upload_only",
                    "recommended_flow": "仅用于测试 onboarding-ready 过滤。",
                    "recommended_flow_en": "For onboarding-ready filter regression testing only.",
                }
            },
        },
    }
    monkeypatch.setattr(provider_registry_module, "SOURCE_PROVIDER_PROFILES", fake_profiles)
    audit = provider_registry_module.build_driver_coverage_audit(["UnknownDrive", "FakeCaptureGap"], target="guangya")
    filtered = provider_registry_module.filter_driver_coverage_audit(
        audit,
        only_onboarding_ready=True,
        onboarding_stage="ready_for_guide",
    )
    text = provider_registry_module.render_driver_coverage_audit_markdown(filtered)
    assert "- 只看可直接接入: `True`" in text
    assert "- 接入阶段: `ready_for_guide`" in text
    assert "`FakeCaptureGap` | P2 | add_guide" in text
    assert "`UnknownDrive`" not in text


def test_provider_coverage_scaffold_endpoint_returns_grouped_backlog(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_scaffold",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["totalBacklog"] == 1
    assert payload["byNextAction"]["add_profile_first"][0]["driver"] == "UnknownDrive"
    assert payload["items"][0]["missingItems"] == ["profile", "guide", "capture", "capability"]


def test_provider_coverage_scaffold_endpoint_respects_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_scaffold",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen", "Thunder"],
            "target": "guangya",
            "next_action": "add_profile_first",
            "missing_item": "profile",
            "only_gaps": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["totalBacklog"] == 1
    assert list(payload["byNextAction"].keys()) == ["add_profile_first"]
    assert payload["items"][0]["driver"] == "UnknownDrive"


def test_provider_coverage_scaffold_markdown_endpoint_renders_task_groups(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_scaffold_markdown",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen"],
            "target": "guangya",
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "# CloudPan Bridge 驱动补全任务" in text
    assert "### `add_profile_first`" in text
    assert "`UnknownDrive` | P1" in text
    assert "缺口: `profile, guide, capture, capability`" in text


def test_provider_coverage_scaffold_markdown_endpoint_respects_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_scaffold_markdown",
        json={
            "drivers": ["UnknownDrive", "AliyundriveOpen", "Thunder"],
            "target": "guangya",
            "next_action": "add_profile_first",
            "missing_item": "profile",
            "only_gaps": True,
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "### `add_profile_first`" in text
    assert "`UnknownDrive`" in text
    assert "`Thunder`" not in text


def test_provider_capability_assess_endpoint_uses_analysis_summary(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "189Cloud",
            "analysis_summary": {
                "total": 3,
                "fast_upload_ready": 3,
                "md5_ready": 3,
                "gcid_ready": 0,
                "missing_fast_upload": 0,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["level"] == "fast_upload_partial"
    assert payload["assessedLevel"] == "fast_upload_supported"
    assert payload["fastUploadDecision"]["level"] == "native_fast_upload"
    assert payload["fastUploadDecision"]["bucket"] == "全部可秒传"
    assert payload["score"]["fastReady"] == 3
    assert payload["strategy"]["recommendedMode"] == "direct_metadata_first"
    assert payload["strategy"]["shouldAnalyzeFirst"] is False
    assert payload["strategy"]["preferPendingTree"] is False
    assert payload["sourceTargetRoute"]["decision_bucket"] == "capture_gap_before_fast"
    assert payload["sourceTargetRoute"]["bridge_recoverable_fast_hashes"] == ["md5"]
    assert payload["sourceTargetRoute"]["route_honesty"] == "capture_missing_before_fast_upload"
    assert payload["sourceTargetRoute"]["fallback_execution_mode"] == "stream_upload"


def test_provider_capability_assess_accepts_grouped_target_and_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "189Cloud",
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                }
            },
            "analysis_summary": {
                "total": 2,
                "fast_upload_ready": 2,
                "md5_ready": 2,
                "gcid_ready": 0,
                "missing_fast_upload": 0,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["targetProfile"]["key"] == "guangya"
    assert payload["assessedLevel"] == "fast_upload_supported"


def test_provider_capability_assess_prefers_enrichment_mode_when_directory_needs_more_hashes(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "Thunder",
            "analysis_summary": {
                "total": 2,
                "fast_upload_ready": 0,
                "md5_ready": 0,
                "gcid_ready": 0,
                "missing_fast_upload": 2,
                "pickcode_ready": 2,
                "sha1_ready": 2,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceProfile"]["supportsFingerprintEnrichment"] is True
    assert payload["fastUploadDecision"]["level"] == "fast_upload_after_enrichment"
    assert payload["strategy"]["recommendedMode"] == "enrich_then_direct"
    assert payload["sourceTargetRoute"]["decision_bucket"] == "capture_gap_before_fast"
    assert payload["sourceTargetRoute"]["bridge_recoverable_fast_hashes"] == ["md5", "gcid"]
    assert payload["sourceTargetRoute"]["preferred_execution_mode"] == "record_pending_only"
    assert any(item["key"] == "provider_refresh_supported" for item in payload["strategy"]["suggestedActions"])


def test_provider_capability_assess_without_analysis_requires_probe_first(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "Baidu",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["level"] == "fast_upload_partial"
    assert payload["assessedLevel"] == "fast_upload_partial"
    assert payload["strategy"]["recommendedMode"] == "analyze_first"
    assert payload["strategy"]["shouldAnalyzeFirst"] is True


def test_provider_capability_assess_can_use_dynamic_live_driver_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    info = OpenListDriverInfo(
        name="UnknownDrive",
        common=[OpenListDriverField(name="refresh_token", required=True)],
        additional=[OpenListDriverField(name="root_folder_id", default="root")],
        config={},
    )
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "UnknownDrive",
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                }
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceProfile"]["isDynamicInference"] is True
    assert payload["level"] == "download_upload_only"
    assert payload["isDynamicCapability"] is True
    assert payload["strategy"]["recommendedMode"] == "analyze_first"


def test_provider_capability_assess_download_only_prefers_pending_tree(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/capability_assess",
        json={
            "driver": "AliyundriveOpen",
            "analysis_summary": {
                "total": 4,
                "fast_upload_ready": 0,
                "md5_ready": 0,
                "gcid_ready": 0,
                "missing_fast_upload": 4,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["level"] == "download_upload_only"
    assert payload["assessedLevel"] == "download_upload_only"
    assert payload["strategy"]["recommendedMode"] == "pending_tree_first"
    assert payload["strategy"]["preferPendingTree"] is True


def test_provider_capability_openlist_target_defaults_to_download_upload_only(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "openlist"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/api/provider/capability?driver=Thunder&target=openlist")
    assert response.status_code == 200
    payload = response.json()
    assert payload["targetProfile"]["key"] == "openlist"
    assert payload["level"] == "download_upload_only"
    assert "OpenList" in payload["recommendedFlowEn"]


def test_provider_coverage_audit_accepts_grouped_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "drivers": ["UnknownDrive", "Thunder"],
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                },
                "ui": {
                    "coverage_filters": {
                        "onlyGaps": True,
                        "nextAction": "add_profile_first",
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["rows"]) >= 1
    assert all(item["nextAction"] == "add_profile_first" for item in payload["rows"])
    assert all(item["nextAction"] == "add_profile_first" for item in payload["backlog"])


def test_provider_coverage_audit_uses_live_openlist_drivers_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_names", lambda self: ["Thunder", "UnknownDrive"])
    info = OpenListDriverInfo(
        name="UnknownDrive",
        common=[OpenListDriverField(name="refresh_token", required=True)],
        additional=[OpenListDriverField(name="root_folder_id", default="root")],
        config={},
    )
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info if driver == "UnknownDrive" else OpenListDriverInfo(name="Thunder", common=[], additional=[], config={}))
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/provider/coverage_audit",
        json={
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                }
            }
        },
    )
    assert response.status_code == 200
    payload = response.json()
    rows = {item["driver"]: item for item in payload["rows"]}
    assert "Thunder" in rows
    assert "UnknownDrive" in rows
    assert rows["UnknownDrive"]["profileIsDynamic"] is True
    assert rows["UnknownDrive"]["captureIsDynamic"] is True
    assert rows["UnknownDrive"]["capabilityIsDynamic"] is True
    assert rows["UnknownDrive"]["nextAction"] == "add_guide"


def test_provider_coverage_scaffold_accepts_grouped_filters(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/provider/coverage_scaffold",
        json={
            "drivers": ["UnknownDrive", "Thunder"],
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                },
                "ui": {
                    "coverage_filters": {
                        "onlyGaps": True,
                        "nextAction": "add_profile_first",
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["totalBacklog"] >= 1
    assert all(item["nextAction"] == "add_profile_first" for item in payload["items"])


def test_provider_coverage_scaffold_markdown_uses_live_openlist_drivers_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_names", lambda self: ["UnknownDrive"])
    info = OpenListDriverInfo(
        name="UnknownDrive",
        common=[OpenListDriverField(name="refresh_token", required=True)],
        additional=[OpenListDriverField(name="root_folder_id", default="root")],
        config={},
    )
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/provider/coverage_scaffold_markdown",
        json={
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                }
            }
        },
    )
    assert response.status_code == 200
    text = response.text
    assert "# CloudPan Bridge 驱动补全任务" in text
    assert "`UnknownDrive`" in text
    assert "### `add_guide`" in text


def test_provider_capture_prefill_accepts_grouped_provider_and_driver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_session": {
    "provider_captures": {
      "quark": {
        "provider": "quark",
        "status": "captured",
        "message": "from config",
        "captured": {
          "cookie_header": "sid=1; token=2"
        }
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    info = OpenListDriverInfo(
        name="Quark",
        common=[OpenListDriverField(name="cookie", required=True)],
        additional=[],
        config={},
    )
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/provider/capture/prefill",
        json={
            "grouped_config": {},
            "provider": "quark",
            "driver": "Quark",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["values"]["cookie"] == "sid=1; token=2"
    assert payload["missing_required"] == []


def test_provider_capture_prefill_accepts_grouped_nested_provider_and_driver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_session": {
    "provider_captures": {
      "quark": {
        "provider": "quark",
        "status": "captured",
        "message": "from config",
        "captured": {
          "cookie_header": "sid=1; token=2"
        }
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    info = OpenListDriverInfo(
        name="Quark",
        common=[OpenListDriverField(name="cookie", required=True)],
        additional=[],
        config={},
    )
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/provider/capture/prefill",
        json={
            "grouped_config": {
                "ui": {
                    "provider_capture": {
                        "provider": "quark",
                        "driver": "Quark"
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["values"]["cookie"] == "sid=1; token=2"
    assert payload["missing_required"] == []


def test_pending_run_selected_stream_accepts_grouped_selected_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  },
  "targets": {
    "active_target": "guangya"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    seen: dict[str, object] = {}

    class ImmediateThread:
        def __init__(self, target: object, args: tuple[object, ...] = (), daemon: bool = False) -> None:
            seen["thread_target"] = getattr(target, "__name__", str(target))
            seen["thread_args"] = args

        def start(self) -> None:
            return None

    monkeypatch.setattr(webapp_module, "Thread", ImmediateThread)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/pending/run_selected_stream",
        json={
            "grouped_config": {
                "targets": {
                    "active_target": "guangya"
                },
                "sync": {
                    "selected_paths": [
                        "folder/a.jpg",
                        "/folder/b.jpg",
                    ]
                }
            }
        },
    )
    assert response.status_code == 200
    assert response.json()["selected"] == 2
    assert seen["thread_target"] == "run_pending_selected_stream_job"
    assert seen["thread_args"] == (["/folder/a.jpg", "/folder/b.jpg"],)


def test_openlist_storage_create_accepts_grouped_driver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    seen: dict[str, object] = {}
    info = OpenListDriverInfo(
        name="Quark",
        common=[OpenListDriverField(name="cookie", required=True)],
        additional=[],
        config={},
    )

    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info)

    def fake_build_storage_payload(info_obj: OpenListDriverInfo, values: dict[str, object]) -> dict[str, object]:
        seen["driver_name"] = info_obj.name
        seen["values"] = values
        return {"mount_path": "/quark", **values}

    def fake_create_storage(self: object, driver: str, body: dict[str, object]) -> dict[str, object]:
        seen["driver"] = driver
        seen["body"] = body
        return {"ok": True, "driver": driver, "body": body}

    monkeypatch.setattr(webapp_module, "build_storage_payload", fake_build_storage_payload)
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "create_storage", fake_create_storage)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/openlist/storage/create",
        json={
            "grouped_config": {},
            "driver": "Quark",
            "values": {
                "cookie": "sid=1; token=2"
            },
        },
    )
    assert response.status_code == 200
    assert seen["driver"] == "Quark"
    assert seen["driver_name"] == "Quark"
    assert seen["values"] == {"cookie": "sid=1; token=2"}


def test_openlist_storage_create_accepts_grouped_nested_driver_and_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge import webapp as webapp_module

    seen: dict[str, object] = {}
    info = OpenListDriverInfo(
        name="Quark",
        common=[OpenListDriverField(name="cookie", required=True)],
        additional=[],
        config={},
    )

    monkeypatch.setattr(webapp_module.OpenListAdminClient, "driver_info", lambda self, driver: info)

    def fake_build_storage_payload(info_obj: OpenListDriverInfo, values: dict[str, object]) -> dict[str, object]:
        seen["driver_name"] = info_obj.name
        seen["values"] = values
        return {"mount_path": "/quark", **values}

    def fake_create_storage(self: object, driver: str, body: dict[str, object]) -> dict[str, object]:
        seen["driver"] = driver
        seen["body"] = body
        return {"ok": True, "driver": driver, "body": body}

    monkeypatch.setattr(webapp_module, "build_storage_payload", fake_build_storage_payload)
    monkeypatch.setattr(webapp_module.OpenListAdminClient, "create_storage", fake_create_storage)
    client = TestClient(webapp_module.create_app(config_path))
    response = client.post(
        "/api/openlist/storage/create",
        json={
            "grouped_config": {
                "ui": {
                    "storage_create": {
                        "driver": "Quark",
                        "values": {
                            "cookie": "sid=1; token=2"
                        }
                    }
                }
            }
        },
    )
    assert response.status_code == 200
    assert seen["driver"] == "Quark"
    assert seen["driver_name"] == "Quark"
    assert seen["values"] == {"cookie": "sid=1; token=2"}


def test_source_analyze_endpoint_returns_summary(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from unittest.mock import patch
    from cloudpan_bridge.webapp import create_app

    fake_entries = [
        SourceEntry(path="/src/a.bin", md5="ABC", size=10, provider="openlist", hash_type="md5"),
        SourceEntry(path="/src/b.bin", md5="", size=20, provider="Thunder", hash_type="gcid", gcid="D" * 40),
    ]
    fake_plan = [SyncPlanItem(source=fake_entries[0], action="create", reason="新增文件")]
    app = create_app(config_path)
    client = TestClient(app)
    with patch("cloudpan_bridge.webapp.SyncRunner.analyze", return_value=(fake_entries, fake_plan, ["/src/c.bin"])):
        response = client.post("/api/source/analyze", json={"source_path": "/src", "limit": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["gcid_ready"] == 1
    assert payload["plan_total"] == 1
    assert payload["removed_total"] == 1
    assert payload["target_key"] == "guangya"
    assert payload["fastUploadDecision"]["level"] == "native_fast_upload"
    assert payload["sourceEnrichmentBatch"]["candidate_hash_counts"]["gcid"] == 1
    assert payload["sourceEnrichmentBatch"]["bridge_execution_state_counts"]["api_bridge_prepared_but_not_executed"] == 1
    assert payload["transferPlanPreview"]["reason_code_counts"]["fast_hash_ready"] == 2
    assert payload["transferPlanPreview"]["next_action_hint_counts"]["direct_fast_upload_ready"] == 2
    assert payload["transferPlanPreview"]["bridge_maturity_level_counts"]["capture_missing"] == 1
    assert payload["transferPlanPreview"]["bridge_missing_expected_hash_counts"]["md5"] == 1
    assert payload["transferPlanPreview"]["bridge_missing_expected_hash_counts"]["sha1"] == 1
    assert payload["transferPlanPreview"]["missing_target_fast_hash_counts"]["md5"] == 1
    assert payload["sourceTargetRoute"]["decision_bucket"] == "openlist_upload_path"
    assert payload["sourceTargetRoute"]["route_honesty"] == "openlist_only_for_now"
    assert payload["entries"][0]["transferPlan"]["mode"] == "fast_upload"
    assert payload["entries"][0]["transferPlan"]["reason_code"] == "fast_hash_ready"
    assert payload["entries"][0]["transferPlan"]["next_action_hint"] == "direct_fast_upload_ready"
    assert payload["entries"][0]["transferPlan"]["target_fast_hashes"] == ["md5", "gcid"]
    assert payload["truncated"] is True


def test_source_miaochuan_preview_endpoint_returns_payload(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from unittest.mock import patch
    from cloudpan_bridge.webapp import create_app

    fake_entries = [
        SourceEntry(path="/src/a.bin", md5="ABCDEF0123456789ABCDEF0123456789", size=10, provider="openlist", hash_type="md5"),
        SourceEntry(path="/src/b.bin", md5="", size=20, provider="Thunder", hash_type="gcid", gcid="F" * 40),
    ]
    app = create_app(config_path)
    client = TestClient(app)
    with patch("cloudpan_bridge.webapp.SyncRunner.analyze", return_value=(fake_entries, [], [])):
        response = client.post("/api/source/miaochuan_preview", json={"source_path": "/src"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_key"] == "guangya"
    assert payload["fastUploadDecision"]["level"] == "native_fast_upload"
    assert payload["sourceEnrichmentBatch"]["candidate_hash_counts"]["gcid"] == 1
    assert payload["sourceTargetRoute"]["decision_bucket"] == "openlist_upload_path"
    assert payload["sourceTargetRoute"]["preferred_execution_mode"] == "stream_upload"
    assert payload["payload"]["totalFilesCount"] == 2
    assert payload["payload"]["files"][0]["path"] == "/a.bin"
    assert "\"gcid\": \"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF\"" in payload["payload_text"]


def test_assess_directory_fast_upload_supports_camel_case_target_capability() -> None:
    payload = assess_directory_fast_upload(
        {
            "total": 5,
            "fast_upload_ready": 0,
            "missing_fast_upload": 5,
            "sha256_ready": 5,
            "pre_hash_ready": 2,
        },
        target_capability={
            "fastUploadHashes": ["md5", "sha256"],
            "fallbackModes": ["download_upload"],
        },
    )
    assert payload["supports_fast_upload"] is True
    assert payload["level"] == "fast_upload_after_enrichment"
    assert payload["bucket"] == "需补指纹后再判断"
    assert payload["enrichment_ready"] == 5


def test_miaochuan_diagnose_payload_summary() -> None:
    diagnosis = GuangyaMiaochuanImporter.diagnose_payload(
        {
            "files": [
                {
                    "path": "/a.bin",
                    "size": "10",
                    "etag": "ABCDEF0123456789ABCDEF0123456789",
                    "provider": "quark",
                    "hashType": "md5",
                },
                {
                    "path": "/b.bin",
                    "size": "20",
                    "gcid": "F" * 40,
                    "provider": "thunder",
                    "hashType": "gcid",
                },
            ]
        }
    )
    assert diagnosis["total"] == 2
    assert diagnosis["total_size"] == 30
    assert diagnosis["md5_count"] == 1
    assert diagnosis["gcid_count"] == 1
    assert diagnosis["provider_counts"] == {"quark": 1, "thunder": 1}
    assert diagnosis["sample"][1]["gcid"] == "F" * 40


def test_miaochuan_diagnose_endpoint_returns_summary(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    app = create_app(config_path)
    client = TestClient(app)
    response = client.post(
        "/api/miaochuan/diagnose",
        json={
            "miaochuan_payload": json.dumps(
                {
                    "files": [
                        {
                            "path": "/demo.zip",
                            "size": "123",
                            "etag": "ABCDEF0123456789ABCDEF0123456789",
                            "provider": "189cloud",
                            "hashType": "md5",
                        }
                    ]
                }
            )
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["md5_count"] == 1
    assert payload["provider_counts"] == {"189cloud": 1}


def test_miaochuan_import_rejects_non_guangya_target(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "target_key": "quark"
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    app = create_app(config_path)
    client = TestClient(app)
    response = client.post(
        "/api/miaochuan/import",
        json={
            "target_key": "quark",
            "miaochuan_payload": json.dumps(
                {
                    "files": [
                        {
                            "path": "/demo.zip",
                            "size": "123",
                            "etag": "ABCDEF0123456789ABCDEF0123456789",
                        }
                    ]
                }
            ),
        },
    )
    assert response.status_code == 400
    assert "当前秒传 JSON 直导仅支持 guangya" in response.json()["detail"]


def test_miaochuan_diagnose_accepts_grouped_payload(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "sync": {
    "source_path": "/src",
    "target_path": "/dst"
  }
}
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.post(
        "/api/miaochuan/diagnose",
        json={
            "grouped_config": {
                "sync": {}
            },
            "miaochuan_payload": json.dumps(
                {
                    "files": [
                        {
                            "path": "/demo.zip",
                            "size": "123",
                            "etag": "ABCDEF0123456789ABCDEF0123456789",
                            "provider": "189cloud",
                            "hashType": "md5",
                        }
                    ]
                }
            ),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["provider_counts"] == {"189cloud": 1}


def test_serialize_and_summarize_source_entries() -> None:
    entries = [
        SourceEntry(path="/a.bin", md5="abc", size=10, provider="openlist", hash_type="md5"),
        SourceEntry(path="/b.bin", md5="", size=20, provider="Thunder", hash_type="gcid", gcid="C" * 40, sha256="E" * 64, pre_hash="F" * 32),
        SourceEntry(path="/c.bin", md5="", size=30, provider="Quark", hash_type="sha1", sha1="D" * 40, slice_md5="1" * 32, pickcode="pc-3", content_hash="2" * 64),
    ]
    assert serialize_source_entry(entries[1])["gcid"] == "C" * 40
    assert serialize_source_entry(entries[2])["sha1"] == "D" * 40
    assert serialize_source_entry(entries[1])["sha256"] == "E" * 64
    assert serialize_source_entry(entries[1])["preHash"] == "F" * 32
    assert serialize_source_entry(entries[2])["sliceMd5"] == "1" * 32
    assert serialize_source_entry(entries[2])["contentHash"] == "2" * 64
    summary = summarize_source_entries(entries)
    assert summary["total"] == 3
    assert summary["gcid_ready"] == 1
    assert summary["sha1_ready"] == 1
    assert summary["sha256_ready"] == 1
    assert summary["pre_hash_ready"] == 1
    assert summary["slice_md5_ready"] == 1
    assert summary["content_hash_ready"] == 1
    assert summary["fast_upload_ready"] == 2
    assert summary["missing_md5"] == 2
    assert summary["missing_fast_upload"] == 1
    assert summary["provider_counts"]["Thunder"] == 1


def test_build_source_miaochuan_payload_uses_relative_paths() -> None:
    entries = [
        SourceEntry(path="/root/a.bin", md5="ABCDEF0123456789ABCDEF0123456789", size=10, provider="openlist", hash_type="md5"),
        SourceEntry(path="/root/sub/b.bin", md5="", size=20, provider="Thunder", hash_type="gcid", gcid="E" * 40, sha256="1" * 64, pre_hash="2" * 32),
        SourceEntry(path="/root/sub/c.bin", md5="", size=30, provider="Quark", hash_type="sha1", sha1="F" * 40, slice_md5="3" * 32, pickcode="pc-9", content_hash="4" * 64),
    ]
    payload = build_source_miaochuan_payload(entries, "/root")
    assert payload["totalFilesCount"] == 2
    assert payload["files"][0]["path"] == "/a.bin"
    assert payload["files"][1]["path"] == "/sub/b.bin"
    assert payload["files"][0]["etag"] == "abcdef0123456789abcdef0123456789"
    assert payload["files"][1]["gcid"] == "E" * 40
    assert payload["files"][1]["sha256"] == "1" * 64
    assert payload["files"][1]["preHash"] == "2" * 32
    assert payload["skipped"][0]["path"] == "/root/sub/c.bin"


def test_sync_state_roundtrip_preserves_extended_fingerprint_fields() -> None:
    state = SyncState(
        files={
            "/a.bin": SyncFileState(
                path="/a.bin",
                md5="ABC",
                size=10,
                sha1="D" * 40,
                sha256="E" * 64,
                pre_hash="F" * 32,
                slice_md5="1" * 32,
                content_hash="2" * 64,
                provider_specific={"contenthash": "raw-content"},
            )
        },
        pending_files={
            "/b.bin": PendingFileState(
                path="/b.bin",
                md5="",
                size=20,
                gcid="C" * 40,
                sha256="3" * 64,
                provider_specific={"driver_token": "abc"},
            )
        },
    )
    restored = SyncState.from_dict(state.to_dict())
    assert restored.files["/a.bin"].sha256 == "E" * 64
    assert restored.files["/a.bin"].pre_hash == "F" * 32
    assert restored.files["/a.bin"].slice_md5 == "1" * 32
    assert restored.files["/a.bin"].content_hash == "2" * 64
    assert restored.files["/a.bin"].provider_specific["contenthash"] == "raw-content"
    assert restored.pending_files["/b.bin"].sha256 == "3" * 64
    assert restored.pending_files["/b.bin"].provider_specific["driver_token"] == "abc"


def test_app_config_roundtrip_supports_console_admin_credentials() -> None:
    config = AppConfig.from_payload(
        {
            "app": {
                "bind_host": "0.0.0.0",
                "bind_port": 9000,
                "admin_username": "bridge-admin",
                "admin_password": "secret-pass",
            },
            "sync": {
                "source_path": "/src",
                "target_path": "/dst",
            },
            "state": {
                "state_file": ".state/sync-state.json",
                "export_file": ".work/source-export.jsonl",
                "temp_dir": ".work/download-cache",
                "log_file": ".state/sync.log",
            },
        }
    )
    assert config.app_admin_username == "bridge-admin"
    assert config.app_admin_password == "secret-pass"
    grouped = config.to_dict()
    assert grouped["app"]["admin_username"] == "bridge-admin"
    assert grouped["app"]["admin_password"] == "secret-pass"


def test_console_auth_disabled_keeps_api_open(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "app": {
                    "bind_host": "127.0.0.1",
                    "bind_port": 8765,
                    "admin_username": "",
                    "admin_password": "",
                },
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "state": {
                    "state_file": str(tmp_path / "sync-state.json"),
                    "export_file": str(tmp_path / "source-export.jsonl"),
                    "temp_dir": str(tmp_path / "download-cache"),
                    "log_file": str(tmp_path / "sync.log"),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    status = client.get("/api/auth/status")
    assert status.status_code == 200
    assert status.json()["enabled"] is False
    response = client.get("/api/config")
    assert response.status_code == 200


def test_console_auth_login_logout_flow(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "app": {
                    "bind_host": "127.0.0.1",
                    "bind_port": 8765,
                    "admin_username": "admin",
                    "admin_password": "pass123",
                },
                "sync": {
                    "source_path": "/src",
                    "target_path": "/dst",
                },
                "state": {
                    "state_file": str(tmp_path / "sync-state.json"),
                    "export_file": str(tmp_path / "source-export.jsonl"),
                    "temp_dir": str(tmp_path / "download-cache"),
                    "log_file": str(tmp_path / "sync.log"),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))

    unauthorized = client.get("/api/config")
    assert unauthorized.status_code == 401

    status = client.get("/api/auth/status")
    assert status.status_code == 200
    assert status.json()["enabled"] is True
    assert status.json()["authenticated"] is False

    wrong_login = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert wrong_login.status_code == 401

    login = client.post("/api/auth/login", json={"username": "admin", "password": "pass123"})
    assert login.status_code == 200
    assert login.json()["authenticated"] is True

    authorized = client.get("/api/config")
    assert authorized.status_code == 200

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200

    unauthorized_again = client.get("/api/config")
    assert unauthorized_again.status_code == 401


def test_index_page_contains_auth_lock_and_workflow_shell(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    from cloudpan_bridge.webapp import create_app

    client = TestClient(create_app(config_path))
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    assert 'id="auth-lock-panel"' in text
    assert 'id="workflow-roadmap"' in text
    assert 'id="open-auth-login-inline"' in text
    assert 'id="overview-route-summary"' in text
    assert 'data-tab="task"' in text
    assert 'data-tab="execute"' in text
