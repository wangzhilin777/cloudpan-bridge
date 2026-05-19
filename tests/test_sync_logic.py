import json
from pathlib import Path, PurePosixPath

from fastapi.testclient import TestClient
import pytest

import cloudpan_bridge.provider_registry as provider_registry_module
from cloudpan_bridge.config import AppConfig
from cloudpan_bridge.guangya_direct import GuangyaMiaochuanImporter
from cloudpan_bridge.guangya import GuangyaService
from cloudpan_bridge.models import PendingFileState, QueueItemState, SourceEntry, SyncFileState, SyncPlanItem, SyncState, normalize_posix_path
from cloudpan_bridge.openlist_admin import OpenListDriverField, OpenListDriverInfo, build_storage_payload
from cloudpan_bridge.openlist import OpenListClient
from cloudpan_bridge.provider_capture import (
    build_capture_alias_to_spec_key_map,
    build_capture_supported_driver_aliases,
    build_driver_capture_spec,
    build_driver_prefill_values,
    default_provider_specs,
    derive_capture_requirements_from_fields,
    resolve_capture_spec_for_driver,
)
from cloudpan_bridge.syncer import (
    SyncRunner,
    build_plan,
    build_source_miaochuan_payload,
    relative_target_path,
    render_tree,
    serialize_source_entry,
    summarize_source_entries,
)
from cloudpan_bridge.target_adapter import GuangyaTargetAdapter
from cloudpan_bridge.webapp import (
    build_pending_selected_execution_groups,
    compute_rate_limit_cooldown_ms,
    is_rate_limit_error_message,
)


def test_normalize_posix_path() -> None:
    assert normalize_posix_path("abc/def.txt") == "/abc/def.txt"
    assert normalize_posix_path("/abc/../abc/def.txt") == "/abc/def.txt"


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
    assert cfg.provider_captures["quark"]["captured"]["cookie_header"] == "k=v"
    nested = cfg.to_dict()
    assert nested["sync"]["source_path"] == "/src"
    assert nested["targets"]["guangya"]["device_id"] == "device"
    assert nested["source_session"]["provider_captures"]["quark"]["captured"]["cookie_header"] == "k=v"
    flat = cfg.to_flat_dict()
    assert flat["bind_port"] == 9876
    assert flat["openlist_password"] == "demo"


def test_config_supports_flat_legacy_structure_and_writes_nested(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
  "target_key": "guangya",
  "openlist_password": "legacy-pass",
  "guangya_refresh_token": "legacy-refresh"
}
""".strip(),
        encoding="utf-8",
    )
    cfg = AppConfig.load(path)
    serialized = cfg.to_dict()
    assert serialized["sync"]["source_path"] == "/src"
    assert serialized["targets"]["active_target"] == "guangya"
    assert serialized["targets"]["guangya"]["refresh_token"] == "legacy-refresh"
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
    item = build_plan([SourceEntry(path="/src/a.txt", md5="ABC", size=5 * 1024 * 1024, last_op_time="1")], SyncState())[0][0]
    assert runner._should_auto_download(item) is True


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
    assert payload["implemented_targets"] == ["guangya"]
    assert payload["target_implementation_status"]["guangya"]["known_profile"] is True
    assert payload["target_implementation_status"]["guangya"]["implemented"] is True
    assert payload["target_implementation_status"]["guangya"]["selectable"] is True


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

    sync_response = client.post("/api/sync/start", json={"mode": "dry_run"})
    assert sync_response.status_code == 400
    assert "目标端 quark 当前既没有内置档案，也没有实现可写入适配器" in sync_response.json()["detail"]


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
    assert payload["config_meta"]["storage"] == "nested_with_flat_compat"
    assert payload["config_meta"]["active_target"] == "guangya"


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
    assert {"guangya", "quark", "123pan", "189cloud", "baidu", "thunder", "aliyundriveopen", "onedrive", "pikpak", "139yun"} <= set(specs)
    assert "cookie_header" in specs["quark"].required_keys
    assert "bdstoken" in specs["baidu"].required_keys
    assert "authorization" in specs["thunder"].required_keys
    assert "refresh_token" in specs["aliyundriveopen"].required_keys
    assert "refresh_token" in specs["onedrive"].required_keys
    assert "refresh_token" in specs["pikpak"].required_keys
    assert "authorization" in specs["139yun"].required_keys


def test_capture_alias_registry_resolves_real_spec_keys() -> None:
    alias_map = build_capture_alias_to_spec_key_map()
    supported = build_capture_supported_driver_aliases()
    assert alias_map["aliyundriveopen"] == "aliyundriveopen"
    assert alias_map["alipan"] == "aliyundriveopen"
    assert alias_map["baidunetdisk"] == "baidu"
    assert alias_map["123open"] == "123pan"
    assert "quarkopen" in supported

    resolved = resolve_capture_spec_for_driver("AliyunDriveOpen")
    assert resolved["specKey"] == "aliyundriveopen"
    assert resolved["matchedAlias"] == "aliyundriveopen"
    assert resolved["loginUrl"].startswith("https://")

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
    config_path.write_text(
        """
{
  "source_path": "/src",
  "target_path": "/dst",
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
""".strip(),
        encoding="utf-8",
    )
    from cloudpan_bridge.webapp import create_app

    app = create_app(config_path)
    client = TestClient(app)
    status = client.get("/api/status")
    assert status.status_code == 200
    body = status.json()
    assert body["provider_captures"]["quark"]["captured"]["cookie_header"] == "sid=1; token=2"


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
    assert payload["guides"]["quark"]["defaults"]["web_proxy"] == "true"
    assert payload["source_profiles"]["189cloud"]["recommendedRateProfile"] == "safe"
    assert payload["source_profiles"]["189cloud"]["loginMode"] == "cookie + sessionKey style fields"
    assert payload["source_profiles"]["quark"]["docLinks"][0] == "https://doc.oplist.org/guide/drivers/quark.html"
    assert payload["source_profiles"]["thunder"]["hashFieldsSupported"] == ["gcid"]
    assert payload["target_profiles"]["guangya"]["fastUploadHashes"] == ["md5", "gcid"]
    assert payload["target_profiles"]["guangya"]["authMode"] == "authorization + access_token + refresh_token + device_id"
    assert payload["target_profiles"]["guangya"]["autoCreateDir"] is True
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
    assert providers["onedrive"]["required_keys"] == ["refresh_token"]
    assert providers["pikpak"]["login_url"] == "https://mypikpak.com/drive/all"
    assert providers["139yun"]["required_keys"] == ["authorization"]
    assert providers["aliyundriveopen"]["source_profile"]["key"] == "aliyundriveopen"
    assert providers["onedrive"]["source_profile"]["recommendedRateProfile"] == "balanced"
    assert providers["139yun"]["source_profile"]["docLinks"] == ["https://doc.oplist.org/guide/drivers/139.html"]
    assert providers["aliyundriveopen"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/aliyundrive_open"
    assert providers["139yun"]["guide"]["docUrl"] == "https://doc.oplist.org/guide/drivers/139.html"


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
    assert rows["unknowndrive"]["nextAction"] == "add_profile_first"
    assert rows["unknowndrive"]["priorityRank"] == 1


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
    assert payload["score"]["fastReady"] == 3
    assert payload["strategy"]["recommendedMode"] == "direct_metadata_first"
    assert payload["strategy"]["shouldAnalyzeFirst"] is False
    assert payload["strategy"]["preferPendingTree"] is False


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
    assert payload["payload"]["totalFilesCount"] == 2
    assert payload["payload"]["files"][0]["path"] == "/a.bin"
    assert "\"gcid\": \"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF\"" in payload["payload_text"]


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


def test_serialize_and_summarize_source_entries() -> None:
    entries = [
        SourceEntry(path="/a.bin", md5="abc", size=10, provider="openlist", hash_type="md5"),
        SourceEntry(path="/b.bin", md5="", size=20, provider="Thunder", hash_type="gcid", gcid="C" * 40),
        SourceEntry(path="/c.bin", md5="", size=30, provider="Quark", hash_type="sha1", sha1="D" * 40, pickcode="pc-3"),
    ]
    assert serialize_source_entry(entries[1])["gcid"] == "C" * 40
    assert serialize_source_entry(entries[2])["sha1"] == "D" * 40
    summary = summarize_source_entries(entries)
    assert summary["total"] == 3
    assert summary["gcid_ready"] == 1
    assert summary["sha1_ready"] == 1
    assert summary["fast_upload_ready"] == 2
    assert summary["missing_md5"] == 2
    assert summary["missing_fast_upload"] == 1
    assert summary["provider_counts"]["Thunder"] == 1


def test_build_source_miaochuan_payload_uses_relative_paths() -> None:
    entries = [
        SourceEntry(path="/root/a.bin", md5="ABCDEF0123456789ABCDEF0123456789", size=10, provider="openlist", hash_type="md5"),
        SourceEntry(path="/root/sub/b.bin", md5="", size=20, provider="Thunder", hash_type="gcid", gcid="E" * 40),
        SourceEntry(path="/root/sub/c.bin", md5="", size=30, provider="Quark", hash_type="sha1", sha1="F" * 40, pickcode="pc-9"),
    ]
    payload = build_source_miaochuan_payload(entries, "/root")
    assert payload["totalFilesCount"] == 2
    assert payload["files"][0]["path"] == "/a.bin"
    assert payload["files"][1]["path"] == "/sub/b.bin"
    assert payload["files"][0]["etag"] == "abcdef0123456789abcdef0123456789"
    assert payload["files"][1]["gcid"] == "E" * 40
    assert payload["skipped"][0]["path"] == "/root/sub/c.bin"
