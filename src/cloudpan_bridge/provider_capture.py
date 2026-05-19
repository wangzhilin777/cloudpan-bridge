from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from threading import Lock, Thread
from typing import Any

from .openlist_admin import OpenListDriverField


def _normalize_cookie_header(cookies: dict[str, str]) -> str:
    parts = [f"{key}={value}" for key, value in cookies.items() if str(key).strip() and value not in ("", None)]
    return "; ".join(parts)


def _find_nested_token_fields(payload: Any, result: dict[str, Any] | None = None) -> dict[str, Any]:
    result = result or {}
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_lower = str(key).lower()
            if key_lower in {
                "access_token",
                "accesstoken",
                "refresh_token",
                "refreshtoken",
                "token",
                "authorization",
                "device_id",
                "x-device-id",
                "did",
                "dt",
                "bdstoken",
                "captcha_token",
                "x-captcha-token",
                "client_id",
                "x-client-id",
                "session_key",
                "sessionkey",
            }:
                result[key_lower] = value
            elif isinstance(value, (dict, list)):
                _find_nested_token_fields(value, result)
    elif isinstance(payload, list):
        for item in payload:
            _find_nested_token_fields(item, result)
    return result


def _normalize_captured_fields(raw: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in raw.items():
        if value in ("", None, {}, []):
            continue
        key_lower = str(key).lower()
        if key_lower in {"access_token", "accesstoken"}:
            normalized["access_token"] = str(value)
        elif key_lower == "token":
            text = str(value)
            if text.count(".") >= 2:
                normalized["access_token"] = text
            else:
                normalized["token"] = text
        elif key_lower in {"refresh_token", "refreshtoken"}:
            normalized["refresh_token"] = str(value)
        elif key_lower in {"authorization"}:
            normalized["authorization"] = str(value)
        elif key_lower in {"device_id", "x-device-id"}:
            normalized["device_id"] = str(value)
        elif key_lower == "did":
            normalized["did"] = str(value)
            normalized.setdefault("device_id", str(value))
        elif key_lower == "dt":
            normalized["dt"] = str(value)
        elif key_lower == "bdstoken":
            normalized["bdstoken"] = str(value)
        elif key_lower in {"captcha_token", "x-captcha-token"}:
            normalized["captcha_token"] = str(value)
        elif key_lower in {"client_id", "x-client-id"}:
            normalized["client_id"] = str(value)
        elif key_lower in {"session_key", "sessionkey"}:
            normalized["session_key"] = str(value)
        elif key_lower == "cookie_header":
            normalized["cookie_header"] = str(value)
        elif key_lower == "cookies" and isinstance(value, dict):
            normalized["cookies"] = {str(k): str(v) for k, v in value.items() if str(k).strip()}
        elif key_lower == "user_agent":
            normalized["user_agent"] = str(value)
        else:
            normalized[key_lower] = value
    if normalized.get("authorization") and not str(normalized["authorization"]).lower().startswith("bearer "):
        token = str(normalized["authorization"]).strip()
        if token.count(".") >= 2:
            normalized["authorization"] = f"Bearer {token}"
    return normalized


@dataclass(slots=True)
class ProviderCaptureSpec:
    key: str
    label: str
    login_url: str
    session_dir: str
    recommended_drivers: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    required_keys: list[str] = field(default_factory=list)
    header_aliases: list[str] = field(default_factory=list)
    storage_aliases: list[str] = field(default_factory=list)
    page_probe: str = "return {};"
    description: str = ""


@dataclass(slots=True)
class CaptureSnapshot:
    provider: str
    status: str = "idle"
    message: str = ""
    captured: dict[str, Any] = field(default_factory=dict)
    debug_events: list[dict[str, Any]] = field(default_factory=list)


def _slugify_provider_key(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return text or "driver"


def _ordered_unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = str(value or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def normalize_provider_alias(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())
    return text


def guess_login_url_for_driver(driver: str) -> str:
    text = str(driver or "").strip().lower()
    if not text:
        return ""
    mapping = [
        (("quark",), "https://drive.quark.cn/"),
        (("123", "123pan"), "https://www.123pan.com/"),
        (("189", "cloud189"), "https://cloud.189.cn/"),
        (("baidu",), "https://pan.baidu.com/disk/main"),
        (("thunder", "xunlei"), "https://pan.xunlei.com/"),
        (("guangya",), "https://www.guangyapan.com/"),
        (("aliyun", "alipan", "aliyundrive"), "https://www.alipan.com/"),
        (("pikpak",), "https://mypikpak.com/drive/all"),
        (("onedrive",), "https://onedrive.live.com/"),
        (("dropbox",), "https://www.dropbox.com/login"),
        (("google", "gdrive", "googledrive"), "https://drive.google.com/drive/my-drive"),
        (("seafile",), "https://cloud.seafile.com/"),
        (("mega",), "https://mega.nz/fm"),
        (("115",), "https://115.com/"),
    ]
    for keywords, url in mapping:
        if any(keyword in text for keyword in keywords):
            return url
    return ""


def derive_capture_requirements_from_fields(fields: list[OpenListDriverField]) -> dict[str, Any]:
    required_keys: list[str] = []
    header_aliases: list[str] = ["authorization", "cookie", "x-device-id", "did", "dt", "x-captcha-token", "x-client-id"]
    storage_aliases: list[str] = [
        "access_token",
        "refresh_token",
        "token",
        "authorization",
        "device_id",
        "did",
        "dt",
        "bdstoken",
        "captcha_token",
        "client_id",
        "session_key",
        "sessionkey",
        "user_agent",
    ]
    matched_fields: list[str] = []
    for field in fields:
        key = str(field.name or "").strip().lower()
        if not key:
            continue
        matched_fields.append(field.name)
        if "cookie" in key:
            required_keys.append("cookie_header")
        elif "bdstoken" in key:
            required_keys.append("bdstoken")
        elif "refresh" in key:
            required_keys.append("refresh_token")
        elif "access" in key or key.endswith("token"):
            required_keys.append("access_token")
        elif "auth" in key:
            required_keys.append("authorization")
        elif "device" in key or key == "did":
            required_keys.append("device_id")
        elif key == "dt":
            required_keys.append("dt")
        elif "captcha" in key:
            required_keys.append("captcha_token")
        elif "client" in key:
            required_keys.append("client_id")
        elif "session" in key:
            required_keys.append("session_key")
        elif "useragent" in key or "user_agent" in key:
            required_keys.append("user_agent")
    if not required_keys:
        required_keys = ["cookie_header"]
    return {
        "required_keys": _ordered_unique(required_keys),
        "header_aliases": _ordered_unique(header_aliases),
        "storage_aliases": _ordered_unique(storage_aliases),
        "matched_fields": matched_fields,
    }


def build_driver_capture_spec(driver: str, fields: list[OpenListDriverField], login_url: str = "") -> ProviderCaptureSpec:
    hints = derive_capture_requirements_from_fields(fields)
    display_name = str(driver or "UnknownDriver").strip() or "UnknownDriver"
    final_login_url = str(login_url or "").strip() or guess_login_url_for_driver(display_name)
    required = list(hints["required_keys"])
    fields_text = ", ".join(hints["matched_fields"][:10]) or "cookie/token"
    return ProviderCaptureSpec(
        key=f"driver::{_slugify_provider_key(display_name)}",
        label=f"{display_name} 通用抓取",
        login_url=final_login_url,
        session_dir=f"driver-{_slugify_provider_key(display_name)}",
        recommended_drivers=[display_name],
        domains=[],
        required_keys=required,
        header_aliases=list(hints["header_aliases"]),
        storage_aliases=list(hints["storage_aliases"]),
        page_probe="""
        return {
          href: location.href,
          cookie: document.cookie || "",
          userAgent: navigator.userAgent || "",
          access_token: window.localStorage.getItem("access_token") || window.sessionStorage.getItem("access_token") || "",
          refresh_token: window.localStorage.getItem("refresh_token") || window.sessionStorage.getItem("refresh_token") || "",
          session_key: window.localStorage.getItem("sessionKey") || window.sessionStorage.getItem("sessionKey") || ""
        };
        """,
        description=f"按当前 OpenList 驱动字段生成的通用网页登录抓取方案，优先尝试回填: {fields_text}",
    )


def default_provider_specs() -> dict[str, ProviderCaptureSpec]:
    return {
        "guangya": ProviderCaptureSpec(
            key="guangya",
            label="光鸭云盘",
            login_url="https://www.guangyapan.com/",
            session_dir="guangya",
            recommended_drivers=["guangya"],
            domains=["guangyapan.com", "api.guangyapan.com"],
            required_keys=["authorization", "access_token", "refresh_token", "device_id"],
            header_aliases=["authorization", "did", "dt", "x-device-id"],
            storage_aliases=["access_token", "refresh_token", "authorization", "device_id", "did", "dt", "x-device-id"],
            page_probe="""
            return {
              access_token: window.localStorage.getItem("access_token") || "",
              refresh_token: window.localStorage.getItem("refresh_token") || "",
              device_id: window.localStorage.getItem("device_id") || ""
            };
            """,
            description="自动抓取 Guangya Authorization、access_token、refresh_token、device_id。",
        ),
        "quark": ProviderCaptureSpec(
            key="quark",
            label="夸克网盘",
            login_url="https://drive.quark.cn/",
            session_dir="quark",
            recommended_drivers=["Quark", "QuarkOpen", "QuarkTV"],
            domains=["pan.quark.cn", "drive.quark.cn", "drive-pc.quark.cn", "pc-api.uc.cn"],
            required_keys=["cookie_header"],
            header_aliases=["cookie", "authorization"],
            storage_aliases=["access_token", "refresh_token", "token"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              userAgent: navigator.userAgent || ""
            };
            """,
            description="优先抓取夸克 Cookie，供挂载或分享页秒传扩展使用。",
        ),
        "123pan": ProviderCaptureSpec(
            key="123pan",
            label="123 网盘",
            login_url="https://www.123pan.com/",
            session_dir="123pan",
            recommended_drivers=["123Pan", "123Open"],
            domains=["123pan.com", "123pan.cn", "123684.cn"],
            required_keys=["cookie_header"],
            header_aliases=["authorization", "cookie"],
            storage_aliases=["access_token", "refresh_token", "token"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              access_token: window.localStorage.getItem("access_token") || window.sessionStorage.getItem("access_token") || ""
            };
            """,
            description="抓取 123 网盘 Cookie 与常见 token 字段。",
        ),
        "189cloud": ProviderCaptureSpec(
            key="189cloud",
            label="天翼云盘",
            login_url="https://cloud.189.cn/",
            session_dir="189cloud",
            recommended_drivers=["189Cloud", "189CloudPC", "189CloudTV"],
            domains=["cloud.189.cn"],
            required_keys=["cookie_header"],
            header_aliases=["authorization", "cookie"],
            storage_aliases=["access_token", "refresh_token", "sessionKey", "session_key"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              sessionKey: window.localStorage.getItem("sessionKey") || window.sessionStorage.getItem("sessionKey") || ""
            };
            """,
            description="抓取天翼云盘 Cookie 与 sessionKey 类字段，便于后续挂载和元数据扩展。",
        ),
        "baidu": ProviderCaptureSpec(
            key="baidu",
            label="百度网盘",
            login_url="https://pan.baidu.com/disk/main",
            session_dir="baidu",
            recommended_drivers=["BaiduNetdisk", "BaiduPhoto"],
            domains=["pan.baidu.com", "yun.baidu.com"],
            required_keys=["cookie_header", "bdstoken"],
            header_aliases=["cookie"],
            storage_aliases=["bdstoken", "access_token", "refresh_token"],
            page_probe="""
            const page = window;
            const yunData = page.yunData || {};
            const candidates = [
              new URLSearchParams(location.search).get("bdstoken") || "",
              yunData.MYBDSTOKEN || "",
              yunData.bdstoken || "",
              page.locals?.bdstoken || "",
              page.context?.bdstoken || "",
              page.config?.bdstoken || "",
              window.localStorage.getItem("bdstoken") || "",
              window.sessionStorage.getItem("bdstoken") || ""
            ].filter(Boolean);
            return {
              href: location.href,
              cookie: document.cookie || "",
              bdstoken: candidates[0] || ""
            };
            """,
            description="抓取百度 Cookie 与 bdstoken，便于后续目录/文件元数据补全。",
        ),
        "thunder": ProviderCaptureSpec(
            key="thunder",
            label="迅雷云盘",
            login_url="https://pan.xunlei.com/",
            session_dir="thunder",
            recommended_drivers=["Thunder", "ThunderX", "ThunderExpert"],
            domains=["pan.xunlei.com", "api-pan.xunlei.com"],
            required_keys=["authorization", "device_id"],
            header_aliases=["authorization", "x-device-id", "x-captcha-token", "x-client-id", "cookie"],
            storage_aliases=["access_token", "refresh_token", "device_id", "x-device-id"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              userAgent: navigator.userAgent || ""
            };
            """,
            description="抓取迅雷 Authorization、x-device-id、x-captcha-token、x-client-id。",
        ),
        "aliyundriveopen": ProviderCaptureSpec(
            key="aliyundriveopen",
            label="阿里云盘 Open",
            login_url="https://www.alipan.com/",
            session_dir="aliyundriveopen",
            recommended_drivers=["AliyundriveOpen", "AliyunDrive", "Alipan"],
            domains=["alipan.com", "aliyundrive.com", "api.oplist.org"],
            required_keys=["refresh_token"],
            header_aliases=["authorization", "cookie"],
            storage_aliases=["refresh_token", "access_token", "token", "authorization", "device_id"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              access_token: window.localStorage.getItem("access_token") || window.sessionStorage.getItem("access_token") || "",
              refresh_token: window.localStorage.getItem("refresh_token") || window.sessionStorage.getItem("refresh_token") || ""
            };
            """,
            description="优先抓取阿里云盘 Open 的 Refresh Token；如后续仍需在线 API 或开放平台参数，请结合驱动接入说明填写。",
        ),
        "onedrive": ProviderCaptureSpec(
            key="onedrive",
            label="OneDrive",
            login_url="https://onedrive.live.com/",
            session_dir="onedrive",
            recommended_drivers=["OneDrive"],
            domains=["onedrive.live.com", "login.live.com", "microsoft.com", "graph.microsoft.com"],
            required_keys=["refresh_token"],
            header_aliases=["authorization", "cookie"],
            storage_aliases=["refresh_token", "access_token", "token", "authorization"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              access_token: window.localStorage.getItem("access_token") || window.sessionStorage.getItem("access_token") || "",
              refresh_token: window.localStorage.getItem("refresh_token") || window.sessionStorage.getItem("refresh_token") || ""
            };
            """,
            description="优先抓取 OneDrive 登录态里的 refresh_token / access_token；如果最终仍需 Azure 应用参数，请按驱动说明补齐。",
        ),
        "pikpak": ProviderCaptureSpec(
            key="pikpak",
            label="PikPak",
            login_url="https://mypikpak.com/drive/all",
            session_dir="pikpak",
            recommended_drivers=["PikPak"],
            domains=["mypikpak.com", "user.mypikpak.com", "drive.mypikpak.com"],
            required_keys=["refresh_token"],
            header_aliases=["authorization", "cookie"],
            storage_aliases=["refresh_token", "access_token", "token", "authorization", "device_id"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              access_token: window.localStorage.getItem("access_token") || window.sessionStorage.getItem("access_token") || "",
              refresh_token: window.localStorage.getItem("refresh_token") || window.sessionStorage.getItem("refresh_token") || ""
            };
            """,
            description="优先抓取 PikPak refresh_token / access_token；若平台差异导致后续异常，再按驱动说明改用对应端来源。",
        ),
        "139yun": ProviderCaptureSpec(
            key="139yun",
            label="139 云盘",
            login_url="https://yun.139.com/",
            session_dir="139yun",
            recommended_drivers=["139Yun", "139"],
            domains=["yun.139.com"],
            required_keys=["authorization"],
            header_aliases=["authorization", "cookie"],
            storage_aliases=["authorization", "access_token", "token", "refresh_token"],
            page_probe="""
            return {
              href: location.href,
              cookie: document.cookie || "",
              authorization: window.localStorage.getItem("authorization") || window.sessionStorage.getItem("authorization") || ""
            };
            """,
            description="优先抓取 139 云盘 Authorization；目录 ID、代理与更多参数仍建议按驱动接入说明补齐。",
        ),
    }


def build_capture_supported_driver_aliases(
    specs: dict[str, ProviderCaptureSpec] | None = None,
) -> set[str]:
    capture_specs = specs or default_provider_specs()
    aliases: set[str] = set()
    for spec_key, spec in capture_specs.items():
        normalized_key = normalize_provider_alias(spec_key)
        if normalized_key:
            aliases.add(normalized_key)
        normalized_spec = normalize_provider_alias(spec.key)
        if normalized_spec:
            aliases.add(normalized_spec)
        for driver in list(spec.recommended_drivers or []):
            normalized_driver = normalize_provider_alias(driver)
            if normalized_driver:
                aliases.add(normalized_driver)
    return aliases


def build_capture_alias_to_spec_key_map(
    specs: dict[str, ProviderCaptureSpec] | None = None,
) -> dict[str, str]:
    capture_specs = specs or default_provider_specs()
    alias_map: dict[str, str] = {}
    for spec_key, spec in capture_specs.items():
        candidates = [spec_key, spec.key, *(list(spec.recommended_drivers or []))]
        for item in candidates:
            normalized = normalize_provider_alias(item)
            if normalized and normalized not in alias_map:
                alias_map[normalized] = spec_key
    return alias_map


def resolve_capture_spec_for_driver(
    driver: str,
    specs: dict[str, ProviderCaptureSpec] | None = None,
) -> dict[str, str]:
    capture_specs = specs or default_provider_specs()
    alias_map = build_capture_alias_to_spec_key_map(capture_specs)
    normalized = normalize_provider_alias(driver)
    spec_key = alias_map.get(normalized, "")
    spec = capture_specs.get(spec_key) if spec_key else None
    return {
        "driver": str(driver or ""),
        "normalized": normalized,
        "specKey": spec_key,
        "matchedAlias": normalized if spec_key else "",
        "label": str(spec.label) if spec else "",
        "loginUrl": str(spec.login_url) if spec else "",
    }


class ProviderCaptureManager:
    def __init__(self, base_dir: Path, specs: dict[str, ProviderCaptureSpec] | None = None):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.specs = specs or default_provider_specs()
        self.lock = Lock()
        self.max_debug_events = 100
        self.snapshots_map = {
            key: CaptureSnapshot(provider=key, message=f"等待抓取 {spec.label} 登录信息")
            for key, spec in self.specs.items()
        }

    def definitions_payload(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for spec in self.specs.values():
            items.append(
                {
                    "key": spec.key,
                    "label": spec.label,
                    "login_url": spec.login_url,
                    "recommended_drivers": list(spec.recommended_drivers),
                    "required_keys": list(spec.required_keys),
                    "description": spec.description,
                }
            )
        return items

    def snapshots(self) -> dict[str, dict[str, Any]]:
        with self.lock:
            return {key: self._snapshot_to_dict(value) for key, value in self.snapshots_map.items()}

    def snapshot(self, provider: str) -> dict[str, Any]:
        key = str(provider or "").strip().lower()
        with self.lock:
            snapshot = self.snapshots_map.get(key)
            if snapshot is None:
                return {
                    "provider": key,
                    "status": "missing",
                    "message": f"未知 provider: {key}",
                    "captured": {},
                    "debug_events": [],
                }
            return self._snapshot_to_dict(snapshot)

    def start(self, provider: str, spec_override: ProviderCaptureSpec | None = None) -> None:
        key = str(provider or "").strip().lower()
        spec = spec_override
        if spec is None and key not in self.specs:
            raise RuntimeError(f"不支持的 provider: {provider}")
        if spec is None:
            spec = self.specs[key]
        with self.lock:
            current = self.snapshots_map.get(key)
            if current and current.status == "running":
                return
            self.snapshots_map[key] = CaptureSnapshot(
                provider=key,
                status="running",
                message=f"正在打开 Edge 并等待 {spec.label} 登录...",
            )
        Thread(target=self._run, args=(key, spec), daemon=True).start()

    def _snapshot_to_dict(self, snapshot: CaptureSnapshot) -> dict[str, Any]:
        return {
            "provider": snapshot.provider,
            "status": snapshot.status,
            "message": snapshot.message,
            "captured": snapshot.captured,
            "debug_events": list(snapshot.debug_events),
        }

    def _run(self, provider: str, spec: ProviderCaptureSpec) -> None:
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # noqa: BLE001
            self._finish(provider, "error", f"Playwright 不可用: {exc}")
            return

        captured: dict[str, Any] = {}
        debug_events: list[dict[str, Any]] = []

        def update_captured(data: dict[str, Any]) -> None:
            normalized = _normalize_captured_fields(data)
            if not normalized:
                return
            for key, value in normalized.items():
                captured[key] = value

        def push_debug_event(kind: str, url: str, data: dict[str, Any] | None = None) -> None:
            payload = {"kind": kind, "url": url, "data": data or {}}
            debug_events.append(payload)
            if len(debug_events) > self.max_debug_events:
                del debug_events[:-self.max_debug_events]

        def matches_domain(url: str) -> bool:
            return not spec.domains or any(domain in url for domain in spec.domains)

        def complete_if_ready() -> bool:
            return any(str(captured.get(key) or "").strip() for key in spec.required_keys)

        try:
            with sync_playwright() as pw:
                context = pw.chromium.launch_persistent_context(
                    str(self.base_dir / spec.session_dir),
                    headless=False,
                    channel="msedge",
                )
                page = context.pages[0] if context.pages else context.new_page()
                if not spec.login_url:
                    self._finish(provider, "error", f"{spec.label} 缺少登录地址，请先补充 login_url。", captured, debug_events)
                    context.close()
                    return

                def on_request(request) -> None:  # type: ignore[no-untyped-def]
                    if not matches_domain(request.url):
                        return
                    headers = request.headers
                    found: dict[str, Any] = {}
                    for alias in spec.header_aliases:
                        value = headers.get(alias)
                        if value:
                            found[alias] = value
                    if found:
                        update_captured(found)
                        visible = dict(found)
                        if "cookie" in visible:
                            visible["cookie"] = "***"
                        push_debug_event("request", request.url, visible)

                def on_response(response) -> None:  # type: ignore[no-untyped-def]
                    if not matches_domain(response.url):
                        return
                    content_type = response.headers.get("content-type", "")
                    if "application/json" not in content_type:
                        return
                    try:
                        payload = response.json()
                    except Exception:  # noqa: BLE001
                        return
                    found = _find_nested_token_fields(payload)
                    normalized = {key: value for key, value in found.items() if key in {item.lower() for item in spec.storage_aliases}}
                    if normalized:
                        update_captured(normalized)
                        push_debug_event("response", response.url, normalized)

                context.on("request", on_request)
                page.on("response", on_response)
                page.goto(spec.login_url, wait_until="domcontentloaded")

                for _ in range(240):
                    try:
                        cookies = {
                            str(item.get("name") or ""): str(item.get("value") or "")
                            for item in context.cookies()
                            if str(item.get("name") or "").strip()
                        }
                        if cookies:
                            update_captured({"cookies": cookies, "cookie_header": _normalize_cookie_header(cookies)})
                    except Exception:  # noqa: BLE001
                        pass

                    try:
                        storage_dump = page.evaluate(
                            """
                            () => {
                              const result = {};
                              for (const store of [window.localStorage, window.sessionStorage]) {
                                for (let i = 0; i < store.length; i += 1) {
                                  const key = store.key(i);
                                  if (!key) continue;
                                  result[key] = store.getItem(key);
                                }
                              }
                              return result;
                            }
                            """
                        )
                        if isinstance(storage_dump, dict):
                            storage_found: dict[str, Any] = {}
                            for raw_key, raw_value in storage_dump.items():
                                if raw_value in ("", None):
                                    continue
                                key = str(raw_key)
                                if key.lower() in {item.lower() for item in spec.storage_aliases}:
                                    storage_found[key] = raw_value
                                try:
                                    nested = json.loads(str(raw_value))
                                except Exception:  # noqa: BLE001
                                    continue
                                storage_found.update(_find_nested_token_fields(nested))
                            if storage_found:
                                update_captured(storage_found)
                                push_debug_event("storage", "browser-storage", storage_found)
                    except Exception:  # noqa: BLE001
                        pass

                    try:
                        probe_payload = page.evaluate(f"() => {{ {spec.page_probe} }}")
                        if isinstance(probe_payload, dict):
                            update_captured(probe_payload)
                    except Exception:  # noqa: BLE001
                        pass

                    if complete_if_ready():
                        self._finish(provider, "captured", f"已抓到 {spec.label} 登录信息，可回填到页面。", captured, debug_events)
                        context.close()
                        return
                    page.wait_for_timeout(1000)

                self._finish(provider, "timeout", f"等待 {spec.label} 登录抓取超时。", captured, debug_events)
                context.close()
        except Exception as exc:  # noqa: BLE001
            self._finish(provider, "error", f"{spec.label} 抓取失败: {exc}", captured, debug_events)

    def _finish(
        self,
        provider: str,
        status: str,
        message: str,
        captured: dict[str, Any] | None = None,
        debug_events: list[dict[str, Any]] | None = None,
    ) -> None:
        with self.lock:
            self.snapshots_map[provider] = CaptureSnapshot(
                provider=provider,
                status=status,
                message=message,
                captured=captured or {},
                debug_events=debug_events or [],
            )


class GuangyaCaptureManager:
    def __init__(self, base_dir: Path):
        self.manager = ProviderCaptureManager(base_dir)

    def snapshot(self) -> dict[str, Any]:
        return self.manager.snapshot("guangya")

    def start(self) -> None:
        self.manager.start("guangya")


def normalize_provider_capture_entry(provider: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = dict(payload or {})
    captured = _normalize_captured_fields(dict(raw.get("captured") or {}))
    return {
        "provider": str(provider or raw.get("provider") or "").strip().lower(),
        "status": str(raw.get("status") or ("captured" if captured else "idle")),
        "message": str(raw.get("message") or ""),
        "captured": captured,
    }


def build_driver_prefill_values(
    fields: list[OpenListDriverField],
    captured: dict[str, Any] | None,
    provider: str,
) -> dict[str, str]:
    data = _normalize_captured_fields(dict(captured or {}))
    normalized_provider = str(provider or "").strip().lower()
    result: dict[str, str] = {}

    for field in fields:
        field_name = str(field.name or "")
        key = field_name.lower()
        value = ""
        if "cookie" in key:
            value = str(data.get("cookie_header") or "")
        elif "bdstoken" in key:
            value = str(data.get("bdstoken") or "")
        elif "refresh" in key:
            value = str(data.get("refresh_token") or "")
        elif "access" in key or key.endswith("token"):
            value = str(data.get("access_token") or data.get("token") or "")
        elif "auth" in key:
            value = str(data.get("authorization") or "")
        elif "device" in key or key == "did":
            value = str(data.get("device_id") or data.get("did") or "")
        elif key == "dt":
            value = str(data.get("dt") or "")
        elif "captcha" in key:
            value = str(data.get("captcha_token") or "")
        elif "client" in key:
            value = str(data.get("client_id") or "")
        elif "session" in key:
            value = str(data.get("session_key") or "")
        elif "useragent" in key or "user_agent" in key:
            value = str(data.get("user_agent") or "")
        elif normalized_provider == "quark" and "cookie" in key:
            value = str(data.get("cookie_header") or "")
        if value:
            result[field_name] = value
    return result
