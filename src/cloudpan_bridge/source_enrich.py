from __future__ import annotations

from typing import Any, Callable

from .config import AppConfig
from .models import SourceEntry
from .source_bridge_executor import execute_source_bridge
from .source_enrich_bridge import build_bridge_runtime
from .source_enrich_rules import MAINSTREAM_SOURCE_PROVIDERS, build_provider_rule

LogFn = Callable[[str], None]


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
    return {
        "provider_key": normalized,
        "supported": supported,
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
