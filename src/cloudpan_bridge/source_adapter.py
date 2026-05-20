from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Protocol

from .config import AppConfig
from .models import SourceEntry, SyncState
from .openlist import OpenListClient
from .provider_registry import build_source_mapping_context
from .source_enrich import build_source_enrichment_runtime


class SourceProvider(Protocol):
    def ensure_auth(self) -> None: ...
    def close(self) -> None: ...
    def list_roots(self) -> list[str]: ...
    def list_dir(self, path: str) -> dict[str, Any]: ...
    def walk_tree(self, source_root: str) -> list[SourceEntry]: ...
    def walk_leaf_dirs(self, root_path: str) -> Iterable[str]: ...
    def get_file_fingerprints(self, path: str) -> list[SourceEntry]: ...
    def download_stream(self, source_path: str, temp_dir: Path) -> Path: ...
    def get_auth_state(self) -> dict[str, str]: ...
    def get_provider_key(self) -> str: ...
    def get_runtime_context(self) -> dict[str, Any]: ...


def resolve_source_mount_path(
    source_path: str,
    mapping: dict[str, str],
    fallback_mount_path: str = "",
) -> str:
    normalized_source_path = str(source_path or "").strip()
    normalized_fallback = str(fallback_mount_path or "").strip()
    if not normalized_source_path:
        return normalized_fallback
    candidates = [str(path).strip() for path in dict(mapping or {}).keys() if str(path).strip()]
    best_match = ""
    for candidate in candidates:
        if normalized_source_path == candidate or normalized_source_path.startswith(candidate.rstrip("/") + "/"):
            if len(candidate) > len(best_match):
                best_match = candidate
    if best_match:
        return best_match
    if normalized_fallback and (
        normalized_source_path == normalized_fallback
        or normalized_source_path.startswith(normalized_fallback.rstrip("/") + "/")
    ):
        return normalized_fallback
    return normalized_fallback


def build_source_provider_context(
    config: AppConfig,
    *,
    source_path: str = "",
    mount_path: str = "",
    requested_driver: str = "",
) -> dict[str, Any]:
    effective_source_path = str(source_path or config.source_path or "/").strip() or "/"
    mapping = dict(config.mount_provider_mapping or {})
    resolved_mount_path = resolve_source_mount_path(effective_source_path, mapping, mount_path)
    configured_override = str(mapping.get(resolved_mount_path) or "").strip() if resolved_mount_path else ""
    effective_driver = configured_override or str(requested_driver or "").strip()
    return build_source_mapping_context(
        mount_path=resolved_mount_path,
        requested_driver=str(requested_driver or "").strip(),
        effective_driver=effective_driver,
        source_profile_override=configured_override,
        source_path=effective_source_path,
        target=config.target_key,
    )


def build_source_provider_resolution(
    config: AppConfig,
    context: dict[str, Any],
) -> dict[str, Any]:
    preference = str(config.source_provider_preference or "auto").strip().lower() or "auto"
    if preference not in {"auto", "openlist_only", "direct_preferred"}:
        preference = "auto"
    provider_key = str(context.get("provider_key") or "")
    direct_candidate = bool(context.get("provider_key") not in {"", "generic_openlist_driver", "openlist"})
    source_enrichment = build_source_enrichment_runtime(config, provider_key)
    direct_provider_ready = bool(
        direct_candidate
        and source_enrichment.get("supported")
        and source_enrichment.get("capture_ready")
    )
    selected_source_mode = "openlist_mount"
    selected_provider_key = "openlist"
    fallback_reason = ""
    selection_reason = "默认使用 OpenList 挂载源执行。"
    if preference == "openlist_only":
        selection_reason = "已显式指定只使用 OpenList 挂载源。"
    elif preference == "direct_preferred":
        if direct_provider_ready:
            selected_source_mode = "direct_provider_bridge_pending"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前已识别到直连 provider 候选与可用补指纹运行态，但真实直连 source provider 仍待后续实现，暂回退 OpenList 执行。"
            selection_reason = "已优先尝试直连 source provider 路径，但当前版本仍会保守回退到 OpenList。"
        elif direct_candidate:
            fallback_reason = "当前已识别到直连 provider 候选，但补指纹运行态尚未 ready，暂回退 OpenList 执行。"
            selection_reason = "已配置为优先直连 source provider，但当前尚未满足直连执行条件。"
    elif preference == "auto":
        if direct_provider_ready:
            selected_source_mode = "openlist_with_direct_candidate"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前 source provider 具备直连候选与可用补指纹运行态，但尚未接入真实直连实现，先保守走 OpenList。"
            selection_reason = "自动模式已检测到可用直连候选，后续可继续提升到真实直连执行。"
    return {
        "requested_provider_preference": preference,
        "selected_source_mode": selected_source_mode,
        "selected_provider_key": selected_provider_key,
        "direct_provider_candidate": direct_candidate,
        "direct_provider_ready": direct_provider_ready,
        "source_enrichment": source_enrichment,
        "fallback_reason": fallback_reason,
        "selection_reason": selection_reason,
    }


def build_source_runtime_status(
    config: AppConfig,
    *,
    source_path: str = "",
    mount_path: str = "",
    requested_driver: str = "",
) -> dict[str, Any]:
    context = build_source_provider_context(
        config,
        source_path=source_path,
        mount_path=mount_path,
        requested_driver=requested_driver,
    )
    resolution = build_source_provider_resolution(config, context)
    return {
        **context,
        **resolution,
        "provider_class": "OpenListSourceProvider",
        "provider_factory": "create_source_provider",
        "execution_provider_class": "OpenListSourceProvider",
        "execution_provider_factory": "create_source_provider",
        "auth_state": {
            "base_url": str(config.openlist_url or ""),
            "username": str(config.openlist_username or ""),
            "has_token": bool(str(config.openlist_token or "").strip()),
        },
    }


def source_ensure_auth(source: SourceProvider) -> None:
    if hasattr(source, "ensure_auth"):
        source.ensure_auth()  # type: ignore[call-arg]
        return
    if hasattr(source, "ensure_login"):
        source.ensure_login()  # type: ignore[attr-defined]
        return
    raise RuntimeError("当前源端 provider 缺少 ensure_auth/ensure_login 接口。")


def source_walk_tree(source: SourceProvider, source_root: str) -> list[SourceEntry]:
    if hasattr(source, "walk_tree"):
        return source.walk_tree(source_root)  # type: ignore[call-arg]
    if hasattr(source, "export_tree"):
        return source.export_tree(source_root)  # type: ignore[attr-defined]
    raise RuntimeError("当前源端 provider 缺少 walk_tree/export_tree 接口。")


def source_download_stream(source: SourceProvider, source_path: str, temp_dir: Path) -> Path:
    if hasattr(source, "download_stream"):
        return source.download_stream(source_path, temp_dir)  # type: ignore[call-arg]
    if hasattr(source, "download_file"):
        return source.download_file(source_path, temp_dir)  # type: ignore[attr-defined]
    raise RuntimeError("当前源端 provider 缺少 download_stream/download_file 接口。")


def source_get_file_fingerprints(source: SourceProvider, path: str) -> list[SourceEntry]:
    if hasattr(source, "get_file_fingerprints"):
        return list(source.get_file_fingerprints(path) or [])  # type: ignore[call-arg]
    return []


def source_get_runtime_context(source: SourceProvider) -> dict[str, Any]:
    if hasattr(source, "get_runtime_context"):
        return dict(source.get_runtime_context() or {})  # type: ignore[call-arg]
    provider_key = "unknown"
    if hasattr(source, "get_provider_key"):
        provider_key = str(source.get_provider_key() or "unknown")  # type: ignore[call-arg]
    return {
        "provider_key": provider_key,
        "source_mode": "unknown",
    }


class SourceProviderCompatMixin:
    def ensure_auth(self) -> None:
        self.ensure_login()  # type: ignore[attr-defined]

    def walk_tree(self, source_root: str) -> list[SourceEntry]:
        return self.export_tree(source_root)  # type: ignore[attr-defined]

    def download_stream(self, source_path: str, temp_dir: Path) -> Path:
        return self.download_file(source_path, temp_dir)  # type: ignore[attr-defined]

    def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
        return []

    def get_runtime_context(self) -> dict[str, Any]:
        return {}


class OpenListSourceProvider(SourceProviderCompatMixin):
    def __init__(
        self,
        base_url: str,
        token: str = "",
        username: str = "",
        password: str = "",
        page_size: int = 200,
        request_interval_ms: int = 300,
        runtime_context: dict[str, Any] | None = None,
        on_progress: Any | None = None,
    ) -> None:
        self.runtime_context = dict(runtime_context or {})
        self.client = OpenListClient(
            base_url=base_url,
            token=token,
            username=username,
            password=password,
            on_progress=on_progress,
            page_size=page_size,
            request_interval_ms=request_interval_ms,
        )

    def close(self) -> None:
        self.client.close()

    def list_roots(self) -> list[str]:
        source_ensure_auth(self)
        listing = self.client.list_directories("/")
        directories = list(listing.get("directories") or [])
        roots = [str(item.get("path") or "").strip() for item in directories if str(item.get("path") or "").strip()]
        return roots or ["/"]

    def list_dir(self, path: str) -> dict[str, Any]:
        source_ensure_auth(self)
        return self.client.list_directories(path)

    def walk_tree(self, source_root: str) -> list[SourceEntry]:
        source_ensure_auth(self)
        return self.client.export_tree(source_root)

    def walk_leaf_dirs(self, root_path: str) -> Iterable[str]:
        source_ensure_auth(self)
        yield from self.client.iter_leaf_directories(root_path)

    def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
        source_ensure_auth(self)
        return self.client.get_file_fingerprints(path)

    def download_stream(self, source_path: str, temp_dir: Path) -> Path:
        source_ensure_auth(self)
        return self.client.download_file(source_path, temp_dir)

    def get_auth_state(self) -> dict[str, str]:
        return {
            "base_url": self.client.base_url,
            "token": self.client.token,
            "username": self.client.username,
        }

    def get_provider_key(self) -> str:
        return "openlist"

    def get_runtime_context(self) -> dict[str, Any]:
        return dict(self.runtime_context)


def create_source_provider(
    config: AppConfig,
    state: SyncState | None = None,
    *,
    on_progress: Any | None = None,
) -> SourceProvider:
    _ = state
    runtime_context = build_source_runtime_status(config)
    return OpenListSourceProvider(
        base_url=config.openlist_url,
        token=config.openlist_token,
        username=config.openlist_username,
        password=config.openlist_password,
        page_size=config.openlist_page_size,
        request_interval_ms=config.openlist_request_interval_ms,
        runtime_context=runtime_context,
        on_progress=on_progress,
    )
