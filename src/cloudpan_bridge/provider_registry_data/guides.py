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

