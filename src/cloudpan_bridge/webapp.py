from __future__ import annotations

from dataclasses import asdict
import json
import secrets
import time
from pathlib import Path, PurePosixPath
from threading import Lock, Thread
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

from .config import AppConfig, write_example_config
from .guangya_direct import GuangyaMiaochuanImporter, normalize_guangya_authorization
from .logs import AppLogger
from .models import normalize_posix_path
from .openlist_admin import OpenListAdminClient, build_storage_payload
from .openlist import OpenListClient
from .openlist_runtime import ManagedOpenListRuntime
from .provider_capture import (
    ProviderCaptureManager,
    build_driver_capture_spec,
    build_driver_prefill_values,
    normalize_provider_capture_entry,
)
from .provider_registry import (
    build_driver_coverage_audit,
    build_driver_coverage_scaffold,
    filter_driver_coverage_audit,
    assess_driver_target_capability,
    build_source_mapping_context as build_registry_source_mapping_context,
    build_driver_capability_matrix,
    build_driver_target_capability,
    get_driver_guide,
    get_source_profile_by_key_or_alias,
    list_driver_guides,
    list_source_profiles,
    list_target_profiles,
    render_driver_coverage_audit_markdown,
    render_driver_coverage_scaffold_markdown,
)
from .source_adapter import build_source_provider_context, build_source_runtime_status
from .fast_upload_decision import assess_directory_fast_upload
from .target_adapter import build_target_preflight_capability, supported_target_keys
from .syncer import (
    SyncRunner,
    build_source_miaochuan_payload,
    load_state,
    save_state,
    serialize_source_entry,
    summarize_source_entries,
)
from .web_runtime_utils import (
    build_pending_selected_execution_groups,
    compute_rate_limit_cooldown_ms,
    is_rate_limit_error_message,
)


def create_app(config_path: Path) -> FastAPI:
    config_path = config_path.resolve()
    if not config_path.exists():
        write_example_config(config_path)
    config = AppConfig.load(config_path)
    config.ensure_parent_dirs()
    logger = AppLogger(config.log_file)
    provider_capture = ProviderCaptureManager(config.state_file.parent / "browser-sessions")
    sync_state: dict[str, Any] = {
        "running": False,
        "last_summary": None,
        "last_error": "",
        "pending_downloads": [],
        "directory_browser": None,
        "current_task": {},
        "current_source_context": {},
        "persistent_pending": [],
        "persistent_pending_groups": [],
        "source_queue": [],
        "queue_runner": {"running": False, "current_source": "", "remaining": 0},
    }
    sync_lock = Lock()
    runtime = ManagedOpenListRuntime(
        mode=config.openlist_mode,
        configured_url=config.openlist_url,
        data_dir=config.managed_openlist_data_dir,
        binary_path=config.managed_openlist_bin,
        port=config.managed_openlist_port,
        init_admin_username=config.managed_openlist_init_username,
        init_admin_password=config.managed_openlist_init_password,
        docker_image=config.managed_openlist_docker_image,
        docker_container_name=config.managed_openlist_docker_container_name,
    )
    auth_cookie_name = "cpb_session"
    auth_sessions: set[str] = set()

    app = FastAPI(title="CloudPan Bridge Sync Console")

    def admin_auth_enabled() -> bool:
        return bool(str(config.app_admin_username or "").strip() and str(config.app_admin_password or "").strip())

    def get_authenticated_username(request: Request) -> str:
        if not admin_auth_enabled():
            return ""
        session_token = str(request.cookies.get(auth_cookie_name) or "").strip()
        if not session_token or session_token not in auth_sessions:
            return ""
        return str(config.app_admin_username or "").strip()

    @app.middleware("http")
    async def require_console_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        path = request.url.path
        if (
            admin_auth_enabled()
            and path.startswith("/api/")
            and path not in {"/api/auth/login", "/api/auth/status"}
            and not get_authenticated_username(request)
        ):
            return JSONResponse(status_code=401, content={"detail": "请先登录控制台。"})
        return await call_next(request)

    def is_guangya_auth_error(message: str) -> bool:
        text = (message or "").lower()
        return "401 unauthorized" in text or "get_file_list" in text and "401" in text

    def refresh_runtime() -> ManagedOpenListRuntime:
        nonlocal runtime, config
        runtime.mode = config.openlist_mode
        runtime.configured_url = config.openlist_url.rstrip("/")
        runtime.data_dir = config.managed_openlist_data_dir
        runtime.binary_path = config.managed_openlist_bin
        runtime.port = config.managed_openlist_port
        runtime.init_admin_username = str(config.managed_openlist_init_username or "admin").strip() or "admin"
        runtime.init_admin_password = str(config.managed_openlist_init_password or "")
        runtime.docker_image = str(config.managed_openlist_docker_image or "openlistteam/openlist:latest").strip() or "openlistteam/openlist:latest"
        runtime.docker_container_name = str(config.managed_openlist_docker_container_name or "cloudpan-bridge-openlist").strip() or "cloudpan-bridge-openlist"
        runtime.data_dir.mkdir(parents=True, exist_ok=True)
        return runtime

    def effective_openlist_url() -> str:
        current_runtime = refresh_runtime()
        if AppConfig.is_managed_openlist_mode(config.openlist_mode):
            return current_runtime.active_url()
        return config.openlist_url.rstrip("/")

    def ensure_runtime_ready() -> None:
        current_runtime = refresh_runtime()
        if AppConfig.is_managed_openlist_mode(config.openlist_mode):
            status = current_runtime.start()
            if not status.running:
                raise RuntimeError(status.message or "Managed OpenList 启动失败")

    def build_openlist_client(
        *,
        openlist_url: str | None = None,
        openlist_username: str | None = None,
        openlist_password: str | None = None,
        openlist_token: str | None = None,
        on_progress: Any | None = None,
        page_size: int | None = None,
        request_interval_ms: int | None = None,
    ) -> OpenListClient:
        ensure_runtime_ready()
        return OpenListClient(
            base_url=str(openlist_url or effective_openlist_url()),
            token=str(openlist_token if openlist_token is not None else config.openlist_token),
            username=str(openlist_username if openlist_username is not None else config.openlist_username),
            password=str(openlist_password if openlist_password is not None else config.openlist_password),
            on_progress=on_progress,
            page_size=page_size if page_size is not None else config.openlist_page_size,
            request_interval_ms=(
                request_interval_ms if request_interval_ms is not None else config.openlist_request_interval_ms
            ),
        )

    def build_admin_client(token: str | None = None) -> OpenListAdminClient:
        ensure_runtime_ready()
        return OpenListAdminClient(
            base_url=effective_openlist_url(),
            token=str(token if token is not None else config.openlist_token),
        )

    def build_target_preflight(target_key: str = "") -> dict[str, Any]:
        normalized = str(target_key or config.target_key or "guangya").strip().lower() or "guangya"
        target_profiles = list_target_profiles()
        implemented_targets = supported_target_keys()
        known_profile = normalized in target_profiles
        implemented = normalized in implemented_targets
        selectable = known_profile and implemented
        state = load_state(config.state_file)
        adapter_capability = build_target_preflight_capability(config, state, normalized)
        if selectable:
            if adapter_capability.get("configured"):
                message = "当前目标端已实现且已补齐基础配置，可继续执行同步任务。"
            else:
                missing_text = ", ".join(list(adapter_capability.get("missing_fields") or [])) or "配置项"
                message = f"当前目标端已实现，但仍缺少配置：{missing_text}"
        elif known_profile:
            message = f"目标端 {normalized} 目前只有档案定义，还没有实现可写入适配器。"
        else:
            message = f"目标端 {normalized} 当前既没有内置档案，也没有实现可写入适配器。"
        return {
            "target_key": normalized,
            "known_profile": known_profile,
            "implemented": implemented,
            "selectable": selectable,
            "configured": bool(adapter_capability.get("configured")) if implemented else False,
            "missing_fields": list(adapter_capability.get("missing_fields") or []),
            "adapter_capability": adapter_capability,
            "message": message,
        }

    def require_selectable_target(target_key: str = "") -> dict[str, Any]:
        preflight = build_target_preflight(target_key)
        if not preflight["selectable"]:
            raise HTTPException(status_code=400, detail=preflight["message"])
        return preflight

    def require_miaochuan_target(target_key: str = "") -> str:
        normalized = str(target_key or config.target_key or "guangya").strip().lower() or "guangya"
        if normalized != "guangya":
            raise HTTPException(status_code=400, detail=f"当前秒传 JSON 直导仅支持 guangya，目标端 {normalized} 暂不支持此入口。")
        require_selectable_target(normalized)
        return normalized

    def deep_merge_dicts(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base)
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                if not value:
                    merged[key] = {}
                    continue
                merged[key] = deep_merge_dicts(dict(merged.get(key) or {}), value)
            else:
                merged[key] = value
        return merged

    def payload_nested_get(payload: dict[str, Any] | None, path: tuple[str, ...], default: Any = "") -> Any:
        current: Any = payload or {}
        for key in path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def payload_nested_set(payload: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
        current: dict[str, Any] = payload
        for key in path[:-1]:
            existing = current.get(key)
            if not isinstance(existing, dict):
                existing = {}
                current[key] = existing
            current = existing
        current[path[-1]] = value

    def save_grouped_config_updates(updates: dict[tuple[str, ...], Any]) -> bool:
        grouped_patch: dict[str, Any] = {}
        changed = False
        current_grouped = load_grouped_config_payload()
        for path, value in updates.items():
            if payload_nested_get(current_grouped, path, None) == value:
                continue
            payload_nested_set(grouped_patch, path, value)
            changed = True
        if changed:
            save_config_payload({"grouped_config": grouped_patch})
        return changed

    def retain_explicit_grouped_updates(updates: dict[tuple[str, ...], Any]) -> dict[tuple[str, ...], Any]:
        return {
            path: value
            for path, value in updates.items()
            if value is not None
        }

    def resolve_payload_value(
        payload: dict[str, Any] | None,
        flat_key: str,
        grouped_path: tuple[str, ...] | None = None,
        default: Any = "",
    ) -> Any:
        raw = payload or {}
        flat_value = raw.get(flat_key)
        if flat_value not in ("", None):
            return flat_value
        if grouped_path:
            grouped_value = payload_nested_get(raw.get("grouped_config") if isinstance(raw.get("grouped_config"), dict) else {}, grouped_path, None)
            if grouped_value not in ("", None):
                return grouped_value
        return default

    def normalize_sync_payload(payload: dict[str, Any] | None, runtime_config: AppConfig) -> dict[str, Any]:
        raw = dict(payload or {})
        normalized = dict(raw)
        normalized["source_path"] = str(
            resolve_payload_value(raw, "source_path", ("sync", "source_path"), runtime_config.source_path or "/")
        )
        normalized["source_root_for_target"] = str(
            resolve_payload_value(raw, "source_root_for_target", default=normalized["source_path"])
        )
        normalized["target_key"] = str(
            resolve_payload_value(raw, "target_key", ("targets", "active_target"), runtime_config.target_key or "guangya")
        )
        normalized["guangya_authorization"] = str(
            resolve_payload_value(
                raw,
                "guangya_authorization",
                ("targets", "guangya", "authorization"),
                runtime_config.guangya_authorization or "",
            )
        )
        normalized["miaochuan_payload"] = str(resolve_payload_value(raw, "miaochuan_payload", default=raw.get("miaochuan_payload") or ""))
        selected_paths = resolve_payload_value(raw, "selected_paths", ("sync", "selected_paths"), raw.get("selected_paths") or [])
        normalized["selected_paths"] = [
            normalize_posix_path(path)
            for path in list(selected_paths or [])
            if str(path).strip()
        ]
        return normalized

    def normalize_registry_payload(payload: dict[str, Any] | None, runtime_config: AppConfig) -> dict[str, Any]:
        raw = dict(payload or {})
        normalized = dict(raw)
        normalized["target"] = str(resolve_payload_value(raw, "target", ("targets", "active_target"), runtime_config.target_key or "guangya"))
        normalized["only_gaps"] = bool(resolve_payload_value(raw, "only_gaps", ("ui", "coverage_filters", "onlyGaps"), raw.get("only_gaps") or False))
        normalized["only_onboarding_ready"] = bool(resolve_payload_value(raw, "only_onboarding_ready", ("ui", "coverage_filters", "onlyOnboardingReady"), raw.get("only_onboarding_ready") or False))
        normalized["next_action"] = str(resolve_payload_value(raw, "next_action", ("ui", "coverage_filters", "nextAction"), raw.get("next_action") or ""))
        normalized["missing_item"] = str(resolve_payload_value(raw, "missing_item", ("ui", "coverage_filters", "missingItem"), raw.get("missing_item") or ""))
        normalized["capability_level"] = str(resolve_payload_value(raw, "capability_level", ("ui", "coverage_filters", "capabilityLevel"), raw.get("capability_level") or ""))
        normalized["profile_key"] = str(resolve_payload_value(raw, "profile_key", ("ui", "coverage_filters", "profileKey"), raw.get("profile_key") or ""))
        normalized["onboarding_stage"] = str(resolve_payload_value(raw, "onboarding_stage", ("ui", "coverage_filters", "onboardingStage"), raw.get("onboarding_stage") or ""))
        return normalized

    def build_registry_filter_kwargs(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "only_gaps": bool(payload.get("only_gaps")),
            "only_onboarding_ready": bool(payload.get("only_onboarding_ready")),
            "next_action": str(payload.get("next_action") or ""),
            "missing_item": str(payload.get("missing_item") or ""),
            "capability_level": str(payload.get("capability_level") or ""),
            "profile_key": str(payload.get("profile_key") or ""),
            "onboarding_stage": str(payload.get("onboarding_stage") or ""),
        }

    def normalize_capability_payload(payload: dict[str, Any] | None, runtime_config: AppConfig) -> dict[str, Any]:
        raw = normalize_registry_payload(payload, runtime_config)
        mapping_context = resolve_source_mapping_context(raw, runtime_config)
        raw["mount_path"] = mapping_context["mount_path"]
        raw["source_profile_override"] = mapping_context["source_profile_override"]
        raw["requested_driver"] = mapping_context["requested_driver"]
        raw["driver"] = mapping_context["effective_driver"]
        analysis_summary = raw.get("analysis_summary")
        raw["analysis_summary"] = analysis_summary if isinstance(analysis_summary, dict) else {}
        return raw

    def resolve_source_mapping_context(payload: dict[str, Any] | None, runtime_config: AppConfig) -> dict[str, Any]:
        raw = dict(payload or {})
        source_path = str(resolve_payload_value(raw, "source_path", ("sync", "source_path"), default="")).strip()
        mount_path = str(resolve_payload_value(raw, "mount_path", ("ui", "browser", "mounted_source"), default="")).strip()
        requested_driver = str(resolve_payload_value(raw, "driver", default="")).strip()
        return build_source_provider_context(
            runtime_config,
            source_path=source_path,
            mount_path=mount_path,
            requested_driver=requested_driver,
        )

    def build_current_task_snapshot(
        mode: str,
        runtime_config: AppConfig,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raw = dict(payload or {})
        source_path = normalize_posix_path(str(raw.get("source_path") or runtime_config.source_path or "/"))
        source_root_for_target = normalize_posix_path(
            str(raw.get("source_root_for_target") or source_path or runtime_config.source_path or "/")
        )
        target_key = str(raw.get("target_key") or runtime_config.target_key or "guangya").strip().lower() or "guangya"
        target_path = normalize_posix_path(str(raw.get("target_path") or runtime_config.target_path or "/"))
        mapping_context = resolve_source_mapping_context(
            {
                "source_path": source_path,
                "mount_path": raw.get("mount_path") or payload_nested_get(load_grouped_config_payload(), ("ui", "browser", "mounted_source"), ""),
                "driver": str(raw.get("driver") or ""),
            },
            runtime_config,
        )
        return {
            "mode": mode,
            "source_path": source_path,
            "source_root_for_target": source_root_for_target,
            "target_key": target_key,
            "target_path": target_path,
            "selected_paths_count": len(list(raw.get("selected_paths") or [])),
            "source_mapping_context": mapping_context,
        }

    def normalize_provider_capture_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
        raw = dict(payload or {})
        normalized = dict(raw)
        normalized["provider"] = str(
            resolve_payload_value(raw, "provider", ("ui", "provider_capture", "provider"), default="")
        ).strip().lower()
        normalized["driver"] = str(
            resolve_payload_value(raw, "driver", ("ui", "provider_capture", "driver"), default="")
        ).strip()
        normalized["login_url"] = str(
            resolve_payload_value(raw, "login_url", ("ui", "provider_capture", "login_url"), default="")
        ).strip()
        return normalized

    def normalize_storage_create_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
        raw = dict(payload or {})
        normalized = dict(raw)
        normalized["driver"] = str(
            resolve_payload_value(raw, "driver", ("ui", "storage_create", "driver"), default="")
        ).strip()
        grouped_values = payload_nested_get(
            raw.get("grouped_config") if isinstance(raw.get("grouped_config"), dict) else {},
            ("ui", "storage_create", "values"),
            {},
        )
        values = raw.get("values")
        normalized["values"] = dict(values or grouped_values or {})
        return normalized

    def normalize_queue_payload(payload: dict[str, Any] | None, runtime_config: AppConfig) -> dict[str, Any]:
        raw = dict(payload or {})
        normalized = dict(raw)
        normalized["source_path"] = str(
            resolve_payload_value(raw, "source_path", ("sync", "source_path"), runtime_config.source_path or "")
        )
        return normalized

    def resolve_registry_drivers(payload: dict[str, Any]) -> list[str]:
        drivers = payload.get("drivers")
        if isinstance(drivers, list):
            normalized = [str(item or "").strip() for item in drivers if str(item or "").strip()]
            if normalized:
                return normalized
        with build_admin_client() as client:
            live_drivers = [str(item or "").strip() for item in client.driver_names() if str(item or "").strip()]
        if live_drivers:
            return live_drivers
        raise HTTPException(status_code=400, detail="缺少 drivers，且当前 OpenList 也没有返回可审计的驱动列表")

    def build_live_driver_fields_map(drivers: list[str]) -> dict[str, list[Any]]:
        result: dict[str, list[Any]] = {}
        if not drivers:
            return result
        try:
            with build_admin_client() as client:
                for driver in drivers:
                    try:
                        info = client.driver_info(driver)
                    except Exception:
                        continue
                    fields = [*list(info.common or []), *list(info.additional or [])]
                    normalized = "".join(ch.lower() for ch in str(driver or "") if ch.isalnum())
                    if normalized and fields:
                        result[normalized] = fields
        except Exception:
            return {}
        return result

    def load_config_payload() -> dict[str, Any]:
        normalized = AppConfig.load(config_path)
        payload = normalized.to_flat_dict()
        if config_path.exists():
            raw_payload = json.loads(config_path.read_text(encoding="utf-8"))
            for key in ("openlist_password", "guangya_authorization", "guangya_access_token", "guangya_refresh_token", "guangya_device_id", "openlist_token"):
                if key in raw_payload:
                    payload[key] = raw_payload.get(key, payload.get(key, ""))
        return payload

    def load_grouped_config_payload() -> dict[str, Any]:
        normalized_model = AppConfig.load(config_path)
        normalized = normalized_model.to_dict()
        if not config_path.exists():
            return normalized
        raw_payload = json.loads(config_path.read_text(encoding="utf-8"))
        flat_keys = set(normalized_model.to_flat_dict().keys()) | {"grouped_config", "config_meta", "effective_openlist_url"}
        grouped_explicit = dict(raw_payload.get("grouped_config", {}) or {}) if isinstance(raw_payload.get("grouped_config"), dict) else {}
        raw_grouped = {
            key: value
            for key, value in raw_payload.items()
            if key not in flat_keys
        }
        if grouped_explicit:
            raw_grouped = deep_merge_dicts(raw_grouped, grouped_explicit)
        return deep_merge_dicts(normalized, raw_grouped)

    def save_config_payload(payload: dict[str, Any]) -> None:
        grouped_patch = dict(payload.get("grouped_config", {}) or {}) if isinstance(payload.get("grouped_config"), dict) else {}
        current_grouped = load_grouped_config_payload()
        if grouped_patch:
            current_grouped = deep_merge_dicts(current_grouped, grouped_patch)
        merged = AppConfig.from_payload(current_grouped).to_flat_dict()
        merged.update(
            {
                key: value
                for key, value in payload.items()
                if key not in {"grouped_config", "config_meta", "effective_openlist_url"}
            }
        )
        normalized = AppConfig.from_payload(merged)
        final_payload = deep_merge_dicts(current_grouped, normalized.to_dict())
        config_path.write_text(json.dumps(final_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def merged_provider_capture_snapshots() -> dict[str, dict[str, Any]]:
        payload = load_config_payload()
        stored = {
            str(provider): normalize_provider_capture_entry(str(provider), value)
            for provider, value in dict(payload.get("provider_captures", {}) or {}).items()
        }
        live = {
            str(provider): normalize_provider_capture_entry(str(provider), snapshot)
            for provider, snapshot in provider_capture.snapshots().items()
        }
        merged = dict(stored)
        for provider, snapshot in live.items():
            live_captured = dict(snapshot.get("captured") or {})
            if live_captured:
                merged[provider] = snapshot
            elif provider not in merged:
                merged[provider] = snapshot
        return merged

    def persist_guangya_tokens_to_config() -> None:
        nonlocal config
        state = load_state(config.state_file)
        tokens = state.get_target_state("guangya")
        if not tokens:
            return
        updates = {
            ("targets", "guangya", "access_token"): str(tokens.get("access_token", "")),
            ("targets", "guangya", "refresh_token"): str(tokens.get("refresh_token", "")),
            ("targets", "guangya", "device_id"): str(tokens.get("device_id", "")),
        }
        changed = save_grouped_config_updates(retain_explicit_grouped_updates(updates))
        if changed:
            config = AppConfig.load(config_path)
            logger.info("光鸭 token/device_id 已自动写回配置")

    def persist_guangya_capture_to_config() -> None:
        nonlocal config
        snapshot = provider_capture.snapshot("guangya")
        captured = snapshot.get("captured") if isinstance(snapshot, dict) else {}
        if not isinstance(captured, dict):
            return
        authorization = normalize_guangya_authorization(str(captured.get("authorization") or ""))
        access_token = str(captured.get("access_token") or "")
        refresh_token = str(captured.get("refresh_token") or "")
        device_id = str(captured.get("x-device-id") or captured.get("did") or captured.get("device_id") or "")
        if not any([authorization, access_token, refresh_token, device_id]):
            return
        updates = {
            ("targets", "guangya", "authorization"): authorization,
            ("targets", "guangya", "access_token"): access_token,
            ("targets", "guangya", "refresh_token"): refresh_token,
            ("targets", "guangya", "device_id"): device_id,
        }
        changed = save_grouped_config_updates(retain_explicit_grouped_updates(updates))
        if changed:
            config = AppConfig.load(config_path)
            logger.info("光鸭 Authorization/token/device_id 已自动写回配置")

    def persist_provider_captures_to_config() -> None:
        nonlocal config
        snapshots = merged_provider_capture_snapshots()
        current_grouped = load_grouped_config_payload()
        existing = dict(payload_nested_get(current_grouped, ("source_session", "provider_captures"), {}) or {})
        changed = False
        for provider, snapshot in snapshots.items():
            captured = snapshot.get("captured") if isinstance(snapshot, dict) else {}
            if not isinstance(captured, dict) or not captured:
                continue
            normalized_snapshot = {
                "provider": provider,
                "status": str(snapshot.get("status") or ""),
                "message": str(snapshot.get("message") or ""),
                "captured": captured,
            }
            if existing.get(provider) != normalized_snapshot:
                existing[provider] = normalized_snapshot
                changed = True
        if changed:
            save_grouped_config_updates({
                ("source_session", "provider_captures"): existing,
            })
            config = AppConfig.load(config_path)

    def build_provider_prefill(provider: str, driver: str) -> dict[str, Any]:
        normalized_provider = str(provider or "").strip().lower()
        normalized_driver = str(driver or "").strip()
        if not normalized_provider:
            raise HTTPException(status_code=400, detail="缺少 provider")
        if not normalized_driver:
            raise HTTPException(status_code=400, detail="缺少 driver")
        with build_admin_client() as client:
            info = client.driver_info(normalized_driver)
        snapshots = merged_provider_capture_snapshots()
        snapshot = snapshots.get(normalized_provider) or normalize_provider_capture_entry(normalized_provider, {})
        captured = dict(snapshot.get("captured") or {})
        fields = [*info.common, *info.additional]
        values = build_driver_prefill_values(fields, captured, normalized_provider)
        missing_required = [
            field.name
            for field in fields
            if field.required and field.name not in values
        ]
        return {
            "provider": normalized_provider,
            "driver": normalized_driver,
            "capture": snapshot,
            "values": values,
            "missing_required": missing_required,
            "matched_fields": sorted(values.keys()),
        }

    def build_provider_capture_definition_payload() -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for item in provider_capture.definitions_payload():
            profile = get_source_profile_by_key_or_alias(str(item.get("key") or ""))
            candidates = [
                *(item.get("recommended_drivers") or []),
                *(profile.get("driverAliases") or []),
                profile.get("key") or "",
                item.get("key") or "",
            ]
            guide = None
            for candidate in candidates:
                guide = get_driver_guide(str(candidate or ""))
                if guide:
                    break
            provider_key = str(profile.get("key") or item.get("key") or "")
            auth_mode = str(profile.get("loginMode") or "")
            default_mount_values = dict(profile.get("defaultMountValues") or {})
            guide_defaults = dict((guide or {}).get("defaults") or {})
            recommended_defaults = {
                **default_mount_values,
                **guide_defaults,
            }
            required_keys = list(item.get("required_keys") or [])
            header_aliases = list(item.get("header_aliases") or [])
            storage_aliases = list(item.get("storage_aliases") or [])
            capture_mode = str(item.get("capture_mode") or "browser").lower() or "browser"
            direct_api_supported = bool(
                provider_key
                and provider_key != "generic"
                and (
                    bool(profile.get("supportsFingerprintEnrichment"))
                    or required_keys
                    or capture_mode in {"browser", "manual"}
                )
            )
            items.append(
                {
                    **item,
                    "provider_key": provider_key,
                    "auth_mode": auth_mode,
                    "source_profile": profile,
                    "guide": guide,
                    "auth_interface": {
                        "auth_mode": auth_mode,
                        "browser_capture": {
                            "supported": capture_mode == "browser",
                            "capture_mode": capture_mode,
                            "login_url": str(item.get("login_url") or ""),
                            "required_keys": required_keys,
                            "header_aliases": header_aliases,
                            "storage_aliases": storage_aliases,
                        },
                        "manual_fields": {
                            "supported": True,
                            "required_keys": required_keys,
                            "header_aliases": header_aliases,
                            "storage_aliases": storage_aliases,
                        },
                        "openlist_mount": {
                            "supported": True,
                            "driver_aliases": list(profile.get("driverAliases") or []),
                            "default_mount_values": default_mount_values,
                        },
                        "direct_api": {
                            "supported": direct_api_supported,
                            "provider_key": provider_key,
                            "supports_fingerprint_enrichment": bool(profile.get("supportsFingerprintEnrichment")),
                            "likely_hashes": list(profile.get("likelyHashes") or []),
                        },
                        "docs": {
                            "doc_url": str((guide or {}).get("docUrl") or ""),
                            "doc_url_candidates": list((guide or {}).get("docUrlCandidates") or []),
                        },
                        "recommended_defaults": {
                            "mount_values": recommended_defaults,
                            "rate_profile": str(profile.get("recommendedRateProfile") or "safe"),
                        },
                    },
                }
            )
        return items

    def current_state_payload() -> dict[str, Any]:
        state = load_state(config.state_file)
        pending_items = [
            item.to_dict()
            for item in sorted(state.pending_files.values(), key=lambda row: (row.source_root, row.path))
        ]
        pending_groups: list[dict[str, Any]] = []
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in pending_items:
            group_path = str(PurePosixPath(item["path"]).parent)
            grouped.setdefault(group_path, []).append(item)
        for group_path in sorted(grouped):
            items = grouped[group_path]
            pending_groups.append(
                {
                    "directory": group_path,
                    "count": len(items),
                    "items": items,
                }
            )
        queue_items = [item.to_dict() for item in state.source_queue]
        return {
            "persistent_pending": pending_items,
            "persistent_pending_groups": pending_groups,
            "source_queue": queue_items,
        }

    def sync_runtime_with_state() -> None:
        snapshot = current_state_payload()
        with sync_lock:
            sync_state["persistent_pending"] = snapshot["persistent_pending"]
            sync_state["persistent_pending_groups"] = snapshot["persistent_pending_groups"]
            sync_state["source_queue"] = snapshot["source_queue"]

    def run_sync_job(mode: str, payload: dict[str, Any] | None = None) -> bool:
        nonlocal config
        config = AppConfig.load(config_path)
        payload = normalize_sync_payload(payload, config)
        active_source = str(payload.get("source_path") or config.source_path)
        source_root_for_target = str(payload.get("source_root_for_target") or active_source)
        selected_paths = list(payload.get("selected_paths") or [])
        guangya_authorization = str(payload.get("guangya_authorization") or "").strip()
        miaochuan_payload = str(payload.get("miaochuan_payload") or "")
        try:
            runtime_task = build_current_task_snapshot(mode, config, payload)
            with sync_lock:
                sync_state["current_task"] = runtime_task
                sync_state["current_source_context"] = dict(runtime_task.get("source_mapping_context") or {})
            if mode in {"dry_run", "direct"} and active_source.strip() == "/":
                raise RuntimeError("当前 source_path 还是 OpenList 根目录 / 。请先进入具体挂载目录，再使用“使用当前目录作为源目录”，或把最底层目录批量入队。")
            logger.info(f"开始同步任务: {mode}")
            if active_source:
                logger.info(f"本次同步源目录: {active_source}")
            run_config = AppConfig.load(config_path)
            if AppConfig.is_managed_openlist_mode(run_config.openlist_mode):
                ensure_runtime_ready()
                run_config.openlist_url = effective_openlist_url()
            run_config.source_path = active_source
            runner = SyncRunner(run_config, log=logger.info, source_root_for_target=source_root_for_target)
            if mode == "dry_run":
                summary = runner.run(
                    allow_download_upload=False,
                    dry_run=True,
                )
            elif mode == "direct":
                summary = runner.run_direct_phase()
            elif mode == "full":
                summary = runner.run(allow_download_upload=True, dry_run=False)
            elif mode == "download_selected":
                summary = runner.run_selected_downloads(selected_paths)
            elif mode == "miaochuan_import":
                authorization = (
                    guangya_authorization
                    or run_config.guangya_authorization
                    or f"Bearer {run_config.guangya_access_token}".strip()
                )
                with GuangyaMiaochuanImporter(authorization) as importer:
                    summary = importer.import_payload(
                        miaochuan_payload,
                        run_config.target_path,
                    )
            else:
                raise RuntimeError(f"unknown mode: {mode}")
            with sync_lock:
                sync_state["last_summary"] = summary.to_dict() if hasattr(summary, "to_dict") else dict(summary)
                sync_state["last_error"] = ""
                if mode == "download_selected":
                    previous = list(sync_state.get("pending_downloads", []))
                    selected = set(selected_paths)
                    failed_selected = set(summary.pending_downloads or [])
                    sync_state["pending_downloads"] = [
                        path for path in previous if path not in selected or path in failed_selected
                    ]
                else:
                    sync_state["pending_downloads"] = list(summary.pending_downloads or [])
            persist_guangya_tokens_to_config()
            sync_runtime_with_state()
            return True
        except Exception as exc:  # noqa: BLE001
            error_message = str(exc)
            if is_guangya_auth_error(error_message):
                error_message = "光鸭登录态已失效或 access_token 无法继续使用，请重新点击“打开光鸭登录并自动抓取”，然后再继续同步。"
            logger.error(f"同步任务失败: {error_message}")
            state = load_state(config.state_file)
            SyncRunner._update_queue_item(
                state,
                active_source,
                last_status="error",
                last_summary={},
                last_error=error_message,
            )
            save_state(config.state_file, state)
            with sync_lock:
                sync_state["last_error"] = error_message
            sync_runtime_with_state()
            return False
        finally:
            with sync_lock:
                sync_state["running"] = False
                sync_state["current_task"] = {}

    def run_queue_job() -> None:
        nonlocal config
        current_source = ""
        try:
            config = AppConfig.load(config_path)
            state = load_state(config.state_file)
            enabled = [item for item in state.source_queue if item.enabled]
            total = len(enabled)
            if not enabled:
                logger.info("目录队列为空，没有可执行目录。")
                return
            for index, next_item in enumerate(enabled, start=1):
                current_source = next_item.source_path
                task_snapshot = build_current_task_snapshot(
                    "direct",
                    config,
                    {
                        "source_path": current_source,
                        "source_root_for_target": next_item.source_root_for_target or current_source,
                    },
                )
                with sync_lock:
                    sync_state["queue_runner"] = {
                        "running": True,
                        "current_source": current_source,
                        "remaining": total - index + 1,
                        "source_mapping_context": dict(task_snapshot.get("source_mapping_context") or {}),
                    }
                    sync_state["current_source_context"] = dict(task_snapshot.get("source_mapping_context") or {})
                logger.info(f"开始执行队列目录 [{index}/{total}]: {current_source}")
                ok = run_sync_job(
                    "direct",
                    {
                        "source_path": current_source,
                        "source_root_for_target": next_item.source_root_for_target or current_source,
                    },
                )
                if not ok and is_guangya_auth_error(str(sync_state.get("last_error") or "")):
                    logger.error("检测到光鸭登录态失效，已停止后续队列执行。请重新抓取光鸭登录信息后再继续。")
                    break
                if not ok and is_rate_limit_error_message(str(sync_state.get("last_error") or "")):
                    cooldown_ms = compute_rate_limit_cooldown_ms(AppConfig.load(config_path), current_source)
                    logger.info(f"检测到疑似风控/限流，自动冷却等待 {cooldown_ms} ms 后继续队列。")
                    time.sleep(cooldown_ms / 1000)
                sync_runtime_with_state()
                delay_ms = max(0, int(AppConfig.load(config_path).queue_interval_ms))
                if delay_ms > 0 and index < total:
                    logger.info(f"队列间隔等待 {delay_ms} ms")
                    time.sleep(delay_ms / 1000)
            logger.info("目录队列本轮已执行完毕。")
        finally:
            with sync_lock:
                sync_state["queue_runner"] = {"running": False, "current_source": "", "remaining": 0}
                sync_state["running"] = False
                sync_state["current_source_context"] = {}

    def run_leaf_stream_job(root_path: str) -> None:
        run_leaf_stream_job_with_mode(root_path, "direct")

    def run_leaf_stream_job_with_mode(root_path: str, mode: str) -> None:
        nonlocal config
        client: OpenListClient | None = None
        try:
            config = AppConfig.load(config_path)
            refresh_runtime()
            client = build_openlist_client(
                on_progress=logger.info,
                page_size=config.openlist_page_size,
                request_interval_ms=config.openlist_request_interval_ms,
            )
            logger.info(f"开始最底层目录边扫边执行 ({mode}): {root_path}")
            count = 0
            for leaf_path in client.iter_leaf_directories(root_path):
                count += 1
                task_snapshot = build_current_task_snapshot(
                    mode,
                    config,
                    {
                        "source_path": leaf_path,
                        "source_root_for_target": root_path,
                    },
                )
                with sync_lock:
                    sync_state["queue_runner"] = {
                        "running": True,
                        "current_source": leaf_path,
                        "remaining": -1,
                        "source_mapping_context": dict(task_snapshot.get("source_mapping_context") or {}),
                    }
                    sync_state["running"] = True
                    sync_state["current_source_context"] = dict(task_snapshot.get("source_mapping_context") or {})
                logger.info(f"发现最底层目录并立即执行 [{count}]: {leaf_path}")
                ok = run_sync_job(
                    mode,
                    {
                        "source_path": leaf_path,
                        "source_root_for_target": root_path,
                    },
                )
                if not ok and is_guangya_auth_error(str(sync_state.get("last_error") or "")):
                    logger.error("检测到光鸭登录态失效，已停止最底层目录边扫边同步。请重新抓取光鸭登录信息后再继续。")
                    break
                if not ok and is_rate_limit_error_message(str(sync_state.get("last_error") or "")):
                    cooldown_ms = compute_rate_limit_cooldown_ms(AppConfig.load(config_path), leaf_path)
                    logger.info(f"检测到疑似风控/限流，自动冷却等待 {cooldown_ms} ms 后继续扫描。")
                    time.sleep(cooldown_ms / 1000)
                delay_ms = max(0, int(AppConfig.load(config_path).queue_interval_ms))
                if delay_ms > 0:
                    logger.info(f"目录间隔等待 {delay_ms} ms")
                    time.sleep(delay_ms / 1000)
            logger.info(f"最底层目录边扫边执行完成，共处理 {count} 个目录。")
        finally:
            if client is not None:
                client.close()
            with sync_lock:
                sync_state["queue_runner"] = {"running": False, "current_source": "", "remaining": 0}
                sync_state["running"] = False
                sync_state["current_source_context"] = {}

    def run_pending_selected_stream_job(selected_paths: list[str]) -> None:
        nonlocal config
        try:
            state = load_state(config.state_file)
            items = build_pending_selected_execution_groups(selected_paths, state.pending_files)
            total = len(items)
            if not items:
                logger.info("没有可执行的已勾选待补传目录。")
                return
            logger.info(f"已按最底层优先拆分出 {total} 个待补传目录批次。")
            for index, (directory, paths) in enumerate(items, start=1):
                task_snapshot = build_current_task_snapshot(
                    "download_selected",
                    AppConfig.load(config_path),
                    {
                        "source_path": directory,
                        "selected_paths": paths,
                    },
                )
                with sync_lock:
                    sync_state["queue_runner"] = {
                        "running": True,
                        "current_source": directory,
                        "remaining": total - index + 1,
                        "source_mapping_context": dict(task_snapshot.get("source_mapping_context") or {}),
                    }
                    sync_state["running"] = True
                    sync_state["current_source_context"] = dict(task_snapshot.get("source_mapping_context") or {})
                logger.info(f"开始按勾选目录顺序补传 [{index}/{total}]: {directory}")
                ok = run_sync_job(
                    "download_selected",
                    {
                        "source_path": directory,
                        "selected_paths": paths,
                    },
                )
                if not ok and is_guangya_auth_error(str(sync_state.get("last_error") or "")):
                    logger.error("检测到光鸭登录态失效，已停止后续勾选目录补传。请重新抓取光鸭登录信息后再继续。")
                    break
                if not ok and is_rate_limit_error_message(str(sync_state.get("last_error") or "")):
                    cooldown_ms = compute_rate_limit_cooldown_ms(AppConfig.load(config_path), directory)
                    logger.info(f"检测到疑似风控/限流，自动冷却等待 {cooldown_ms} ms 后继续补传。")
                    time.sleep(cooldown_ms / 1000)
                delay_ms = max(0, int(AppConfig.load(config_path).queue_interval_ms))
                if delay_ms > 0 and index < total:
                    logger.info(f"目录间隔等待 {delay_ms} ms")
                    time.sleep(delay_ms / 1000)
            logger.info("按勾选目录顺序补传执行完毕。")
        finally:
            with sync_lock:
                sync_state["queue_runner"] = {"running": False, "current_source": "", "remaining": 0}
                sync_state["running"] = False
                sync_state["current_source_context"] = {}

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        html_path = Path(__file__).with_name("web").joinpath("index.html")
        return html_path.read_text(encoding="utf-8")

    @app.get("/assets/{asset_path:path}")
    def web_asset(asset_path: str) -> FileResponse:
        assets_root = Path(__file__).with_name("web").joinpath("assets").resolve()
        candidate = (assets_root / asset_path).resolve()
        if not str(candidate).startswith(str(assets_root)) or not candidate.is_file():
            raise HTTPException(status_code=404, detail="asset not found")
        media_type = "text/plain"
        suffix = candidate.suffix.lower()
        if suffix == ".css":
            media_type = "text/css"
        elif suffix == ".js":
            media_type = "application/javascript"
        elif suffix == ".json":
            media_type = "application/json"
        return FileResponse(candidate, media_type=media_type)

    @app.get("/api/auth/status")
    def auth_status(request: Request) -> dict[str, Any]:
        username = get_authenticated_username(request)
        return {
            "enabled": admin_auth_enabled(),
            "authenticated": bool(username) or not admin_auth_enabled(),
            "username": username,
        }

    @app.post("/api/auth/login")
    def auth_login(payload: dict[str, Any] | None = None) -> Response:
        payload = dict(payload or {})
        if not admin_auth_enabled():
            return JSONResponse({"ok": True, "enabled": False, "authenticated": True, "username": ""})
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "")
        if username != str(config.app_admin_username or "").strip() or password != str(config.app_admin_password or ""):
            raise HTTPException(status_code=401, detail="控制台账号或密码错误。")
        session_token = secrets.token_urlsafe(32)
        auth_sessions.add(session_token)
        response = JSONResponse(
            {
                "ok": True,
                "enabled": True,
                "authenticated": True,
                "username": str(config.app_admin_username or "").strip(),
            }
        )
        response.set_cookie(
            auth_cookie_name,
            session_token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/",
        )
        return response

    @app.post("/api/auth/logout")
    def auth_logout(request: Request) -> Response:
        session_token = str(request.cookies.get(auth_cookie_name) or "").strip()
        if session_token:
            auth_sessions.discard(session_token)
        response = JSONResponse({"ok": True})
        response.delete_cookie(auth_cookie_name, path="/")
        return response

    @app.get("/api/config")
    def get_config() -> dict[str, Any]:
        payload = load_config_payload()
        payload["effective_openlist_url"] = effective_openlist_url()
        payload["grouped_config"] = load_grouped_config_payload()
        payload["config_meta"] = {
            "storage": "nested_with_flat_compat",
            "active_target": config.target_key,
        }
        return payload

    @app.post("/api/config")
    def save_config(payload: dict[str, Any]) -> dict[str, Any]:
        nonlocal config
        previous_auth = (str(config.app_admin_username or ""), str(config.app_admin_password or ""))
        save_config_payload(payload)
        config = AppConfig.load(config_path)
        config.ensure_parent_dirs()
        current_auth = (str(config.app_admin_username or ""), str(config.app_admin_password or ""))
        if current_auth != previous_auth:
            auth_sessions.clear()
        refresh_runtime()
        logger.info("配置已更新")
        return {"ok": True}

    @app.get("/api/status")
    def get_status() -> dict[str, Any]:
        persist_guangya_capture_to_config()
        persist_provider_captures_to_config()
        with sync_lock:
            state = dict(sync_state)
        persistent_state = load_state(config.state_file)
        snapshots = merged_provider_capture_snapshots()
        active_target = str(config.target_key or "guangya").strip().lower() or "guangya"
        target_states = {
            key: {
                "field_count": len(dict(value or {})),
                "fields": sorted(str(field) for field in dict(value or {}).keys()),
            }
            for key, value in dict(persistent_state.target_states or {}).items()
        }
        active_target_state = persistent_state.get_target_state(active_target)
        grouped = load_grouped_config_payload()
        source_runtime = build_source_runtime_status(
            config,
            source_path=str(config.source_path or "/"),
            mount_path=payload_nested_get(grouped, ("ui", "browser", "mounted_source"), ""),
            requested_driver="",
        )
        return {
            "sync": state,
            "source_runtime": source_runtime,
            "active_target": active_target,
            "active_target_state": {
                "target_key": active_target,
                "field_count": len(active_target_state),
                "fields": sorted(active_target_state.keys()),
                "has_state": bool(active_target_state),
            },
            "target_states": target_states,
            "guangya_capture": snapshots.get("guangya", provider_capture.snapshot("guangya")),
            "provider_captures": snapshots,
            "provider_definitions": provider_capture.definitions_payload(),
            "openlist_runtime": refresh_runtime().status().to_dict(),
            "logs": logger.tail(200),
        }

    @app.post("/api/sync/start")
    def start_sync(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        config = AppConfig.load(config_path)
        payload = normalize_sync_payload(payload, config)
        require_selectable_target(str(payload.get("target_key") or config.target_key or "guangya"))
        with sync_lock:
            if sync_state["running"]:
                raise HTTPException(status_code=409, detail="同步任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
        mode = str(payload.get("mode") or "dry_run")
        worker = Thread(
            target=run_sync_job,
            args=(mode, payload),
            daemon=True,
        )
        worker.start()
        return {"ok": True}

    @app.post("/api/miaochuan/import")
    def start_miaochuan_import(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        config = AppConfig.load(config_path)
        payload = normalize_sync_payload(payload, config)
        require_miaochuan_target(str(payload.get("target_key") or config.target_key or "guangya"))
        miaochuan_payload = str(payload.get("miaochuan_payload") or "").strip()
        if not miaochuan_payload:
            raise HTTPException(status_code=400, detail="请先粘贴秒传 JSON。")
        with sync_lock:
            if sync_state["running"]:
                raise HTTPException(status_code=409, detail="同步任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
        worker = Thread(
            target=run_sync_job,
            args=(
                "miaochuan_import",
                {
                    "miaochuan_payload": miaochuan_payload,
                    "guangya_authorization": str(
                        resolve_payload_value(
                            payload,
                            "guangya_authorization",
                            ("targets", "guangya", "authorization"),
                            config.guangya_authorization or "",
                        )
                    ).strip(),
                },
            ),
            daemon=True,
        )
        worker.start()
        return {"ok": True}

    @app.post("/api/miaochuan/diagnose")
    def diagnose_miaochuan_payload(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = dict(payload or {})
        miaochuan_payload = str(resolve_payload_value(payload, "miaochuan_payload", default=payload.get("miaochuan_payload") or "")).strip()
        if not miaochuan_payload:
            raise HTTPException(status_code=400, detail="请先粘贴秒传 JSON。")
        try:
            diagnosis = GuangyaMiaochuanImporter.diagnose_payload(miaochuan_payload)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return diagnosis

    @app.post("/api/leaf/run_stream")
    def run_leaf_stream(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        config = AppConfig.load(config_path)
        require_selectable_target(str(resolve_payload_value(payload, "target_key", ("targets", "active_target"), config.target_key or "guangya")))
        root_path = str(resolve_payload_value(payload, "source_path", ("sync", "source_path"), config.source_path or "/")).strip()
        normalized = "/" + root_path.lstrip("/")
        if normalized == "/":
            raise HTTPException(status_code=400, detail="不能从 OpenList 根目录 / 开始边扫边同步，请先进入具体挂载目录。")
        with sync_lock:
            if sync_state["running"] or sync_state.get("queue_runner", {}).get("running"):
                raise HTTPException(status_code=409, detail="同步任务或队列任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
            sync_state["queue_runner"] = {"running": True, "current_source": "", "remaining": -1}
        worker = Thread(target=run_leaf_stream_job, args=(normalized,), daemon=True)
        worker.start()
        return {"ok": True, "source_path": normalized}

    @app.post("/api/leaf/run_stream_full")
    def run_leaf_stream_full(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        config = AppConfig.load(config_path)
        require_selectable_target(str(resolve_payload_value(payload, "target_key", ("targets", "active_target"), config.target_key or "guangya")))
        root_path = str(resolve_payload_value(payload, "source_path", ("sync", "source_path"), config.source_path or "/")).strip()
        normalized = "/" + root_path.lstrip("/")
        if normalized == "/":
            raise HTTPException(status_code=400, detail="不能从 OpenList 根目录 / 开始边扫边同步+补传，请先进入具体挂载目录。")
        with sync_lock:
            if sync_state["running"] or sync_state.get("queue_runner", {}).get("running"):
                raise HTTPException(status_code=409, detail="同步任务或队列任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
            sync_state["queue_runner"] = {"running": True, "current_source": "", "remaining": -1}
        worker = Thread(target=run_leaf_stream_job_with_mode, args=(normalized, "full"), daemon=True)
        worker.start()
        return {"ok": True, "source_path": normalized}

    @app.post("/api/pending/run_selected_stream")
    def run_pending_selected_stream(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        config = AppConfig.load(config_path)
        payload = normalize_sync_payload(payload, config)
        require_selectable_target(str(payload.get("target_key") or config.target_key or "guangya"))
        selected_paths = list(payload.get("selected_paths") or [])
        if not selected_paths:
            raise HTTPException(status_code=400, detail="请先勾选至少一个待补传文件或目录。")
        with sync_lock:
            if sync_state["running"] or sync_state.get("queue_runner", {}).get("running"):
                raise HTTPException(status_code=409, detail="同步任务或队列任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
            sync_state["queue_runner"] = {"running": True, "current_source": "", "remaining": 0}
        worker = Thread(target=run_pending_selected_stream_job, args=(selected_paths,), daemon=True)
        worker.start()
        return {"ok": True, "selected": len(selected_paths)}

    @app.post("/api/queue/add")
    def add_queue_item(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = normalize_queue_payload(payload, config)
        source_path = str(resolve_payload_value(payload, "source_path", ("sync", "source_path"), config.source_path)).strip()
        if not source_path:
            raise HTTPException(status_code=400, detail="缺少 source_path")
        state = load_state(config.state_file)
        normalized = "/" + source_path.lstrip("/")
        if normalized == "/":
            raise HTTPException(status_code=400, detail="不能把 OpenList 根目录 / 直接加入队列，请先进入具体挂载目录。")
        if not any(item.source_path == normalized for item in state.source_queue):
            from .models import QueueItemState
            state.source_queue.append(QueueItemState(source_path=normalized, source_root_for_target=normalized))
            save_state(config.state_file, state)
        sync_runtime_with_state()
        return {"ok": True}

    @app.post("/api/queue/remove")
    def remove_queue_item(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = normalize_queue_payload(payload, config)
        source_path = "/" + str(payload.get("source_path") or "").lstrip("/")
        state = load_state(config.state_file)
        state.source_queue = [item for item in state.source_queue if item.source_path != source_path]
        save_state(config.state_file, state)
        sync_runtime_with_state()
        return {"ok": True}

    @app.post("/api/queue/run_next")
    def run_next_queue_item() -> dict[str, Any]:
        nonlocal config
        state = load_state(config.state_file)
        next_index = next((idx for idx, item in enumerate(state.source_queue) if item.enabled), None)
        if next_index is None:
            raise HTTPException(status_code=400, detail="队列里没有可运行的源目录")
        next_item = state.source_queue.pop(next_index)
        state.source_queue.append(next_item)
        save_state(config.state_file, state)
        sync_runtime_with_state()
        with sync_lock:
            if sync_state["running"]:
                raise HTTPException(status_code=409, detail="同步任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
        config = AppConfig.load(config_path)
        require_selectable_target(config.target_key)
        worker = Thread(
            target=run_sync_job,
            args=(
                "direct",
                {
                    "source_path": next_item.source_path,
                    "source_root_for_target": next_item.source_root_for_target or next_item.source_path,
                },
            ),
            daemon=True,
        )
        worker.start()
        return {"ok": True, "source_path": next_item.source_path}

    @app.post("/api/queue/add_leaf_units")
    def add_queue_leaf_units(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        root_path = str(resolve_payload_value(payload, "source_path", ("sync", "source_path"), config.source_path or "/")).strip()
        if not root_path:
            raise HTTPException(status_code=400, detail="缺少 source_path")
        if ("/" + root_path.lstrip("/")) == "/":
            raise HTTPException(status_code=400, detail="不能从 OpenList 根目录 / 收集最底层目录，请先进入具体挂载目录。")
        client = build_openlist_client(
            openlist_url=str(resolve_payload_value(payload, "openlist_url", ("openlist", "url"), effective_openlist_url())),
            openlist_username=str(resolve_payload_value(payload, "openlist_username", ("openlist", "username"), config.openlist_username)),
            openlist_password=str(resolve_payload_value(payload, "openlist_password", ("openlist", "password"), config.openlist_password)),
            openlist_token=str(resolve_payload_value(payload, "openlist_token", ("openlist", "token"), config.openlist_token)),
        )
        try:
            leaf_units = client.collect_leaf_directories(root_path)
        finally:
            client.close()
        state = load_state(config.state_file)
        existing = {item.source_path for item in state.source_queue}
        added = 0
        from .models import QueueItemState
        for path in leaf_units:
            if not path or path in existing:
                continue
            state.source_queue.append(
                QueueItemState(
                    source_path=path,
                    source_root_for_target="/" + root_path.lstrip("/"),
                )
            )
            existing.add(path)
            added += 1
        save_state(config.state_file, state)
        sync_runtime_with_state()
        return {"ok": True, "added": added, "units": leaf_units}

    @app.post("/api/queue/run_all")
    def run_all_queue_items() -> dict[str, Any]:
        require_selectable_target()
        with sync_lock:
            if sync_state["running"] or sync_state.get("queue_runner", {}).get("running"):
                raise HTTPException(status_code=409, detail="同步任务或队列任务正在运行")
            sync_state["running"] = True
            sync_state["last_error"] = ""
            sync_state["queue_runner"] = {"running": True, "current_source": "", "remaining": 0}
        worker = Thread(target=run_queue_job, daemon=True)
        worker.start()
        return {"ok": True}

    @app.post("/api/openlist/login")
    def openlist_login(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        runtime_mode = AppConfig.normalize_openlist_mode(
            str(resolve_payload_value(payload, "openlist_mode", ("openlist", "mode"), config.openlist_mode))
        )
        connection_path = (
            ("openlist", "connections", "external_remote")
            if runtime_mode == "external_remote"
            else ("openlist", "connections", "managed_binary")
            if AppConfig.is_managed_openlist_mode(runtime_mode)
            else ("openlist", "connections", "external_local")
        )
        client = OpenListClient(
            base_url=str(resolve_payload_value(payload, "openlist_url", ("openlist", "url"), config.openlist_url)),
            username=str(resolve_payload_value(payload, "openlist_username", ("openlist", "username"), config.openlist_username)),
            password=str(resolve_payload_value(payload, "openlist_password", ("openlist", "password"), config.openlist_password)),
            token=str(resolve_payload_value(payload, "openlist_token", ("openlist", "token"), "")),
        )
        try:
            client.ensure_login()
            updates: dict[tuple[str, ...], Any] = {
                ("openlist", "url"): client.base_url,
                ("openlist", "username"): client.username,
                ("openlist", "token"): client.token,
                (*connection_path, "url"): client.base_url,
                (*connection_path, "username"): client.username,
                (*connection_path, "token"): client.token,
            }
            if resolve_payload_value(payload, "openlist_password", ("openlist", "password"), ""):
                updates[("openlist", "password")] = client.password
                updates[(*connection_path, "password")] = client.password
            save_grouped_config_updates(updates)
            config = AppConfig.load(config_path)
            logger.info("OpenList 登录成功，token 已写回配置")
            return {"ok": True, "openlist_token": client.token}
        except Exception as exc:  # noqa: BLE001
            logger.error(f"OpenList 登录失败: {exc}")
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            client.close()

    @app.get("/api/openlist/runtime/status")
    def get_openlist_runtime_status() -> dict[str, Any]:
        return refresh_runtime().status().to_dict()

    @app.post("/api/openlist/runtime/install")
    def install_openlist_runtime() -> dict[str, Any]:
        nonlocal config
        current_runtime = refresh_runtime()
        try:
            status = current_runtime.install_binary()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"OpenList runtime 拉取失败: {exc}")
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        updates = {
            ("openlist", "managed_runtime", "bin"): status.binary,
        }
        if save_grouped_config_updates(retain_explicit_grouped_updates(updates)):
            config = AppConfig.load(config_path)
        logger.info(f"OpenList runtime 已就绪: {status.binary}")
        return status.to_dict()

    @app.post("/api/openlist/runtime/start")
    def start_openlist_runtime() -> dict[str, Any]:
        status = refresh_runtime().start()
        if not status.running and AppConfig.is_managed_openlist_mode(config.openlist_mode):
            logger.error(f"OpenList runtime 启动失败: {status.message}")
            raise HTTPException(status_code=400, detail=status.message or "Managed OpenList 启动失败")
        if status.running:
            logger.info(f"OpenList runtime 已就绪: {status.active_url}")
        return status.to_dict()

    @app.get("/api/openlist/drivers")
    def get_openlist_drivers() -> dict[str, Any]:
        with build_admin_client() as client:
            return {"items": client.driver_names()}

    @app.get("/api/openlist/driver_info")
    def get_openlist_driver_info(driver: str) -> dict[str, Any]:
        if not driver.strip():
            raise HTTPException(status_code=400, detail="缺少 driver")
        with build_admin_client() as client:
            info = client.driver_info(driver)
        return {
            "name": info.name,
            "config": info.config,
            "common": [asdict(field) for field in info.common],
            "additional": [asdict(field) for field in info.additional],
        }

    @app.get("/api/provider/driver_blueprint")
    def get_provider_driver_blueprint(driver: str) -> dict[str, Any]:
        if not driver.strip():
            raise HTTPException(status_code=400, detail="缺少 driver")
        with build_admin_client() as client:
            info = client.driver_info(driver)
        spec = build_driver_capture_spec(driver, [*info.common, *info.additional])
        guide = get_driver_guide(driver)
        return {
            "key": spec.key,
            "label": spec.label,
            "capture_mode": spec.capture_mode,
            "login_url": spec.login_url,
            "recommended_drivers": list(spec.recommended_drivers),
            "required_keys": list(spec.required_keys),
            "description": spec.description,
            "driver": driver,
            "guide": guide,
        }

    @app.get("/api/provider/registry")
    def get_provider_registry() -> dict[str, Any]:
        implemented_targets = supported_target_keys()
        target_profiles = list_target_profiles()
        provider_catalog = build_provider_capture_definition_payload()
        grouped = load_grouped_config_payload()
        source_context = resolve_source_mapping_context(
            {
                "mount_path": payload_nested_get(grouped, ("ui", "browser", "mounted_source"), ""),
                "source_path": str(config.source_path or "/"),
                "driver": "",
            },
            config,
        )
        current_source_capability = (
            build_driver_target_capability(source_context["effective_driver"], target=config.target_key)
            if source_context["effective_driver"]
            else None
        )
        return {
            "guides": list_driver_guides(),
            "source_profiles": list_source_profiles(),
            "target_profiles": target_profiles,
            "provider_catalog": provider_catalog,
            "driver_matrix": build_driver_capability_matrix(target=config.target_key),
            "active_target": config.target_key,
            "source_mapping": dict(config.mount_provider_mapping or {}),
            "current_source_context": {
                **source_context,
                "source_path": str(config.source_path or "/"),
                "current_capability": current_source_capability,
            },
            "implemented_targets": implemented_targets,
            "target_implementation_status": {
                key: {
                    "known_profile": key in target_profiles,
                    "implemented": key in implemented_targets,
                    "selectable": key in target_profiles and key in implemented_targets,
                }
                for key in target_profiles.keys()
            },
        }

    @app.get("/api/provider/source_mapping")
    def get_provider_source_mapping() -> dict[str, Any]:
        return {
            "items": dict(config.mount_provider_mapping or {}),
        }

    @app.post("/api/provider/source_mapping")
    def save_provider_source_mapping(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        raw = dict(payload or {})
        mapping_payload = raw.get("mapping")
        if isinstance(mapping_payload, dict):
            next_mapping = {
                normalize_posix_path(path): str(profile or "").strip()
                for path, profile in mapping_payload.items()
                if str(path).strip() and str(profile or "").strip()
            }
        else:
            mount_path = normalize_posix_path(str(raw.get("mount_path") or "").strip())
            if not mount_path:
                raise HTTPException(status_code=400, detail="缺少 mount_path")
            next_mapping = dict(config.mount_provider_mapping or {})
            profile_key = str(raw.get("profile_key") or "").strip()
            if profile_key:
                next_mapping[mount_path] = profile_key
            else:
                next_mapping.pop(mount_path, None)
        changed = save_grouped_config_updates({
            ("source_session", "mount_provider_mapping"): next_mapping,
        })
        if changed:
            config = AppConfig.load(config_path)
            config.ensure_parent_dirs()
            logger.info("源 Profile 覆盖映射已更新")
        return {
            "ok": True,
            "changed": changed,
            "items": dict(config.mount_provider_mapping or {}),
        }

    @app.get("/api/target/preflight")
    def get_target_preflight(target: str = "") -> dict[str, Any]:
        return build_target_preflight(target)

    @app.get("/api/provider/capability")
    def get_provider_capability(driver: str, target: str = "") -> dict[str, Any]:
        if not driver.strip():
            raise HTTPException(status_code=400, detail="缺少 driver")
        effective_target = str(target or config.target_key or "guangya").strip() or "guangya"
        context = resolve_source_mapping_context({"driver": driver}, config)
        capability = build_driver_target_capability(context["effective_driver"] or driver, target=effective_target)
        capability["sourceMappingContext"] = context
        return capability

    @app.post("/api/provider/coverage_audit")
    def post_provider_coverage_audit(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = normalize_registry_payload(payload, config)
        drivers = resolve_registry_drivers(payload)
        target = str(payload.get("target") or config.target_key or "guangya").strip() or "guangya"
        audit = build_driver_coverage_audit(drivers, target=target, live_driver_fields_map=build_live_driver_fields_map(drivers))
        return filter_driver_coverage_audit(audit, **build_registry_filter_kwargs(payload))

    @app.post("/api/provider/coverage_audit_markdown")
    def post_provider_coverage_audit_markdown(payload: dict[str, Any] | None = None) -> PlainTextResponse:
        payload = normalize_registry_payload(payload, config)
        drivers = resolve_registry_drivers(payload)
        target = str(payload.get("target") or config.target_key or "guangya").strip() or "guangya"
        audit = build_driver_coverage_audit(drivers, target=target, live_driver_fields_map=build_live_driver_fields_map(drivers))
        audit = filter_driver_coverage_audit(audit, **build_registry_filter_kwargs(payload))
        markdown = render_driver_coverage_audit_markdown(audit)
        return PlainTextResponse(markdown, media_type="text/markdown; charset=utf-8")

    @app.post("/api/provider/coverage_scaffold")
    def post_provider_coverage_scaffold(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = normalize_registry_payload(payload, config)
        drivers = resolve_registry_drivers(payload)
        target = str(payload.get("target") or config.target_key or "guangya").strip() or "guangya"
        audit = build_driver_coverage_audit(drivers, target=target, live_driver_fields_map=build_live_driver_fields_map(drivers))
        audit = filter_driver_coverage_audit(audit, **build_registry_filter_kwargs(payload))
        return build_driver_coverage_scaffold(audit)

    @app.post("/api/provider/coverage_scaffold_markdown")
    def post_provider_coverage_scaffold_markdown(payload: dict[str, Any] | None = None) -> PlainTextResponse:
        payload = normalize_registry_payload(payload, config)
        drivers = resolve_registry_drivers(payload)
        target = str(payload.get("target") or config.target_key or "guangya").strip() or "guangya"
        audit = build_driver_coverage_audit(drivers, target=target, live_driver_fields_map=build_live_driver_fields_map(drivers))
        audit = filter_driver_coverage_audit(audit, **build_registry_filter_kwargs(payload))
        scaffold = build_driver_coverage_scaffold(audit)
        markdown = render_driver_coverage_scaffold_markdown(scaffold)
        return PlainTextResponse(markdown, media_type="text/markdown; charset=utf-8")

    @app.post("/api/provider/capability_assess")
    def post_provider_capability_assess(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = normalize_capability_payload(payload, config)
        driver = str(payload.get("driver") or "").strip()
        target = str(payload.get("target") or config.target_key or "guangya").strip() or "guangya"
        if not driver:
            raise HTTPException(status_code=400, detail="缺少 driver")
        summary = dict(payload.get("analysis_summary") or {})
        result = assess_driver_target_capability(
            driver,
            analysis_summary=summary,
            target=target,
            live_driver_fields_map=build_live_driver_fields_map([driver]),
        )
        result["sourceMappingContext"] = build_registry_source_mapping_context(
            mount_path=str(payload.get("mount_path") or ""),
            requested_driver=str(payload.get("requested_driver") or ""),
            effective_driver=driver,
            source_profile_override=str(payload.get("source_profile_override") or ""),
            source_path=str(payload.get("source_path") or ""),
            target=target,
            live_driver_fields_map=build_live_driver_fields_map([driver]),
        )
        return result

    @app.get("/api/openlist/storages")
    def get_openlist_storages(page: int = 1, per_page: int = 200) -> dict[str, Any]:
        with build_admin_client() as client:
            payload = client.storage_list(page=page, per_page=per_page)
        return payload

    @app.post("/api/openlist/storage/create")
    def create_openlist_storage(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = normalize_storage_create_payload(payload)
        driver = str(payload.get("driver") or "").strip()
        values = dict(payload.get("values") or {})
        if not driver:
            raise HTTPException(status_code=400, detail="缺少 driver")
        with build_admin_client() as client:
            info = client.driver_info(driver)
            body = build_storage_payload(info, values)
            result = client.create_storage(driver, body)
        logger.info(f"已创建 OpenList 挂载: {driver}")
        return result

    @app.post("/api/openlist/list_dirs")
    def openlist_list_dirs(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        client = build_openlist_client(
            openlist_url=str(resolve_payload_value(payload, "openlist_url", ("openlist", "url"), effective_openlist_url())),
            openlist_username=str(resolve_payload_value(payload, "openlist_username", ("openlist", "username"), config.openlist_username)),
            openlist_password=str(resolve_payload_value(payload, "openlist_password", ("openlist", "password"), config.openlist_password)),
            openlist_token=str(resolve_payload_value(payload, "openlist_token", ("openlist", "token"), config.openlist_token)),
        )
        try:
            browser = client.list_directories(str(resolve_payload_value(payload, "path", ("ui", "browser", "current_path"), "/")))
            with sync_lock:
                sync_state["directory_browser"] = browser
            return {"ok": True, **browser}
        except Exception as exc:  # noqa: BLE001
            logger.error(f"OpenList 浏览目录失败: {exc}")
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            client.close()

    @app.post("/api/source/analyze")
    def analyze_source(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        source_path = str(resolve_payload_value(payload, "source_path", ("sync", "source_path"), config.source_path or "/")).strip()
        target_key = str(resolve_payload_value(payload, "target_key", ("targets", "active_target"), config.target_key or "guangya")).strip() or "guangya"
        run_config = AppConfig.load(config_path)
        if AppConfig.is_managed_openlist_mode(run_config.openlist_mode):
            ensure_runtime_ready()
            run_config.openlist_url = effective_openlist_url()
        run_config.source_path = "/" + source_path.lstrip("/")
        runner = SyncRunner(run_config, log=logger.info)
        try:
            entries, plan, removed_paths = runner.analyze()
        finally:
            runner.source.close()
        limit = max(1, int(resolve_payload_value(payload, "limit", default=200) or 200))
        summary = summarize_source_entries(entries)
        preflight = build_target_preflight(target_key)
        fast_upload_decision = assess_directory_fast_upload(summary, target_capability=dict(preflight.get("adapter_capability") or {}))
        return {
            "source_path": run_config.source_path,
            "summary": summary,
            "target_key": target_key,
            "fastUploadDecision": fast_upload_decision,
            "plan_total": len(plan),
            "removed_total": len(removed_paths),
            "entries": [serialize_source_entry(entry) for entry in entries[:limit]],
            "truncated": len(entries) > limit,
        }

    @app.post("/api/source/miaochuan_preview")
    def build_source_miaochuan_preview(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal config
        payload = payload or {}
        source_path = str(resolve_payload_value(payload, "source_path", ("sync", "source_path"), config.source_path or "/")).strip()
        target_key = str(resolve_payload_value(payload, "target_key", ("targets", "active_target"), config.target_key or "guangya")).strip() or "guangya"
        run_config = AppConfig.load(config_path)
        if AppConfig.is_managed_openlist_mode(run_config.openlist_mode):
            ensure_runtime_ready()
            run_config.openlist_url = effective_openlist_url()
        run_config.source_path = "/" + source_path.lstrip("/")
        runner = SyncRunner(run_config, log=logger.info)
        try:
            entries, plan, removed_paths = runner.analyze()
        finally:
            runner.source.close()
        miaochuan_payload = build_source_miaochuan_payload(entries, run_config.source_path)
        summary = summarize_source_entries(entries)
        preflight = build_target_preflight(target_key)
        return {
            "source_path": run_config.source_path,
            "summary": summary,
            "target_key": target_key,
            "fastUploadDecision": assess_directory_fast_upload(summary, target_capability=dict(preflight.get("adapter_capability") or {})),
            "plan_total": len(plan),
            "removed_total": len(removed_paths),
            "payload": miaochuan_payload,
            "payload_text": json.dumps(miaochuan_payload, ensure_ascii=False, indent=2),
        }

    @app.post("/api/logs/clear")
    def clear_logs() -> dict[str, Any]:
        logger.clear()
        logger.info("日志已清空")
        return {"ok": True}

    @app.post("/api/guangya/capture/start")
    def start_guangya_capture() -> dict[str, Any]:
        provider_capture.start("guangya")
        logger.info("已启动光鸭登录抓取")
        return {"ok": True}

    @app.get("/api/provider/captures")
    def get_provider_captures() -> dict[str, Any]:
        persist_provider_captures_to_config()
        return {
            "providers": build_provider_capture_definition_payload(),
            "snapshots": merged_provider_capture_snapshots(),
        }

    @app.post("/api/provider/capture/start")
    def start_provider_capture(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = normalize_provider_capture_payload(payload)
        provider = str(payload.get("provider") or "").strip().lower()
        driver = str(payload.get("driver") or "").strip()
        login_url = str(payload.get("login_url") or "").strip()
        if not provider:
            raise HTTPException(status_code=400, detail="缺少 provider")
        try:
            if provider.startswith("driver::"):
                if not driver:
                    raise HTTPException(status_code=400, detail="通用驱动抓取缺少 driver")
                with build_admin_client() as client:
                    info = client.driver_info(driver)
                dynamic_spec = build_driver_capture_spec(driver, [*info.common, *info.additional], login_url=login_url)
                provider_capture.start(provider, dynamic_spec)
                provider_name = dynamic_spec.label
            else:
                provider_capture.start(provider)
                provider_name = next(
                    (item["label"] for item in provider_capture.definitions_payload() if item["key"] == provider),
                    provider,
                )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        snapshot = provider_capture.snapshot(provider)
        if str(snapshot.get("status") or "") == "manual":
            logger.info(f"{provider_name} 已切换为手动凭证模式")
        else:
            logger.info(f"已启动 {provider_name} 登录抓取")
        return {"ok": True, "provider": provider}

    @app.post("/api/provider/capture/prefill")
    def provider_capture_prefill(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = normalize_provider_capture_payload(payload)
        provider = str(payload.get("provider") or "").strip().lower()
        driver = str(payload.get("driver") or "").strip()
        return build_provider_prefill(provider, driver)

    sync_runtime_with_state()
    return app
