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
    return {
        "mode": mode,
        "reason": reason,
        "fast_hash_hits": fast_hash_hits,
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
    return {
        "total": len(entries),
        "mode_counts": counts,
        "fast_hash_counts": fast_hash_counts,
        "auto_download_threshold_mb": max(0, int(auto_download_threshold_mb or 0)),
        "allow_full_fallback": bool(allow_full_fallback),
    }
