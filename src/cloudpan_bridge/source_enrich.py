from __future__ import annotations

import json
from typing import Any, Callable

from .config import AppConfig
from .models import SourceEntry
from .source_bridge_executor import execute_source_bridge
from .source_enrich_bridge import build_bridge_runtime
from .source_enrich_rules import MAINSTREAM_SOURCE_PROVIDERS, build_provider_rule

LogFn = Callable[[str], None]

CAPTURE_CACHE_PATH_KEYS = ("file_hashes_by_path", "fingerprints_by_path", "hash_cache_by_path", "entry_hashes_by_path")
CAPTURE_CACHE_ID_KEYS = ("file_hashes_by_id", "fingerprints_by_id", "hash_cache_by_id", "entry_hashes_by_id")
CAPTURE_CACHE_COLLECTION_KEYS = ("file_hashes", "fingerprints", "hash_cache", "entries", "items")
CAPTURE_CACHE_HASH_KEYS = ("md5", "gcid", "sha1", "sha256", "crc64", "pre_hash", "slice_md5", "content_hash", "pickcode")
CAPTURE_CACHE_NESTED_COLLECTION_KEYS = ("items", "entries", "files", "list", "records", "children", "value")


def _canonicalize_capture_key(value: Any) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _iter_capture_named_values(captured: dict[str, Any], aliases: tuple[str, ...]) -> list[Any]:
    alias_set = {_canonicalize_capture_key(item) for item in aliases if str(item or "").strip()}
    values: list[Any] = []
    for key, value in captured.items():
        if _canonicalize_capture_key(key) in alias_set:
            values.append(value)
    return values


def _iter_capture_collection_entries(value: Any) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                entries.append(item)
    elif isinstance(value, dict):
        nested_keys = (*CAPTURE_CACHE_NESTED_COLLECTION_KEYS, "data", "result", "payload")
        if value and not any(key in value for key in nested_keys) and all(isinstance(item, dict) for item in value.values()):
            for item in value.values():
                entries.append(item)
        for nested_key in CAPTURE_CACHE_NESTED_COLLECTION_KEYS:
            nested_entries = value.get(nested_key)
            if isinstance(nested_entries, list):
                for item in nested_entries:
                    if isinstance(item, dict):
                        entries.append(item)
        for nested_key in ("data", "result", "payload"):
            nested_value = value.get(nested_key)
            if isinstance(nested_value, (dict, list)):
                entries.extend(_iter_capture_collection_entries(nested_value))
    return entries


def _parse_capture_json(value: Any) -> Any:
    text = str(value or "").strip()
    if len(text) < 2:
        return value
    if not ((text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]"))):
        return value
    try:
        return json.loads(text)
    except Exception:
        return value


def _build_bridge_preparation_summary(bridge_runtime: dict[str, Any]) -> dict[str, Any]:
    preparation = dict(bridge_runtime.get("preparation") or {})
    return {
        "execution_state": str(preparation.get("execution_state") or ""),
        "transport_hint": str(preparation.get("transport_hint") or ""),
        "fingerprint_expectation": list(preparation.get("fingerprint_expectation") or []),
        "preferred_hashes": list(preparation.get("preferred_hashes") or []),
        "selected_group": list(preparation.get("selected_group") or []),
        "selected_field_names": list(preparation.get("selected_field_names") or []),
        "selected_field_count": int(preparation.get("selected_field_count") or 0),
        "available": bool(preparation.get("available")),
        "throttle_defaults": dict(preparation.get("throttle_defaults") or {}),
        "fallback_policy": dict(preparation.get("fallback_policy") or {}),
        "degrade_to": list(preparation.get("degrade_to") or []),
    }


def _extract_capture_cache_summary(captured: dict[str, Any]) -> dict[str, Any]:
    path_count = 0
    id_count = 0
    collection_count = 0
    hash_fields: set[str] = set()

    def collect_hash_fields(payload: Any, *, depth: int = 0) -> None:
        if depth > 4:
            return
        if isinstance(payload, str):
            parsed = _parse_capture_json(payload)
            if parsed is not payload:
                collect_hash_fields(parsed, depth=depth + 1)
            return
        if isinstance(payload, list):
            for item in payload:
                collect_hash_fields(item, depth=depth + 1)
            return
        if not isinstance(payload, dict):
            return
        algorithm = str(payload.get("algorithm") or payload.get("alg") or payload.get("name") or payload.get("type") or "").strip().lower()
        algorithm_value = payload.get("value")
        if algorithm == "sha1hash":
            algorithm = "sha1"
        elif algorithm == "sha256hash":
            algorithm = "sha256"
        elif algorithm == "crc64hash":
            algorithm = "crc64"
        elif algorithm == "md5hash":
            algorithm = "md5"
        elif algorithm in {"md5sum", "md5_sum"}:
            algorithm = "md5"
        elif algorithm in {"gcidhash", "gcid_hash"}:
            algorithm = "gcid"
        elif algorithm in {"pickcode", "pick_code"}:
            algorithm = "pickcode"
        elif algorithm == "contenthash":
            algorithm = "content_hash"
        if algorithm in CAPTURE_CACHE_HASH_KEYS and str(algorithm_value or "").strip():
            hash_fields.add(algorithm)
        for key, value in payload.items():
            normalized = str(key or "").strip().lower()
            if normalized == "sha1hash":
                normalized = "sha1"
            elif normalized == "sha256hash":
                normalized = "sha256"
            elif normalized == "crc64hash":
                normalized = "crc64"
            elif normalized == "md5hash":
                normalized = "md5"
            elif normalized in {"md5sum", "md5_sum"}:
                normalized = "md5"
            elif normalized in {"gcidhash", "gcid_hash"}:
                normalized = "gcid"
            elif normalized in {"pickcode", "pick_code"}:
                normalized = "pickcode"
            elif normalized == "contenthash":
                normalized = "content_hash"
            if normalized in CAPTURE_CACHE_HASH_KEYS and str(value or "").strip():
                hash_fields.add(normalized)
            collect_hash_fields(value, depth=depth + 1)

    for mapping in _iter_capture_named_values(captured, CAPTURE_CACHE_PATH_KEYS):
        if isinstance(mapping, dict):
            for item in mapping.values():
                if isinstance(item, (dict, list, str)):
                    path_count += 1
                    collect_hash_fields(item)

    for mapping in _iter_capture_named_values(captured, CAPTURE_CACHE_ID_KEYS):
        if isinstance(mapping, dict):
            for item in mapping.values():
                if isinstance(item, (dict, list, str)):
                    id_count += 1
                    collect_hash_fields(item)

    for collection in _iter_capture_named_values(captured, CAPTURE_CACHE_COLLECTION_KEYS):
        for item in _iter_capture_collection_entries(collection):
            collection_count += 1
            collect_hash_fields(item)

    lookup_modes: list[str] = []
    if path_count:
        lookup_modes.append("path")
    if id_count:
        lookup_modes.append("source_id")
    if collection_count:
        lookup_modes.append("collection_scan")
    return {
        "available": bool(path_count or id_count or collection_count),
        "entry_count": int(path_count + id_count + collection_count),
        "path_entry_count": int(path_count),
        "id_entry_count": int(id_count),
        "collection_entry_count": int(collection_count),
        "lookup_modes": lookup_modes,
        "hash_fields": sorted(hash_fields),
    }


def _build_bridge_maturity_summary(bridge_runtime: dict[str, Any], bridge_preparation_summary: dict[str, Any]) -> dict[str, Any]:
    status = str(bridge_runtime.get("status") or "").strip()
    mode = str(bridge_runtime.get("mode") or "").strip()
    execution_state = str(bridge_preparation_summary.get("execution_state") or "").strip()
    ready = bool(bridge_runtime.get("ready"))
    if status == "bridge_ready" and mode == "session_snapshot":
        return {
            "level": "session_snapshot_ready",
            "honesty": "capture_ready_normalization_only",
            "summary": "已具备会话快照归并能力，可提升当前目录的指纹覆盖率，但真实直连传输仍未落地。",
        }
    if status == "bridge_ready_but_api_pending" and ready:
        if bridge_preparation_summary.get("capture_cache_available"):
            cache_hashes = ", ".join(list(bridge_preparation_summary.get("capture_cache_hash_fields") or [])) or "-"
            return {
                "level": "api_capture_ready_with_cache",
                "honesty": "api_prepared_with_capture_cache",
                "summary": f"登录态已满足 API bridge 准备条件，且当前抓取快照里已有可消费的文件级哈希缓存（{cache_hashes}），建议先分析目录并优先消费缓存。",
            }
        return {
            "level": "api_capture_ready_pending_provider_enrich",
            "honesty": "api_prepared_not_executed",
            "summary": "登录态已满足 API bridge 准备条件，但当前版本还没有真正执行 provider API 补指纹。",
        }
    if status == "bridge_capture_missing":
        return {
            "level": "capture_missing",
            "honesty": "waiting_capture",
            "summary": "当前还缺少关键登录态字段，暂时无法进入主流 provider 的补指纹准备态。",
        }
    if execution_state == "bridge_not_registered" or status == "bridge_not_declared":
        return {
            "level": "not_registered",
            "honesty": "openlist_only",
            "summary": "当前 provider 还没有注册专用 bridge，只能使用 OpenList 已暴露的元数据。",
        }
    return {
        "level": "unknown",
        "honesty": "manual_review",
        "summary": "当前 bridge 运行态需要人工复核后再决定是否继续扩展。",
    }


def supports_enrichment(provider_key: str) -> bool:
    return str(provider_key or "").strip().lower() in MAINSTREAM_SOURCE_PROVIDERS


def build_source_enrichment_runtime(config: AppConfig, provider_key: str) -> dict[str, Any]:
    normalized = str(provider_key or "").strip().lower()
    rule = build_provider_rule(normalized)
    supported = normalized in MAINSTREAM_SOURCE_PROVIDERS
    capture_snapshot = dict((config.provider_captures or {}).get(normalized) or {})
    captured = dict(capture_snapshot.get("captured") or {})
    capture_fields = list(rule.get("capture_fields") or [])
    present_capture_fields = [field for field in capture_fields if str(captured.get(field) or "").strip()]
    capture_required = bool(rule.get("capture_required"))
    bridge_runtime = build_bridge_runtime(normalized, captured)
    capture_ready = bool(bridge_runtime.get("ready")) if capture_required else True
    bridge_preparation_summary = _build_bridge_preparation_summary(bridge_runtime)
    capture_cache_summary = _extract_capture_cache_summary(captured)
    bridge_preparation_summary["capture_cache_available"] = bool(capture_cache_summary.get("available"))
    bridge_preparation_summary["capture_cache_entry_count"] = int(capture_cache_summary.get("entry_count") or 0)
    bridge_preparation_summary["capture_cache_path_entry_count"] = int(capture_cache_summary.get("path_entry_count") or 0)
    bridge_preparation_summary["capture_cache_id_entry_count"] = int(capture_cache_summary.get("id_entry_count") or 0)
    bridge_preparation_summary["capture_cache_collection_entry_count"] = int(capture_cache_summary.get("collection_entry_count") or 0)
    bridge_preparation_summary["capture_cache_lookup_modes"] = list(capture_cache_summary.get("lookup_modes") or [])
    bridge_preparation_summary["capture_cache_hash_fields"] = list(capture_cache_summary.get("hash_fields") or [])
    bridge_maturity_summary = _build_bridge_maturity_summary(bridge_runtime, bridge_preparation_summary)
    return {
        "provider_key": normalized,
        "supported": supported,
        "capture_snapshot": capture_snapshot,
        "captured_fields": captured,
        "preferred_hashes": list(rule.get("preferred_hashes") or []),
        "capture_required": capture_required,
        "capture_ready": capture_ready,
        "capture_fields": capture_fields,
        "capture_fields_present": present_capture_fields,
        "capture_status": str(capture_snapshot.get("status") or ("captured" if present_capture_fields else "idle")),
        "hash_aliases": dict(rule.get("hash_aliases") or {}),
        "strategy_level": str(rule.get("strategy_level") or ("provider_normalization" if supported else "openlist_only")),
        "bridge_status": str(bridge_runtime.get("status") or (rule.get("bridge_status") or ("capture_guided_normalization" if supported else "not_supported"))),
        "bridge_runtime": bridge_runtime,
        "bridge_preparation_summary": bridge_preparation_summary,
        "capture_cache_summary": capture_cache_summary,
        "bridge_maturity_summary": bridge_maturity_summary,
        "runtime_mode": "openlist_first_provider_snapshot_enrichment" if supported else "openlist_only",
    }

def enrich_entry(entry: SourceEntry, config: AppConfig, log: LogFn | None = None) -> tuple[SourceEntry, dict[str, Any]]:
    runtime = build_source_enrichment_runtime(config, entry.provider)
    if not runtime.get("supported"):
        return entry, {**runtime, "changed": False, "added_hashes": [], "message": "当前 provider 还没有专用 enrich 实现。"}
    merged, bridge_report = execute_source_bridge(entry, runtime)
    changed = bool(bridge_report.get("changed"))
    added_hashes = list(bridge_report.get("added_hashes") or [])
    message = str(bridge_report.get("message") or ("已按 provider bridge 归并出补充指纹。" if changed else "当前 provider 没有额外可归并的指纹。"))
    if log:
        if changed:
            log(
                f"[直连补指纹] {entry.path}: 新增 {', '.join(added_hashes)} | "
                f"executor={bridge_report.get('bridge_executor', '-')} | "
                f"state={bridge_report.get('bridge_execution_state', '-')}"
            )
        elif bridge_report.get("candidate_hashes"):
            log(
                f"[直连补指纹候选] {entry.path}: "
                f"candidates={','.join(list(bridge_report.get('candidate_hashes') or [])) or '-'} | "
                f"pending={bridge_report.get('pending_reason', '-')}"
            )
    return merged, {
        **runtime,
        **bridge_report,
        "changed": changed,
        "added_hashes": added_hashes,
        "message": message,
    }


def enrich_batch(entries: list[SourceEntry], config: AppConfig, log: LogFn | None = None) -> tuple[list[SourceEntry], dict[str, Any]]:
    enriched: list[SourceEntry] = []
    changed_count = 0
    added_hash_counts: dict[str, int] = {}
    candidate_hash_counts: dict[str, int] = {}
    pending_reason_counts: dict[str, int] = {}
    bridge_execution_state_counts: dict[str, int] = {}
    provider_stage_counts: dict[str, int] = {}
    fast_ready_after_bridge = 0
    provider_key = str(entries[0].provider if entries else "").strip().lower()
    runtime = build_source_enrichment_runtime(config, provider_key)
    for entry in entries:
        merged, report = enrich_entry(entry, config, log=log)
        enriched.append(merged)
        if report.get("changed"):
            changed_count += 1
            for field in list(report.get("added_hashes") or []):
                added_hash_counts[field] = added_hash_counts.get(field, 0) + 1
        for field in list(report.get("candidate_hashes") or []):
            candidate_hash_counts[field] = candidate_hash_counts.get(field, 0) + 1
        pending_reason = str(report.get("pending_reason") or "").strip()
        if pending_reason:
            pending_reason_counts[pending_reason] = pending_reason_counts.get(pending_reason, 0) + 1
        execution_state = str(report.get("bridge_execution_state") or "").strip()
        if execution_state:
            bridge_execution_state_counts[execution_state] = bridge_execution_state_counts.get(execution_state, 0) + 1
        provider_stage = str(report.get("provider_stage") or "").strip()
        if provider_stage:
            provider_stage_counts[provider_stage] = provider_stage_counts.get(provider_stage, 0) + 1
        if report.get("fast_upload_ready_after_bridge"):
            fast_ready_after_bridge += 1
    return enriched, {
        **runtime,
        "total": len(entries),
        "changed_count": changed_count,
        "added_hash_counts": added_hash_counts,
        "candidate_hash_counts": candidate_hash_counts,
        "pending_reason_counts": pending_reason_counts,
        "bridge_execution_state_counts": bridge_execution_state_counts,
        "provider_stage_counts": provider_stage_counts,
        "fast_ready_after_bridge": fast_ready_after_bridge,
    }
