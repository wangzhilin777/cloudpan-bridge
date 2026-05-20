from __future__ import annotations

from typing import Any, Callable

from .config import AppConfig
from .models import SourceEntry, normalize_fingerprint_value

LogFn = Callable[[str], None]


MAINSTREAM_SOURCE_PROVIDERS = {
    "189cloud": {
        "preferred_hashes": ["md5"],
        "capture_required": True,
        "capture_fields": ["cookie_header", "session_key", "access_token", "refresh_token"],
    },
    "quark": {
        "preferred_hashes": ["md5"],
        "capture_required": True,
        "capture_fields": ["cookie_header", "access_token", "refresh_token"],
    },
    "123pan": {
        "preferred_hashes": ["md5"],
        "capture_required": True,
        "capture_fields": ["cookie_header", "access_token", "refresh_token"],
    },
    "baidu": {
        "preferred_hashes": ["md5"],
        "capture_required": True,
        "capture_fields": ["cookie_header", "bdstoken", "access_token", "refresh_token"],
    },
    "thunder": {
        "preferred_hashes": ["gcid", "md5"],
        "capture_required": True,
        "capture_fields": ["authorization", "device_id", "x-device-id", "access_token", "refresh_token"],
    },
    "aliyundriveopen": {
        "preferred_hashes": ["sha1", "md5"],
        "capture_required": True,
        "capture_fields": ["refresh_token", "access_token", "authorization"],
    },
    "onedrive": {
        "preferred_hashes": ["sha1", "md5"],
        "capture_required": True,
        "capture_fields": ["refresh_token", "access_token", "authorization"],
    },
}


HASH_ALIASES = {
    "md5": ["md5", "etag", "file_md5", "content_md5"],
    "gcid": ["gcid", "file_gcid"],
    "sha1": ["sha1", "content_sha1"],
    "sha256": ["sha256", "content_sha256"],
    "crc64": ["crc64"],
    "pre_hash": ["pre_hash", "prehash"],
    "slice_md5": ["slice_md5", "slicemd5"],
    "pickcode": ["pickcode"],
    "content_hash": ["content_hash", "contenthash"],
}


def supports_enrichment(provider_key: str) -> bool:
    return str(provider_key or "").strip().lower() in MAINSTREAM_SOURCE_PROVIDERS


def build_source_enrichment_runtime(config: AppConfig, provider_key: str) -> dict[str, Any]:
    normalized = str(provider_key or "").strip().lower()
    rule = dict(MAINSTREAM_SOURCE_PROVIDERS.get(normalized) or {})
    capture_snapshot = dict((config.provider_captures or {}).get(normalized) or {})
    captured = dict(capture_snapshot.get("captured") or {})
    capture_fields = list(rule.get("capture_fields") or [])
    present_capture_fields = [field for field in capture_fields if str(captured.get(field) or "").strip()]
    capture_required = bool(rule.get("capture_required"))
    capture_ready = bool(present_capture_fields) if capture_required else True
    return {
        "provider_key": normalized,
        "supported": bool(rule),
        "preferred_hashes": list(rule.get("preferred_hashes") or []),
        "capture_required": capture_required,
        "capture_ready": capture_ready,
        "capture_fields": capture_fields,
        "capture_fields_present": present_capture_fields,
        "capture_status": str(capture_snapshot.get("status") or ("captured" if present_capture_fields else "idle")),
        "runtime_mode": "openlist_first_provider_snapshot_enrichment" if rule else "openlist_only",
    }


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


def _pick_hash_value(entry: SourceEntry, logical_key: str) -> str:
    aliases = list(HASH_ALIASES.get(logical_key) or [logical_key])
    for payload in _collect_raw_sources(entry):
        for alias in aliases:
            value = payload.get(alias)
            if not str(value or "").strip():
                continue
            uppercase = logical_key not in {"pickcode"}
            return normalize_fingerprint_value(value, uppercase=uppercase)
    return ""


def enrich_entry(entry: SourceEntry, config: AppConfig, log: LogFn | None = None) -> tuple[SourceEntry, dict[str, Any]]:
    runtime = build_source_enrichment_runtime(config, entry.provider)
    if not runtime.get("supported"):
        return entry, {**runtime, "changed": False, "added_hashes": [], "message": "当前 provider 还没有专用 enrich 实现。"}

    added_hashes: list[str] = []
    merged = SourceEntry(
        path=entry.path,
        md5=entry.md5 or _pick_hash_value(entry, "md5"),
        size=entry.size,
        last_op_time=entry.last_op_time,
        source_id=entry.source_id,
        provider=entry.provider,
        hash_type=entry.hash_type,
        gcid=entry.gcid or _pick_hash_value(entry, "gcid"),
        etag=entry.etag or _pick_hash_value(entry, "md5"),
        sha1=entry.sha1 or _pick_hash_value(entry, "sha1"),
        sha256=entry.sha256 or _pick_hash_value(entry, "sha256"),
        crc64=entry.crc64 or _pick_hash_value(entry, "crc64"),
        pre_hash=entry.pre_hash or _pick_hash_value(entry, "pre_hash"),
        slice_md5=entry.slice_md5 or _pick_hash_value(entry, "slice_md5"),
        pickcode=entry.pickcode or _pick_hash_value(entry, "pickcode"),
        content_hash=entry.content_hash or _pick_hash_value(entry, "content_hash"),
        extra_hashes=dict(entry.extra_hashes or {}),
        provider_specific=dict(entry.provider_specific or {}),
        raw_hash_info=dict(entry.raw_hash_info or {}),
    )
    for field in ("md5", "gcid", "sha1", "sha256", "crc64", "pre_hash", "slice_md5", "pickcode", "content_hash"):
        if not getattr(entry, field) and getattr(merged, field):
            added_hashes.append(field)
    changed = bool(added_hashes)
    message = "已从现有元数据归并出补充指纹。" if changed else "当前 provider 没有额外可归并的指纹。"
    if changed and log:
        log(f"[直连补指纹] {entry.path}: 新增 {', '.join(added_hashes)}")
    return merged, {
        **runtime,
        "changed": changed,
        "added_hashes": added_hashes,
        "message": message,
    }


def enrich_batch(entries: list[SourceEntry], config: AppConfig, log: LogFn | None = None) -> tuple[list[SourceEntry], dict[str, Any]]:
    enriched: list[SourceEntry] = []
    changed_count = 0
    added_hash_counts: dict[str, int] = {}
    provider_key = str(entries[0].provider if entries else "").strip().lower()
    runtime = build_source_enrichment_runtime(config, provider_key)
    for entry in entries:
        merged, report = enrich_entry(entry, config, log=log)
        enriched.append(merged)
        if report.get("changed"):
            changed_count += 1
            for field in list(report.get("added_hashes") or []):
                added_hash_counts[field] = added_hash_counts.get(field, 0) + 1
    return enriched, {
        **runtime,
        "total": len(entries),
        "changed_count": changed_count,
        "added_hash_counts": added_hash_counts,
    }
