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

TARGET_PROFILES: dict[str, dict[str, Any]] = {
    "guangya": {
        "key": "guangya",
        "label": "Guangya",
        "label_zh": "光鸭云盘",
        "auth_mode": "authorization + access_token + refresh_token + device_id",
        "token_refresh": "refresh_token rotating",
        "auto_create_dir": True,
        "fast_upload_hashes": ["md5", "gcid"],
        "fallback_modes": ["stream_upload", "download_upload"],
        "description": {
            "zh": "当前首个正式目标端。优先尝试 MD5 / GCID 元数据秒传，未命中再降级到补传。",
            "en": "Current primary target adapter. It tries MD5 / GCID metadata-based fast upload first, then falls back to reupload.",
        },
        "research_notes": {
            "zh": "已验证 token 写回、目录自动创建、下载补传与元数据秒传基础链路。后续仍需继续补强 token 刷新时机与更细的接口兼容性矩阵。",
            "en": "Token persistence, auto directory creation, reupload fallback, and metadata-based fast upload are already wired. More token-refresh timing and API compatibility details still need expansion.",
        },
    }
}

SOURCE_PROVIDER_PROFILES: dict[str, dict[str, Any]] = {
    "generic": {
        "key": "generic",
        "label": "Generic OpenList Source",
        "label_zh": "通用 OpenList 源",
        "driver_aliases": [],
        "login_mode": "dynamic form or generic web capture",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "unknown",
        "capture_strategy": "先用当前 OpenList driver 字段生成通用抓取模板，再人工验证。",
        "capture_strategy_en": "Generate a generic capture template from current OpenList driver fields, then validate manually.",
        "doc_links": [],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "未知驱动一律按保守模式处理，不能默认承诺秒传。",
            "en": "Unknown drivers are always treated conservatively and should never promise fast upload by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先分析目录，再决定是否下载补传。",
                "recommended_flow_en": "Analyze first, then decide whether to use download-upload fallback.",
                "notes": {
                    "zh": "未知驱动默认按最保守方式处理。只有在确认可提供 MD5 / GCID 后，才建议强化秒传路径。",
                    "en": "Unknown drivers are treated conservatively. Only switch to fast upload after confirming MD5 / GCID is available.",
                },
            }
        },
    },
    "189cloud": {
        "key": "189cloud",
        "label": "189Cloud",
        "label_zh": "天翼云盘",
        "driver_aliases": ["189cloud", "189cloudpc", "189cloudtv"],
        "login_mode": "cookie + sessionKey style fields",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "stable",
        "capture_strategy": "优先抓 Cookie 与 sessionKey，再回填挂载表单。",
        "capture_strategy_en": "Capture Cookie and sessionKey first, then prefill mount fields.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/189cloud"],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "整盘和相册类目录扫描要控制频率，建议先从具体业务目录开始。",
            "en": "Whole-drive and album-like scans should be throttled. Start from concrete working directories first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "优先元数据秒传，未命中时按目录小批量补传。",
                "recommended_flow_en": "Try metadata fast upload first, then reupload small batches by directory.",
                "notes": {
                    "zh": "常见场景下可从 OpenList 拿到 MD5，但整盘扫描时要控制频率。",
                    "en": "MD5 is often available through OpenList, but whole-drive scans should be throttled.",
                },
            }
        },
    },
    "quark": {
        "key": "quark",
        "label": "Quark",
        "label_zh": "夸克网盘",
        "driver_aliases": ["quark", "quarkopen", "quarktv"],
        "login_mode": "cookie focused",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "proxy_sensitive",
        "capture_strategy": "网页端抓 Cookie，必要时补齐请求头，并优先启用本机代理策略。",
        "capture_strategy_en": "Capture Cookie from the web session, add missing headers if needed, and prefer native/local proxy policy.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/quark.html"],
        "default_mount_values": {
            "web_proxy": "true",
            "webdav_policy": "native_proxy",
            "proxy_range": "true",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "夸克对代理与风控更敏感，不适合一开始就跑高并发补传。",
            "en": "Quark is more sensitive to proxy and rate-control issues, so avoid aggressive fallback concurrency.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "先验证当前挂载是否稳定返回哈希，再决定是否跑边扫边同步。",
                "recommended_flow_en": "Verify hash availability first, then decide whether to use streaming leaf sync.",
                "notes": {
                    "zh": "夸克更容易受代理和风控影响，不建议一开始就跑大范围自动补传。",
                    "en": "Quark is more sensitive to proxy and rate control, so avoid aggressive fallback at the beginning.",
                },
            }
        },
    },
    "123pan": {
        "key": "123pan",
        "label": "123Pan",
        "label_zh": "123 网盘",
        "driver_aliases": ["123pan", "123open"],
        "login_mode": "developer credentials or cookie capture fallback",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "conditional",
        "capture_strategy": "Open 驱动优先走开发者参数；普通场景可先抓 Cookie 与常见 token 字段。",
        "capture_strategy_en": "Prefer developer credentials for Open drivers; otherwise capture Cookie and common token fields first.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/123_open"],
        "default_mount_values": {
            "root_folder_id": "0",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "哈希可用性受开放平台参数影响，建议先小目录验证。",
            "en": "Hash availability depends on open-platform parameters, so verify with a small directory first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "优先秒传，失败后保留待补传树，按目录分批补。",
                "recommended_flow_en": "Prefer fast upload first, then keep a pending tree and reupload by directory.",
                "notes": {
                    "zh": "123 的哈希可用性受具体驱动和开放参数影响，建议先用小目录验证。",
                    "en": "Hash availability depends on the exact 123 driver and open-platform parameters. Start with small directories.",
                },
            }
        },
    },
    "baidu": {
        "key": "baidu",
        "label": "Baidu",
        "label_zh": "百度网盘",
        "driver_aliases": ["baidunetdisk", "baiduphoto", "baidu"],
        "login_mode": "refresh token / online api / cookie helpers",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "ua_or_proxy_sensitive",
        "capture_strategy": "优先官方 token 工具或在线 API 方案，Cookie 抓取只作为补充。",
        "capture_strategy_en": "Prefer official token tool or online API flow. Treat Cookie capture only as a supplement.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/baidu"],
        "default_mount_values": {
            "use_online_api": "true",
            "root_folder_path": "/",
            "web_proxy": "true",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "百度大文件和大目录更容易碰到 UA、代理和风控要求。",
            "en": "Large Baidu files and directories are more likely to hit UA, proxy, and rate-control constraints.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "先跑元数据同步，命中不足时优先留待补传，不要直接大批量下载补传。",
                "recommended_flow_en": "Start with metadata sync. If hit rate is low, keep pending items instead of aggressive reupload.",
                "notes": {
                    "zh": "百度大目录更容易碰到风控、UA 和代理要求，适合慢速、分目录推进。",
                    "en": "Large Baidu directories are more likely to hit rate control, UA, and proxy requirements. Move slowly by directory.",
                },
            }
        },
    },
    "thunder": {
        "key": "thunder",
        "label": "Thunder",
        "label_zh": "迅雷云盘",
        "driver_aliases": ["thunder", "thunderx", "thunderexpert", "xunlei"],
        "login_mode": "authorization + device/client headers",
        "likely_hashes": ["gcid"],
        "hash_fields_supported": ["gcid"],
        "download_link_supported": "header_sensitive",
        "capture_strategy": "优先抓 Authorization、x-device-id、x-client-id、x-captcha-token 等完整头信息。",
        "capture_strategy_en": "Capture full Authorization, x-device-id, x-client-id, x-captcha-token, and similar headers first.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/thunder"],
        "default_mount_values": {
            "proxy_range": "true",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "更常见的是 GCID，不是 MD5；逆向驱动对参数完整性更敏感。",
            "en": "GCID is more common than MD5 here, and reverse-engineered drivers are more sensitive to missing parameters.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "优先 GCID 路径，未命中时严格限制补传规模。",
                "recommended_flow_en": "Prefer the GCID path first, then strictly limit fallback reupload batches.",
                "notes": {
                    "zh": "迅雷更常见的是 GCID 而不是 MD5，适合先看元数据分析结果再决定是否继续。",
                    "en": "Thunder more commonly provides GCID instead of MD5. Check the analysis result before scaling up.",
                },
            }
        },
    },
    "aliyundriveopen": {
        "key": "aliyundriveopen",
        "label": "AliyunDrive Open",
        "label_zh": "阿里云盘 Open",
        "driver_aliases": ["aliyundriveopen", "aliyundrive", "alipan", "aliyun"],
        "login_mode": "refresh token + online api or own open platform app",
        "likely_hashes": ["sha1"],
        "hash_fields_supported": ["sha1"],
        "download_link_supported": "stable",
        "capture_strategy": "优先走 OpenList 官方文档推荐的刷新令牌 / 在线 API 流程。",
        "capture_strategy_en": "Prefer the refresh-token / online-API flow recommended by the OpenList documentation.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/aliyundrive_open"],
        "default_mount_values": {
            "root_folder_id": "root",
            "use_online_api": "true",
            "api_url": "https://api.oplist.org/alicloud/renewapi",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "当前更偏 SHA1 指纹链路，若无 MD5 / GCID，对 Guangya 默认按补传处理。",
            "en": "This profile is currently more SHA1-oriented. Without MD5 or GCID, Guangya should default to fallback reupload.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先稳定挂载和目录浏览，再评估是否需要补充外部秒传 JSON。",
                "recommended_flow_en": "Stabilize mounting and browsing first, then decide whether an external fast-upload JSON flow is needed.",
                "notes": {
                    "zh": "阿里云盘更常见的是 SHA1 方向，若缺少 MD5 / GCID，则对 Guangya 通常只能补传。",
                    "en": "AliyunDrive more commonly exposes SHA1-like fingerprints. Without MD5 / GCID, Guangya usually needs reupload fallback.",
                },
            }
        },
    },
    "onedrive": {
        "key": "onedrive",
        "label": "OneDrive",
        "label_zh": "OneDrive",
        "driver_aliases": ["onedrive"],
        "login_mode": "online api or own Azure app",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "stable",
        "capture_strategy": "优先使用在线 API 或 Azure 应用配置，网页登录抓取不是主路径。",
        "capture_strategy_en": "Prefer online API or Azure application configuration. Web capture is not the primary path.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/onedrive"],
        "default_mount_values": {
            "use_online_api": "true",
            "chunk_size": "5",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "若当前驱动不能稳定提供 MD5 / GCID，就不应宣传成对 Guangya 可秒传。",
            "en": "If the current driver cannot provide MD5 or GCID stably, it must not be presented as Guangya fast-upload capable.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "以目录浏览和中转上传为主，不默认承诺秒传。",
                "recommended_flow_en": "Treat it primarily as browse plus relay/upload. Do not promise fast upload by default.",
                "notes": {
                    "zh": "若 OpenList 当前不能稳定提供 MD5 / GCID，就不应把 OneDrive 组合宣传成可秒传。",
                    "en": "If OpenList cannot stably provide MD5 / GCID, the OneDrive combination should not be presented as fast-upload capable.",
                },
            }
        },
    },
    "pikpak": {
        "key": "pikpak",
        "label": "PikPak",
        "label_zh": "PikPak",
        "driver_aliases": ["pikpak"],
        "login_mode": "account password or refresh token",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "conditional",
        "capture_strategy": "先尝试账号密码，再按官方方案补充平台对应的 refresh token。",
        "capture_strategy_en": "Try account-password first, then add a platform-matching refresh token if needed.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/pikpak.html"],
        "default_mount_values": {
            "root_folder_id": "root",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "实际快传能力受平台细节影响更大，当前应按保守策略处理。",
            "en": "Actual fast-upload behavior depends more on platform-specific details, so treat it conservatively for now.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "优先先验证浏览稳定性，再按需小规模补传。",
                "recommended_flow_en": "Verify browsing stability first, then do small fallback batches only when needed.",
                "notes": {
                    "zh": "PikPak 的实际快传能力依赖更多平台细节，当前对 Guangya 应按保守策略提示。",
                    "en": "PikPak fast-upload behavior depends on more platform-specific details, so Guangya should treat it conservatively for now.",
                },
            }
        },
    },
    "139yun": {
        "key": "139yun",
        "label": "139Yun",
        "label_zh": "139 云盘",
        "driver_aliases": ["139yun", "139"],
        "login_mode": "browser devtools capture",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "proxy_sensitive",
        "capture_strategy": "通过浏览器开发者工具抓 Authorization、目录 ID 和代理相关参数。",
        "capture_strategy_en": "Use browser DevTools to capture Authorization, folder IDs, and proxy-related parameters.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/139.html"],
        "default_mount_values": {
            "proxy_range": "true",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "偏浏览器抓参与代理调优型驱动，默认不应承诺对 Guangya 秒传。",
            "en": "This is more of a browser-capture and proxy-tuning driver, so it should not promise Guangya fast upload by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先完成授权参数校验，再谨慎分析哈希情况，不要直接跑整盘。",
                "recommended_flow_en": "Validate auth parameters first, then analyze hashes carefully. Avoid whole-drive runs immediately.",
                "notes": {
                    "zh": "139 更偏浏览器抓参与代理调优型驱动，默认不应承诺对 Guangya 秒传。",
                    "en": "139Yun is more of a browser-capture and proxy-tuning driver, so it should not promise Guangya fast upload by default.",
                },
            }
        },
    },
}

CAPABILITY_LEVEL_ORDER = [
    "fast_upload_supported",
    "fast_upload_partial",
    "relay_supported",
    "download_upload_only",
    "unsupported",
]


def _normalize_key(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


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
    key = _normalize_key(driver)
    guide = DRIVER_GUIDES.get(key)
    if guide is None:
        return None
    return _serialize_driver_guide(guide)


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
        "likelyHashes": list(profile.get("likely_hashes") or []),
        "hashFieldsSupported": list(profile.get("hash_fields_supported") or []),
        "downloadLinkSupported": str(profile.get("download_link_supported") or ""),
        "captureStrategy": str(profile.get("capture_strategy") or ""),
        "captureStrategyEn": str(profile.get("capture_strategy_en") or ""),
        "docLinks": list(profile.get("doc_links") or []),
        "defaultMountValues": dict(profile.get("default_mount_values") or {}),
        "recommendedRateProfile": str(profile.get("recommended_rate_profile") or "safe"),
        "riskNotes": dict(profile.get("risk_notes") or {}),
        "capabilityToTargets": capability_to_targets,
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


def build_driver_target_capability(driver: str, target: str = "guangya") -> dict[str, Any]:
    source_profile = get_source_profile_by_driver(driver)
    target_key = str(target or "guangya").strip().lower() or "guangya"
    target_profile = _serialize_target_profile(TARGET_PROFILES.get(target_key, TARGET_PROFILES["guangya"]))
    target_capability = dict(source_profile.get("capabilityToTargets") or {}).get(target_key, {})
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
    }


def build_driver_capability_matrix(target: str = "guangya") -> dict[str, dict[str, Any]]:
    matrix: dict[str, dict[str, Any]] = {}
    for profile in SOURCE_PROVIDER_PROFILES.values():
        for alias in list(profile.get("driver_aliases") or []):
            matrix[_normalize_key(alias)] = build_driver_target_capability(alias, target=target)
    return matrix
