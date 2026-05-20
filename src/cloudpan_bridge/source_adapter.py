from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Protocol

from .config import AppConfig
from .models import SourceEntry, SyncState
from .openlist import OpenListClient
from .provider_registry_data import TARGET_PROFILES
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
    target_capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preference = str(config.source_provider_preference or "auto").strip().lower() or "auto"
    if preference not in {"auto", "openlist_only", "direct_preferred"}:
        preference = "auto"
    provider_key = str(context.get("provider_key") or "")
    direct_candidate = bool(context.get("provider_key") not in {"", "generic_openlist_driver", "openlist"})
    source_enrichment = build_source_enrichment_runtime(config, provider_key)
    bridge_runtime = dict(source_enrichment.get("bridge_runtime") or {})
    bridge_preparation = dict(bridge_runtime.get("preparation") or {})
    bridge_status = str(bridge_runtime.get("status") or "")
    direct_provider_ready = bool(
        direct_candidate
        and source_enrichment.get("supported")
        and bridge_status in {"bridge_ready", "bridge_ready_but_normalization_only"}
    )
    direct_provider_api_pending = bool(
        direct_candidate
        and source_enrichment.get("supported")
        and bridge_status == "bridge_ready_but_api_pending"
    )
    direct_provider_capture_missing = bool(
        direct_candidate
        and source_enrichment.get("supported")
        and bridge_status == "bridge_capture_missing"
    )
    selected_source_mode = "openlist_mount"
    selected_provider_key = "openlist"
    fallback_reason = ""
    selection_reason = "默认使用 OpenList 挂载源执行。"
    if preference == "openlist_only":
        selection_reason = "已显式指定只使用 OpenList 挂载源。"
    elif preference == "direct_preferred":
        if direct_provider_ready:
            selected_source_mode = "direct_provider_bridge_ready"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前已识别到直连 provider 候选，且会话桥接补指纹已 ready；当前版本仍未接入真实 source provider 传输链路，暂回退 OpenList 执行。"
            selection_reason = "已优先命中可用的会话桥接补指纹路径，但当前版本仍会保守回退到 OpenList。"
        elif direct_provider_api_pending:
            selected_source_mode = "direct_provider_api_pending"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前已识别到 API 型直连 provider 候选，登录态也已满足 bridge 准备条件，但真实 provider API enrich 仍未执行，暂回退 OpenList。"
            selection_reason = "已配置为优先直连 source provider，但当前只到 API bridge 准备态，还不能视为真正 ready。"
        elif direct_provider_capture_missing:
            selected_source_mode = "direct_provider_capture_missing"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前已识别到直连 provider 候选，但仍缺关键登录态字段，暂回退 OpenList 执行。"
            selection_reason = "已配置为优先直连 source provider，但当前尚未满足 bridge capture 条件。"
        elif direct_candidate:
            selected_source_mode = "direct_provider_unclassified"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前已识别到直连 provider 候选，但 bridge 运行态尚未达到可执行级别，暂回退 OpenList 执行。"
            selection_reason = "已配置为优先直连 source provider，但当前桥接状态仍需继续细化。"
    elif preference == "auto":
        if direct_provider_ready:
            selected_source_mode = "openlist_with_bridge_ready_candidate"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前 source provider 的会话桥接补指纹已 ready，但尚未接入真实直连传输实现，先保守走 OpenList。"
            selection_reason = "自动模式已检测到可用会话桥接补指纹候选，后续可继续提升到真实直连执行。"
        elif direct_provider_api_pending:
            selected_source_mode = "openlist_with_api_bridge_candidate"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前 source provider 已到 API bridge 准备态，但真实 provider API enrich 仍未执行，先保守走 OpenList。"
            selection_reason = "自动模式已检测到 API 型直连候选，但当前还不能把它当成真正 ready 的直连执行链路。"
        elif direct_provider_capture_missing:
            selected_source_mode = "openlist_with_capture_gap_candidate"
            selected_provider_key = provider_key or "openlist"
            fallback_reason = "当前 source provider 有直连候选，但关键登录态字段仍不完整，先保守走 OpenList。"
            selection_reason = "自动模式已识别出主流 provider 候选，但当前仍缺少 bridge capture。"
    source_target_route = build_source_target_route_summary(
        context,
        source_enrichment,
        target_key=str(config.target_key or "guangya"),
        resolution={
            "selected_source_mode": selected_source_mode,
            "selected_provider_key": selected_provider_key,
            "direct_provider_candidate": direct_candidate,
            "direct_provider_ready": direct_provider_ready,
            "direct_provider_api_pending": direct_provider_api_pending,
            "direct_provider_capture_missing": direct_provider_capture_missing,
        },
        target_capability=target_capability,
    )
    return {
        "requested_provider_preference": preference,
        "selected_source_mode": selected_source_mode,
        "selected_provider_key": selected_provider_key,
        "direct_provider_candidate": direct_candidate,
        "direct_provider_ready": direct_provider_ready,
        "direct_provider_api_pending": direct_provider_api_pending,
        "direct_provider_capture_missing": direct_provider_capture_missing,
        "source_enrichment": source_enrichment,
        "bridge_preparation": bridge_preparation,
        "fallback_reason": fallback_reason,
        "selection_reason": selection_reason,
        "source_target_route": source_target_route,
    }


def _normalize_hash_list(values: list[Any] | None = None) -> list[str]:
    return [str(item or "").strip().lower() for item in list(values or []) if str(item or "").strip()]


def build_source_target_route_summary(
    context: dict[str, Any],
    source_enrichment: dict[str, Any],
    *,
    target_key: str,
    resolution: dict[str, Any] | None = None,
    target_capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_target = str(target_key or "guangya").strip().lower() or "guangya"
    target_profile = dict(TARGET_PROFILES.get(normalized_target, {}) or {})
    capability = {**target_profile, **dict(target_capability or {})}
    target_fast_hashes = _normalize_hash_list(capability.get("fast_upload_hashes") or capability.get("fastUploadHashes"))
    target_fallback_modes = _normalize_hash_list(capability.get("fallback_modes") or capability.get("fallbackModes"))
    bridge_preparation = dict(source_enrichment.get("bridge_preparation_summary") or {})
    bridge_status = str(source_enrichment.get("bridge_status") or "")
    preferred_hashes = _normalize_hash_list(source_enrichment.get("preferred_hashes") or bridge_preparation.get("preferred_hashes"))
    expected_hashes = _normalize_hash_list(bridge_preparation.get("fingerprint_expectation"))
    native_fast_candidate_hashes = [key for key in target_fast_hashes if key in preferred_hashes]
    bridge_recoverable_fast_hashes = [key for key in target_fast_hashes if key in expected_hashes]
    resolution = dict(resolution or {})
    direct_candidate = bool(resolution.get("direct_provider_candidate")) or bool(source_enrichment.get("supported"))
    direct_ready = bool(resolution.get("direct_provider_ready")) or bridge_status in {"bridge_ready", "bridge_ready_but_normalization_only"}
    api_pending = bool(resolution.get("direct_provider_api_pending")) or bridge_status == "bridge_ready_but_api_pending"
    capture_missing = bool(resolution.get("direct_provider_capture_missing")) or bridge_status == "bridge_capture_missing"
    decision_bucket = "openlist_upload_path"
    next_focus = "openlist_first"
    route_honesty = "openlist_only_for_now"
    preferred_execution_mode = "stream_upload"
    fallback_execution_mode = target_fallback_modes[0] if target_fallback_modes else "record_pending_only"
    summary = "当前默认通过 OpenList 源端执行，再按目标端能力决定快传或普通上传。"
    if not target_fast_hashes:
        decision_bucket = "target_upload_only"
        next_focus = "target_fallback_upload"
        route_honesty = "target_has_no_metadata_fast_upload"
        preferred_execution_mode = target_fallback_modes[0] if target_fallback_modes else "stream_upload"
        summary = "当前目标端没有元数据秒传能力，这个源端组合会稳定落到普通上传/覆盖或补传路径。"
    elif direct_ready and bridge_recoverable_fast_hashes:
        decision_bucket = "session_bridge_fast_candidate"
        next_focus = "validate_fast_hash_hit_rate"
        route_honesty = "session_bridge_ready_but_transport_not_direct"
        preferred_execution_mode = "fast_upload"
        fallback_execution_mode = target_fallback_modes[0] if target_fallback_modes else "record_pending_only"
        summary = (
            "当前源端会话桥接已 ready，且理论上能补到目标端所需的快传哈希；"
            f"优先关注 {', '.join(bridge_recoverable_fast_hashes)} 的命中率。"
        )
    elif api_pending and bridge_recoverable_fast_hashes:
        decision_bucket = "api_bridge_fast_candidate"
        next_focus = "provider_api_enrich"
        route_honesty = "provider_api_not_implemented_yet"
        preferred_execution_mode = "record_pending_only"
        summary = (
            "当前源端已进入 API bridge 准备态，但真实 enrich 还没落地；"
            f"理论上最值得补齐的是 {', '.join(bridge_recoverable_fast_hashes)}。"
        )
    elif capture_missing and bridge_recoverable_fast_hashes:
        decision_bucket = "capture_gap_before_fast"
        next_focus = "collect_provider_capture"
        route_honesty = "capture_missing_before_fast_upload"
        preferred_execution_mode = "record_pending_only"
        summary = (
            "当前源端理论上可以补到目标端快传哈希，但还缺关键登录态；"
            f"优先补齐 capture 后再验证 {', '.join(bridge_recoverable_fast_hashes)}。"
        )
    elif direct_candidate and native_fast_candidate_hashes:
        decision_bucket = "native_hash_candidate"
        next_focus = "inspect_openlist_hash_coverage"
        route_honesty = "openlist_metadata_may_already_be_enough"
        preferred_execution_mode = "fast_upload"
        summary = (
            "当前源端档案本身就偏向目标端认可的快传哈希，先检查 OpenList 当前目录是否已经暴露"
            f" {', '.join(native_fast_candidate_hashes)}。"
        )
    elif direct_candidate:
        decision_bucket = "provider_candidate_but_fallback_first"
        next_focus = "pending_tree_or_stream_upload"
        route_honesty = "provider_overlap_weak"
        preferred_execution_mode = "record_pending_only" if "download_upload" in target_fallback_modes else (target_fallback_modes[0] if target_fallback_modes else "stream_upload")
        summary = "当前源端虽然已有主流 provider 候选，但和目标端快传哈希重叠不强，建议优先保守补传。"
    return {
        "source_driver": str(context.get("effective_driver") or context.get("driver") or ""),
        "source_provider_key": str(source_enrichment.get("provider_key") or context.get("provider_key") or ""),
        "target_key": normalized_target,
        "target_fast_hashes": target_fast_hashes,
        "target_fallback_modes": target_fallback_modes,
        "preferred_hashes": preferred_hashes,
        "expected_hashes": expected_hashes,
        "native_fast_candidate_hashes": native_fast_candidate_hashes,
        "bridge_recoverable_fast_hashes": bridge_recoverable_fast_hashes,
        "decision_bucket": decision_bucket,
        "next_focus": next_focus,
        "route_honesty": route_honesty,
        "preferred_execution_mode": preferred_execution_mode,
        "fallback_execution_mode": fallback_execution_mode,
        "summary": summary,
        "selected_source_mode": str(resolution.get("selected_source_mode") or ""),
        "selected_provider_key": str(resolution.get("selected_provider_key") or ""),
    }


def build_source_runtime_status(
    config: AppConfig,
    *,
    source_path: str = "",
    mount_path: str = "",
    requested_driver: str = "",
    target_capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = build_source_provider_context(
        config,
        source_path=source_path,
        mount_path=mount_path,
        requested_driver=requested_driver,
    )
    resolution = build_source_provider_resolution(config, context, target_capability=target_capability)
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
