from __future__ import annotations

import json
import re
from typing import Any, Callable

from .models import SourceEntry, normalize_fingerprint_value


BridgeExecuteFn = Callable[[SourceEntry, dict[str, Any]], tuple[SourceEntry, dict[str, Any]]]

HEX_LENGTHS: dict[str, int] = {
    "md5": 32,
    "sha1": 40,
    "sha256": 64,
}

NESTED_HASH_CONTAINER_KEYS = {
    "hash_info",
    "hashinfo",
    "hashes",
    "file_hashes",
    "filehashes",
    "digest",
    "digests",
    "content",
    "content_info",
    "contentinfo",
    "meta",
    "metadata",
}


def _collect_nested_payloads(value: Any, *, depth: int = 0) -> list[dict[str, Any]]:
    if depth > 3:
        return []
    payloads: list[dict[str, Any]] = []
    if isinstance(value, dict):
        normalized = {str(key): item for key, item in value.items()}
        payloads.append(normalized)
        for key, item in normalized.items():
            key_lower = str(key).strip().lower()
            if isinstance(item, dict) and (key_lower in NESTED_HASH_CONTAINER_KEYS or depth == 0):
                payloads.extend(_collect_nested_payloads(item, depth=depth + 1))
            elif isinstance(item, list) and key_lower in NESTED_HASH_CONTAINER_KEYS:
                for child in item:
                    payloads.extend(_collect_nested_payloads(child, depth=depth + 1))
            elif isinstance(item, str) and (key_lower in NESTED_HASH_CONTAINER_KEYS or depth == 0):
                payloads.extend(_collect_nested_payloads(_try_parse_json(item), depth=depth + 1))
    elif isinstance(value, list):
        for item in value:
            payloads.extend(_collect_nested_payloads(item, depth=depth + 1))
    elif isinstance(value, str):
        parsed = _try_parse_json(value)
        if parsed is not None and parsed is not value:
            payloads.extend(_collect_nested_payloads(parsed, depth=depth + 1))
    return payloads


def _try_parse_json(value: Any) -> Any:
    text = str(value or "").strip()
    if len(text) < 2:
        return value
    if not ((text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]"))):
        return value
    try:
        return json.loads(text)
    except Exception:
        return value


def _dedupe_payloads(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[tuple[str, str], ...]] = set()
    unique: list[dict[str, Any]] = []
    for payload in payloads:
        signature = tuple(sorted((str(key), str(value)) for key, value in payload.items()))
        if signature in seen:
            continue
        seen.add(signature)
        unique.append(payload)
    return unique


def _collect_raw_sources(entry: SourceEntry) -> list[dict[str, Any]]:
    payloads = [
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
    nested_payloads: list[dict[str, Any]] = []
    for payload in payloads:
        nested_payloads.extend(_collect_nested_payloads(payload))
    return _dedupe_payloads([*payloads, *nested_payloads])


def _pick_hash_value(entry: SourceEntry, logical_key: str, aliases_map: dict[str, list[str]]) -> str:
    aliases = list(aliases_map.get(logical_key) or [logical_key])
    for payload in _collect_raw_sources(entry):
        for alias in aliases:
            value = payload.get(alias)
            if not str(value or "").strip():
                continue
            uppercase = logical_key not in {"pickcode"}
            return normalize_fingerprint_value(value, uppercase=uppercase)
        derived = _derive_hash_value(payload, logical_key)
        if derived:
            return derived
    return ""


def _derive_hash_value(payload: dict[str, Any], logical_key: str) -> str:
    length = HEX_LENGTHS.get(logical_key)
    if not length:
        return ""
    candidate_fields = [
        payload.get("content_hash"),
        payload.get("contenthash"),
        payload.get("etag"),
        payload.get("hash"),
        payload.get("digest"),
    ]
    for raw in candidate_fields:
        derived = _extract_tagged_hash(raw, logical_key, length)
        if derived:
            return derived
    return ""


def _extract_tagged_hash(value: Any, logical_key: str, length: int) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    direct_pattern = rf"(?i)\b([a-f0-9]{{{length}}})\b"
    if logical_key != "md5":
        tagged_pattern = rf"(?i)\b{re.escape(logical_key)}\b[^a-f0-9]*([a-f0-9]{{{length}}})\b"
        tagged_match = re.search(tagged_pattern, text)
        if tagged_match:
            return normalize_fingerprint_value(tagged_match.group(1))
    else:
        md5_tagged_pattern = rf"(?i)\b(md5|content[-_ ]?md5|file[-_ ]?md5)\b[^a-f0-9]*([a-f0-9]{{{length}}})\b"
        tagged_match = re.search(md5_tagged_pattern, text)
        if tagged_match:
            return normalize_fingerprint_value(tagged_match.group(2))
    if logical_key != "md5":
        return ""
    direct_match = re.fullmatch(direct_pattern, text)
    if direct_match:
        return normalize_fingerprint_value(direct_match.group(1))
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


def _attach_bridge_metadata(entry: SourceEntry, report: dict[str, Any]) -> None:
    provider_specific = dict(entry.provider_specific or {})
    candidate_hashes = [str(item).strip() for item in list(report.get("candidate_hashes") or []) if str(item).strip()]
    if candidate_hashes:
        provider_specific["__bridge_candidate_hashes"] = ",".join(candidate_hashes)
    pending_reason = str(report.get("pending_reason") or "").strip()
    if pending_reason:
        provider_specific["__bridge_pending_reason"] = pending_reason
    execution_state = str(report.get("bridge_execution_state") or "").strip()
    if execution_state:
        provider_specific["__bridge_execution_state"] = execution_state
    provider_stage = str(report.get("provider_stage") or "").strip()
    if provider_stage:
        provider_specific["__bridge_provider_stage"] = provider_stage
    transport_hint = str(report.get("bridge_transport_hint") or "").strip()
    if transport_hint:
        provider_specific["__bridge_transport_hint"] = transport_hint
    maturity_level = str(report.get("bridge_maturity_level") or "").strip()
    if maturity_level:
        provider_specific["__bridge_maturity_level"] = maturity_level
    maturity_honesty = str(report.get("bridge_maturity_honesty") or "").strip()
    if maturity_honesty:
        provider_specific["__bridge_maturity_honesty"] = maturity_honesty
    expected_hashes = [str(item).strip() for item in list(report.get("bridge_expected_hashes") or []) if str(item).strip()]
    if expected_hashes:
        provider_specific["__bridge_expected_hashes"] = ",".join(expected_hashes)
    missing_expected_hashes = [str(item).strip() for item in list(report.get("bridge_missing_expected_hashes") or []) if str(item).strip()]
    if missing_expected_hashes:
        provider_specific["__bridge_missing_expected_hashes"] = ",".join(missing_expected_hashes)
    entry.provider_specific = provider_specific


def _fingerprint_presence(entry: SourceEntry) -> dict[str, bool]:
    return {
        "md5": bool(entry.md5),
        "gcid": bool(entry.gcid),
        "sha1": bool(entry.sha1),
        "sha256": bool(entry.sha256),
        "crc64": bool(entry.crc64),
        "pre_hash": bool(entry.pre_hash),
        "slice_md5": bool(entry.slice_md5),
        "pickcode": bool(entry.pickcode),
        "content_hash": bool(entry.content_hash),
    }


def _candidate_hashes(entry: SourceEntry) -> list[str]:
    presence = _fingerprint_presence(entry)
    ordered = ["md5", "gcid", "sha1", "slice_md5", "crc64", "content_hash", "pickcode", "pre_hash", "sha256"]
    return [key for key in ordered if presence.get(key)]


def _build_report(
    entry: SourceEntry,
    merged: SourceEntry,
    runtime: dict[str, Any],
    *,
    executor_name: str,
    execution_state: str,
    message: str,
    provider_stage: str,
    pending_reason: str = "",
) -> dict[str, Any]:
    added_hashes: list[str] = []
    for field in ("md5", "gcid", "sha1", "sha256", "crc64", "pre_hash", "slice_md5", "pickcode", "content_hash"):
        if not getattr(entry, field) and getattr(merged, field):
            added_hashes.append(field)
    bridge_runtime = dict(runtime.get("bridge_runtime") or {})
    preparation = dict(bridge_runtime.get("preparation") or {})
    merged_presence = _fingerprint_presence(merged)
    bridge_maturity = dict(runtime.get("bridge_maturity_summary") or {})
    expected_hashes = [str(item).strip().lower() for item in list(preparation.get("fingerprint_expectation") or []) if str(item).strip()]
    missing_expected_hashes = [key for key in expected_hashes if not merged_presence.get(key)]
    return {
        "changed": bool(added_hashes),
        "added_hashes": added_hashes,
        "bridge_execution_state": execution_state,
        "bridge_executor": executor_name,
        "provider_stage": provider_stage,
        "bridge_transport_hint": str(preparation.get("transport_hint") or "-"),
        "bridge_maturity_level": str(bridge_maturity.get("level") or ""),
        "bridge_maturity_honesty": str(bridge_maturity.get("honesty") or ""),
        "bridge_expected_hashes": expected_hashes,
        "bridge_missing_expected_hashes": missing_expected_hashes,
        "bridge_selected_group": list(preparation.get("selected_group") or []),
        "bridge_hook_registered": bool(bridge_runtime.get("hook_registered")),
        "candidate_hashes": _candidate_hashes(merged),
        "fast_upload_ready_after_bridge": bool(merged.md5 or merged.gcid),
        "fingerprint_presence": merged_presence,
        "pending_reason": pending_reason,
        "message": message,
    }


def _normalize_session_snapshot(entry: SourceEntry, runtime: dict[str, Any], *, executor_name: str) -> tuple[SourceEntry, dict[str, Any]]:
    aliases_map = dict(runtime.get("hash_aliases") or {})
    merged = _merge_entry_from_aliases(entry, aliases_map)
    candidate_hashes = _candidate_hashes(merged)
    pending_reason = ""
    if not (merged.md5 or merged.gcid) and candidate_hashes:
        pending_reason = "non_fast_hashes_only_after_session_snapshot"
    report = _build_report(
        entry,
        merged,
        runtime,
        executor_name=executor_name,
        execution_state="session_snapshot_normalized",
        provider_stage="session_snapshot",
        pending_reason=pending_reason,
        message="已通过 session snapshot bridge 归并当前可见元数据。",
    )
    _attach_bridge_metadata(merged, report)
    return merged, report


def _normalize_api_placeholder(entry: SourceEntry, runtime: dict[str, Any], *, executor_name: str) -> tuple[SourceEntry, dict[str, Any]]:
    aliases_map = dict(runtime.get("hash_aliases") or {})
    merged = _merge_entry_from_aliases(entry, aliases_map)
    candidate_hashes = _candidate_hashes(merged)
    pending_reason = ""
    if not (merged.md5 or merged.gcid):
        pending_reason = "provider_api_bridge_not_executed_yet"
    report = _build_report(
        entry,
        merged,
        runtime,
        executor_name=executor_name,
        execution_state="api_bridge_prepared_but_not_executed",
        provider_stage="api_placeholder",
        pending_reason=pending_reason,
        message="已命中 provider API bridge 准备态，当前版本先归并现有元数据，真实 API enrich 仍待后续接入。",
    )
    _attach_bridge_metadata(merged, report)
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
        report = {
            "changed": False,
            "added_hashes": [],
            "bridge_execution_state": "bridge_not_registered",
            "bridge_executor": "",
            "provider_stage": "none",
            "bridge_transport_hint": "-",
            "bridge_maturity_level": "",
            "bridge_maturity_honesty": "",
            "bridge_selected_group": [],
            "bridge_hook_registered": False,
            "candidate_hashes": _candidate_hashes(entry),
            "fast_upload_ready_after_bridge": bool(entry.md5 or entry.gcid),
            "fingerprint_presence": _fingerprint_presence(entry),
            "pending_reason": "bridge_not_registered",
            "message": "当前 provider 还没有 bridge executor。",
        }
        _attach_bridge_metadata(entry, report)
        return entry, report
    return executor(entry, runtime)
