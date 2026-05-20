from __future__ import annotations

from typing import Any

from .models import SourceEntry


def _entry_hash_map(entry: SourceEntry) -> dict[str, str]:
    return {
        "md5": str(entry.md5 or "").strip(),
        "gcid": str(entry.gcid or "").strip(),
        "sha1": str(entry.sha1 or "").strip(),
        "sha256": str(entry.sha256 or "").strip(),
        "crc64": str(entry.crc64 or "").strip(),
    }


def _entry_bridge_metadata(entry: SourceEntry) -> dict[str, Any]:
    provider_specific = dict(entry.provider_specific or {})
    candidate_hashes = [
        str(item).strip().lower()
        for item in str(provider_specific.get("__bridge_candidate_hashes") or "").split(",")
        if str(item).strip()
    ]
    return {
        "candidate_hashes": candidate_hashes,
        "pending_reason": str(provider_specific.get("__bridge_pending_reason") or "").strip(),
        "execution_state": str(provider_specific.get("__bridge_execution_state") or "").strip(),
        "provider_stage": str(provider_specific.get("__bridge_provider_stage") or "").strip(),
        "transport_hint": str(provider_specific.get("__bridge_transport_hint") or "").strip(),
        "maturity_level": str(provider_specific.get("__bridge_maturity_level") or "").strip(),
        "maturity_honesty": str(provider_specific.get("__bridge_maturity_honesty") or "").strip(),
        "expected_hashes": [
            str(item).strip().lower()
            for item in str(provider_specific.get("__bridge_expected_hashes") or "").split(",")
            if str(item).strip()
        ],
        "missing_expected_hashes": [
            str(item).strip().lower()
            for item in str(provider_specific.get("__bridge_missing_expected_hashes") or "").split(",")
            if str(item).strip()
        ],
    }


def compute_fast_upload_hits(entry: SourceEntry, target_capability: dict[str, Any] | None = None) -> list[str]:
    capability = dict(target_capability or {})
    supported = [str(item or "").strip().lower() for item in list(capability.get("fast_upload_hashes") or capability.get("fastUploadHashes") or []) if str(item or "").strip()]
    values = _entry_hash_map(entry)
    return [key for key in supported if values.get(key)]


def _supported_fast_hashes(target_capability: dict[str, Any] | None = None) -> list[str]:
    capability = dict(target_capability or {})
    return [
        str(item or "").strip().lower()
        for item in list(capability.get("fast_upload_hashes") or capability.get("fastUploadHashes") or [])
        if str(item or "").strip()
    ]


def plan_transfer_mode(
    entry: SourceEntry,
    target_capability: dict[str, Any] | None = None,
    *,
    auto_download_threshold_mb: int = 0,
    allow_full_fallback: bool = False,
) -> dict[str, Any]:
    capability = dict(target_capability or {})
    fallback_modes = [str(item or "").strip().lower() for item in list(capability.get("fallback_modes") or capability.get("fallbackModes") or []) if str(item or "").strip()]
    supported_fast_hashes = _supported_fast_hashes(capability)
    fast_hash_hits = compute_fast_upload_hits(entry, capability)
    bridge_meta = _entry_bridge_metadata(entry)
    bridge_candidates = list(bridge_meta.get("candidate_hashes") or [])
    bridge_expected_hashes = list(bridge_meta.get("expected_hashes") or [])
    bridge_missing_expected_hashes = list(bridge_meta.get("missing_expected_hashes") or [])
    entry_hash_values = _entry_hash_map(entry)
    missing_target_fast_hashes = [key for key in supported_fast_hashes if not entry_hash_values.get(key)]
    bridge_recoverable_fast_hashes = [key for key in supported_fast_hashes if key in bridge_expected_hashes]
    bridge_missing_recoverable_fast_hashes = [key for key in bridge_recoverable_fast_hashes if key in bridge_missing_expected_hashes]
    threshold_bytes = max(0, int(auto_download_threshold_mb or 0)) * 1024 * 1024
    small_file_auto = bool(threshold_bytes > 0 and int(entry.size) <= threshold_bytes)
    mode = "record_pending_only"
    reason_code = "no_auto_fallback"
    next_action_hint = "manual_review"
    reason = "当前目标端不支持可直接使用的快传指纹，且本轮未允许自动降级。"
    if fast_hash_hits:
        mode = "fast_upload"
        reason_code = "fast_hash_ready"
        next_action_hint = "direct_fast_upload_ready"
        reason = f"目标端支持当前文件的快传指纹: {', '.join(fast_hash_hits)}"
    elif "download_upload" in fallback_modes and small_file_auto:
        mode = "download_upload"
        reason_code = "small_file_auto_fallback"
        next_action_hint = "fallback_download_upload_ready"
        reason = "文件命中小文件自动补传阈值，建议直接下载后上传。"
    elif "download_upload" in fallback_modes and allow_full_fallback:
        mode = "download_upload"
        reason_code = "full_download_fallback_allowed"
        next_action_hint = "fallback_download_upload_ready"
        reason = "当前执行模式允许完整降级到下载后上传。"
    elif "stream_upload" in fallback_modes and allow_full_fallback:
        mode = "stream_upload"
        reason_code = "full_stream_fallback_allowed"
        next_action_hint = "fallback_stream_upload_ready"
        reason = "当前执行模式允许目标端走普通上传/流式写入。"
    elif "download_upload" in fallback_modes or "stream_upload" in fallback_modes:
        mode = "record_pending_only"
        reason_code = "fallback_available_but_deferred"
        next_action_hint = "defer_to_pending_tree"
        reason = "当前目标端可降级上传，但本轮建议先记录到待补传。"
    if not fast_hash_hits and bridge_candidates:
        pending_reason = str(bridge_meta.get("pending_reason") or "")
        execution_state = str(bridge_meta.get("execution_state") or "")
        if pending_reason == "provider_api_bridge_not_executed_yet":
            reason_code = "provider_api_bridge_not_executed_yet"
            next_action_hint = "execute_provider_api_enrich"
            prepared_label = "源端 bridge 已进入 API 准备态"
            next_step_label = "执行真实 provider enrich"
            if execution_state == "api_capture_cache_normalized":
                reason_code = "api_capture_cache_partial"
                next_action_hint = "extend_capture_cache_or_provider_api"
                prepared_label = "源端 bridge 已先吃到抓取缓存里的文件级哈希"
                next_step_label = "继续扩抓取缓存或执行真实 provider enrich"
            if bridge_missing_recoverable_fast_hashes:
                next_action_hint = "execute_provider_api_for_fast_hashes"
                if execution_state == "api_capture_cache_normalized":
                    next_action_hint = "extend_capture_cache_for_fast_hashes"
            if bridge_missing_expected_hashes:
                reason = (
                    f"{prepared_label}，但当前仍缺补齐目标端所需哈希的关键字段；"
                    f"理论预期哈希={', '.join(bridge_expected_hashes or ['-'])}，当前仍缺={', '.join(bridge_missing_expected_hashes)}"
                )
                if bridge_missing_recoverable_fast_hashes:
                    reason += f"；其中目标端当前最关键的是 {', '.join(bridge_missing_recoverable_fast_hashes)}"
                reason += f"；下一步建议={next_step_label}"
            else:
                reason = (
                    f"{prepared_label}，但当前还没有补齐目标端真正可用的快传指纹；"
                    f"目前仅看到候选哈希: {', '.join(bridge_candidates)}"
                )
                reason += f"；下一步建议={next_step_label}"
        elif pending_reason == "non_fast_hashes_only_after_session_snapshot":
            reason_code = "non_fast_hashes_only_after_session_snapshot"
            next_action_hint = "wait_for_fast_hash_or_fallback"
            reason = (
                "源端 session snapshot 已补出候选哈希，但当前仍缺少目标端可直接快传的指纹；"
                f"候选哈希: {', '.join(bridge_candidates)}"
            )
            if missing_target_fast_hashes:
                reason += f"；目标端仍缺={', '.join(missing_target_fast_hashes)}"
        elif supported_fast_hashes:
            reason_code = "target_hash_not_supported"
            next_action_hint = "fallback_target_does_not_accept_hashes"
            reason = (
                "源端已补出候选哈希，但当前目标端不认这些快传指纹；"
                f"源端候选={', '.join(bridge_candidates)}，目标端支持={', '.join(supported_fast_hashes)}"
            )
    elif not fast_hash_hits and not capability.get("supports_fast_upload") and not capability.get("fast_upload_hashes") and ("download_upload" in fallback_modes or "stream_upload" in fallback_modes):
        reason_code = "target_no_fast_capability"
        next_action_hint = "fallback_target_has_no_fast_upload"
        reason = "当前目标端未声明元数据秒传能力，只能走普通上传、流式写入或下载补传。"
    return {
        "mode": mode,
        "reason_code": reason_code,
        "next_action_hint": next_action_hint,
        "reason": reason,
        "fast_hash_hits": fast_hash_hits,
        "target_fast_hashes": supported_fast_hashes,
        "missing_target_fast_hashes": missing_target_fast_hashes,
        "bridge_candidate_hashes": bridge_candidates,
        "bridge_pending_reason": str(bridge_meta.get("pending_reason") or ""),
        "bridge_execution_state": str(bridge_meta.get("execution_state") or ""),
        "bridge_provider_stage": str(bridge_meta.get("provider_stage") or ""),
        "bridge_transport_hint": str(bridge_meta.get("transport_hint") or ""),
        "bridge_maturity_level": str(bridge_meta.get("maturity_level") or ""),
        "bridge_maturity_honesty": str(bridge_meta.get("maturity_honesty") or ""),
        "bridge_expected_hashes": bridge_expected_hashes,
        "bridge_missing_expected_hashes": bridge_missing_expected_hashes,
        "bridge_recoverable_fast_hashes": bridge_recoverable_fast_hashes,
        "bridge_missing_recoverable_fast_hashes": bridge_missing_recoverable_fast_hashes,
        "supports_fast_upload": bool(capability.get("supports_fast_upload") or capability.get("fast_upload_hashes") or capability.get("fastUploadHashes")),
        "fallback_modes": fallback_modes,
        "auto_download_threshold_mb": max(0, int(auto_download_threshold_mb or 0)),
    }


def summarize_transfer_plan(
    entries: list[SourceEntry],
    target_capability: dict[str, Any] | None = None,
    *,
    auto_download_threshold_mb: int = 0,
    allow_full_fallback: bool = False,
) -> dict[str, Any]:
    counts: dict[str, int] = {}
    fast_hash_counts: dict[str, int] = {}
    bridge_candidate_counts: dict[str, int] = {}
    bridge_pending_reason_counts: dict[str, int] = {}
    reason_code_counts: dict[str, int] = {}
    bridge_execution_state_counts: dict[str, int] = {}
    bridge_provider_stage_counts: dict[str, int] = {}
    bridge_transport_hint_counts: dict[str, int] = {}
    bridge_maturity_level_counts: dict[str, int] = {}
    bridge_maturity_honesty_counts: dict[str, int] = {}
    bridge_missing_expected_hash_counts: dict[str, int] = {}
    missing_target_fast_hash_counts: dict[str, int] = {}
    bridge_missing_recoverable_fast_hash_counts: dict[str, int] = {}
    next_action_hint_counts: dict[str, int] = {}
    for entry in entries:
        plan = plan_transfer_mode(
            entry,
            target_capability,
            auto_download_threshold_mb=auto_download_threshold_mb,
            allow_full_fallback=allow_full_fallback,
        )
        mode = str(plan.get("mode") or "record_pending_only")
        counts[mode] = counts.get(mode, 0) + 1
        for key in list(plan.get("fast_hash_hits") or []):
            fast_hash_counts[key] = fast_hash_counts.get(key, 0) + 1
        for key in list(plan.get("bridge_candidate_hashes") or []):
            bridge_candidate_counts[key] = bridge_candidate_counts.get(key, 0) + 1
        reason_code = str(plan.get("reason_code") or "").strip()
        if reason_code:
            reason_code_counts[reason_code] = reason_code_counts.get(reason_code, 0) + 1
        next_action_hint = str(plan.get("next_action_hint") or "").strip()
        if next_action_hint:
            next_action_hint_counts[next_action_hint] = next_action_hint_counts.get(next_action_hint, 0) + 1
        pending_reason = str(plan.get("bridge_pending_reason") or "").strip()
        if pending_reason:
            bridge_pending_reason_counts[pending_reason] = bridge_pending_reason_counts.get(pending_reason, 0) + 1
        bridge_execution_state = str(plan.get("bridge_execution_state") or "").strip()
        if bridge_execution_state:
            bridge_execution_state_counts[bridge_execution_state] = bridge_execution_state_counts.get(bridge_execution_state, 0) + 1
        bridge_provider_stage = str(plan.get("bridge_provider_stage") or "").strip()
        if bridge_provider_stage:
            bridge_provider_stage_counts[bridge_provider_stage] = bridge_provider_stage_counts.get(bridge_provider_stage, 0) + 1
        bridge_transport_hint = str(plan.get("bridge_transport_hint") or "").strip()
        if bridge_transport_hint:
            bridge_transport_hint_counts[bridge_transport_hint] = bridge_transport_hint_counts.get(bridge_transport_hint, 0) + 1
        bridge_maturity_level = str(plan.get("bridge_maturity_level") or "").strip()
        if bridge_maturity_level:
            bridge_maturity_level_counts[bridge_maturity_level] = bridge_maturity_level_counts.get(bridge_maturity_level, 0) + 1
        bridge_maturity_honesty = str(plan.get("bridge_maturity_honesty") or "").strip()
        if bridge_maturity_honesty:
            bridge_maturity_honesty_counts[bridge_maturity_honesty] = bridge_maturity_honesty_counts.get(bridge_maturity_honesty, 0) + 1
        for key in list(plan.get("bridge_missing_expected_hashes") or []):
            bridge_missing_expected_hash_counts[key] = bridge_missing_expected_hash_counts.get(key, 0) + 1
        for key in list(plan.get("missing_target_fast_hashes") or []):
            missing_target_fast_hash_counts[key] = missing_target_fast_hash_counts.get(key, 0) + 1
        for key in list(plan.get("bridge_missing_recoverable_fast_hashes") or []):
            bridge_missing_recoverable_fast_hash_counts[key] = bridge_missing_recoverable_fast_hash_counts.get(key, 0) + 1
    return {
        "total": len(entries),
        "mode_counts": counts,
        "fast_hash_counts": fast_hash_counts,
        "bridge_candidate_counts": bridge_candidate_counts,
        "bridge_pending_reason_counts": bridge_pending_reason_counts,
        "reason_code_counts": reason_code_counts,
        "bridge_execution_state_counts": bridge_execution_state_counts,
        "bridge_provider_stage_counts": bridge_provider_stage_counts,
        "bridge_transport_hint_counts": bridge_transport_hint_counts,
        "bridge_maturity_level_counts": bridge_maturity_level_counts,
        "bridge_maturity_honesty_counts": bridge_maturity_honesty_counts,
        "bridge_missing_expected_hash_counts": bridge_missing_expected_hash_counts,
        "missing_target_fast_hash_counts": missing_target_fast_hash_counts,
        "bridge_missing_recoverable_fast_hash_counts": bridge_missing_recoverable_fast_hash_counts,
        "next_action_hint_counts": next_action_hint_counts,
        "auto_download_threshold_mb": max(0, int(auto_download_threshold_mb or 0)),
        "allow_full_fallback": bool(allow_full_fallback),
    }
