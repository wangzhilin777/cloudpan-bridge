from __future__ import annotations

from typing import Any


DRIVER_GUIDES: dict[str, dict[str, Any]] = {
    "aliyundriveopen": {
        "doc_url": "https://doc.oplist.org/guide/drivers/aliyundrive_open",
        "summary": {
            "zh": "AliyundriveOpen 不是简单网页登录就能完成的驱动。通常要先去 OpenList/官方页面获取令牌，再回到这里填写 Refresh Token、Root Folder ID、在线 API 等参数。",
            "en": "AliyundriveOpen is not a simple web-login-only driver. You usually need to obtain tokens first, then come back and fill Refresh Token, Root Folder ID, online API and related fields.",
        },
        "steps": {
            "zh": [
                "先阅读官方文档，确认你走的是 OpenList 内置参数方案，还是你自己的开放平台应用方案。",
                "获取令牌时，打开 api.oplist.org，选择阿里云盘应用登录；如果使用 OpenList 提供参数，则客户端 ID 和密钥留空。",
                "扫码授权后，保存 Refresh Token；Access Token 只作临时展示，真正挂载时重点是 Refresh Token。",
                "新增挂载时，Root Folder ID 默认可填 root；如果只挂某个子目录，就去阿里云盘网页打开该目录，取 URL 里的 folder/file_id。",
                "如果走 OpenList 提供参数方案，勾选 Use online api，并把 Api url address 填成 https://api.oplist.org/alicloud/renewapi 。",
                "如使用自己的开放平台应用，则不要勾选 Use online api，自己填写 Client ID / App Secret，Api url address 留空。",
            ],
            "en": [
                "Read the official doc first and decide whether you use OpenList built-in parameters or your own Open Platform app.",
                "Open api.oplist.org and choose AliYun Drive App Login. If using OpenList parameters, leave Client ID and App Secret empty.",
                "After QR authorization, save the Refresh Token. Access Token is only temporary; the mount mainly needs Refresh Token.",
                "For mounting, Root Folder ID can be root by default. If you only want a subfolder, open that folder on Aliyun Drive web and copy the folder/file_id from the URL.",
                "If using OpenList parameters, enable Use online api and set Api url address to https://api.oplist.org/alicloud/renewapi .",
                "If using your own app, do not enable Use online api, fill Client ID / App Secret yourself, and leave Api url address empty.",
            ],
        },
        "defaults": {
            "root_folder_id": "root",
            "use_online_api": "true",
            "api_url": "https://api.oplist.org/alicloud/renewapi",
            "cloud_drive_type": "Default",
            "livp_download_format": "Jpeg",
        },
    },
    "123open": {
        "doc_url": "https://doc.oplist.org/guide/drivers/123_open",
        "summary": {
            "zh": "123 Open 必须使用你自己的开发者密钥，不能只靠网页登录抓取。需要先申请 client_id 和 client_secret，再填写 Root Folder ID 等参数。",
            "en": "123 Open requires your own developer client_id and client_secret. Web login capture alone is not enough.",
        },
        "steps": {
            "zh": [
                "先去 123 开放平台申请开发者，等待审核通过，拿到 client_id 和 client_secret。",
                "申请过程中如果需要云盘 UID，请先登录 123 网盘网页端，在设置页查看账号 ID。",
                "新增挂载时，Refresh Token 保持留空，直接填写你自己的 Client ID 和 Client Secret。",
                "Root Folder ID 默认填 0；如果只挂某个目录，就在 123 网盘网页打开该目录，取 URL 里的 homeFilePath 数字。",
                "如果要启用直链，先在 123 网盘网页端手动开启直链空间（VIP），再回来配置 Direct Link 相关字段。",
            ],
            "en": [
                "Apply for a developer account on 123 Open Platform and wait for approval to obtain client_id and client_secret.",
                "If the application requires Cloud Drive UID, log in to 123 web and find Account ID in Settings.",
                "When mounting, keep Refresh Token empty and fill your own Client ID and Client Secret directly.",
                "Root Folder ID defaults to 0. If you only want one subfolder, open it on 123 web and copy the homeFilePath number from the URL.",
                "If you want direct links, enable direct-link space manually on the 123 web side first, then come back to configure related fields.",
            ],
        },
        "defaults": {
            "refresh_token": "",
            "root_folder_id": "0",
        },
    },
    "quark": {
        "doc_url": "https://doc.oplist.org/guide/drivers/quark.html",
        "summary": {
            "zh": "夸克 / QuarkOpen 主要依赖 Cookie，且官方文档明确说明现在只能强制使用本地代理传输，不能把网页登录抓取理解成“抓完就稳定可用”。",
            "en": "Quark / QuarkOpen mainly relies on Cookie. The official doc also states transfers now require local proxy, so web capture alone is not the whole setup.",
        },
        "steps": {
            "zh": [
                "打开夸克网页端并登录，按 F12 打开开发者工具，在 Network 里找任意带 Cookie 的请求。",
                "把完整 Cookie 抓出来后回填到挂载字段；如果驱动要求别的认证参数，也一起从请求头里补齐。",
                "根据 OpenList 官方说明，夸克现在传输阶段只能强制使用本地代理，建议 WebDAV/Web 代理策略优先走本机代理。",
                "如果你只是做目录读取，Cookie 抓到后通常就能先试挂；如果还要播放或下载，大概率还要配代理。",
            ],
            "en": [
                "Log in to Quark web, open F12 DevTools, and find any request carrying Cookie in Network.",
                "Copy the full Cookie back into mount fields and add any extra auth headers required by the driver.",
                "According to OpenList docs, Quark transfers now require local proxy, so prefer native/local proxy policies.",
                "Cookie is usually enough for directory listing, but playback/download often still needs proxy.",
            ],
        },
        "defaults": {
            "web_proxy": "true",
            "webdav_policy": "native_proxy",
            "proxy_range": "true",
        },
    },
    "thunder": {
        "doc_url": "https://doc.oplist.org/guide/drivers/thunder",
        "summary": {
            "zh": "迅雷驱动不是普通网页登录模式，通常需要较完整的客户端参数，例如 Authorization、Device ID、Client ID、Captcha Token 等。",
            "en": "Thunder is not a simple browser-login driver. It often needs more complete client parameters such as Authorization, Device ID, Client ID and Captcha Token.",
        },
        "steps": {
            "zh": [
                "优先参考 OpenList 官方文档确认当前支持的客户端来源和版本限制。",
                "如果页面抓取只拿到了部分 Header，不足以挂载时，需要从正式客户端或浏览器请求中补齐 Authorization、x-device-id、x-client-id、x-captcha-token。",
                "填写完成后先用小目录验证；迅雷这类逆向驱动更容易因为参数缺失导致后续列表或下载异常。",
                "如果你主要是读取目录而不是传输，先确认能稳定列目录，再考虑代理和下载策略。",
            ],
            "en": [
                "Check the official OpenList doc first for supported client source and version limits.",
                "If browser capture only gets part of the headers, supplement Authorization, x-device-id, x-client-id and x-captcha-token from the real client/browser requests.",
                "Validate with a small directory first. Reverse-engineered drivers like Thunder are sensitive to missing parameters.",
                "If your goal is directory listing first, make that stable before tuning proxy and download behavior.",
            ],
        },
        "defaults": {
            "proxy_range": "true",
        },
    },
    "baidu": {
        "doc_url": "https://doc.oplist.org/guide/drivers/baidu",
        "summary": {
            "zh": "百度网盘支持多种令牌获取方式。简单 Cookie 抓取并不能替代 Refresh Token / Online API 方案，尤其是正式挂载和大文件下载时。",
            "en": "Baidu Netdisk supports multiple token acquisition flows. Simple Cookie capture is not a replacement for Refresh Token / Online API based mounting.",
        },
        "steps": {
            "zh": [
                "优先使用 OpenList 官方 Token 获取工具获取 Refresh Token；如果有开发者权限，可以走自己的 AppKey/SecretKey。",
                "如果没有开发者权限，可以使用 OpenList 提供参数或 OOB 授权方案。",
                "挂载时如果使用 OpenList 在线 API，要勾选 Use Online API；如果使用自己的开发者参数，反而不要勾选。",
                "百度大文件下载经常需要 User-Agent: pan.baidu.com，若你后续下载异常，优先启用代理或补 UA。",
            ],
            "en": [
                "Prefer the official OpenList token tool to get Refresh Token. If you have developer access, you can use your own AppKey/SecretKey.",
                "Without developer access, use OpenList provided parameters or the OOB authorization flow.",
                "If mounting with OpenList online API, enable Use Online API. If using your own developer keys, do not enable it.",
                "Large Baidu downloads often require User-Agent: pan.baidu.com, so enable proxy or add UA if downloads fail later.",
            ],
        },
        "defaults": {
            "use_online_api": "true",
            "root_folder_path": "/",
            "web_proxy": "true",
        },
    },
    "onedrive": {
        "doc_url": "https://doc.oplist.org/guide/drivers/onedrive",
        "summary": {
            "zh": "OneDrive 可以走 OpenList 在线 API，也可以自己注册 Azure 应用。前者简单，后者更稳更独立。",
            "en": "OneDrive can use the OpenList online API or your own Azure application. The first is simpler, the second is more independent and stable.",
        },
        "steps": {
            "zh": [
                "如果想快速挂载，先去 api.oplist.org 按账号类型选择对应 OneDrive 版本，勾选使用 OpenList 提供参数并获取 Refresh Token。",
                "挂载时勾选 Use online API，填入 Refresh Token 即可。",
                "如果担心公共 API 限流，可以按官方文档在 Azure 注册自己的应用，再把 client_id / client_secret 填回来。",
                "如果你的账号本身不支持 API，可以退回 WebDAV 方案。",
            ],
            "en": [
                "For quick setup, go to api.oplist.org, choose the matching OneDrive type, enable OpenList provided parameters, and get Refresh Token.",
                "Enable Use online API when mounting and fill the Refresh Token.",
                "If you worry about public API limits, register your own Azure application and fill client_id / client_secret.",
                "If your account does not support API, fall back to WebDAV.",
            ],
        },
        "defaults": {
            "use_online_api": "true",
            "chunk_size": "5",
        },
    },
    "pikpak": {
        "doc_url": "https://doc.oplist.org/guide/drivers/pikpak.html",
        "summary": {
            "zh": "PikPak 可以直接账号密码登录，但不同平台和 Refresh Token 来源要对应；如果后续播放/下载异常，通常还要调整平台和代理策略。",
            "en": "PikPak can log in with account/password directly, but platform choice and Refresh Token source must match. Playback/download issues often still require proxy tuning.",
        },
        "steps": {
            "zh": [
                "优先直接填账号密码；如果驱动支持 Oauth2 刷新令牌方式，保存后通常会自动补出 Refresh Token 和设备信息。",
                "如果直接登录不稳定，再按官方文档从 Web 端或 Android 端获取对应平台的 Refresh Token。",
                "Root Folder ID 默认可以填 root；如果你只想挂某个目录，就去 PikPak 网页读取对应目录 ID。",
                "如果出现媒体链接异常或自动转码问题，优先启用 Disable media link 或代理策略。",
            ],
            "en": [
                "Start with account/password. If the driver supports Oauth2 refresh-token mode, saving usually auto-fills Refresh Token and device info.",
                "If direct login is unstable, obtain a matching Refresh Token from Web or Android according to the official guide.",
                "Root Folder ID can default to root. If mounting a specific folder only, read the folder ID from PikPak web.",
                "If media links or transcoding cause issues, enable Disable media link or adjust proxy policy first.",
            ],
        },
        "defaults": {
            "root_folder_id": "root",
        },
    },
    "139yun": {
        "doc_url": "https://doc.oplist.org/guide/drivers/139.html",
        "summary": {
            "zh": "139Yun 依赖浏览器开发者工具抓参数，通常不是单次网页登录抓取就够。重点是 Authorization、云盘类型、目录 ID，以及代理相关设置。",
            "en": "139Yun often requires grabbing parameters from browser DevTools, not just a one-click web login capture.",
        },
        "steps": {
            "zh": [
                "先确认 OpenList 版本符合文档要求，再打开 139 云盘网页。",
                "通过浏览器开发者工具 Network 搜索关键词，抓取 Authorization 等关键参数。",
                "Authorization 只填写 Basic 空格后面的内容，不要把 Basic 前缀一起填进去。",
                "如果要挂某个目录，先进入该目录，再取 currentCatalogID 作为对应文件夹 ID。",
                "如果遇到视频在线播放、断点续传异常，优先启用 Web Proxy 或 WebDAV 本地代理，再考虑打开 Proxy Range。",
            ],
            "en": [
                "Make sure your OpenList version matches the doc requirement, then open 139Yun web.",
                "Use browser DevTools Network search to capture Authorization and other key parameters.",
                "For Authorization, only fill the content after 'Basic ' and do not include the Basic prefix itself.",
                "If mounting a specific folder, enter that folder first and use currentCatalogID as the folder ID.",
                "If playback or range download behaves badly, enable Web Proxy or WebDAV native proxy first, then consider Proxy Range.",
            ],
        },
        "defaults": {
            "proxy_range": "true",
        },
    },
}


def _serialize_driver_guide(guide: dict[str, Any]) -> dict[str, Any]:
    return {
        "docUrl": str(guide.get("doc_url") or ""),
        "summary": dict(guide.get("summary") or {}),
        "steps": {
            "zh": list((guide.get("steps") or {}).get("zh") or []),
            "en": list((guide.get("steps") or {}).get("en") or []),
        },
        "defaults": dict(guide.get("defaults") or {}),
    }


def get_driver_guide(driver: str) -> dict[str, Any] | None:
    key = "".join(ch.lower() for ch in str(driver or "") if ch.isalnum())
    guide = DRIVER_GUIDES.get(key)
    if guide is None:
        return None
    return _serialize_driver_guide(guide)


def list_driver_guides() -> dict[str, dict[str, Any]]:
    return {
        key: _serialize_driver_guide(value)
        for key, value in DRIVER_GUIDES.items()
    }
