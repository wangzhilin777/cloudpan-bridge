from __future__ import annotations

from typing import Any


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


