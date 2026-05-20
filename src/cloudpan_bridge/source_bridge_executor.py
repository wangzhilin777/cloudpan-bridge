from __future__ import annotations

from typing import Any, Callable

from .models import SourceEntry, normalize_fingerprint_value


BridgeExecuteFn = Callable[[SourceEntry, dict[str, Any]], tuple[SourceEntry, dict[str, Any]]]


def _collect_raw_sources(entry: SourceEntry) -> list[dict[str, Any]]:
    return [
        dict(entry.raw_hash_info or {}),
        dict(entry.provider_specific or {}),
        dict(entry.extra_hashes or {}),
        {
            "md5": entry.md5,
            "etag": entry.etag,
            "gcid": entry.gcid,
            "sha1": entry.sha1,
            "sha256": entry.sha256,
            "crc64": entry.crc64,
            "pre_hash": entry.pre_hash,
            "slice_md5": entry.slice_md5,
            "pickcode": entry.pickcode,
            "content_hash": entry.content_hash,
        },
    ]


def _pick_hash_value(entry: SourceEntry, logical_key: str, aliases_map: dict[str, list[str]]) -> str:
    aliases = list(aliases_map.get(logical_key) or [logical_key])
    for payload in _collect_raw_sources(entry):
        for alias in aliases:
            value = payload.get(alias)
            if not str(value or "").strip():
                continue
            uppercase = logical_key not in {"pickcode"}
            return normalize_fingerprint_value(value, uppercase=uppercase)
    return ""


def _merge_entry_from_aliases(entry: SourceEntry, aliases_map: dict[str, list[str]]) -> SourceEntry:
    return SourceEntry(
        path=entry.path,
        md5=entry.md5 or _pick_hash_value(entry, "md5", aliases_map),
        size=entry.size,
        last_op_time=entry.last_op_time,
        source_id=entry.source_id,
        provider=entry.provider,
        hash_type=entry.hash_type,
        gcid=entry.gcid or _pick_hash_value(entry, "gcid", aliases_map),
        etag=entry.etag or _pick_hash_value(entry, "md5", aliases_map),
        sha1=entry.sha1 or _pick_hash_value(entry, "sha1", aliases_map),
        sha256=entry.sha256 or _pick_hash_value(entry, "sha256", aliases_map),
        crc64=entry.crc64 or _pick_hash_value(entry, "crc64", aliases_map),
        pre_hash=entry.pre_hash or _pick_hash_value(entry, "pre_hash", aliases_map),
        slice_md5=entry.slice_md5 or _pick_hash_value(entry, "slice_md5", aliases_map),
        pickcode=entry.pickcode or _pick_hash_value(entry, "pickcode", aliases_map),
        content_hash=entry.content_hash or _pick_hash_value(entry, "content_hash", aliases_map),
        extra_hashes=dict(entry.extra_hashes or {}),
        provider_specific=dict(entry.provider_specific or {}),
        raw_hash_info=dict(entry.raw_hash_info or {}),
    )


def _build_report(entry: SourceEntry, merged: SourceEntry, runtime: dict[str, Any], *, executor_name: str, execution_state: str, message: str) -> dict[str, Any]:
    added_hashes: list[str] = []
    for field in ("md5", "gcid", "sha1", "sha256", "crc64", "pre_hash", "slice_md5", "pickcode", "content_hash"):
        if not getattr(entry, field) and getattr(merged, field):
            added_hashes.append(field)
    bridge_runtime = dict(runtime.get("bridge_runtime") or {})
    preparation = dict(bridge_runtime.get("preparation") or {})
    return {
        "changed": bool(added_hashes),
        "added_hashes": added_hashes,
        "bridge_execution_state": execution_state,
        "bridge_executor": executor_name,
        "bridge_transport_hint": str(preparation.get("transport_hint") or "-"),
        "bridge_selected_group": list(preparation.get("selected_group") or []),
        "bridge_hook_registered": bool(bridge_runtime.get("hook_registered")),
        "message": message,
    }


def _normalize_session_snapshot(entry: SourceEntry, runtime: dict[str, Any], *, executor_name: str) -> tuple[SourceEntry, dict[str, Any]]:
    aliases_map = dict(runtime.get("hash_aliases") or {})
    merged = _merge_entry_from_aliases(entry, aliases_map)
    report = _build_report(
        entry,
        merged,
        runtime,
        executor_name=executor_name,
        execution_state="session_snapshot_normalized",
        message="已通过 session snapshot bridge 归并当前可见元数据。",
    )
    return merged, report


def _normalize_api_placeholder(entry: SourceEntry, runtime: dict[str, Any], *, executor_name: str) -> tuple[SourceEntry, dict[str, Any]]:
    aliases_map = dict(runtime.get("hash_aliases") or {})
    merged = _merge_entry_from_aliases(entry, aliases_map)
    report = _build_report(
        entry,
        merged,
        runtime,
        executor_name=executor_name,
        execution_state="api_bridge_prepared_but_not_executed",
        message="已命中 provider API bridge 准备态，当前版本先归并现有元数据，真实 API enrich 仍待后续接入。",
    )
    return merged, report


def execute_189cloud_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_session_snapshot(entry, runtime, executor_name="prepare_189cloud_session_bridge")


def execute_quark_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_session_snapshot(entry, runtime, executor_name="prepare_quark_session_bridge")


def execute_123pan_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_session_snapshot(entry, runtime, executor_name="prepare_123pan_session_bridge")


def execute_baidu_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_session_snapshot(entry, runtime, executor_name="prepare_baidu_session_bridge")


def execute_thunder_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_api_placeholder(entry, runtime, executor_name="prepare_thunder_api_bridge")


def execute_aliyundriveopen_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_api_placeholder(entry, runtime, executor_name="prepare_aliyundriveopen_api_bridge")


def execute_onedrive_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    return _normalize_api_placeholder(entry, runtime, executor_name="prepare_onedrive_api_bridge")


SOURCE_BRIDGE_EXECUTORS: dict[str, BridgeExecuteFn] = {
    "189cloud": execute_189cloud_bridge,
    "quark": execute_quark_bridge,
    "123pan": execute_123pan_bridge,
    "baidu": execute_baidu_bridge,
    "thunder": execute_thunder_bridge,
    "aliyundriveopen": execute_aliyundriveopen_bridge,
    "onedrive": execute_onedrive_bridge,
}


def execute_source_bridge(entry: SourceEntry, runtime: dict[str, Any]) -> tuple[SourceEntry, dict[str, Any]]:
    provider_key = str(runtime.get("provider_key") or entry.provider or "").strip().lower()
    executor = SOURCE_BRIDGE_EXECUTORS.get(provider_key)
    if not executor:
        return entry, {
            "changed": False,
            "added_hashes": [],
            "bridge_execution_state": "bridge_not_registered",
            "bridge_executor": "",
            "bridge_transport_hint": "-",
            "bridge_selected_group": [],
            "bridge_hook_registered": False,
            "message": "当前 provider 还没有 bridge executor。",
        }
    return executor(entry, runtime)
