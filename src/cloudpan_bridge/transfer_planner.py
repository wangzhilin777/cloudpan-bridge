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
    }


def compute_fast_upload_hits(entry: SourceEntry, target_capability: dict[str, Any] | None = None) -> list[str]:
    capability = dict(target_capability or {})
    supported = [str(item or "").strip().lower() for item in list(capability.get("fast_upload_hashes") or capability.get("fastUploadHashes") or []) if str(item or "").strip()]
    values = _entry_hash_map(entry)
    return [key for key in supported if values.get(key)]


def plan_transfer_mode(
    entry: SourceEntry,
    target_capability: dict[str, Any] | None = None,
    *,
    auto_download_threshold_mb: int = 0,
    allow_full_fallback: bool = False,
) -> dict[str, Any]:
    capability = dict(target_capability or {})
    fallback_modes = [str(item or "").strip().lower() for item in list(capability.get("fallback_modes") or capability.get("fallbackModes") or []) if str(item or "").strip()]
    fast_hash_hits = compute_fast_upload_hits(entry, capability)
    bridge_meta = _entry_bridge_metadata(entry)
    bridge_candidates = list(bridge_meta.get("candidate_hashes") or [])
    threshold_bytes = max(0, int(auto_download_threshold_mb or 0)) * 1024 * 1024
    small_file_auto = bool(threshold_bytes > 0 and int(entry.size) <= threshold_bytes)
    mode = "record_pending_only"
    reason = "当前目标端不支持可直接使用的快传指纹，且本轮未允许自动降级。"
    if fast_hash_hits:
        mode = "fast_upload"
        reason = f"目标端支持当前文件的快传指纹: {', '.join(fast_hash_hits)}"
    elif "download_upload" in fallback_modes and small_file_auto:
        mode = "download_upload"
        reason = "文件命中小文件自动补传阈值，建议直接下载后上传。"
    elif "download_upload" in fallback_modes and allow_full_fallback:
        mode = "download_upload"
        reason = "当前执行模式允许完整降级到下载后上传。"
    elif "stream_upload" in fallback_modes and allow_full_fallback:
        mode = "stream_upload"
        reason = "当前执行模式允许目标端走普通上传/流式写入。"
    elif "download_upload" in fallback_modes or "stream_upload" in fallback_modes:
        mode = "record_pending_only"
        reason = "当前目标端可降级上传，但本轮建议先记录到待补传。"
    if not fast_hash_hits and bridge_candidates:
        pending_reason = str(bridge_meta.get("pending_reason") or "")
        supported_fast = [str(item or "").strip().lower() for item in list(capability.get("fast_upload_hashes") or capability.get("fastUploadHashes") or []) if str(item or "").strip()]
        if pending_reason == "provider_api_bridge_not_executed_yet":
            reason = (
                "源端 bridge 已进入 API 准备态，但当前版本还没有执行真实 provider enrich；"
                f"目前仅看到候选哈希: {', '.join(bridge_candidates)}"
            )
        elif pending_reason == "non_fast_hashes_only_after_session_snapshot":
            reason = (
                "源端 session snapshot 已补出候选哈希，但当前仍缺少目标端可直接快传的指纹；"
                f"候选哈希: {', '.join(bridge_candidates)}"
            )
        elif supported_fast:
            reason = (
                "源端已补出候选哈希，但当前目标端不认这些快传指纹；"
                f"源端候选={', '.join(bridge_candidates)}，目标端支持={', '.join(supported_fast)}"
            )
    return {
        "mode": mode,
        "reason": reason,
        "fast_hash_hits": fast_hash_hits,
        "bridge_candidate_hashes": bridge_candidates,
        "bridge_pending_reason": str(bridge_meta.get("pending_reason") or ""),
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
        pending_reason = str(plan.get("bridge_pending_reason") or "").strip()
        if pending_reason:
            bridge_pending_reason_counts[pending_reason] = bridge_pending_reason_counts.get(pending_reason, 0) + 1
    return {
        "total": len(entries),
        "mode_counts": counts,
        "fast_hash_counts": fast_hash_counts,
        "bridge_candidate_counts": bridge_candidate_counts,
        "bridge_pending_reason_counts": bridge_pending_reason_counts,
        "auto_download_threshold_mb": max(0, int(auto_download_threshold_mb or 0)),
        "allow_full_fallback": bool(allow_full_fallback),
    }
