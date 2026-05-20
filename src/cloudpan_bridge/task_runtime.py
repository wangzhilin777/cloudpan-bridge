from __future__ import annotations

from typing import Any

from .config import AppConfig
from .models import normalize_posix_path
from .source_adapter import build_source_provider_context, build_source_runtime_status


def resolve_source_mapping_context(
    runtime_config: AppConfig,
    *,
    source_path: str = "",
    mount_path: str = "",
    requested_driver: str = "",
) -> dict[str, Any]:
    return build_source_provider_context(
        runtime_config,
        source_path=source_path,
        mount_path=mount_path,
        requested_driver=requested_driver,
    )


def build_current_task_snapshot(
    mode: str,
    runtime_config: AppConfig,
    *,
    source_path: str = "",
    source_root_for_target: str = "",
    target_key: str = "",
    target_path: str = "",
    selected_paths: list[str] | None = None,
    mount_path: str = "",
    requested_driver: str = "",
) -> dict[str, Any]:
    normalized_source_path = normalize_posix_path(str(source_path or runtime_config.source_path or "/"))
    normalized_source_root_for_target = normalize_posix_path(
        str(source_root_for_target or normalized_source_path or runtime_config.source_path or "/")
    )
    normalized_target_key = str(target_key or runtime_config.target_key or "guangya").strip().lower() or "guangya"
    normalized_target_path = normalize_posix_path(str(target_path or runtime_config.target_path or "/"))
    source_mapping_context = resolve_source_mapping_context(
        runtime_config,
        source_path=normalized_source_path,
        mount_path=mount_path,
        requested_driver=requested_driver,
    )
    source_runtime_context = build_source_runtime_status(
        runtime_config,
        source_path=normalized_source_path,
        mount_path=str(source_mapping_context.get("mount_path") or ""),
        requested_driver=requested_driver,
    )
    return {
        "mode": mode,
        "source_path": normalized_source_path,
        "source_root_for_target": normalized_source_root_for_target,
        "target_key": normalized_target_key,
        "target_path": normalized_target_path,
        "selected_paths_count": len(list(selected_paths or [])),
        "source_mapping_context": source_mapping_context,
        "source_runtime_context": source_runtime_context,
    }
