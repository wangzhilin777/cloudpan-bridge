from __future__ import annotations

from typing import Any, Callable

from .source_enrich_rules import build_provider_rule

BridgePrepareFn = Callable[[dict[str, Any]], dict[str, Any]]


def _build_base_result(provider_key: str, captured: dict[str, Any], *, transport_hint: str, fingerprint_expectation: list[str]) -> dict[str, Any]:
    rule = build_provider_rule(provider_key)
    bridge = dict(rule.get("bridge") or {})
    throttle_defaults = dict(rule.get("throttle_defaults") or {})
    fallback_policy = dict(rule.get("fallback_policy") or {})
    preferred_hashes = [str(item).strip().lower() for item in list(rule.get("preferred_hashes") or []) if str(item).strip()]
    groups = [
        [str(item).strip() for item in list(group or []) if str(item).strip()]
        for group in list(bridge.get("required_groups") or [])
    ]
    selected_group: list[str] = []
    for group in groups:
        if group and all(str(captured.get(item) or "").strip() for item in group):
            selected_group = list(group)
            break
    selected_fields = {
        key: str(captured.get(key) or "").strip()
        for key in selected_group
        if str(captured.get(key) or "").strip()
    }
    return {
        "provider_key": str(provider_key or "").strip().lower(),
        "available": bool(selected_group),
        "mode": str(bridge.get("mode") or "none"),
        "hook_name": str(bridge.get("hook_name") or ""),
        "selected_group": selected_group,
        "selected_field_names": list(selected_fields.keys()),
        "selected_field_count": len(selected_fields),
        "transport_hint": transport_hint,
        "fingerprint_expectation": list(fingerprint_expectation),
        "preferred_hashes": preferred_hashes,
        "throttle_defaults": throttle_defaults,
        "fallback_policy": fallback_policy,
        "degrade_to": ["openlist_normalization", "download_upload"],
        "execution_state": "prepared" if selected_group else "missing_capture",
    }


def prepare_189cloud_session_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("189cloud", captured, transport_hint="cookie_or_session_snapshot", fingerprint_expectation=["md5"])


def prepare_quark_session_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("quark", captured, transport_hint="cookie_snapshot", fingerprint_expectation=["md5", "sha1", "slice_md5"])


def prepare_123pan_session_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("123pan", captured, transport_hint="cookie_snapshot", fingerprint_expectation=["md5", "sha1"])


def prepare_baidu_session_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("baidu", captured, transport_hint="cookie_plus_bdstoken", fingerprint_expectation=["md5", "slice_md5"])


def prepare_thunder_api_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("thunder", captured, transport_hint="authorization_plus_device_id", fingerprint_expectation=["gcid", "md5", "sha1"])


def prepare_aliyundriveopen_api_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("aliyundriveopen", captured, transport_hint="refresh_token_or_authorization", fingerprint_expectation=["sha1", "md5", "crc64"])


def prepare_onedrive_api_bridge(captured: dict[str, Any]) -> dict[str, Any]:
    return _build_base_result("onedrive", captured, transport_hint="refresh_token_or_authorization", fingerprint_expectation=["sha1", "md5", "content_hash"])


SOURCE_BRIDGE_REGISTRY: dict[str, BridgePrepareFn] = {
    "189cloud": prepare_189cloud_session_bridge,
    "quark": prepare_quark_session_bridge,
    "123pan": prepare_123pan_session_bridge,
    "baidu": prepare_baidu_session_bridge,
    "thunder": prepare_thunder_api_bridge,
    "aliyundriveopen": prepare_aliyundriveopen_api_bridge,
    "onedrive": prepare_onedrive_api_bridge,
}


def has_source_bridge(provider_key: str) -> bool:
    return str(provider_key or "").strip().lower() in SOURCE_BRIDGE_REGISTRY


def prepare_source_bridge(provider_key: str, captured: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized = str(provider_key or "").strip().lower()
    captured = dict(captured or {})
    bridge_fn = SOURCE_BRIDGE_REGISTRY.get(normalized)
    if not bridge_fn:
        return {
            "provider_key": normalized,
            "available": False,
            "mode": "none",
            "hook_name": "",
            "selected_group": [],
            "selected_field_names": [],
            "selected_field_count": 0,
            "transport_hint": "openlist_only",
            "fingerprint_expectation": [],
            "preferred_hashes": [],
            "throttle_defaults": {},
            "fallback_policy": {},
            "degrade_to": ["openlist_normalization", "download_upload"],
            "execution_state": "bridge_not_registered",
            "hook_registered": False,
        }
    result = dict(bridge_fn(captured) or {})
    result["hook_registered"] = True
    return result
