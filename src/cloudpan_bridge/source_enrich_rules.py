from __future__ import annotations

from typing import Any


GENERIC_HASH_ALIASES: dict[str, list[str]] = {
    "md5": ["md5", "file_md5", "content_md5"],
    "gcid": ["gcid", "file_gcid"],
    "sha1": ["sha1", "content_sha1"],
    "sha256": ["sha256", "content_sha256"],
    "crc64": ["crc64"],
    "pre_hash": ["pre_hash", "prehash"],
    "slice_md5": ["slice_md5", "slicemd5"],
    "pickcode": ["pickcode"],
    "content_hash": ["content_hash", "contenthash"],
}


MAINSTREAM_SOURCE_PROVIDERS: dict[str, dict[str, Any]] = {
    "189cloud": {
        "preferred_hashes": ["md5"],
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
        aliases[str(logical_key)] = list(values)
    rule["provider_key"] = normalized
    rule["hash_aliases"] = aliases
    return rule
