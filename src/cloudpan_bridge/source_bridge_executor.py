from __future__ import annotations

import json
import re
from typing import Any, Callable

from .models import SourceEntry, normalize_fingerprint_value


BridgeExecuteFn = Callable[[SourceEntry, dict[str, Any]], tuple[SourceEntry, dict[str, Any]]]

HEX_LENGTHS: dict[str, int] = {
    "md5": 32,
    "gcid": 40,
    "sha1": 40,
    "sha256": 64,
    "crc64": 16,
    "pre_hash": 32,
    "slice_md5": 32,
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

HASH_LABEL_ALIASES = {
    "file_md5": "md5",
    "content_md5": "md5",
    "md5_hash": "md5",
    "md5hash": "md5",
    "file_gcid": "gcid",
    "content_hash": "content_hash",
    "contenthash": "content_hash",
    "content_hash_name": "content_hash_name",
    "contenthashname": "content_hash_name",
    "prehash": "pre_hash",
    "slice-md5": "slice_md5",
    "slicehash": "slice_md5",
    "sha-1": "sha1",
    "sha1_hash": "sha1",
    "sha1hash": "sha1",
    "sha-256": "sha256",
    "sha256_hash": "sha256",
    "sha256hash": "sha256",
    "crc64_hash": "crc64",
    "crc64hash": "crc64",
}

HASH_ITEM_LABEL_KEYS = ("algorithm", "alg", "name", "type", "hash_type", "kind", "label", "key")
HASH_ITEM_VALUE_KEYS = ("value", "hash", "digest", "checksum", "content", "content_hash", "etag", "md5", "sha1", "sha256", "gcid", "crc64", "pre_hash", "slice_md5")


def _iter_collection_entries(value: Any) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                entries.append(item)
    elif isinstance(value, dict):
        for nested_key in ("items", "entries", "files", "list", "records", "children", "value"):
            nested_entries = value.get(nested_key)
            if isinstance(nested_entries, list):
                for item in nested_entries:
                    if isinstance(item, dict):
                        entries.append({str(inner_key): inner_value for inner_key, inner_value in item.items()})
        for nested_key in ("data", "result", "payload"):
            nested_value = value.get(nested_key)
            if isinstance(nested_value, (dict, list)):
                entries.extend(_iter_collection_entries(nested_value))
    return entries


def _normalize_hash_label(value: Any) -> str:
    text = str(value or "").strip().lower().replace(" ", "_")
    if not text:
        return ""
    normalized = HASH_LABEL_ALIASES.get(text, text)
    if normalized in HEX_LENGTHS or normalized in {"content_hash", "pickcode", "etag"}:
        return normalized
    return ""


def _build_hash_payload_from_item(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    normalized = {str(key): item for key, item in value.items()}
    for label_key in HASH_ITEM_LABEL_KEYS:
        label = _normalize_hash_label(normalized.get(label_key))
        if not label:
            continue
        for value_key in HASH_ITEM_VALUE_KEYS:
            raw_value = normalized.get(value_key)
            if str(raw_value or "").strip():
                return {label: raw_value}
    return None


def _normalize_entry_path(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return ""
    if not text.startswith("/"):
        text = f"/{text}"
    while "//" in text:
        text = text.replace("//", "/")
    return text.rstrip("/") or "/"


def _capture_payload_matches_entry(payload: dict[str, Any], entry: SourceEntry) -> bool:
    normalized_entry_path = _normalize_entry_path(entry.path)
    payload_paths = [
        _normalize_entry_path(payload.get("path")),
        _normalize_entry_path(payload.get("file_path")),
        _normalize_entry_path(payload.get("source_path")),
        _normalize_entry_path(payload.get("full_path")),
    ]
    if normalized_entry_path and normalized_entry_path in {path for path in payload_paths if path}:
        return True
    source_id = str(entry.source_id or "").strip()
    payload_ids = [
        str(payload.get(key) or "").strip()
        for key in ("source_id", "file_id", "id", "fid", "res_id", "fs_id", "item_id", "driveItemId", "drive_item_id")
        if str(payload.get(key) or "").strip()
    ]
    if source_id and source_id in payload_ids:
        return True
    return False


def _collect_capture_entry_payloads(entry: SourceEntry, runtime: dict[str, Any]) -> list[dict[str, Any]]:
    captured = dict(runtime.get("captured_fields") or {})
    if not captured:
        return []
    payloads: list[dict[str, Any]] = []
    normalized_entry_path = _normalize_entry_path(entry.path)
    if normalized_entry_path:
        for key in ("file_hashes_by_path", "fingerprints_by_path", "hash_cache_by_path", "entry_hashes_by_path"):
            mapping = captured.get(key)
            if isinstance(mapping, dict):
                direct = mapping.get(normalized_entry_path)
                if isinstance(direct, dict):
                    payloads.append({str(inner_key): inner_value for inner_key, inner_value in direct.items()})
                alt = mapping.get(normalized_entry_path.lstrip("/"))
                if isinstance(alt, dict):
                    payloads.append({str(inner_key): inner_value for inner_key, inner_value in alt.items()})
    source_id = str(entry.source_id or "").strip()
    if source_id:
        for key in ("file_hashes_by_id", "fingerprints_by_id", "hash_cache_by_id", "entry_hashes_by_id"):
            mapping = captured.get(key)
            if isinstance(mapping, dict):
                direct = mapping.get(source_id)
                if isinstance(direct, dict):
                    payloads.append({str(inner_key): inner_value for inner_key, inner_value in direct.items()})
    for key in ("file_hashes", "fingerprints", "hash_cache", "entries", "items"):
        collection = captured.get(key)
        for item in _iter_collection_entries(collection):
            normalized = {str(inner_key): inner_value for inner_key, inner_value in item.items()}
            if _capture_payload_matches_entry(normalized, entry):
                payloads.append(normalized)
    return _dedupe_payloads(payloads)


def _collect_nested_payloads(value: Any, *, depth: int = 0) -> list[dict[str, Any]]:
    if depth > 3:
        return []
    payloads: list[dict[str, Any]] = []
    if isinstance(value, dict):
        normalized = {str(key): item for key, item in value.items()}
        payloads.append(normalized)
        derived_payload = _build_hash_payload_from_item(normalized)
        if derived_payload:
            payloads.append(derived_payload)
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
            derived_payload = _build_hash_payload_from_item(item)
            if derived_payload:
                payloads.append(derived_payload)
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


def _collect_raw_sources(entry: SourceEntry, extra_payloads: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
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
    payloads.extend(list(extra_payloads or []))
    nested_payloads: list[dict[str, Any]] = []
    for payload in payloads:
        nested_payloads.extend(_collect_nested_payloads(payload))
    return _dedupe_payloads([*payloads, *nested_payloads])


def _pick_hash_value(entry: SourceEntry, logical_key: str, aliases_map: dict[str, list[str]], extra_payloads: list[dict[str, Any]] | None = None) -> str:
    aliases = list(aliases_map.get(logical_key) or [logical_key])
    for payload in _collect_raw_sources(entry, extra_payloads):
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
    derived_from_named_content = _derive_hash_value_from_named_content(payload, logical_key)
    if derived_from_named_content:
        return derived_from_named_content
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


def _derive_hash_value_from_named_content(payload: dict[str, Any], logical_key: str) -> str:
    length = HEX_LENGTHS.get(logical_key)
    if not length:
        return ""
    content_hash_name = str(
        payload.get("content_hash_name")
        or payload.get("contenthashname")
        or payload.get("contentHashName")
        or ""
    ).strip().lower().replace("-", "_")
    content_hash_value = str(
        payload.get("content_hash")
        or payload.get("contenthash")
        or payload.get("contentHash")
        or ""
    ).strip()
    if not content_hash_name or not content_hash_value:
        return ""
    if content_hash_name != logical_key:
        return ""
    direct_pattern = rf"(?i)^[a-f0-9]{{{length}}}$"
    if not re.fullmatch(direct_pattern, content_hash_value):
        return ""
    uppercase = logical_key not in {"pickcode", "content_hash"}
    return normalize_fingerprint_value(content_hash_value, uppercase=uppercase)


def _merge_entry_from_aliases(entry: SourceEntry, aliases_map: dict[str, list[str]], extra_payloads: list[dict[str, Any]] | None = None) -> SourceEntry:
    return SourceEntry(
        path=entry.path,
        md5=entry.md5 or _pick_hash_value(entry, "md5", aliases_map, extra_payloads),
        size=entry.size,
        last_op_time=entry.last_op_time,
        source_id=entry.source_id,
        provider=entry.provider,
        hash_type=entry.hash_type,
        gcid=entry.gcid or _pick_hash_value(entry, "gcid", aliases_map, extra_payloads),
        etag=entry.etag or _pick_hash_value(entry, "md5", aliases_map, extra_payloads),
        sha1=entry.sha1 or _pick_hash_value(entry, "sha1", aliases_map, extra_payloads),
        sha256=entry.sha256 or _pick_hash_value(entry, "sha256", aliases_map, extra_payloads),
        crc64=entry.crc64 or _pick_hash_value(entry, "crc64", aliases_map, extra_payloads),
        pre_hash=entry.pre_hash or _pick_hash_value(entry, "pre_hash", aliases_map, extra_payloads),
        slice_md5=entry.slice_md5 or _pick_hash_value(entry, "slice_md5", aliases_map, extra_payloads),
        pickcode=entry.pickcode or _pick_hash_value(entry, "pickcode", aliases_map, extra_payloads),
        content_hash=entry.content_hash or _pick_hash_value(entry, "content_hash", aliases_map, extra_payloads),
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
    maturity_level = str(bridge_maturity.get("level") or "")
    maturity_honesty = str(bridge_maturity.get("honesty") or "")
    if execution_state == "api_capture_cache_normalized":
        maturity_level = "api_capture_cache_ready"
        maturity_honesty = "capture_cache_snapshot_only"
    expected_hashes = [str(item).strip().lower() for item in list(preparation.get("fingerprint_expectation") or []) if str(item).strip()]
    missing_expected_hashes = [key for key in expected_hashes if not merged_presence.get(key)]
    return {
        "changed": bool(added_hashes),
        "added_hashes": added_hashes,
        "bridge_execution_state": execution_state,
        "bridge_executor": executor_name,
        "provider_stage": provider_stage,
        "bridge_transport_hint": str(preparation.get("transport_hint") or "-"),
        "bridge_maturity_level": maturity_level,
        "bridge_maturity_honesty": maturity_honesty,
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
    capture_payloads = _collect_capture_entry_payloads(entry, runtime)
    merged = _merge_entry_from_aliases(entry, aliases_map, capture_payloads)
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
    capture_payloads = _collect_capture_entry_payloads(entry, runtime)
    merged = _merge_entry_from_aliases(entry, aliases_map, capture_payloads)
    candidate_hashes = _candidate_hashes(merged)
    pending_reason = ""
    execution_state = "api_bridge_prepared_but_not_executed"
    provider_stage = "api_placeholder"
    message = "已命中 provider API bridge 准备态，当前版本先归并现有元数据，真实 API enrich 仍待后续接入。"
    if capture_payloads:
        execution_state = "api_capture_cache_normalized"
        provider_stage = "api_capture_cache"
        message = "已从 provider capture 快照缓存中归并文件级哈希，真实在线 provider API enrich 仍待后续接入。"
    if not (merged.md5 or merged.gcid):
        pending_reason = "provider_api_bridge_not_executed_yet"
    report = _build_report(
        entry,
        merged,
        runtime,
        executor_name=executor_name,
        execution_state=execution_state,
        provider_stage=provider_stage,
        pending_reason=pending_reason,
        message=message,
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
