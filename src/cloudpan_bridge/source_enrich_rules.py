from __future__ import annotations

from typing import Any


GENERIC_HASH_ALIASES: dict[str, list[str]] = {
    "md5": ["md5", "file_md5", "content_md5", "md5Hash", "md5_hash"],
    "gcid": ["gcid", "file_gcid"],
    "sha1": ["sha1", "content_sha1", "sha1Hash", "sha1_hash"],
    "sha256": ["sha256", "content_sha256", "sha256Hash", "sha256_hash"],
    "crc64": ["crc64", "crc64Hash", "crc64_hash"],
    "pre_hash": ["pre_hash", "prehash"],
    "slice_md5": ["slice_md5", "slicemd5"],
    "pickcode": ["pickcode"],
    "content_hash": ["content_hash", "contenthash", "contentHash"],
}


MAINSTREAM_SOURCE_PROVIDERS: dict[str, dict[str, Any]] = {
    "189cloud": {
        "preferred_hashes": ["md5"],
        "throttle_defaults": {
            "rate_mode": "safe",
            "page_size": 200,
            "request_interval_ms": 900,
            "directory_interval_ms": 2500,
            "small_batch_only": False,
        },
        "fallback_policy": {
            "allow_auto_download": True,
            "download_selected_only": False,
            "pending_only_when_hash_missing": False,
            "summary": "天翼优先吃 OpenList 暴露的 md5，缺关键哈希时允许按安全节奏继续补传。",
        },
        "capture_required": True,
        "capture_fields": ["cookie_header", "session_key", "access_token", "refresh_token"],
        "bridge": {
            "mode": "session_snapshot",
            "implemented": True,
            "required_groups": [
                ["cookie_header"],
                ["session_key"],
                ["access_token", "refresh_token"],
            ],
            "hook_name": "prepare_189cloud_session_bridge",
        },
        "hash_aliases": {
            "md5": ["md5", "file_md5", "content_md5", "etag"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "capture_guided_normalization",
    },
    "quark": {
        "preferred_hashes": ["md5"],
        "throttle_defaults": {
            "rate_mode": "strict",
            "page_size": 100,
            "request_interval_ms": 1500,
            "directory_interval_ms": 3000,
            "small_batch_only": True,
        },
        "fallback_policy": {
            "allow_auto_download": False,
            "download_selected_only": True,
            "pending_only_when_hash_missing": True,
            "summary": "夸克优先保守分页与目录间隔，缺 md5 时建议先进待补传树，再按目录小批量补传。",
        },
        "capture_required": True,
        "capture_fields": ["cookie_header", "access_token", "refresh_token"],
        "bridge": {
            "mode": "session_snapshot",
            "implemented": True,
            "required_groups": [
                ["cookie_header"],
                ["access_token", "refresh_token"],
            ],
            "hook_name": "prepare_quark_session_bridge",
        },
        "hash_aliases": {
            "md5": ["md5", "file_md5", "content_md5", "etag"],
            "sha1": ["sha1", "content_sha1"],
            "pre_hash": ["pre_hash", "prehash"],
            "slice_md5": ["slice_md5", "slicemd5"],
            "content_hash": ["content_hash", "contenthash"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "capture_guided_normalization",
    },
    "123pan": {
        "preferred_hashes": ["md5"],
        "throttle_defaults": {
            "rate_mode": "safe",
            "page_size": 150,
            "request_interval_ms": 1100,
            "directory_interval_ms": 2500,
            "small_batch_only": False,
        },
        "fallback_policy": {
            "allow_auto_download": True,
            "download_selected_only": False,
            "pending_only_when_hash_missing": False,
            "summary": "123Pan 优先 md5，再参考 sha1；如果目录分析结果稳定，可接受正常补传节奏。",
        },
        "capture_required": True,
        "capture_fields": ["cookie_header", "access_token", "refresh_token"],
        "bridge": {
            "mode": "session_snapshot",
            "implemented": True,
            "required_groups": [
                ["cookie_header"],
                ["access_token", "refresh_token"],
            ],
            "hook_name": "prepare_123pan_session_bridge",
        },
        "hash_aliases": {
            "md5": ["md5", "file_md5", "content_md5", "etag"],
            "sha1": ["sha1", "content_sha1"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "capture_guided_normalization",
    },
    "baidu": {
        "preferred_hashes": ["md5"],
        "throttle_defaults": {
            "rate_mode": "strict",
            "page_size": 100,
            "request_interval_ms": 1800,
            "directory_interval_ms": 3500,
            "small_batch_only": True,
        },
        "fallback_policy": {
            "allow_auto_download": False,
            "download_selected_only": True,
            "pending_only_when_hash_missing": True,
            "summary": "百度优先 md5 与 slice_md5，风控更敏感，建议缺关键哈希时先记待补传。",
        },
        "capture_required": True,
        "capture_fields": ["cookie_header", "bdstoken", "access_token", "refresh_token"],
        "bridge": {
            "mode": "session_snapshot",
            "implemented": True,
            "required_groups": [
                ["cookie_header", "bdstoken"],
                ["access_token", "refresh_token", "bdstoken"],
            ],
            "hook_name": "prepare_baidu_session_bridge",
        },
        "hash_aliases": {
            "md5": ["md5", "file_md5", "content_md5", "etag"],
            "slice_md5": ["slice_md5", "slicemd5"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "capture_guided_normalization",
    },
    "thunder": {
        "preferred_hashes": ["gcid", "md5"],
        "throttle_defaults": {
            "rate_mode": "strict",
            "page_size": 80,
            "request_interval_ms": 1800,
            "directory_interval_ms": 3200,
            "small_batch_only": True,
        },
        "fallback_policy": {
            "allow_auto_download": False,
            "download_selected_only": True,
            "pending_only_when_hash_missing": True,
            "summary": "迅雷优先 gcid 和 md5；在真实 API enrich 未接通前，缺关键哈希时建议只记录待补传。",
        },
        "capture_required": True,
        "capture_fields": ["authorization", "device_id", "x-device-id", "access_token", "refresh_token"],
        "bridge": {
            "mode": "provider_api",
            "implemented": False,
            "required_groups": [
                ["authorization", "device_id"],
                ["access_token", "device_id"],
            ],
            "hook_name": "prepare_thunder_api_bridge",
        },
        "hash_aliases": {
            "gcid": ["gcid", "file_gcid"],
            "md5": ["md5", "file_md5", "content_md5", "etag"],
            "sha1": ["sha1", "content_sha1"],
            "pre_hash": ["pre_hash", "prehash"],
            "pickcode": ["pickcode"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "capture_guided_normalization",
    },
    "aliyundriveopen": {
        "preferred_hashes": ["sha1", "md5"],
        "throttle_defaults": {
            "rate_mode": "safe",
            "page_size": 120,
            "request_interval_ms": 1200,
            "directory_interval_ms": 2500,
            "small_batch_only": True,
        },
        "fallback_policy": {
            "allow_auto_download": False,
            "download_selected_only": True,
            "pending_only_when_hash_missing": True,
            "summary": "阿里云盘 Open 优先 sha1，再补 md5；当前 API bridge 仍属准备态，建议先分析后补传。",
        },
        "capture_required": True,
        "capture_fields": ["refresh_token", "access_token", "authorization"],
        "bridge": {
            "mode": "provider_api",
            "implemented": False,
            "required_groups": [
                ["refresh_token"],
                ["authorization"],
            ],
            "hook_name": "prepare_aliyundriveopen_api_bridge",
        },
        "hash_aliases": {
            "sha1": ["sha1", "content_sha1"],
            "md5": ["md5", "file_md5", "content_md5"],
            "crc64": ["crc64"],
            "content_hash": ["content_hash", "contenthash"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "direct_bridge_pending",
    },
    "onedrive": {
        "preferred_hashes": ["sha1", "md5"],
        "throttle_defaults": {
            "rate_mode": "safe",
            "page_size": 120,
            "request_interval_ms": 1200,
            "directory_interval_ms": 2500,
            "small_batch_only": False,
        },
        "fallback_policy": {
            "allow_auto_download": False,
            "download_selected_only": True,
            "pending_only_when_hash_missing": True,
            "summary": "OneDrive 优先 sha1；在 content hash 仍待真实 enrich 时，建议先记录缺口再按目录补传。",
        },
        "capture_required": True,
        "capture_fields": ["refresh_token", "access_token", "authorization"],
        "bridge": {
            "mode": "provider_api",
            "implemented": False,
            "required_groups": [
                ["refresh_token"],
                ["authorization"],
            ],
            "hook_name": "prepare_onedrive_api_bridge",
        },
        "hash_aliases": {
            "sha1": ["sha1", "content_sha1"],
            "md5": ["md5", "file_md5", "content_md5"],
            "content_hash": ["content_hash", "contenthash"],
        },
        "strategy_level": "provider_normalization",
        "bridge_status": "direct_bridge_pending",
    },
}


def build_provider_rule(provider_key: str) -> dict[str, Any]:
    normalized = str(provider_key or "").strip().lower()
    rule = dict(MAINSTREAM_SOURCE_PROVIDERS.get(normalized) or {})
    aliases = {
        logical_key: list(values)
        for logical_key, values in GENERIC_HASH_ALIASES.items()
    }
    for logical_key, values in dict(rule.get("hash_aliases") or {}).items():
        key = str(logical_key)
        merged_values: list[str] = []
        for item in [*(aliases.get(key) or []), *list(values)]:
            normalized_item = str(item or "").strip()
            if normalized_item and normalized_item not in merged_values:
                merged_values.append(normalized_item)
        aliases[key] = merged_values
    rule["provider_key"] = normalized
    rule["hash_aliases"] = aliases
    return rule
