from __future__ import annotations

from typing import Any

from .openlist_admin import OpenListDriverField
from .fast_upload_decision import assess_directory_fast_upload
from .provider_capture import (
    build_capture_supported_driver_aliases,
    build_driver_capture_spec,
    derive_capture_requirements_from_fields,
    guess_login_url_for_driver,
    resolve_capture_spec_for_driver,
)
from .provider_registry_data import (
    CAPABILITY_LEVEL_ORDER,
    DRIVER_GUIDES,
    SOURCE_PROVIDER_PROFILES,
    TARGET_PROFILES,
)


def _normalize_key(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _safe_dynamic_profile_key(driver: str) -> str:
    normalized = _normalize_key(driver)
    return f"dynamic_{normalized or 'driver'}"


def _extract_dynamic_default_mount_values(fields: list[OpenListDriverField]) -> dict[str, str]:
    allowlist = {
        "root_folder_id",
        "root_folder_path",
        "use_online_api",
        "api_url",
        "web_proxy",
        "webdav_policy",
        "proxy_range",
        "chunk_size",
        "cloud_drive_type",
        "livp_download_format",
        "disable_media_link",
    }
    result: dict[str, str] = {}
    for field in fields:
        name = str(field.name or "").strip()
        if not name:
            continue
        normalized = str(name).lower()
        if normalized not in allowlist:
            continue
        default = str(field.default or "").strip()
        if default:
            result[name] = default
    return result


def _infer_dynamic_login_mode(requirements: dict[str, Any]) -> str:
    required = {str(item or "").strip().lower() for item in list(requirements.get("required_keys") or [])}
    if "refresh_token" in required:
        return "refresh token oriented"
    if "cookie_header" in required and "authorization" in required:
        return "cookie + authorization"
    if "authorization" in required:
        return "authorization header oriented"
    if "cookie_header" in required:
        return "cookie focused"
    return "dynamic driver form"


def build_dynamic_source_profile(driver: str, fields: list[OpenListDriverField], target: str = "guangya") -> dict[str, Any]:
    display_name = str(driver or "").strip() or "UnknownDriver"
    requirements = derive_capture_requirements_from_fields(fields)
    matched_fields = [str(item or "") for item in list(requirements.get("matched_fields") or []) if str(item or "").strip()]
    required_keys = [str(item or "") for item in list(requirements.get("required_keys") or []) if str(item or "").strip()]
    login_mode = _infer_dynamic_login_mode(requirements)
    default_mount_values = _extract_dynamic_default_mount_values(fields)
    has_refresh = "refresh_token" in {item.lower() for item in required_keys}
    has_auth = "authorization" in {item.lower() for item in required_keys}
    has_cookie = "cookie_header" in {item.lower() for item in required_keys}
    rate_profile = "safe" if has_cookie or has_auth else "balanced" if has_refresh else "safe"
    login_url = guess_login_url_for_driver(display_name)
    capability_level = "download_upload_only"
    capability_notes_zh = (
        "该能力是根据当前 OpenList live 驱动字段动态推断出的保守结论，默认只承诺目录读取 + 下载补传，不承诺秒传。"
    )
    capability_notes_en = (
        "This capability is a conservative inference from the current live OpenList driver fields. It only promises listing plus download-upload fallback, not fast upload."
    )
    doc_links = [login_url] if login_url else []
    profile = {
        "key": _safe_dynamic_profile_key(display_name),
        "label": f"{display_name} (Dynamic)",
        "label_zh": f"{display_name}（动态推断）",
        "driver_aliases": [display_name],
        "login_mode": login_mode,
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "inferred_from_live_driver",
        "capture_strategy": (
            "根据当前 OpenList live driver 字段自动推断登录参数和挂载默认值，先完成挂载与小目录验证，再逐步补专用档案。"
        ),
        "capture_strategy_en": (
            "Infer auth fields and mount defaults from the live OpenList driver definition first, validate with a small directory, and then promote to a dedicated profile later."
        ),
        "doc_links": doc_links,
        "default_mount_values": default_mount_values,
        "recommended_rate_profile": rate_profile,
        "risk_notes": {
            "zh": (
                "当前还是动态推断档案，不应把它当成已人工验证完成的专用驱动支持。优先小目录、低频率、先验证下载链路。"
            ),
            "en": (
                "This is still a dynamically inferred profile, not a fully human-verified dedicated driver profile. Prefer small directories, low frequency, and download-path validation first."
            ),
        },
        "capability_to_targets": {
            str(target or "guangya").strip().lower() or "guangya": {
                "level": capability_level,
                "recommended_flow": "先用小目录验证挂载、列表和下载，再决定是否放量补传。",
                "recommended_flow_en": "Validate mount, listing, and download on a small directory first, then scale fallback uploads gradually.",
                "notes": {
                    "zh": capability_notes_zh,
                    "en": capability_notes_en,
                },
            }
        },
        "is_dynamic_inference": True,
        "dynamic_required_keys": required_keys,
        "dynamic_matched_fields": matched_fields,
    }
    return _serialize_source_profile(profile)


def _guess_driver_doc_urls(driver: str) -> list[str]:
    raw = str(driver or "").strip()
    normalized = _normalize_key(raw)
    candidates: list[str] = []
    if raw:
        candidates.append(f"https://doc.oplist.org/guide/drivers/{raw}")
    if normalized and normalized != raw:
        candidates.append(f"https://doc.oplist.org/guide/drivers/{normalized}")
    if normalized:
        alias_variants = {
            "189cloud": "189",
            "aliyundriveopen": "aliyundrive_open",
            "123open": "123_open",
            "139yun": "139.html",
            "googledrive": "google_drive",
            "quark": "quark.html",
            "pikpak": "pikpak.html",
        }
        mapped = alias_variants.get(normalized, "")
        if mapped:
            candidates.append(f"https://doc.oplist.org/guide/drivers/{mapped}")
    candidates.append("https://doc.oplist.org/guide/drivers/")
    seen: set[str] = set()
    result: list[str] = []
    for item in candidates:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _collect_guide_doc_candidates(driver: str, guide: dict[str, Any] | None = None) -> list[str]:
    source_profile = get_source_profile_by_key_or_alias(driver)
    candidates: list[str] = []
    if guide and guide.get("doc_url"):
        candidates.append(str(guide.get("doc_url") or ""))
    candidates.extend(str(link or "") for link in list(source_profile.get("docLinks") or source_profile.get("doc_links") or []))
    for alias in list(source_profile.get("driverAliases") or source_profile.get("driver_aliases") or []):
        candidates.extend(_guess_driver_doc_urls(str(alias or "")))
    candidates.extend(_guess_driver_doc_urls(driver))
    seen: set[str] = set()
    result: list[str] = []
    for item in candidates:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _serialize_driver_guide(guide: dict[str, Any]) -> dict[str, Any]:
    return {
        "docUrl": str(guide.get("doc_url") or ""),
        "docUrlCandidates": list(guide.get("doc_url_candidates") or []),
        "summary": dict(guide.get("summary") or {}),
        "steps": {
            "zh": list((guide.get("steps") or {}).get("zh") or []),
            "en": list((guide.get("steps") or {}).get("en") or []),
        },
        "defaults": dict(guide.get("defaults") or {}),
        "isGenericFallback": bool(guide.get("is_generic_fallback", False)),
    }


def _build_generic_driver_guide(driver: str) -> dict[str, Any] | None:
    display_name = str(driver or "").strip()
    if not display_name:
        return None
    login_url = ""
    capture_match = resolve_capture_spec_for_driver(display_name)
    if capture_match.get("loginUrl"):
        login_url = str(capture_match.get("loginUrl") or "")
    generic_doc_url = "https://doc.oplist.org/guide/drivers/"
    login_hint = login_url or "对应网盘官网登录页"
    return {
        "doc_url": generic_doc_url,
        "summary": {
            "zh": f"{display_name} 暂时还没有仓库内置的专用接入说明，当前先提供一个通用 OpenList 驱动接入兜底流程。",
            "en": f"{display_name} does not have a dedicated in-repo onboarding guide yet. A generic OpenList driver onboarding fallback is provided for now.",
        },
        "steps": {
            "zh": [
                "先在挂载页读取当前驱动的实时字段，优先按 OpenList 返回的真实字段名填写，不要自己猜参数名。",
                f"如果该驱动需要网页登录态，先用页面里的“源网盘登录抓取”打开 {login_hint}，抓到 Cookie / Token / Header 后再回填挂载表单。",
                "先用一个小目录验证列目录、分页和小文件下载是否稳定，再考虑跑大目录或边扫边同步。",
                "如果后续验证通过，再把这个驱动补进 provider registry 的专用 guide / capture / capability 条目。",
            ],
            "en": [
                "Load the live driver fields from the mount page first, and fill the exact OpenList field names instead of guessing parameters.",
                f"If this driver requires web session data, use the source-login capture panel to open {login_hint}, capture Cookie / Token / Header values, and prefill the mount form.",
                "Validate listing, pagination, and small-file download with a small directory before running large scans or streaming sync.",
                "Once verified, promote this driver into dedicated provider-registry guide / capture / capability entries.",
            ],
        },
        "defaults": {},
        "is_generic_fallback": True,
    }


def _resolve_guide_key(driver: str) -> tuple[str, dict[str, Any] | None]:
    normalized = _normalize_key(driver)
    if not normalized:
        return "", None
    direct = DRIVER_GUIDES.get(normalized)
    if direct is not None:
        return normalized, direct

    source_profile = get_source_profile_by_key_or_alias(driver)
    profile_key = _normalize_key(source_profile.get("key") or "")
    if profile_key:
        profile_guide = DRIVER_GUIDES.get(profile_key)
        if profile_guide is not None:
            return profile_key, profile_guide
    for alias in list(source_profile.get("driverAliases") or []):
        alias_key = _normalize_key(alias)
        alias_guide = DRIVER_GUIDES.get(alias_key)
        if alias_guide is not None:
            return alias_key, alias_guide
    return "", None


def get_driver_guide(driver: str) -> dict[str, Any] | None:
    _matched_key, guide = _resolve_guide_key(driver)
    if guide is not None:
        enriched = dict(guide)
        enriched["doc_url_candidates"] = _collect_guide_doc_candidates(driver, guide)
        return _serialize_driver_guide(enriched)
    fallback = _build_generic_driver_guide(driver)
    if fallback is None:
        return None
    fallback["doc_url_candidates"] = _collect_guide_doc_candidates(driver, fallback)
    return _serialize_driver_guide(fallback)


def list_driver_guides() -> dict[str, dict[str, Any]]:
    return {
        key: _serialize_driver_guide(value)
        for key, value in DRIVER_GUIDES.items()
    }


def _serialize_target_profile(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": str(profile.get("key") or ""),
        "label": str(profile.get("label") or ""),
        "labelZh": str(profile.get("label_zh") or ""),
        "authMode": str(profile.get("auth_mode") or ""),
        "tokenRefresh": str(profile.get("token_refresh") or ""),
        "autoCreateDir": bool(profile.get("auto_create_dir", False)),
        "fastUploadHashes": list(profile.get("fast_upload_hashes") or []),
        "fallbackModes": list(profile.get("fallback_modes") or []),
        "description": dict(profile.get("description") or {}),
        "researchNotes": dict(profile.get("research_notes") or {}),
    }


def _serialize_source_profile(profile: dict[str, Any]) -> dict[str, Any]:
    hash_fields_supported = list(profile.get("hash_fields_supported") or [])
    likely_hashes = list(profile.get("likely_hashes") or [])
    supports_fingerprint_enrichment = bool(hash_fields_supported or likely_hashes)
    capability_to_targets = {
        str(target): {
            "level": str(value.get("level") or "unsupported"),
            "recommendedFlow": str(value.get("recommended_flow") or ""),
            "recommendedFlowEn": str(value.get("recommended_flow_en") or ""),
            "notes": dict(value.get("notes") or {}),
        }
        for target, value in dict(profile.get("capability_to_targets") or {}).items()
    }
    return {
        "key": str(profile.get("key") or ""),
        "label": str(profile.get("label") or ""),
        "labelZh": str(profile.get("label_zh") or ""),
        "driverAliases": list(profile.get("driver_aliases") or []),
        "loginMode": str(profile.get("login_mode") or ""),
        "likelyHashes": likely_hashes,
        "hashFieldsSupported": hash_fields_supported,
        "supportsFingerprintEnrichment": supports_fingerprint_enrichment,
        "downloadLinkSupported": str(profile.get("download_link_supported") or ""),
        "captureStrategy": str(profile.get("capture_strategy") or ""),
        "captureStrategyEn": str(profile.get("capture_strategy_en") or ""),
        "docLinks": list(profile.get("doc_links") or []),
        "defaultMountValues": dict(profile.get("default_mount_values") or {}),
        "recommendedRateProfile": str(profile.get("recommended_rate_profile") or "safe"),
        "riskNotes": dict(profile.get("risk_notes") or {}),
        "capabilityToTargets": capability_to_targets,
        "isDynamicInference": bool(profile.get("is_dynamic_inference", False)),
        "dynamicRequiredKeys": list(profile.get("dynamic_required_keys") or []),
        "dynamicMatchedFields": list(profile.get("dynamic_matched_fields") or []),
    }


def list_target_profiles() -> dict[str, dict[str, Any]]:
    return {
        key: _serialize_target_profile(value)
        for key, value in TARGET_PROFILES.items()
    }


def list_source_profiles() -> dict[str, dict[str, Any]]:
    return {
        key: _serialize_source_profile(value)
        for key, value in SOURCE_PROVIDER_PROFILES.items()
    }


def get_source_profile_by_driver(driver: str) -> dict[str, Any]:
    normalized = _normalize_key(driver)
    for profile in SOURCE_PROVIDER_PROFILES.values():
        aliases = [_normalize_key(item) for item in list(profile.get("driver_aliases") or [])]
        if normalized and normalized in aliases:
            return _serialize_source_profile(profile)
    return _serialize_source_profile(SOURCE_PROVIDER_PROFILES["generic"])


def get_source_profile_by_key_or_alias(value: str) -> dict[str, Any]:
    normalized = _normalize_key(value)
    if not normalized:
        return _serialize_source_profile(SOURCE_PROVIDER_PROFILES["generic"])
    for profile in SOURCE_PROVIDER_PROFILES.values():
        profile_key = _normalize_key(profile.get("key") or "")
        aliases = [_normalize_key(item) for item in list(profile.get("driver_aliases") or [])]
        if normalized == profile_key or normalized in aliases:
            return _serialize_source_profile(profile)
    return _serialize_source_profile(SOURCE_PROVIDER_PROFILES["generic"])


def build_driver_target_capability(
    driver: str,
    target: str = "guangya",
    live_driver_fields_map: dict[str, list[OpenListDriverField]] | None = None,
) -> dict[str, Any]:
    source_profile = get_source_profile_by_driver(driver)
    normalized_driver = _normalize_key(driver)
    live_fields = list((live_driver_fields_map or {}).get(normalized_driver) or [])
    if str(source_profile.get("key") or "") == "generic" and live_fields:
        source_profile = build_dynamic_source_profile(driver, live_fields, target=target)
    target_key = str(target or "guangya").strip().lower() or "guangya"
    target_profile = _serialize_target_profile(TARGET_PROFILES.get(target_key, TARGET_PROFILES["guangya"]))
    capability_to_targets = dict(source_profile.get("capabilityToTargets") or {})
    target_capability = dict(capability_to_targets.get(target_key) or {})
    if not target_capability and target_key in {"openlist", "localfs", "webdav", "s3", "seafile", "azureblob", "ftp", "sftp", "smb"}:
        if target_key == "openlist":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 OpenList 目标端，但按普通上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the OpenList target, but it is handled as normal upload/overwrite rather than cross-cloud fast upload.",
                "notes": {
                    "zh": "适合把 OpenList 作为聚合目标端或中转目标端；如果你要真正秒传，仍应优先选择具备元数据导入能力的目标端。",
                    "en": "Use OpenList as an aggregated writable target or relay target. For true metadata-based fast upload, prefer a target that supports direct import.",
                },
            }
        elif target_key == "localfs":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 LocalFS 本地目录目标端，但只按普通下载后写入/覆盖处理，不承诺秒传。",
                "recommendedFlowEn": "This combination can write into the LocalFS target, but it only uses normal download-then-write/overwrite without any fast-upload promise.",
                "notes": {
                    "zh": "适合作为本地导出、联调或兜底目标端；如果你要真正跨盘秒传，仍应优先选择具备元数据导入能力的目标端。",
                    "en": "Use it as a local export, integration-test, or fallback target. For real cross-cloud fast upload, prefer a target with metadata-import support.",
                },
            }
        elif target_key == "webdav":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 WebDAV 目标端，但只按普通上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the WebDAV target, but it only uses normal upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为 NAS、私有云或第三方 WebDAV 的统一目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a unified target for NAS, private cloud, or third-party WebDAV storage. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        elif target_key == "s3":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 S3 目标端，但只按普通对象上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the S3 target, but it only uses normal object upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为对象存储桶、备份桶或云原生归档目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a target for object-storage buckets, backup buckets, or cloud-native archives. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        elif target_key == "seafile":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 Seafile 目标端，但只按普通上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the Seafile target, but it only uses normal upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为团队资料库、私有云文档库或 Seafile 归档目录目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a target for team libraries, private-cloud document vaults, or Seafile archive directories. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        elif target_key == "azureblob":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 Azure Blob 目标端，但只按普通对象上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the Azure Blob target, but it only uses normal object upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为 Azure 对象存储、归档容器或备份容器目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a target for Azure object storage, archive containers, or backup containers. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        elif target_key == "smb":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 SMB 目标端，但只按普通共享目录上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the SMB target, but it only uses normal shared-folder upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为 NAS、局域网共享或 Windows 文件服务器目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a target for NAS, LAN shares, or Windows file servers. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        elif target_key == "ftp":
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 FTP 目标端，但只按普通上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the FTP target, but it only uses normal upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为传统 NAS、服务器目录或轻量存储目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a target for legacy NAS, server directories, or lightweight storage. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        else:
            target_capability = {
                "level": "download_upload_only",
                "recommendedFlow": "当前组合可写入 SFTP 目标端，但只按普通上传/覆盖处理，不承诺跨盘秒传。",
                "recommendedFlowEn": "This combination can write into the SFTP target, but it only uses normal upload/overwrite and does not promise any cross-cloud fast upload.",
                "notes": {
                    "zh": "适合作为 Linux 主机、NAS 或云服务器目录目标端；如果你要真正秒传，仍应优先选择支持元数据导入的目标端。",
                    "en": "Use it as a target for Linux hosts, NAS systems, or cloud-server directories. For true fast upload, still prefer a target with metadata-import support.",
                },
            }
        source_profile = dict(source_profile)
        source_profile["capabilityToTargets"] = {
            **capability_to_targets,
            target_key: dict(target_capability),
        }
    level = str(target_capability.get("level") or "unsupported")
    if level not in CAPABILITY_LEVEL_ORDER:
        level = "unsupported"
    return {
        "driver": str(driver or ""),
        "sourceProfile": source_profile,
        "targetProfile": target_profile,
        "level": level,
        "recommendedFlow": str(target_capability.get("recommendedFlow") or ""),
        "recommendedFlowEn": str(target_capability.get("recommendedFlowEn") or ""),
        "notes": dict(target_capability.get("notes") or {}),
        "isDynamicCapability": bool(source_profile.get("isDynamicInference", False)),
    }


def build_driver_capability_matrix(
    target: str = "guangya",
    live_driver_fields_map: dict[str, list[OpenListDriverField]] | None = None,
) -> dict[str, dict[str, Any]]:
    matrix: dict[str, dict[str, Any]] = {}
    for profile in SOURCE_PROVIDER_PROFILES.values():
        for alias in list(profile.get("driver_aliases") or []):
            matrix[_normalize_key(alias)] = build_driver_target_capability(
                alias,
                target=target,
                live_driver_fields_map=live_driver_fields_map,
            )
    return matrix


def build_source_mapping_context(
    *,
    mount_path: str = "",
    requested_driver: str = "",
    effective_driver: str = "",
    source_profile_override: str = "",
    source_path: str = "",
    target: str = "guangya",
    live_driver_fields_map: dict[str, list[OpenListDriverField]] | None = None,
) -> dict[str, Any]:
    requested = str(requested_driver or "").strip()
    effective = str(effective_driver or requested_driver or "generic").strip() or "generic"
    target_key = str(target or "guangya").strip().lower() or "guangya"
    source_profile = get_source_profile_by_key_or_alias(effective)
    capability = build_driver_target_capability(
        effective,
        target=target_key,
        live_driver_fields_map=live_driver_fields_map,
    )
    target_profile = dict(capability.get("targetProfile") or {})
    capability_level = str(capability.get("level") or "unsupported")
    fallback_strategy = {
        "fast_upload_supported": "metadata_then_fallback",
        "fast_upload_partial": "metadata_then_pending",
        "download_upload_only": "download_upload_only",
        "relay_supported": "stream_relay_first",
        "unsupported": "manual_verify_first",
    }.get(capability_level, "analyze_then_probe")
    provider_key = str(source_profile.get("key") or "")
    if provider_key == "generic":
        provider_key = "generic_openlist_driver"
    target_fast_upload_hashes = list(target_profile.get("fastUploadHashes") or [])
    supports_fast_upload = capability_level in {"fast_upload_supported", "fast_upload_partial"} or bool(target_fast_upload_hashes)
    target_mode = "metadata_import" if target_fast_upload_hashes else "direct_write"
    return {
        "mount_path": str(mount_path or "").strip(),
        "source_path": str(source_path or "").strip(),
        "requested_driver": requested,
        "effective_driver": effective,
        "provider_key": provider_key or _normalize_key(effective) or "generic_openlist_driver",
        "source_profile_key": str(source_profile.get("key") or "generic"),
        "source_mode": "openlist_mount",
        "target_key": target_key,
        "target_mode": target_mode,
        "source_profile_override": str(source_profile_override or "").strip(),
        "supports_fingerprint_enrichment": bool(source_profile.get("supportsFingerprintEnrichment")),
        "supports_direct_target_write": bool(target_profile.get("key")),
        "supports_fast_upload": supports_fast_upload,
        "target_fast_upload_hashes": target_fast_upload_hashes,
        "fallback_strategy": fallback_strategy,
        "capability_level": capability_level,
    }


def build_driver_coverage_audit(
    drivers: list[str],
    target: str = "guangya",
    live_driver_fields_map: dict[str, list[OpenListDriverField]] | None = None,
) -> dict[str, Any]:
    matrix = build_driver_capability_matrix(target=target, live_driver_fields_map=live_driver_fields_map)
    capture_supported_aliases = build_capture_supported_driver_aliases()

    rows: list[dict[str, Any]] = []
    totals = {
        "total": 0,
        "profile": 0,
        "guide": 0,
        "capture": 0,
        "capability": 0,
    }
    gap_buckets = {
        "missingProfile": 0,
        "missingGuide": 0,
        "missingCapture": 0,
        "missingCapability": 0,
        "fullyCovered": 0,
    }
    backlog: list[dict[str, Any]] = []
    for driver in sorted({str(item or "").strip() for item in drivers if str(item or "").strip()}, key=lambda item: item.lower()):
        normalized = _normalize_key(driver)
        profile = get_source_profile_by_driver(driver)
        live_fields = list((live_driver_fields_map or {}).get(normalized) or [])
        profile_is_dynamic = False
        if str(profile.get("key") or "") == "generic" and live_fields:
            profile = build_dynamic_source_profile(driver, live_fields, target=target)
            profile_is_dynamic = True
        has_profile = str(profile.get("key") or "") != "generic"
        guide = get_driver_guide(driver)
        has_guide = guide is not None and not bool((guide or {}).get("isGenericFallback"))
        matched_guide_key, _matched_guide = _resolve_guide_key(driver)
        capture_match = resolve_capture_spec_for_driver(driver)
        capture_is_dynamic = False
        if (not bool(capture_match.get("specKey")) or normalized not in capture_supported_aliases) and live_fields:
            dynamic_spec = build_driver_capture_spec(driver, live_fields)
            capture_match = {
                "driver": driver,
                "normalized": normalized,
                "specKey": dynamic_spec.key,
                "matchedAlias": normalized,
                "label": dynamic_spec.label,
                "loginUrl": dynamic_spec.login_url,
            }
            capture_is_dynamic = True
        has_capture = bool(capture_match.get("specKey")) and (
            normalized in capture_supported_aliases or capture_is_dynamic
        )
        capability = matrix.get(normalized)
        if capability is None and live_fields:
            capability = build_driver_target_capability(
                driver,
                target=target,
                live_driver_fields_map=live_driver_fields_map,
            )
        capability_level = str((capability or {}).get("level") or "")
        has_capability = bool(capability_level and capability_level != "unsupported")
        capability_is_dynamic = bool((capability or {}).get("isDynamicCapability"))
        coverage_score = int(has_profile) + int(has_guide) + int(has_capture) + int(has_capability)
        missing_items: list[str] = []
        if not has_profile:
            missing_items.append("profile")
            gap_buckets["missingProfile"] += 1
        if not has_guide:
            missing_items.append("guide")
            gap_buckets["missingGuide"] += 1
        if not has_capture:
            missing_items.append("capture")
            gap_buckets["missingCapture"] += 1
        if not has_capability:
            missing_items.append("capability")
            gap_buckets["missingCapability"] += 1
        if not missing_items:
            gap_buckets["fullyCovered"] += 1
        if not has_profile:
            next_action = "add_profile_first"
            priority_rank = 1
            onboarding_stage = "needs_profile_bootstrap"
        elif not has_guide:
            next_action = "add_guide"
            priority_rank = 2
            onboarding_stage = "ready_for_guide"
        elif not has_capture:
            next_action = "add_capture_spec"
            priority_rank = 3
            onboarding_stage = "ready_for_capture"
        elif not has_capability:
            next_action = "assess_target_capability"
            priority_rank = 4
            onboarding_stage = "ready_for_capability"
        else:
            next_action = "covered"
            priority_rank = 99
            onboarding_stage = "covered"
        row = {
            "driver": driver,
            "normalized": normalized,
            "canonicalDriverKey": str(profile.get("key") or "generic"),
            "profileKey": str(profile.get("key") or "generic"),
            "hasProfile": has_profile,
            "profileIsDynamic": profile_is_dynamic,
            "hasGuide": has_guide,
            "matchedGuideKey": matched_guide_key,
            "guideDocUrl": str((guide or {}).get("docUrl") or ""),
            "hasCapture": has_capture,
            "captureIsDynamic": capture_is_dynamic,
            "captureSpecKey": str(capture_match.get("specKey") or ""),
            "captureMatchedAlias": str(capture_match.get("matchedAlias") or ""),
            "captureLoginUrl": str(capture_match.get("loginUrl") or ""),
            "captureLabel": str(capture_match.get("label") or ""),
            "hasCapability": has_capability,
            "capabilityIsDynamic": capability_is_dynamic,
            "capabilityLevel": capability_level or "unsupported",
            "onboardingReady": onboarding_stage in {"ready_for_guide", "ready_for_capture", "ready_for_capability"},
            "onboardingStage": onboarding_stage,
            "coverageScore": coverage_score,
            "docLinks": list(profile.get("docLinks") or []),
            "dynamicRequiredKeys": list(profile.get("dynamicRequiredKeys") or []),
            "dynamicMatchedFields": list(profile.get("dynamicMatchedFields") or []),
            "missingItems": missing_items,
            "nextAction": next_action,
            "priorityRank": priority_rank,
        }
        rows.append(row)
        if missing_items:
            backlog.append(
                {
                    "driver": driver,
                    "normalized": normalized,
                    "canonicalDriverKey": str(profile.get("key") or "generic"),
                    "profileKey": str(profile.get("key") or "generic"),
                    "profileIsDynamic": profile_is_dynamic,
                    "matchedGuideKey": matched_guide_key,
                    "capabilityLevel": capability_level or "unsupported",
                    "capabilityIsDynamic": capability_is_dynamic,
                    "onboardingReady": onboarding_stage in {"ready_for_guide", "ready_for_capture", "ready_for_capability"},
                    "onboardingStage": onboarding_stage,
                    "missingItems": missing_items,
                    "nextAction": next_action,
                    "priorityRank": priority_rank,
                    "coverageScore": coverage_score,
                }
            )
        totals["total"] += 1
        totals["profile"] += int(has_profile)
        totals["guide"] += int(has_guide)
        totals["capture"] += int(has_capture)
        totals["capability"] += int(has_capability)
    backlog.sort(key=lambda item: (int(item["priorityRank"]), int(item["coverageScore"]), str(item["driver"]).lower()))
    execution_plan = build_driver_coverage_execution_plan(rows, backlog)
    return {
        "target": target,
        "rows": rows,
        "totals": totals,
        "gapBuckets": gap_buckets,
        "backlog": backlog,
        "executionPlan": execution_plan,
    }


def build_driver_coverage_execution_plan(rows: list[dict[str, Any]], backlog: list[dict[str, Any]]) -> dict[str, Any]:
    row_by_driver = {
        str(item.get("driver") or ""): item
        for item in rows
        if str(item.get("driver") or "").strip()
    }
    grouped: dict[str, dict[str, Any]] = {}
    for item in backlog:
        driver = str(item.get("driver") or "").strip()
        if not driver:
            continue
        row = row_by_driver.get(driver, {})
        priority_rank = int(item.get("priorityRank") or 99)
        next_action = str(item.get("nextAction") or "")
        onboarding_stage = str(item.get("onboardingStage") or "")
        key = f"{priority_rank}:{next_action}:{onboarding_stage}"
        bucket = grouped.setdefault(
            key,
            {
                "key": key,
                "priorityRank": priority_rank,
                "nextAction": next_action,
                "onboardingStage": onboarding_stage,
                "drivers": [],
                "profileKeys": [],
                "missingItems": [],
                "guideDocUrls": [],
                "captureLoginUrls": [],
                "capabilityLevels": [],
            },
        )
        bucket["drivers"].append(driver)
        profile_key = str(item.get("profileKey") or row.get("profileKey") or "").strip()
        if profile_key and profile_key not in bucket["profileKeys"]:
            bucket["profileKeys"].append(profile_key)
        for missing in list(item.get("missingItems") or []):
            value = str(missing or "").strip()
            if value and value not in bucket["missingItems"]:
                bucket["missingItems"].append(value)
        for url in [str(row.get("guideDocUrl") or "")] + list(row.get("docLinks") or []):
            value = str(url or "").strip()
            if value and value not in bucket["guideDocUrls"]:
                bucket["guideDocUrls"].append(value)
        capture_login = str(row.get("captureLoginUrl") or "").strip()
        if capture_login and capture_login not in bucket["captureLoginUrls"]:
            bucket["captureLoginUrls"].append(capture_login)
        capability_level = str(item.get("capabilityLevel") or row.get("capabilityLevel") or "").strip()
        if capability_level and capability_level not in bucket["capabilityLevels"]:
            bucket["capabilityLevels"].append(capability_level)

    waves = []
    for bucket in sorted(grouped.values(), key=lambda item: (int(item["priorityRank"]), str(item["nextAction"]), str(item["onboardingStage"]))):
        waves.append(
            {
                **bucket,
                "count": len(bucket["drivers"]),
                "drivers": sorted(bucket["drivers"], key=str.lower),
            }
        )
    return {
        "totalBacklog": len(backlog),
        "waveCount": len(waves),
        "waves": waves,
    }


def filter_driver_coverage_audit(
    audit: dict[str, Any],
    *,
    only_gaps: bool = False,
    only_onboarding_ready: bool = False,
    next_action: str = "",
    missing_item: str = "",
    capability_level: str = "",
    profile_key: str = "",
    onboarding_stage: str = "",
) -> dict[str, Any]:
    normalized_next_action = str(next_action or "").strip()
    normalized_missing_item = str(missing_item or "").strip()
    normalized_capability_level = str(capability_level or "").strip()
    normalized_profile_key = str(profile_key or "").strip()
    normalized_onboarding_stage = str(onboarding_stage or "").strip()
    rows = list(audit.get("rows") or [])
    filtered_rows = []
    for item in rows:
        missing_items = list(item.get("missingItems") or [])
        if only_gaps and not missing_items:
            continue
        if only_onboarding_ready and not bool(item.get("onboardingReady")):
            continue
        if normalized_next_action and str(item.get("nextAction") or "") != normalized_next_action:
            continue
        if normalized_missing_item and normalized_missing_item not in missing_items:
            continue
        if normalized_capability_level and str(item.get("capabilityLevel") or "") != normalized_capability_level:
            continue
        if normalized_profile_key and str(item.get("profileKey") or "") != normalized_profile_key:
            continue
        if normalized_onboarding_stage and str(item.get("onboardingStage") or "") != normalized_onboarding_stage:
            continue
        filtered_rows.append(item)

    filtered_backlog = [
        item for item in list(audit.get("backlog") or [])
        if any(str(item.get("driver") or "") == str(row.get("driver") or "") for row in filtered_rows)
    ]
    totals = {
        "total": len(filtered_rows),
        "profile": sum(1 for item in filtered_rows if item.get("hasProfile")),
        "guide": sum(1 for item in filtered_rows if item.get("hasGuide")),
        "capture": sum(1 for item in filtered_rows if item.get("hasCapture")),
        "capability": sum(1 for item in filtered_rows if item.get("hasCapability")),
    }
    gap_buckets = {
        "missingProfile": sum(1 for item in filtered_rows if "profile" in list(item.get("missingItems") or [])),
        "missingGuide": sum(1 for item in filtered_rows if "guide" in list(item.get("missingItems") or [])),
        "missingCapture": sum(1 for item in filtered_rows if "capture" in list(item.get("missingItems") or [])),
        "missingCapability": sum(1 for item in filtered_rows if "capability" in list(item.get("missingItems") or [])),
        "fullyCovered": sum(1 for item in filtered_rows if not list(item.get("missingItems") or [])),
    }
    execution_plan = build_driver_coverage_execution_plan(filtered_rows, filtered_backlog)
    return {
        "target": str(audit.get("target") or "guangya"),
        "rows": filtered_rows,
        "totals": totals,
        "gapBuckets": gap_buckets,
        "backlog": filtered_backlog,
        "executionPlan": execution_plan,
        "filters": {
            "onlyGaps": bool(only_gaps),
            "onlyOnboardingReady": bool(only_onboarding_ready),
            "nextAction": normalized_next_action,
            "missingItem": normalized_missing_item,
            "capabilityLevel": normalized_capability_level,
            "profileKey": normalized_profile_key,
            "onboardingStage": normalized_onboarding_stage,
        },
    }


def render_driver_coverage_audit_markdown(audit: dict[str, Any]) -> str:
    target = str(audit.get("target") or "guangya")
    totals = dict(audit.get("totals") or {})
    gap_buckets = dict(audit.get("gapBuckets") or {})
    backlog = list(audit.get("backlog") or [])
    execution_plan = dict(audit.get("executionPlan") or {})
    rows = list(audit.get("rows") or [])
    filters = dict(audit.get("filters") or {})

    lines = [
        "# CloudPan Bridge 驱动覆盖审计",
        "",
        f"- 目标端: `{target}`",
        f"- 驱动总数: `{totals.get('total', 0)}`",
        f"- 已有 profile: `{totals.get('profile', 0)}`",
        f"- 已有 guide: `{totals.get('guide', 0)}`",
        f"- 已有 capture: `{totals.get('capture', 0)}`",
        f"- 已有 capability: `{totals.get('capability', 0)}`",
        "",
        "## 当前筛选",
        "",
        f"- 只看缺口: `{bool(filters.get('onlyGaps'))}`",
        f"- 只看可直接接入: `{bool(filters.get('onlyOnboardingReady'))}`",
        f"- 下一步动作: `{filters.get('nextAction', '') or '-'}`",
        f"- 缺口类型: `{filters.get('missingItem', '') or '-'}`",
        f"- 能力等级: `{filters.get('capabilityLevel', '') or '-'}`",
        f"- Profile Key: `{filters.get('profileKey', '') or '-'}`",
        f"- 接入阶段: `{filters.get('onboardingStage', '') or '-'}`",
        "",
        "## 缺口汇总",
        "",
        f"- 完全覆盖: `{gap_buckets.get('fullyCovered', 0)}`",
        f"- 缺 profile: `{gap_buckets.get('missingProfile', 0)}`",
        f"- 缺 guide: `{gap_buckets.get('missingGuide', 0)}`",
        f"- 缺 capture: `{gap_buckets.get('missingCapture', 0)}`",
        f"- 缺 capability: `{gap_buckets.get('missingCapability', 0)}`",
        "",
        "## 优先级 Backlog",
        "",
    ]

    if backlog:
        for index, item in enumerate(backlog, start=1):
            lines.append(
                f"{index}. `{item.get('driver', '-')}` | P{item.get('priorityRank', '-')} | "
                f"{item.get('nextAction', '-')} | 缺口: {', '.join(item.get('missingItems') or []) or '-'}"
            )
    else:
        lines.append("- 当前已加载驱动都已覆盖。")

    lines.extend(["", "## 执行波次建议", ""])
    waves = list(execution_plan.get("waves") or [])
    if waves:
        for wave in waves:
            driver_list = ", ".join(f"`{item}`" for item in list(wave.get("drivers") or [])) or "-"
            lines.append(
                f"- Wave P{wave.get('priorityRank', '-')} | `{wave.get('nextAction', '-')}` | `{wave.get('onboardingStage', '-')}` | "
                f"数量: `{wave.get('count', 0)}` | 驱动: {driver_list}"
            )
            lines.append(
                f"  - 缺口: `{', '.join(list(wave.get('missingItems') or [])) or '-'}` | "
                f"Profile: `{', '.join(list(wave.get('profileKeys') or [])) or '-'}`"
            )
    else:
        lines.append("- 当前筛选结果下没有待执行波次。")

    lines.extend(["", "## 全量明细", ""])
    if rows:
        lines.append("| Driver | Profile | Guide | Capture | Capability | Level | Score | Next | Capture Spec | Missing |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for item in rows:
            lines.append(
                f"| `{item.get('driver', '-')}` | "
                f"{'yes' if item.get('hasProfile') else 'no'} | "
                f"{'yes' if item.get('hasGuide') else 'no'} | "
                f"{'yes' if item.get('hasCapture') else 'no'} | "
                f"{'yes' if item.get('hasCapability') else 'no'} | "
                f"`{item.get('capabilityLevel', 'unsupported')}` | "
                f"{item.get('coverageScore', 0)}/4 | "
                f"`{item.get('nextAction', '-')}` | "
                f"`{item.get('captureSpecKey', '-') or '-'}` | "
                f"{', '.join(item.get('missingItems') or []) or '-'} |"
            )
    else:
        lines.append("- 暂无驱动数据。")
    lines.append("")
    return "\n".join(lines)


def build_driver_coverage_scaffold(audit: dict[str, Any]) -> dict[str, Any]:
    backlog = list(audit.get("backlog") or [])
    rows = list(audit.get("rows") or [])
    row_by_driver = {
        str(item.get("driver") or ""): item
        for item in rows
        if str(item.get("driver") or "").strip()
    }
    items: list[dict[str, Any]] = []
    for backlog_item in backlog:
        driver = str(backlog_item.get("driver") or "").strip()
        row = row_by_driver.get(driver, {})
        items.append(
            {
                "driver": driver,
                "normalized": str(backlog_item.get("normalized") or ""),
                "canonicalDriverKey": str(backlog_item.get("canonicalDriverKey") or row.get("canonicalDriverKey") or "generic"),
                "profileKey": str(backlog_item.get("profileKey") or row.get("profileKey") or "generic"),
                "nextAction": str(backlog_item.get("nextAction") or ""),
                "priorityRank": int(backlog_item.get("priorityRank") or 99),
                "onboardingStage": str(backlog_item.get("onboardingStage") or ""),
                "missingItems": list(backlog_item.get("missingItems") or []),
                "guideDocUrl": str(row.get("guideDocUrl") or ""),
                "docLinks": list(row.get("docLinks") or []),
                "captureSpecKey": str(row.get("captureSpecKey") or ""),
                "captureLoginUrl": str(row.get("captureLoginUrl") or ""),
                "captureMatchedAlias": str(row.get("captureMatchedAlias") or ""),
                "capabilityLevel": str(backlog_item.get("capabilityLevel") or row.get("capabilityLevel") or "unsupported"),
            }
        )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(str(item.get("nextAction") or "unknown"), []).append(item)
    for key in grouped:
        grouped[key] = sorted(grouped[key], key=lambda item: (int(item.get("priorityRank") or 99), str(item.get("driver") or "").lower()))
    return {
        "target": str(audit.get("target") or "guangya"),
        "filters": dict(audit.get("filters") or {}),
        "summary": {
            "totalBacklog": len(items),
            "actionCount": len(grouped),
        },
        "byNextAction": grouped,
        "items": items,
        "executionPlan": dict(audit.get("executionPlan") or {}),
    }


def render_driver_coverage_scaffold_markdown(scaffold: dict[str, Any]) -> str:
    target = str(scaffold.get("target") or "guangya")
    filters = dict(scaffold.get("filters") or {})
    summary = dict(scaffold.get("summary") or {})
    by_next_action = dict(scaffold.get("byNextAction") or {})
    execution_plan = dict(scaffold.get("executionPlan") or {})

    lines = [
        "# CloudPan Bridge 驱动补全任务",
        "",
        f"- 目标端: `{target}`",
        f"- 待补驱动数: `{summary.get('totalBacklog', 0)}`",
        f"- 动作分组数: `{summary.get('actionCount', 0)}`",
        "",
        "## 当前筛选",
        "",
        f"- 只看缺口: `{bool(filters.get('onlyGaps'))}`",
        f"- 只看可直接接入: `{bool(filters.get('onlyOnboardingReady'))}`",
        f"- 下一步动作: `{filters.get('nextAction', '') or '-'}`",
        f"- 缺口类型: `{filters.get('missingItem', '') or '-'}`",
        f"- 能力等级: `{filters.get('capabilityLevel', '') or '-'}`",
        f"- Profile Key: `{filters.get('profileKey', '') or '-'}`",
        f"- 接入阶段: `{filters.get('onboardingStage', '') or '-'}`",
        "",
        "## 执行建议",
        "",
    ]

    waves = list(execution_plan.get("waves") or [])
    if waves:
        for wave in waves:
            lines.append(
                f"- Wave P{wave.get('priorityRank', '-')} | `{wave.get('nextAction', '-')}` | "
                f"`{wave.get('onboardingStage', '-')}` | 数量: `{wave.get('count', 0)}`"
            )
    else:
        lines.append("- 当前筛选结果下没有待执行波次。")

    lines.extend(["", "## 分组任务清单", ""])
    if not by_next_action:
        lines.append("- 当前筛选结果下没有待补驱动。")
        lines.append("")
        return "\n".join(lines)

    for action, items in by_next_action.items():
        lines.append(f"### `{action or 'unknown'}`")
        lines.append("")
        for index, item in enumerate(list(items or []), start=1):
            missing_items = ", ".join(list(item.get("missingItems") or [])) or "-"
            doc_links = list(item.get("docLinks") or [])
            guide_doc_url = str(item.get("guideDocUrl") or "")
            capture_login_url = str(item.get("captureLoginUrl") or "")
            lines.append(
                f"{index}. `{item.get('driver', '-')}` | P{item.get('priorityRank', '-')} | "
                f"`{item.get('onboardingStage', '-') or '-'}` | "
                f"`{item.get('capabilityLevel', '-') or '-'}`"
            )
            lines.append(f"   - 缺口: `{missing_items}`")
            lines.append(f"   - Profile: `{item.get('profileKey', '-') or '-'}`")
            lines.append(f"   - Canonical: `{item.get('canonicalDriverKey', '-') or '-'}`")
            lines.append(f"   - Capture Spec: `{item.get('captureSpecKey', '-') or '-'}`")
            lines.append(f"   - 登录入口: `{capture_login_url or '-'}`")
            lines.append(f"   - 主文档: `{guide_doc_url or '-'}`")
            doc_candidates = ", ".join(str(link) for link in doc_links) if doc_links else "-"
            lines.append(f"   - 文档候选: `{doc_candidates}`")
        lines.append("")
    return "\n".join(lines)


def assess_driver_target_capability(
    driver: str,
    analysis_summary: dict[str, Any] | None = None,
    target: str = "guangya",
    live_driver_fields_map: dict[str, list[OpenListDriverField]] | None = None,
) -> dict[str, Any]:
    capability = build_driver_target_capability(driver, target=target, live_driver_fields_map=live_driver_fields_map)
    summary = dict(analysis_summary or {})
    total = int(summary.get("total") or 0)
    fast_ready = int(summary.get("fast_upload_ready") or 0)
    md5_ready = int(summary.get("md5_ready") or 0)
    gcid_ready = int(summary.get("gcid_ready") or 0)
    missing_fast = int(summary.get("missing_fast_upload") or 0)
    base_level = str(capability.get("level") or "unsupported")
    assessed_level = base_level
    rationale_zh = "当前未提供目录分析结果，先按静态矩阵建议处理。"
    rationale_en = "No source analysis summary has been provided yet. Fall back to the static matrix."
    source_profile = dict(capability.get("sourceProfile") or {})
    recommended_rate_profile = str(source_profile.get("recommendedRateProfile") or "safe")
    supports_fingerprint_enrichment = bool(source_profile.get("supportsFingerprintEnrichment"))

    if total > 0:
        if base_level == "fast_upload_partial":
            if fast_ready == 0:
                assessed_level = "download_upload_only"
                rationale_zh = "当前目录没有可直接快传的指纹，虽然驱动理论部分支持秒传，但本目录更适合按补传链路处理。"
                rationale_en = "This directory currently has no fast-upload-ready fingerprints. Even though the driver is partially capable in theory, this directory should be treated as fallback upload."
            elif fast_ready == total:
                assessed_level = "fast_upload_supported"
                rationale_zh = "当前目录全部文件都具备可快传指纹，适合优先走秒传/元数据导入。"
                rationale_en = "All files in this directory have fast-upload-ready fingerprints, so metadata-first upload is strongly preferred."
            else:
                assessed_level = "fast_upload_partial"
                rationale_zh = "当前目录只有部分文件具备可快传指纹，建议先秒传再补传。"
                rationale_en = "Only part of this directory is fast-upload ready, so use metadata-first sync and then fallback reupload."
        elif base_level == "download_upload_only":
            if fast_ready > 0 and (md5_ready > 0 or gcid_ready > 0):
                rationale_zh = "当前目录虽然出现了部分快传指纹，但该驱动对 Guangya 默认仍按保守补传策略处理。"
                rationale_en = "Fast-upload fingerprints do exist in this directory, but this driver is still treated conservatively for Guangya."
            else:
                rationale_zh = "当前目录缺少稳定快传指纹，应按下载补传或待补传链路处理。"
                rationale_en = "This directory lacks stable fast-upload fingerprints, so it should follow the fallback upload path."
        elif base_level == "unsupported":
            rationale_zh = "当前组合仍不在支持范围内，不建议继续自动执行。"
            rationale_en = "This combination is still unsupported and should not proceed automatically."
        else:
            rationale_zh = "当前目录分析与静态矩阵基本一致。"
            rationale_en = "The runtime analysis is broadly consistent with the static matrix."

    fast_ratio = (fast_ready / total) if total > 0 else 0.0
    md5_ratio = (md5_ready / total) if total > 0 else 0.0
    gcid_ratio = (gcid_ready / total) if total > 0 else 0.0
    should_analyze_first = total <= 0
    prefer_leaf_mode = recommended_rate_profile == "safe"
    prefer_pending_tree = assessed_level in {"download_upload_only", "unsupported"}
    recommended_mode = "analyze_first"
    throttle_hint_zh = "先按保守节奏运行，必要时再提速。"
    throttle_hint_en = "Start conservatively and increase speed only after validation."
    suggested_actions = [
        {
            "key": "analyze_source",
            "zh": "先分析当前目录，确认 MD5 / GCID 命中率，再决定是否直接同步。",
            "en": "Analyze the current directory first, then decide whether direct sync is suitable.",
        }
    ]

    if recommended_rate_profile == "safe":
        throttle_hint_zh = "建议优先使用 safe 频率，并按最底层目录小批量推进。"
        throttle_hint_en = "Prefer the safe rate profile and move in small leaf-directory batches."
    elif recommended_rate_profile == "balanced":
        throttle_hint_zh = "建议先用 balanced 频率，从小目录验证后再扩大范围。"
        throttle_hint_en = "Start with the balanced rate profile and expand only after a small-directory validation."
    elif recommended_rate_profile == "fast":
        throttle_hint_zh = "当前驱动相对适合快速验证，但仍建议先跑一个小目录。"
        throttle_hint_en = "This driver is relatively fast-friendly, but you should still validate with a small directory first."

    fast_upload_decision = assess_directory_fast_upload(summary, target_capability=capability.get("targetCapability") or capability.get("targetProfile") or {})

    if not should_analyze_first:
        if assessed_level == "fast_upload_supported":
            recommended_mode = "direct_metadata_first"
            prefer_pending_tree = False
            suggested_actions = [
                {
                    "key": "run_direct",
                    "zh": "当前目录快传指纹齐全，优先直接同步或直接导出秒传 JSON。",
                    "en": "This directory is fully fast-upload ready. Prefer direct sync or direct JSON export/import.",
                },
                {
                    "key": "build_miaochuan_json",
                    "zh": "如果你想更稳，可先生成当前目录秒传 JSON，再导入 Guangya。",
                    "en": "For a steadier path, generate a flash-upload JSON for this directory first, then import it into Guangya.",
                },
            ]
        elif assessed_level == "fast_upload_partial":
            recommended_mode = "leaf_metadata_then_pending"
            prefer_pending_tree = fast_ratio < 0.35
            prefer_leaf_mode = True
            suggested_actions = [
                {
                    "key": "run_leaf_direct",
                    "zh": "当前目录只有部分文件能快传，建议优先按最底层目录边扫边秒传。",
                    "en": "Only part of the directory is fast-upload ready. Prefer leaf-directory scan-and-sync first.",
                },
                {
                    "key": "pending_tree",
                    "zh": "未命中的文件保留到待补传树，再按目录勾选补传，避免一开始就大批量下载上传。",
                    "en": "Keep misses in the pending tree and reupload by directory instead of starting with large fallback batches.",
                },
            ]
            if md5_ratio > 0 and gcid_ratio == 0:
                suggested_actions.append(
                    {
                        "key": "md5_bias",
                        "zh": "当前目录更偏 MD5 指纹，建议优先验证光鸭 MD5 秒传命中率。",
                        "en": "This directory is MD5-heavy. Verify Guangya MD5 hit rate first.",
                    }
                )
            elif gcid_ratio > 0 and md5_ratio == 0:
                suggested_actions.append(
                    {
                        "key": "gcid_bias",
                        "zh": "当前目录更偏 GCID 指纹，建议先看 GCID 路径是否稳定可用。",
                        "en": "This directory is GCID-heavy. Check whether the GCID path is stable first.",
                    }
                )
        elif fast_upload_decision.get("level") == "fast_upload_after_enrichment":
            recommended_mode = "enrich_then_direct"
            prefer_pending_tree = False
            prefer_leaf_mode = True
            suggested_actions = [
                {
                    "key": "enrich_fingerprint_first",
                    "zh": "当前目录需要先补指纹，再决定哪些文件能直接秒传。",
                    "en": "Enrich file fingerprints first, then decide which files can use direct fast upload.",
                },
                {
                    "key": "leaf_probe",
                    "zh": "建议先跑一个小叶子目录，确认补指纹命中率后再扩大范围。",
                    "en": "Probe one small leaf directory first, then expand after verifying the enrichment hit rate.",
                },
            ]
            if supports_fingerprint_enrichment:
                suggested_actions.append(
                    {
                        "key": "provider_refresh_supported",
                        "zh": "当前源 Profile 标记为支持补指纹，执行期会优先回查单文件元数据。",
                        "en": "This source profile is marked as enrichment-capable. Runtime execution will refresh per-file metadata first.",
                    }
                )
            else:
                suggested_actions.append(
                    {
                        "key": "provider_refresh_unknown",
                        "zh": "当前源 Profile 没有明确补指纹能力声明，建议先手动验证小目录。",
                        "en": "This source profile has no explicit enrichment capability declared yet. Validate on a small directory first.",
                    }
                )
        elif assessed_level == "relay_supported":
            recommended_mode = "stream_relay_first"
            prefer_pending_tree = False
            suggested_actions = [
                {
                    "key": "stream_relay",
                    "zh": "当前组合更适合中转流传输，不建议宣传成真正秒传。",
                    "en": "This combination is better treated as relay streaming, not true fast upload.",
                },
                {
                    "key": "small_batch",
                    "zh": "先小批量验证下载链路和上传链路，再决定是否扩大范围。",
                    "en": "Validate the download and upload chains on a small batch before scaling up.",
                },
            ]
        elif assessed_level == "download_upload_only":
            recommended_mode = "pending_tree_first"
            prefer_leaf_mode = True
            prefer_pending_tree = True
            suggested_actions = [
                {
                    "key": "pending_tree",
                    "zh": "当前目录更适合先建待补传树，再按目录勾选补传。",
                    "en": "This directory is better handled through the pending tree and directory-based reupload.",
                },
                {
                    "key": "small_file_threshold",
                    "zh": "可只让小文件自动补传，大文件保留到后续分目录处理。",
                    "en": "Limit automatic fallback to small files and keep larger files for later directory-based execution.",
                },
            ]
        elif assessed_level == "unsupported":
            recommended_mode = "manual_verify_first"
            prefer_leaf_mode = False
            prefer_pending_tree = False
            suggested_actions = [
                {
                    "key": "stop_and_verify",
                    "zh": "当前组合暂不支持自动执行，建议先核对驱动文档、登录态和目标端能力。",
                    "en": "This combination is not ready for automatic execution. Verify driver docs, auth state, and target capability first.",
                },
                {
                    "key": "small_probe",
                    "zh": "如果必须继续，只建议用一个极小目录做人工探测，不要直接跑全盘。",
                    "en": "If you must continue, probe with a very small directory only. Do not run the full tree directly.",
                },
            ]

    return {
        **capability,
        "analysisSummary": summary,
        "assessedLevel": assessed_level,
        "fastUploadDecision": fast_upload_decision,
        "rationale": {
            "zh": rationale_zh,
            "en": rationale_en,
        },
        "score": {
            "total": total,
            "fastReady": fast_ready,
            "md5Ready": md5_ready,
            "gcidReady": gcid_ready,
            "missingFast": missing_fast,
        },
        "strategy": {
            "recommendedMode": recommended_mode,
            "suggestedActions": suggested_actions,
            "throttleHint": {
                "zh": throttle_hint_zh,
                "en": throttle_hint_en,
            },
            "shouldAnalyzeFirst": should_analyze_first,
            "preferLeafMode": prefer_leaf_mode,
            "preferPendingTree": prefer_pending_tree,
            "fastReadyRatio": round(fast_ratio, 4),
            "md5ReadyRatio": round(md5_ratio, 4),
            "gcidReadyRatio": round(gcid_ratio, 4),
        },
    }
