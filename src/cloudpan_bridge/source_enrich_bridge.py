from __future__ import annotations

from typing import Any

from .source_enrich_rules import build_provider_rule


def _matched_groups(captured: dict[str, Any], groups: list[list[str]]) -> list[list[str]]:
    matched: list[list[str]] = []
    for group in groups:
        normalized = [str(item).strip() for item in group if str(item).strip()]
        if normalized and all(str(captured.get(item) or "").strip() for item in normalized):
            matched.append(normalized)
    return matched


def _flatten_missing_keys(groups: list[list[str]], matched: list[list[str]]) -> list[str]:
    if matched:
        return []
    missing: list[str] = []
    for group in groups:
        for item in group:
            normalized = str(item).strip()
            if normalized and normalized not in missing:
                missing.append(normalized)
    return missing


def build_bridge_runtime(provider_key: str, captured: dict[str, Any] | None = None) -> dict[str, Any]:
    rule = build_provider_rule(provider_key)
    bridge = dict(rule.get("bridge") or {})
    groups = [
        [str(item).strip() for item in list(group or []) if str(item).strip()]
        for group in list(bridge.get("required_groups") or [])
    ]
    captured = dict(captured or {})
    matched = _matched_groups(captured, groups)
    hook_name = str(bridge.get("hook_name") or "")
    implemented = bool(bridge.get("implemented"))
    ready = bool(matched) if groups else False
    mode = str(bridge.get("mode") or "")

    if not mode:
        status = "bridge_not_declared"
        next_action = "openlist_only"
    elif not ready:
        status = "bridge_capture_missing"
        next_action = "collect_capture_fields"
    elif implemented:
        status = "bridge_ready"
        next_action = hook_name or "run_provider_bridge"
    elif mode == "session_snapshot":
        status = "bridge_ready_but_normalization_only"
        next_action = hook_name or "wait_for_session_bridge_implementation"
    else:
        status = "bridge_ready_but_api_pending"
        next_action = hook_name or "wait_for_provider_api_implementation"

    return {
        "provider_key": str(provider_key or "").strip().lower(),
        "mode": mode or "none",
        "implemented": implemented,
        "hook_name": hook_name,
        "required_groups": groups,
        "matched_groups": matched,
        "ready": ready,
        "status": status,
        "next_action": next_action,
        "missing_keys": _flatten_missing_keys(groups, matched),
    }
