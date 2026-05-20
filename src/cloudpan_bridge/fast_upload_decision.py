from __future__ import annotations

from typing import Any


FAST_UPLOAD_LEVELS = {
    "native_fast_upload",
    "fast_upload_after_enrichment",
    "partial_fast_upload",
    "upload_only",
    "download_then_upload",
    "unsupported",
}


def assess_directory_fast_upload(
    analysis_summary: dict[str, Any] | None,
    *,
    target_capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = dict(analysis_summary or {})
    capability = dict(target_capability or {})
    total = max(0, int(summary.get("total") or 0))
    fast_ready = max(0, int(summary.get("fast_upload_ready") or 0))
    missing_fast = max(0, int(summary.get("missing_fast_upload") or 0))
    sha1_ready = max(0, int(summary.get("sha1_ready") or 0))
    sha256_ready = max(0, int(summary.get("sha256_ready") or 0))
    pre_hash_ready = max(0, int(summary.get("pre_hash_ready") or 0))
    slice_md5_ready = max(0, int(summary.get("slice_md5_ready") or 0))
    content_hash_ready = max(0, int(summary.get("content_hash_ready") or 0))
    pickcode_ready = max(0, int(summary.get("pickcode_ready") or 0))
    supports_fast_upload = bool(
        capability.get("supports_fast_upload")
        if "supports_fast_upload" in capability
        else capability.get("fastUploadHashes")
    )
    fallback_modes = list(capability.get("fallback_modes") or capability.get("fallbackModes") or [])
    fast_upload_hashes = list(capability.get("fast_upload_hashes") or capability.get("fastUploadHashes") or [])

    enrichment_ready = max(
        sha1_ready,
        sha256_ready,
        pre_hash_ready,
        slice_md5_ready,
        content_hash_ready,
        pickcode_ready,
    )
    level = "unsupported"
    zh = "当前目录还缺少足够信息，暂不建议自动执行。"
    en = "This directory still lacks enough evidence. Automatic execution is not recommended yet."
    bucket = "需补指纹后再判断"

    if not supports_fast_upload:
        level = "upload_only"
        zh = "目标端不支持元数据秒传，当前目录应按普通上传/覆盖或补传处理。"
        en = "The target does not support metadata-based fast upload. Handle this directory through normal upload or fallback reupload."
        bucket = "只能补传"
    elif total <= 0:
        level = "unsupported"
        zh = "当前还没有目录分析结果，先分析后再决定是否秒传。"
        en = "There is no directory analysis result yet. Analyze first before deciding on fast upload."
        bucket = "需补指纹后再判断"
    elif fast_ready >= total:
        level = "native_fast_upload"
        zh = "当前目录全部文件都已具备目标端可直接使用的秒传指纹，可优先原生秒传。"
        en = "All files in this directory already have target-ready fast-upload fingerprints. Native metadata-first sync is preferred."
        bucket = "全部可秒传"
    elif fast_ready > 0:
        level = "partial_fast_upload"
        zh = "当前目录只有部分文件具备原生秒传指纹，建议先秒传再补传。"
        en = "Only part of this directory is natively fast-upload ready. Prefer fast upload first, then fallback."
        bucket = "部分可秒传"
    elif enrichment_ready > 0:
        level = "fast_upload_after_enrichment"
        zh = "当前目录还没有直接可用的秒传指纹，但存在可用于补指纹判断的扩展指纹，应先补指纹再判断。"
        en = "There are no directly usable fast-upload fingerprints yet, but enrichment-capable fingerprints exist. Enrich first, then decide."
        bucket = "需补指纹后再判断"
    elif missing_fast > 0 or "download_upload" in fallback_modes or "stream_upload" in fallback_modes:
        level = "download_then_upload"
        zh = "当前目录缺少可秒传指纹，建议按下载后上传或普通补传处理。"
        en = "This directory lacks fast-upload-ready fingerprints. Handle it through download-then-upload or normal fallback upload."
        bucket = "只能补传"

    return {
        "level": level,
        "bucket": bucket,
        "supports_fast_upload": supports_fast_upload,
        "fast_upload_hashes": fast_upload_hashes,
        "fallback_modes": fallback_modes,
        "fast_ready": fast_ready,
        "missing_fast": missing_fast,
        "enrichment_ready": enrichment_ready,
        "rationale": {
            "zh": zh,
            "en": en,
        },
    }
