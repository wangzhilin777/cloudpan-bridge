from __future__ import annotations

from typing import Any

from .openlist_admin import OpenListDriverField
from .provider_capture import (
    build_capture_supported_driver_aliases,
    build_driver_capture_spec,
    derive_capture_requirements_from_fields,
    guess_login_url_for_driver,
    resolve_capture_spec_for_driver,
)


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
    "p123": {
        "doc_url": "https://doc.oplist.org/guide/drivers/123.html",
        "summary": {
            "zh": "P123 更接近 123 网盘的网页登录 / 分享链路驱动，而不是开放平台驱动。重点是账号密码或分享参数，以及本地代理和防盗链相关设置。",
            "en": "P123 is closer to the web-login / share-link style 123 driver rather than the Open Platform driver. The key parts are account/password or share parameters plus local-proxy and anti-hotlink related settings.",
        },
        "steps": {
            "zh": [
                "先确认你要挂的是个人盘还是分享链接，并按文档选择账号密码模式或 share key / share password 模式。",
                "按文档手动填写 username、password 或分享参数，再确认 root_folder_file_id 等目录字段。",
                "优先启用文档要求的本地代理 / WebDAV 策略，不要把它当成简单网页登录抓取后就稳定可用的驱动。",
                "正式跑大目录前，先小目录验证列目录、下载、防盗链和分页稳定性。"
            ],
            "en": [
                "Decide first whether you are mounting a personal drive or a share link, then choose account/password mode or share-key/share-password mode accordingly.",
                "Fill username, password, or share parameters manually and confirm directory fields such as root_folder_file_id.",
                "Enable the local proxy / WebDAV strategy required by the documentation instead of treating it as a simple web-login-capture driver.",
                "Before running large trees, validate listing, download, anti-hotlink behavior, and pagination on a small directory first."
            ],
        },
        "defaults": {
            "web_proxy": "true",
            "webdav_policy": "native_proxy",
            "proxy_range": "true",
            "root_folder_file_id": "0",
        },
    },
    "189cloud": {
        "doc_url": "https://doc.oplist.org/guide/drivers/189",
        "summary": {
            "zh": "天翼云盘驱动通常以 Cookie 与 sessionKey 类字段为主。网页登录抓取可作为快速起步，但正式挂载前仍建议先验证目录读取、小范围下载和分页稳定性。",
            "en": "189Cloud usually relies on Cookie and sessionKey-like fields. Web capture is a good bootstrap path, but you should still validate listing, small downloads, and pagination stability before large jobs.",
        },
        "steps": {
            "zh": [
                "先登录天翼云盘网页端，确认当前账号和目标目录都能正常打开。",
                "如果页面抓取已拿到 Cookie 与 sessionKey 类字段，可先回填挂载表单并尝试小目录读取。",
                "如果驱动字段里出现更多认证项，优先按当前 OpenList 驱动字段名回填，不要自行臆造参数。",
                "大目录同步前，先在本项目里跑一次源目录分析，确认 OpenList 是否能稳定返回 MD5/分页列表。",
            ],
            "en": [
                "Log in to the 189Cloud web app and make sure the account and target folder open correctly.",
                "If web capture already collected Cookie and sessionKey-like fields, prefill the mount form and validate with a small directory first.",
                "If the driver exposes extra auth fields, fill them according to the actual OpenList driver field names rather than inventing values.",
                "Before syncing large trees, run a source analysis in this project and verify that OpenList returns stable MD5 metadata and paginated listing results.",
            ],
        },
        "defaults": {
            "root_folder_id": "-11",
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
    "googledrive": {
        "doc_url": "https://doc.oplist.org/guide/drivers/google_drive",
        "summary": {
            "zh": "Google Drive 更适合走 OpenList 官方推荐的 OAuth / Refresh Token 方案。浏览器抓取可以辅助确认登录态，但正式挂载仍建议以 Google Cloud 应用参数为准。",
            "en": "Google Drive is better handled with the OAuth / Refresh Token flow recommended by OpenList. Browser capture can help inspect the session, but production mounts should still rely on Google Cloud app parameters.",
        },
        "steps": {
            "zh": [
                "先按官方文档在 Google Cloud Console 创建应用，获取 Client ID / Client Secret，并完成 OAuth 同意页面配置。",
                "使用 OpenList 提供的授权流程获取 Refresh Token；如果页面抓取已经拿到 access_token / refresh_token，也只把它当辅助校验，不建议替代正式 OAuth 配置。",
                "挂载前先确认 Root Folder / Team Drive 等参数是否和你的账号类型一致，再用小目录验证列目录与 MD5 返回情况。",
                "如果目录中混有 Google Docs 这类云原生文件，要预期它们不一定具备普通二进制文件那样的 MD5。"
            ],
            "en": [
                "Create a Google Cloud application first, obtain Client ID / Client Secret, and finish the OAuth consent screen setup.",
                "Use the OpenList authorization flow to obtain a Refresh Token. Even if browser capture already sees access_token / refresh_token, treat that only as a verification aid rather than a replacement for the formal OAuth setup.",
                "Before mounting, verify Root Folder / Team Drive related settings, then validate listing and MD5 availability on a small directory.",
                "If the directory contains Google Docs style native files, do not assume they expose normal binary-file MD5 values."
            ],
        },
        "defaults": {
            "root_folder_path": "/",
        },
    },
    "dropbox": {
        "doc_url": "https://doc.oplist.org/guide/drivers/dropbox",
        "summary": {
            "zh": "Dropbox 建议按 OpenList 文档走自己的 OAuth 应用参数和 Refresh Token 流程。浏览器抓到的登录态可以帮助校验，但不应代替正式挂载参数。",
            "en": "For Dropbox, follow the OpenList documentation and use your own OAuth application plus Refresh Token flow. Browser-captured session data is useful for inspection, but should not replace formal mount parameters.",
        },
        "steps": {
            "zh": [
                "先在 Dropbox App Console 创建应用，获取 App Key / App Secret，并确保作用域符合 OpenList 驱动要求。",
                "通过官方 OAuth 流程获取 Refresh Token；页面抓取得到的 access_token 只适合作辅助诊断，不建议长期直接依赖。",
                "先挂一个小目录验证列目录和下载，再决定是否扩大同步范围。",
                "Dropbox 更常见的是 content hash / 版本标识，而不是稳定的 MD5，因此不要默认把它规划成对 Guangya 可秒传的来源。"
            ],
            "en": [
                "Create an app in the Dropbox App Console first, obtain App Key / App Secret, and ensure the scopes match the OpenList driver requirements.",
                "Use the official OAuth flow to obtain a Refresh Token. Any access_token captured from the browser should be treated as diagnostic only, not as a long-term substitute.",
                "Mount a small directory first and validate listing plus download before scaling up.",
                "Dropbox more commonly exposes content-hash or revision style identifiers rather than stable MD5 values, so do not assume it is Guangya fast-upload ready by default."
            ],
        },
        "defaults": {},
    },
    "openlist": {
        "doc_url": "https://doc.oplist.org/guide/drivers/openlist",
        "summary": {
            "zh": "OpenList 互挂适合把另一个 OpenList / AList 实例接进来，重点是 url、用户名密码或 token、meta password、根目录路径，以及代理策略。",
            "en": "The OpenList driver is for mounting another OpenList / AList instance. The key fields are url, username/password or token, meta password, root path, and proxy strategy.",
        },
        "steps": {
            "zh": [
                "先确认目标 OpenList / AList 实例本身能正常访问，且你已经拿到可用的登录方式。",
                "优先按文档手动填写 url、用户名密码或 token；如果源目录本身带 meta password，也一起补上。",
                "根目录路径先从 / 或一个小目录开始验证，确认列目录、分页和下载都稳定后再扩大范围。",
                "如果你是互挂另一个聚合盘，不要默认把它宣传成 Guangya 秒传来源，先分析它透出的哈希能力。"
            ],
            "en": [
                "Confirm that the target OpenList / AList instance is reachable and that you already have a valid login method.",
                "Fill url plus username/password or token manually first, and add meta password when the source path requires it.",
                "Start from / or a small root path, validate listing, pagination, and download stability, then scale up.",
                "If you are mounting another aggregator, do not present it as a Guangya fast-upload source before verifying the exposed hash behavior."
            ],
        },
        "defaults": {
            "root_folder_path": "/",
            "web_proxy": "false",
        },
    },
    "cloudreve": {
        "doc_url": "https://doc.oplist.org/guide/drivers/cloudreve_v4",
        "summary": {
            "zh": "Cloudreve 驱动既可以走 Cookie，也可以走账号密码或 Refresh Token。浏览器抓取适合起步，但正式挂载前仍建议先确认当前实例版本与认证方式。",
            "en": "The Cloudreve driver can work with Cookie, account/password, or Refresh Token. Browser capture is a good bootstrap path, but you should still verify the current instance version and auth mode before production mounting.",
        },
        "steps": {
            "zh": [
                "先确认你对接的是 Cloudreve v3 还是 v4 实例，并核对 OpenList 当前驱动文档对应的字段要求。",
                "如果页面抓取已经拿到 cookie / refresh_token / access_token，可先回填表单并验证一个小目录。",
                "如果实例更适合用户名密码或 API token，就按文档切回手动填写模式，不要强依赖浏览器抓取。",
                "扩大同步范围前，先验证分页、下载直链和中文文件名是否稳定。"
            ],
            "en": [
                "Confirm whether the target instance is Cloudreve v3 or v4 and match the actual driver-field requirements from the OpenList documentation.",
                "If browser capture already collected cookie / refresh_token / access_token, prefill them and validate on a small directory first.",
                "If the instance is better served by account/password or API token, switch back to manual credentials instead of relying on browser capture.",
                "Before scaling up, verify pagination, direct-download links, and non-ASCII filenames."
            ],
        },
        "defaults": {
            "root_folder_path": "/",
        },
    },
    "github": {
        "doc_url": "https://doc.oplist.org/guide/drivers/github",
        "summary": {
            "zh": "GitHub 驱动更像代码仓库读取驱动，核心是 Personal Access Token、owner、repo、ref/branch，以及仓库内容类型选择。",
            "en": "The GitHub driver is more of a repository-content source. The key fields are Personal Access Token, owner, repo, ref/branch, and content type selection.",
        },
        "steps": {
            "zh": [
                "先创建 GitHub Personal Access Token，并确认仓库可见性和 scope 满足当前读取需求。",
                "按文档手动填写 token、owner、repo、ref 或 branch，再用小仓库或小目录验证列表与下载。",
                "如果你读取的是 release 资源、LFS 或大仓库归档，要额外留意速率限制和 API 配额。",
                "默认不要把 GitHub 当成 Guangya 秒传来源；只有确实能拿到稳定 MD5 时，才适合后续再提升能力判断。"
            ],
            "en": [
                "Create a GitHub Personal Access Token first and confirm that repository visibility plus scopes match the read requirements.",
                "Fill token, owner, repo, ref, or branch manually, then validate listing and download on a small repository or subpath.",
                "If you read release assets, LFS, or large repository archives, pay extra attention to rate limits and API quota.",
                "Do not present GitHub as a Guangya fast-upload source by default. Only upgrade later if stable MD5 exposure is actually proven."
            ],
        },
        "defaults": {
            "ref": "main",
        },
    },
    "alias": {
        "doc_url": "https://doc.oplist.org/guide/advanced/alias",
        "summary": {
            "zh": "Alias 不是单一网盘驱动，而是把多个后端路径重新组合成一个逻辑入口。重点是 paths 列表，以及读取、写入、上传冲突时的策略配置。",
            "en": "Alias is not a single cloud driver. It re-combines multiple backend paths into one logical entry. The key pieces are the paths list plus read, write, and upload conflict policies.",
        },
        "steps": {
            "zh": [
                "先确认 Alias 背后的每个后端路径本身都能稳定列目录和下载，再来配置 Alias 聚合层。",
                "按文档手动填写 paths 列表，并明确 read / write / put 等策略，不要默认沿用单盘思维。",
                "如果 Alias 背后混合了多个哈希能力不同的源端，先对小目录做源分析，不要直接把聚合结果宣传成 Guangya 秒传来源。",
                "正式跑大目录前，先用一个小 Alias 目录验证冲突策略、分页与下载行为。"
            ],
            "en": [
                "Confirm that each backend path behind the Alias can already list and download stably before configuring the Alias aggregation layer.",
                "Fill the paths list manually and define read / write / put policies explicitly instead of assuming single-drive defaults.",
                "If the Alias mixes multiple sources with different hash capabilities, analyze a small directory first and do not present the aggregated result as Guangya fast-upload capable by default.",
                "Before running large trees, validate conflict policy, pagination, and download behavior on a small Alias directory."
            ],
        },
        "defaults": {
            "read_policy": "fcfs",
            "write_policy": "fcfs",
            "put_policy": "fcfs",
        },
    },
    "terabox": {
        "doc_url": "https://doc.oplist.org/guide/drivers/terabox",
        "summary": {
            "zh": "TeraBox 当前更偏浏览器抓 Cookie 的驱动。网页登录抓取可以降低接入门槛，但正式挂载前仍要先验证文档里提到的下载方式与风控约束。",
            "en": "TeraBox is currently more of a browser-cookie-oriented driver. Web capture can reduce onboarding friction, but you still need to verify download mode and anti-abuse constraints from the documentation before production use.",
        },
        "steps": {
            "zh": [
                "先登录 TeraBox 网页端，按文档要求从浏览器请求里抓完整 Cookie。",
                "把 Cookie 回填到挂载字段后，先验证一个小目录的列目录与下载，不要一开始就扫整盘。",
                "如果驱动文档要求额外参数或特殊下载方式，优先按当前 OpenList 文档填写，不要自己猜字段。",
                "默认按保守补传路径处理，除非你已经验证当前驱动能稳定给出适合 Guangya 的 MD5。"
            ],
            "en": [
                "Log in to TeraBox web and capture the full Cookie from browser requests as described in the documentation.",
                "After filling the Cookie back into the mount fields, validate listing and download on a small directory first instead of scanning the whole drive.",
                "If the driver requires extra parameters or a special download mode, follow the current OpenList documentation instead of guessing field names.",
                "Default to conservative fallback upload unless you have already verified that the current driver exposes Guangya-usable MD5 values consistently."
            ],
        },
        "defaults": {},
    },
    "yandexdisk": {
        "doc_url": "https://doc.oplist.org/guide/drivers/yandex",
        "summary": {
            "zh": "Yandex Disk 更适合按 OpenList 文档走 OAuth / Refresh Token 流程。浏览器抓取可辅助校验，但正式挂载仍建议以官方授权流程为准。",
            "en": "Yandex Disk is better handled with the OAuth / Refresh Token flow recommended by the OpenList documentation. Browser capture can help inspect the session, but production mounting should still rely on the official authorization flow.",
        },
        "steps": {
            "zh": [
                "先按文档完成 Yandex 的授权流程，获取 Refresh Token。",
                "如果页面抓取已经看到 access_token / refresh_token，也只把它当辅助校验，不建议替代正式 OAuth 配置。",
                "先用一个小目录验证列目录和下载，再确认根目录路径与代理策略。",
                "默认不要把它宣传成 Guangya 秒传来源；只有确认稳定 MD5 后，才适合再提升能力等级。"
            ],
            "en": [
                "Complete the Yandex authorization flow first and obtain a Refresh Token as described in the documentation.",
                "Even if browser capture already sees access_token / refresh_token, treat that only as a verification aid rather than a replacement for the formal OAuth configuration.",
                "Validate listing and download on a small directory first, then confirm root-path and proxy settings.",
                "Do not present it as a Guangya fast-upload source by default. Only upgrade the capability later if stable MD5 is actually confirmed."
            ],
        },
        "defaults": {
            "root_folder_path": "/",
        },
    },
    "webdav": {
        "doc_url": "https://doc.oplist.org/guide/drivers/webdav",
        "summary": {
            "zh": "WebDAV 更偏传统凭证型驱动，不需要浏览器抓 token。通常只要服务地址、用户名、密码，以及必要时的根目录参数就能挂载。",
            "en": "WebDAV is a classic credential-oriented driver and usually does not require browser token capture. In most cases you only need the service URL, username, password, and optionally a root directory path.",
        },
        "steps": {
            "zh": [
                "先确认目标服务端本身支持标准 WebDAV，并且你已经有可用的 URL、账号和密码。",
                "优先先手动填写 URL / username / password，必要时再补根目录、TLS 或只读等参数。",
                "挂载成功后先用一个小目录验证列目录和下载，不要一开始就拿整个站点做大扫描。",
                "如果后续确实能稳定返回 MD5，再考虑是否提升能力判断；默认先按保守补传处理。"
            ],
            "en": [
                "Confirm that the target server really exposes standard WebDAV and that you already have a valid URL, username, and password.",
                "Fill URL / username / password first, then add root-path, TLS, or read-only related options only when needed.",
                "After mounting, validate listing and download with a small directory instead of scanning the entire site immediately.",
                "Only upgrade the capability level later if MD5 is proven to be stable. Default to conservative fallback upload first."
            ],
        },
        "defaults": {},
    },
    "s3": {
        "doc_url": "https://doc.oplist.org/guide/drivers/s3",
        "summary": {
            "zh": "S3 驱动本质上是手动凭证模式。重点是 endpoint、bucket、region，以及 Access Key / Secret Key 的正确组合。",
            "en": "The S3 driver is fundamentally a manual-credential driver. The key pieces are endpoint, bucket, region, and the correct Access Key / Secret Key pair.",
        },
        "steps": {
            "zh": [
                "先确认你用的是哪一类 S3 兼容服务，以及 endpoint、region、bucket 名称是否准确。",
                "手动填写 endpoint、bucket、Access Key、Secret Key，再根据服务端差异补 path style、SSL、region 等参数。",
                "如果对象存储里有大量分片上传对象，要谨慎对待 ETag，把它当成稳定 MD5 前先做小范围验证。",
                "默认先按下载补传或保守中转思路规划，不要直接把 S3 来源宣传成 Guangya 秒传来源。"
            ],
            "en": [
                "Confirm which S3-compatible service you are using and verify the endpoint, region, and bucket name first.",
                "Fill endpoint, bucket, Access Key, and Secret Key manually, then add path-style, SSL, or region options according to the backend.",
                "If the object store contains many multipart-uploaded objects, treat ETag carefully and validate before interpreting it as stable MD5.",
                "Default to conservative fallback upload planning rather than presenting S3 as a Guangya fast-upload source."
            ],
        },
        "defaults": {},
    },
    "ftp": {
        "doc_url": "https://doc.oplist.org/guide/drivers/ftp",
        "summary": {
            "zh": "FTP 驱动也是手动凭证模式，核心是 host、port、username、password，以及是否走被动模式等连接细节。",
            "en": "FTP is also a manual-credential driver. The core fields are host, port, username, password, and connection details such as passive mode.",
        },
        "steps": {
            "zh": [
                "先确认 FTP 服务端地址、端口和账号信息是否可用，并确认 OpenList 所在环境能连通该服务。",
                "优先手动填写 host、port、username、password，再按实际环境补 passive mode、TLS 等参数。",
                "先挂一个小目录验证列目录、中文文件名和下载稳定性。",
                "默认按保守补传处理，不要在没有源分析结果时直接期待它能提供适合 Guangya 秒传的稳定哈希。"
            ],
            "en": [
                "Confirm the FTP server address, port, and account details first, and make sure the OpenList host can reach it.",
                "Fill host, port, username, and password manually, then add passive-mode or TLS related options according to the environment.",
                "Validate listing, non-ASCII filenames, and download stability on a small directory first.",
                "Treat it conservatively by default instead of expecting stable fast-upload-ready hashes without source analysis evidence."
            ],
        },
        "defaults": {},
    },
    "sftp": {
        "doc_url": "https://doc.oplist.org/guide/drivers/sftp",
        "summary": {
            "zh": "SFTP 也是手动凭证型驱动，通常需要主机、端口、用户名和密码，或私钥认证信息。",
            "en": "SFTP is also a manual-credential driver and typically needs host, port, username, password, or private-key based authentication.",
        },
        "steps": {
            "zh": [
                "先确认 SFTP 服务端地址、端口和认证方式，尤其是密码认证还是私钥认证。",
                "手动填写 host、port、username、password 或 private key 相关字段。",
                "先用一个小目录验证列目录与下载，再扩大到大目录。",
                "默认先按下载补传处理，除非你已经通过源分析确认当前驱动能稳定返回可快传指纹。"
            ],
            "en": [
                "Confirm the SFTP server address, port, and authentication method first, especially whether it uses password or private-key authentication.",
                "Fill host, port, username, password, or private-key related fields manually.",
                "Validate listing and download with a small directory first before scaling to larger trees.",
                "Default to fallback upload unless source analysis proves the current driver can expose stable fast-upload-ready fingerprints."
            ],
        },
        "defaults": {},
    },
    "seafile": {
        "doc_url": "https://doc.oplist.org/guide/drivers/seafile",
        "summary": {
            "zh": "Seafile 更适合手动凭证模式，通常要填写服务地址、账号、密码，以及库或目录相关参数。",
            "en": "Seafile is better treated as a manual-credential driver. You usually need the service URL, username, password, and library or folder related parameters.",
        },
        "steps": {
            "zh": [
                "先确认 Seafile 服务地址、账号和库信息都准确可用。",
                "手动填写 URL、username、password、library 等参数，再先挂一个小库验证列目录和下载。",
                "如果后续需要跑大目录，先做源分析确认当前驱动是否真的返回 MD5。",
                "默认按保守补传处理，不把它直接规划成 Guangya 秒传来源。"
            ],
            "en": [
                "Confirm the Seafile service URL, account, and library information first.",
                "Fill URL, username, password, library, and related fields manually, then validate listing and download on a small library first.",
                "Before scaling to large trees, analyze the source and confirm whether the current driver really exposes MD5.",
                "Treat it conservatively by default rather than assuming it is a Guangya fast-upload source."
            ],
        },
        "defaults": {},
    },
    "smb": {
        "doc_url": "https://doc.oplist.org/guide/drivers/smb",
        "summary": {
            "zh": "SMB 是典型的局域网/文件共享型驱动，核心是 host、share、username、password，以及必要时的 workgroup 等连接参数。",
            "en": "SMB is a classic LAN file-share driver. The core fields are host, share, username, password, and sometimes workgroup-related options.",
        },
        "steps": {
            "zh": [
                "先确认 OpenList 所在环境能够连通 SMB 服务端，并且共享名、账号密码都准确。",
                "手动填写 host、share、username、password，必要时补 port、workgroup 等字段。",
                "先小目录验证列目录、下载和中文文件名，再扩大范围。",
                "默认按保守补传处理，不要在没有源分析时直接期待它能提供适合 Guangya 秒传的稳定哈希。"
            ],
            "en": [
                "Confirm that the OpenList host can really reach the SMB server and that the share name plus credentials are correct.",
                "Fill host, share, username, and password manually, then add port or workgroup only when needed.",
                "Validate listing, download, and non-ASCII filenames on a small directory first before scaling up.",
                "Treat it conservatively by default instead of expecting stable Guangya fast-upload-ready hashes without source analysis."
            ],
        },
        "defaults": {},
    },
    "azureblob": {
        "doc_url": "https://doc.oplist.org/guide/drivers/azure_blob",
        "summary": {
            "zh": "Azure Blob 属于对象存储凭证型驱动，重点是 account name、account key、container 和 endpoint 配置。",
            "en": "Azure Blob is an object-storage credential driver. The key fields are account name, account key, container, and endpoint-related options.",
        },
        "steps": {
            "zh": [
                "先确认 account name、account key、container 以及 endpoint 是否准确。",
                "按驱动说明手动填写这些字段，再先用一个小目录或小 container 前缀验证列目录与下载。",
                "如果对象来自多段上传或特殊网关，不要把 ETag 直接当稳定 MD5。",
                "默认先按保守补传处理，除非你已经验证当前对象可以稳定给出适合 Guangya 的 MD5。"
            ],
            "en": [
                "Confirm account name, account key, container, and endpoint values first.",
                "Fill them manually and validate listing plus download on a small path or container prefix first.",
                "If the objects are exposed through multipart uploads or special gateways, do not interpret ETag as stable MD5 by default.",
                "Default to conservative fallback upload unless you have verified that the current objects expose Guangya-usable MD5 values."
            ],
        },
        "defaults": {},
    },
    "mega": {
        "doc_url": "https://doc.oplist.org/guide/drivers/mega",
        "summary": {
            "zh": "MEGA 当前更适合凭证型接入，重点是账号、密码以及根目录相关配置。浏览器登录页可以参考，但正式挂载仍建议按驱动字段手动填写。",
            "en": "MEGA is currently better handled as a credential-oriented driver. The key fields are account, password, and root-directory related settings. The web login page is a useful reference, but the final mount should still be filled manually.",
        },
        "steps": {
            "zh": [
                "先确认 MEGA 账号本身可以正常登录，并确认 OpenList 版本与当前驱动要求相符。",
                "按驱动说明手动填写 email、password、root 等字段。",
                "先挂一个小目录验证列目录和下载，再考虑扩大同步范围。",
                "默认按保守补传处理，不要在没有源分析前直接把它规划成 Guangya 秒传来源。"
            ],
            "en": [
                "Confirm that the MEGA account can log in normally and that the OpenList version matches the driver requirements.",
                "Fill email, password, root, and related fields manually according to the driver documentation.",
                "Validate listing and download on a small directory first before scaling up.",
                "Default to conservative fallback upload instead of presenting it as a Guangya fast-upload source without source-analysis proof."
            ],
        },
        "defaults": {},
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
    "115": {
        "doc_url": "https://doc.oplist.org/guide/drivers/115",
        "summary": {
            "zh": "115 更偏 Cookie / 浏览器态驱动。网页登录抓取能明显降低接入门槛，但正式跑大目录前仍要先验证下载链路、pickcode/哈希返回情况和风控表现。",
            "en": "115 is more of a Cookie / browser-session oriented driver. Web login capture reduces onboarding friction, but you should still verify download behavior, pickcode/hash availability, and rate-control behavior before scanning large trees.",
        },
        "steps": {
            "zh": [
                "先登录 115 网页端，确认账号本身可以正常列目录和打开目标目录。",
                "优先抓 Cookie 与常见 token 字段，按当前 OpenList 驱动字段名回填，不要自行猜测字段名。",
                "如果后续需要更强的秒传/链路判断，要额外关注 pickcode、sha1、md5 等字段在当前驱动里是否真的可见。",
                "大目录执行前先跑源分析，确认当前挂载到底返回了哪些哈希，再决定是优先元数据路径还是直接按补传规划。"
            ],
            "en": [
                "Log in to the 115 web app first and make sure the account can list directories and open the target folder normally.",
                "Capture Cookie and common token fields first, then prefill the exact OpenList driver field names instead of inventing names.",
                "If you later need stronger fast-upload decisions, explicitly inspect whether pickcode, sha1, md5, and similar fields are truly exposed by the current driver.",
                "Before running large trees, analyze the source directory first and verify which hashes the current mount really returns, then decide whether to prioritize metadata-first flow or fallback upload planning."
            ],
        },
        "defaults": {},
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
    },
    "openlist": {
        "key": "openlist",
        "label": "OpenList",
        "label_zh": "OpenList 挂载目标",
        "auth_mode": "openlist token or username/password",
        "token_refresh": "reuse OpenList auth session",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload"],
        "description": {
            "zh": "第二个正式目标端。用于把源端文件写入 OpenList 挂载目录，当前按普通上传/覆盖链路处理，不承诺跨盘秒传。",
            "en": "Second built-in writable target. It writes files into an OpenList mount and currently uses normal upload/overwrite only, not cross-cloud fast upload.",
        },
        "research_notes": {
            "zh": "当前以 OpenList fs mkdir / remove / form 接口为基础，适合作为真实可写目标端，但仍属于保守中转能力，不应宣传成秒传目标。",
            "en": "This target is based on OpenList fs mkdir / remove / form APIs. It is a real writable target, but still a conservative relay/upload path rather than a fast-upload target.",
        },
    },
    "localfs": {
        "key": "localfs",
        "label": "LocalFS",
        "label_zh": "本地目录目标",
        "auth_mode": "local filesystem path",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "local_copy"],
        "description": {
            "zh": "第三个正式目标端。用于把同步结果直接写入本机目录，适合作为调试、导出或保底目标端。",
            "en": "Third built-in writable target. It writes sync results directly into a local folder and is useful as a debug, export, or fallback target.",
        },
        "research_notes": {
            "zh": "不依赖额外云盘接口，适合作为真实可写适配器样板，但不应宣传成跨盘秒传目标端。",
            "en": "It does not depend on extra cloud APIs and works well as a real writable adapter template, but it should never be presented as a cross-cloud fast-upload target.",
        },
    },
    "webdav": {
        "key": "webdav",
        "label": "WebDAV",
        "label_zh": "WebDAV 目标端",
        "auth_mode": "webdav url + username/password",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第四个正式可写目标端。用于把同步结果写入任意 WebDAV 服务，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Fourth built-in writable target. It writes sync results into any WebDAV service and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为 NAS、私有网盘或第三方 WebDAV 存储的统一目标端；当前能力定位仍是保守上传链路，而不是真跨盘秒传。",
            "en": "Useful as a unified target for NAS, private cloud, or third-party WebDAV storage. The current capability is still a conservative upload path rather than real cross-cloud fast upload.",
        },
    },
    "s3": {
        "key": "s3",
        "label": "S3",
        "label_zh": "S3 / 对象存储目标",
        "auth_mode": "endpoint + bucket + access key/secret",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第七个正式可写目标端。用于把同步结果写入 S3 或兼容对象存储，当前只按普通对象上传/覆盖处理，不承诺元数据秒传。",
            "en": "Seventh built-in writable target. It writes sync results into S3 or compatible object storage and currently uses normal object upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为对象存储桶、备份桶或云原生归档目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a target for object-storage buckets, backup buckets, or cloud-native archives. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
    "azureblob": {
        "key": "azureblob",
        "label": "Azure Blob",
        "label_zh": "Azure Blob 目标",
        "auth_mode": "account url + container + account key",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第九个正式可写目标端。用于把同步结果写入 Azure Blob 容器，当前只按普通对象上传/覆盖处理，不承诺元数据秒传。",
            "en": "Ninth built-in writable target. It writes sync results into Azure Blob containers and currently uses normal object upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为 Azure 对象存储、归档容器或备份容器目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a target for Azure object storage, archive containers, or backup containers. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
    "smb": {
        "key": "smb",
        "label": "SMB",
        "label_zh": "SMB 共享目标",
        "auth_mode": "smb url + username/password",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第八个正式可写目标端。用于把同步结果写入 SMB 共享目录，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Eighth built-in writable target. It writes sync results into SMB share directories and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为 NAS、局域网共享或 Windows 文件服务器目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a target for NAS, LAN shares, or Windows file servers. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
    "ftp": {
        "key": "ftp",
        "label": "FTP",
        "label_zh": "FTP 目标端",
        "auth_mode": "ftp url + username/password",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第五个正式可写目标端。用于把同步结果写入 FTP 存储，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Fifth built-in writable target. It writes sync results into FTP storage and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为传统 NAS、主机面板或轻量服务器目录型目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a directory-style target for legacy NAS, hosting panels, or lightweight servers. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
    "sftp": {
        "key": "sftp",
        "label": "SFTP",
        "label_zh": "SFTP 目标端",
        "auth_mode": "sftp url + username/password",
        "token_refresh": "not required",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第六个正式可写目标端。用于把同步结果写入 SFTP 存储，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Sixth built-in writable target. It writes sync results into SFTP storage and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为 Linux 主机、NAS 或云服务器目录型目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a directory-style target for Linux hosts, NAS systems, or cloud servers. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
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
        "doc_links": ["https://doc.oplist.org/guide/drivers/189"],
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
    "p123": {
        "key": "p123",
        "label": "P123",
        "label_zh": "123 网盘网页/分享驱动",
        "driver_aliases": ["p123", "123sharelink"],
        "login_mode": "manual username/password or share params",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "proxy_sensitive",
        "capture_strategy": "优先手动填写账号密码或分享参数，再按文档启用本地代理与 WebDAV 策略。",
        "capture_strategy_en": "Fill account/password or share parameters manually first, then enable the local-proxy and WebDAV strategy required by the documentation.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/123.html"],
        "default_mount_values": {
            "web_proxy": "true",
            "webdav_policy": "native_proxy",
            "proxy_range": "true",
            "root_folder_file_id": "0",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "P123 更偏网页登录与本地代理调优型驱动，默认不应承诺对 Guangya 秒传。",
            "en": "P123 is more of a web-login and local-proxy-tuning driver, so it should not promise Guangya fast upload by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先完成账号/分享参数与本地代理校验，再按保守补传路径推进。",
                "recommended_flow_en": "Validate account/share parameters and local-proxy behavior first, then continue through conservative fallback upload.",
                "notes": {
                    "zh": "在没有确认稳定 MD5 / GCID 前，不应把 P123 默认宣传成 Guangya 秒传来源。",
                    "en": "Without confirmed stable MD5 / GCID, P123 should not be presented as a Guangya fast-upload source by default.",
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
        "driver_aliases": ["onedrive", "sharepoint"],
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
    "googledrive": {
        "key": "googledrive",
        "label": "Google Drive",
        "label_zh": "Google Drive",
        "driver_aliases": ["googledrive", "googledriveshare", "googlephotos", "gdrive"],
        "login_mode": "oauth refresh token + google cloud app",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "stable",
        "capture_strategy": "优先走 Google OAuth / Refresh Token 正式方案，浏览器抓取只作为辅助检查登录态。",
        "capture_strategy_en": "Prefer the formal Google OAuth / Refresh Token flow. Browser capture should be used only as a session-inspection helper.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/google_drive"],
        "default_mount_values": {
            "root_folder_path": "/",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "Google Docs 等云原生文件不一定具备普通二进制文件的 MD5，建议先小目录验证。",
            "en": "Google-native files such as Google Docs may not expose binary-style MD5 values, so validate with a small directory first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "先分析当前目录的 MD5 覆盖率，命中率高时优先元数据同步，否则按待补传树保守推进。",
                "recommended_flow_en": "Analyze MD5 coverage first. If the hit rate is high, prefer metadata sync; otherwise move conservatively through the pending tree.",
                "notes": {
                    "zh": "Google Drive 对普通二进制文件常能拿到 MD5，但云原生文档和共享盘结构要单独留意。",
                    "en": "Google Drive often exposes MD5 for regular binary files, but native docs and shared-drive structures need extra caution.",
                },
            }
        },
    },
    "dropbox": {
        "key": "dropbox",
        "label": "Dropbox",
        "label_zh": "Dropbox",
        "driver_aliases": ["dropbox"],
        "login_mode": "oauth refresh token + app credentials",
        "likely_hashes": ["content_hash"],
        "hash_fields_supported": ["etag"],
        "download_link_supported": "stable",
        "capture_strategy": "优先使用自己的 Dropbox 应用参数和 Refresh Token，浏览器抓取只作为辅助诊断。",
        "capture_strategy_en": "Prefer your own Dropbox app credentials plus Refresh Token. Use browser capture only as a diagnostic aid.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/dropbox"],
        "default_mount_values": {},
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "Dropbox 更常见的是 content hash / revision 等标识，不应默认承诺对 Guangya 可秒传。",
            "en": "Dropbox more commonly exposes content-hash or revision style identifiers, so do not promise Guangya fast upload by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先稳定挂载和小目录下载，再按补传或中转上传链路规划，不默认承诺秒传。",
                "recommended_flow_en": "Stabilize mounting and small-directory downloads first, then plan via fallback upload or relay-like flow without promising fast upload.",
                "notes": {
                    "zh": "如果后续确认当前 OpenList 驱动能稳定补出 MD5，再考虑提升能力等级；默认先按保守补传处理。",
                    "en": "Only upgrade this capability later if the current OpenList driver is proven to expose stable MD5 values. Default to conservative fallback upload first.",
                },
            }
        },
    },
    "openlist": {
        "key": "openlist",
        "label": "OpenList",
        "label_zh": "OpenList / AList",
        "driver_aliases": ["openlist", "alistv3"],
        "login_mode": "manual url + username/password or token",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "stable",
        "capture_strategy": "优先手动填写 url、用户名密码或 token，再按需要补 meta password、根目录路径与代理策略。",
        "capture_strategy_en": "Fill url plus username/password or token first, then add meta password, root path, and proxy strategy as needed.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/openlist"],
        "default_mount_values": {
            "root_folder_path": "/",
            "web_proxy": "false",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "如果你互挂的是另一个聚合盘，底层真实哈希能力仍要靠源分析确认，默认先按保守补传处理。",
            "en": "If you are mounting another aggregator, the real hash capability still depends on the underlying source analysis. Default to conservative fallback upload first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先验证列目录、分页和下载，再按保守补传路径推进，不默认承诺秒传。",
                "recommended_flow_en": "Validate listing, pagination, and download first, then continue through conservative fallback upload without promising fast upload by default.",
                "notes": {
                    "zh": "互挂 OpenList 不代表天然可秒传，只有底层源端稳定提供 MD5 / GCID 时才适合后续提升能力等级。",
                    "en": "Mounting another OpenList does not imply native fast upload. Only upgrade later if the underlying source stably exposes MD5 / GCID.",
                },
            }
        },
    },
    "cloudreve": {
        "key": "cloudreve",
        "label": "Cloudreve",
        "label_zh": "Cloudreve",
        "driver_aliases": ["cloudreve", "cloudrevev3", "cloudrevev4"],
        "login_mode": "cookie or refresh token or account password",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "stable",
        "capture_strategy": "优先抓取 refresh_token / access_token 或 Cookie，再结合当前实例版本决定是否改回用户名密码。",
        "capture_strategy_en": "Capture refresh_token / access_token or Cookie first, then decide whether the current instance should switch back to account-password mode.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/cloudreve_v4"],
        "default_mount_values": {
            "root_folder_path": "/",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "Cloudreve 的认证方式和哈希暴露更依赖具体实例版本，正式跑前一定先做小目录验证。",
            "en": "Cloudreve authentication and hash exposure depend more on the specific instance version, so always validate on a small directory first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先小目录验证分页、下载和认证方式，再按补传链路推进。",
                "recommended_flow_en": "Validate pagination, download, and auth mode on a small directory first, then continue through fallback upload.",
                "notes": {
                    "zh": "只有确认当前实例稳定给出 MD5 后，才适合考虑更激进的元数据同步路径。",
                    "en": "Only consider a more aggressive metadata-first path after the current instance is proven to expose stable MD5 values.",
                },
            }
        },
    },
    "github": {
        "key": "github",
        "label": "GitHub",
        "label_zh": "GitHub",
        "driver_aliases": ["github"],
        "login_mode": "manual token + owner + repo",
        "likely_hashes": ["sha1"],
        "hash_fields_supported": ["sha1"],
        "download_link_supported": "stable",
        "capture_strategy": "按文档手动填写 token、owner、repo、ref/branch 等字段，不依赖浏览器抓取。",
        "capture_strategy_en": "Fill token, owner, repo, ref/branch, and related fields manually instead of relying on browser capture.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/github"],
        "default_mount_values": {
            "ref": "main",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "GitHub 更偏代码仓库读取场景，常见指纹更接近 sha1 / blob 标识，不应默认承诺 Guangya 秒传。",
            "en": "GitHub is more of a repository-content source. Its common fingerprints are closer to sha1/blob identifiers and should not promise Guangya fast upload by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先用小仓库验证列目录与下载，再按保守补传路径推进。",
                "recommended_flow_en": "Validate listing and download on a small repository first, then continue through conservative fallback upload.",
                "notes": {
                    "zh": "GitHub 常见是 sha1 而不是稳定 MD5，默认不应当作 Guangya 秒传来源。",
                    "en": "GitHub commonly exposes sha1 rather than stable MD5, so it should not be treated as a Guangya fast-upload source by default.",
                },
            }
        },
    },
    "alias": {
        "key": "alias",
        "label": "Alias",
        "label_zh": "Alias 聚合目录",
        "driver_aliases": ["alias"],
        "login_mode": "manual alias path list + policy",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "depends_on_backend",
        "capture_strategy": "手动填写后端 paths 列表与读写冲突策略，再结合底层真实后端做小目录验证。",
        "capture_strategy_en": "Fill backend paths plus read/write conflict policy manually, then validate on a small directory against the real underlying backends.",
        "doc_links": ["https://doc.oplist.org/guide/advanced/alias"],
        "default_mount_values": {
            "read_policy": "fcfs",
            "write_policy": "fcfs",
            "put_policy": "fcfs",
        },
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "Alias 的真实哈希能力取决于背后的源端组合，默认不能把它直接宣传成 Guangya 秒传来源。",
            "en": "The real hash capability of Alias depends on the underlying source combination, so it must not be presented as a Guangya fast-upload source by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先分析 Alias 背后的实际后端与哈希覆盖率，再按保守补传路径推进。",
                "recommended_flow_en": "Analyze the real backends and fingerprint coverage behind the Alias first, then continue through conservative fallback upload.",
                "notes": {
                    "zh": "只有确认 Alias 背后的实际源端稳定给出 MD5 / GCID 时，才适合后续再提升能力判断。",
                    "en": "Only upgrade the capability later if the actual sources behind the Alias are proven to expose stable MD5 / GCID values.",
                },
            }
        },
    },
    "terabox": {
        "key": "terabox",
        "label": "TeraBox",
        "label_zh": "TeraBox",
        "driver_aliases": ["terabox"],
        "login_mode": "browser cookie capture",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "conditional",
        "capture_strategy": "优先抓取浏览器 Cookie，再按当前驱动文档补额外字段与下载策略。",
        "capture_strategy_en": "Capture the browser Cookie first, then add extra fields and download strategy according to the current driver documentation.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/terabox"],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "TeraBox 更偏逆向 Cookie 驱动，风控与下载限制更敏感，正式跑前一定先做小目录验证。",
            "en": "TeraBox is more of a reverse-engineered Cookie-based driver, so anti-abuse and download limits are more sensitive. Always validate on a small directory first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先小目录验证下载，再按保守补传路径推进，不默认承诺秒传。",
                "recommended_flow_en": "Validate download on a small directory first, then continue through conservative fallback upload without promising fast upload by default.",
                "notes": {
                    "zh": "只有确认当前驱动稳定给出 MD5 后，才适合后续再提升能力等级。",
                    "en": "Only upgrade the capability later if the current driver is proven to expose stable MD5 values consistently.",
                },
            }
        },
    },
    "yandexdisk": {
        "key": "yandexdisk",
        "label": "Yandex Disk",
        "label_zh": "Yandex Disk",
        "driver_aliases": ["yandexdisk"],
        "login_mode": "refresh token + oauth flow",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "stable",
        "capture_strategy": "优先按文档走 OAuth / Refresh Token 流程；浏览器抓取只作为辅助校验。",
        "capture_strategy_en": "Prefer the OAuth / Refresh Token flow from the documentation; use browser capture only as a diagnostic aid.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/yandex"],
        "default_mount_values": {
            "root_folder_path": "/",
        },
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "只有确认当前驱动稳定返回 MD5 时，才适合把它当作 Guangya 元数据秒传候选来源。",
            "en": "Only treat it as a Guangya metadata-first candidate after the current driver is proven to expose stable MD5 values.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "先分析小目录的 MD5 覆盖率，命中高时优先元数据同步，否则按补传路径推进。",
                "recommended_flow_en": "Analyze MD5 coverage on a small directory first. Use metadata-first sync only when the hit rate is good; otherwise continue via fallback upload.",
                "notes": {
                    "zh": "Yandex Disk 理论上更接近 MD5 型驱动，但正式跑前仍建议先做小目录验证。",
                    "en": "Yandex Disk is theoretically closer to an MD5-style driver, but you should still validate on a small directory first.",
                },
            }
        },
    },
    "webdav": {
        "key": "webdav",
        "label": "WebDAV",
        "label_zh": "WebDAV",
        "driver_aliases": ["webdav"],
        "login_mode": "manual url + username + password",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "stable",
        "capture_strategy": "优先手动填写服务地址、用户名和密码，浏览器抓取不是主路径。",
        "capture_strategy_en": "Fill service URL, username, and password manually first. Browser capture is not the primary path here.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/webdav"],
        "default_mount_values": {},
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "除非你已经验证当前 WebDAV 来源能稳定给出 MD5，否则默认按保守补传处理。",
            "en": "Unless the current WebDAV source is proven to expose stable MD5 values, treat it conservatively by default.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先验证列目录和下载，再按补传链路推进，不默认承诺秒传。",
                "recommended_flow_en": "Validate listing and download first, then proceed via fallback upload without promising fast upload by default.",
                "notes": {
                    "zh": "WebDAV 的哈希表现取决于后端实现，未验证前不要把它当作 Guangya 秒传来源。",
                    "en": "WebDAV hash behavior depends on the backend implementation, so do not present it as a Guangya fast-upload source before verification.",
                },
            }
        },
    },
    "s3": {
        "key": "s3",
        "label": "S3",
        "label_zh": "S3 / 对象存储",
        "driver_aliases": ["s3"],
        "login_mode": "manual endpoint + bucket + access key",
        "likely_hashes": ["etag"],
        "hash_fields_supported": ["etag"],
        "download_link_supported": "stable",
        "capture_strategy": "手动填写 endpoint、bucket、Access Key、Secret Key，再结合实际服务端补 path style / region 等参数。",
        "capture_strategy_en": "Fill endpoint, bucket, Access Key, and Secret Key manually, then add path-style or region options according to the backend.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/s3"],
        "default_mount_values": {},
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "S3 的 ETag 不一定等于稳定 MD5，尤其是分片上传对象，默认按保守补传处理。",
            "en": "S3 ETag is not always stable MD5, especially for multipart objects, so default to conservative fallback upload.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先按小目录验证对象列表和下载，再走补传路径，不默认承诺秒传。",
                "recommended_flow_en": "Validate object listing and download first on a small bucket path, then use fallback upload rather than promising fast upload.",
                "notes": {
                    "zh": "只有确认当前对象确实给出可用 MD5 时，才适合后续再提升能力等级。",
                    "en": "Only upgrade this capability later if the current objects are proven to expose usable MD5 values.",
                },
            }
        },
    },
    "ftp": {
        "key": "ftp",
        "label": "FTP",
        "label_zh": "FTP",
        "driver_aliases": ["ftp"],
        "login_mode": "manual host + username + password",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "conditional",
        "capture_strategy": "手动填写 host、port、username、password，再按环境补 passive mode / TLS 等参数。",
        "capture_strategy_en": "Fill host, port, username, and password manually, then add passive-mode or TLS options if needed.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/ftp"],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "FTP 更偏传统文件传输，不应在没有源分析时默认承诺 Guangya 秒传。",
            "en": "FTP is a classic file-transfer source and should not promise Guangya fast upload without source-analysis evidence.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "优先小目录验证和保守补传，不默认承诺秒传。",
                "recommended_flow_en": "Prefer small-directory validation plus conservative fallback upload instead of promising fast upload.",
                "notes": {
                    "zh": "如果后续源分析证明确有稳定 MD5，再考虑提升能力等级。",
                    "en": "Only upgrade the capability later if source analysis proves stable MD5 is really available.",
                },
            }
        },
    },
    "sftp": {
        "key": "sftp",
        "label": "SFTP",
        "label_zh": "SFTP",
        "driver_aliases": ["sftp"],
        "login_mode": "manual host + username + password/private key",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "stable",
        "capture_strategy": "手动填写 host、port、username、password 或 private key 相关字段。",
        "capture_strategy_en": "Fill host, port, username, password, or private-key fields manually.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/sftp"],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "SFTP 侧重点在连通性和认证方式，哈希能力要靠实际源分析确认。",
            "en": "For SFTP, connectivity and authentication are the main concerns. Hash capability should be confirmed by real source analysis.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先确认认证和下载稳定，再按补传路径推进。",
                "recommended_flow_en": "Confirm authentication and download stability first, then continue through fallback upload.",
                "notes": {
                    "zh": "未确认 MD5 / GCID 前，不应把它默认规划成秒传来源。",
                    "en": "Do not treat it as a fast-upload source before MD5 / GCID is actually confirmed.",
                },
            }
        },
    },
    "seafile": {
        "key": "seafile",
        "label": "Seafile",
        "label_zh": "Seafile",
        "driver_aliases": ["seafile"],
        "login_mode": "manual url + username + password",
        "likely_hashes": ["md5"],
        "hash_fields_supported": ["md5"],
        "download_link_supported": "stable",
        "capture_strategy": "优先手动填写 URL、账号、密码和库信息，再做小目录验证。",
        "capture_strategy_en": "Fill URL, account, password, and library information manually first, then validate with a small directory.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/seafile"],
        "default_mount_values": {},
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "只有确认当前 Seafile 驱动确实返回 MD5 时，才适合考虑元数据秒传路径。",
            "en": "Only consider metadata-first fast upload after confirming the current Seafile driver truly returns MD5.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "fast_upload_partial",
                "recommended_flow": "先分析小目录的 MD5 覆盖率，命中高时再优先元数据同步，否则按待补传树推进。",
                "recommended_flow_en": "Analyze MD5 coverage on a small library first. Use metadata sync only when the hit rate is good; otherwise continue via the pending tree.",
                "notes": {
                    "zh": "Seafile 在部分场景下可能给出 MD5，但仍建议先做小目录分析验证。",
                    "en": "Seafile may expose MD5 in some environments, but you should still validate on a small library first.",
                },
            }
        },
    },
    "smb": {
        "key": "smb",
        "label": "SMB",
        "label_zh": "SMB",
        "driver_aliases": ["smb"],
        "login_mode": "manual host + share + username + password",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "stable",
        "capture_strategy": "手动填写 host、share、username、password，再按环境补 workgroup / port 等字段。",
        "capture_strategy_en": "Fill host, share, username, and password manually, then add workgroup or port fields if needed.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/smb"],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "SMB 更偏局域网共享接入，哈希能力要靠源分析确认，默认先按保守补传处理。",
            "en": "SMB is more of a LAN-share source. Confirm hash capability by source analysis and default to conservative fallback upload first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先验证列目录和下载稳定性，再按补传路径推进。",
                "recommended_flow_en": "Validate listing and download stability first, then continue through fallback upload.",
                "notes": {
                    "zh": "未确认稳定 MD5 前，不应把 SMB 默认规划成 Guangya 秒传来源。",
                    "en": "Do not treat SMB as a Guangya fast-upload source before stable MD5 is confirmed.",
                },
            }
        },
    },
    "azureblob": {
        "key": "azureblob",
        "label": "Azure Blob",
        "label_zh": "Azure Blob",
        "driver_aliases": ["azureblob"],
        "login_mode": "manual account name + account key + container",
        "likely_hashes": ["etag"],
        "hash_fields_supported": ["etag"],
        "download_link_supported": "stable",
        "capture_strategy": "手动填写 account name、account key、container、endpoint 等字段，再做小范围验证。",
        "capture_strategy_en": "Fill account name, account key, container, endpoint, and related fields manually, then validate on a small scope first.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/azure_blob"],
        "default_mount_values": {},
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "Azure Blob 的 ETag 不一定能直接当稳定 MD5，默认按保守补传处理。",
            "en": "Azure Blob ETag is not always safe to interpret as stable MD5, so default to conservative fallback upload.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先验证对象列表与下载，再按补传路径推进，不默认承诺秒传。",
                "recommended_flow_en": "Validate object listing and download first, then continue via fallback upload without promising fast upload by default.",
                "notes": {
                    "zh": "只有确认当前对象稳定给出可用 MD5 时，才适合后续再提升能力等级。",
                    "en": "Only upgrade the capability later if the current objects are proven to expose usable MD5 values consistently.",
                },
            }
        },
    },
    "mega": {
        "key": "mega",
        "label": "MEGA",
        "label_zh": "MEGA",
        "driver_aliases": ["mega"],
        "login_mode": "manual email + password + root",
        "likely_hashes": [],
        "hash_fields_supported": [],
        "download_link_supported": "conditional",
        "capture_strategy": "按驱动说明手动填写 email、password、root 等字段，网页登录只作为参考入口。",
        "capture_strategy_en": "Fill email, password, root, and related fields manually. The web login page is a reference only.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/mega"],
        "default_mount_values": {},
        "recommended_rate_profile": "balanced",
        "risk_notes": {
            "zh": "MEGA 的哈希与下载行为仍应以源分析结果为准，默认先按保守补传处理。",
            "en": "MEGA hash behavior and download stability should still be verified through source analysis. Default to conservative fallback upload first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先小目录验证列目录和下载，再按补传路径推进。",
                "recommended_flow_en": "Validate listing and download on a small directory first, then continue through fallback upload.",
                "notes": {
                    "zh": "在没有确认稳定 MD5 / GCID 前，不应把 MEGA 默认宣传成 Guangya 秒传来源。",
                    "en": "Without confirmed stable MD5 / GCID, MEGA should not be presented as a Guangya fast-upload source by default.",
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
    "115": {
        "key": "115",
        "label": "115",
        "label_zh": "115 网盘",
        "driver_aliases": ["115", "115share"],
        "login_mode": "cookie + browser session fields",
        "likely_hashes": ["sha1", "pickcode"],
        "hash_fields_supported": ["sha1", "pickcode"],
        "download_link_supported": "conditional",
        "capture_strategy": "优先抓 Cookie 与常见会话字段，再结合驱动实际返回的 pickcode / sha1 / md5 决定后续路线。",
        "capture_strategy_en": "Capture Cookie and common session fields first, then decide the next path based on whether the driver really exposes pickcode / sha1 / md5.",
        "doc_links": ["https://doc.oplist.org/guide/drivers/115"],
        "default_mount_values": {},
        "recommended_rate_profile": "safe",
        "risk_notes": {
            "zh": "115 的哈希表现和下载行为更依赖当前驱动实现，正式跑前一定先做小目录源分析。",
            "en": "115 hash exposure and download behavior depend heavily on the current driver implementation, so always analyze a small directory first.",
        },
        "capability_to_targets": {
            "guangya": {
                "level": "download_upload_only",
                "recommended_flow": "先验证当前驱动是否真的返回 MD5 / 可快传指纹；默认按补传或外部秒传 JSON 辅助路线处理。",
                "recommended_flow_en": "Verify whether the current driver really exposes MD5 or other fast-upload-ready fingerprints first. Default to fallback upload or an external flash-upload JSON assisted flow.",
                "notes": {
                    "zh": "115 常见的是 pickcode / sha1 一类字段，若缺少 MD5 / GCID，就不应默认宣传成 Guangya 秒传来源。",
                    "en": "115 more commonly exposes pickcode / sha1 style fields. Without MD5 / GCID, it should not be presented as a Guangya fast-upload source by default.",
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

ONBOARDING_STAGE_ORDER = [
    "needs_profile_bootstrap",
    "ready_for_guide",
    "ready_for_capture",
    "ready_for_capability",
    "covered",
]


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
    if not target_capability and target_key in {"openlist", "localfs", "webdav", "s3", "azureblob", "ftp", "sftp", "smb"}:
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
