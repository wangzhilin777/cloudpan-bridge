from __future__ import annotations

from typing import Any


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
            "zh": "第五个正式可写目标端。用于把同步结果写入 S3 或兼容对象存储，当前只按普通对象上传/覆盖处理，不承诺元数据秒传。",
            "en": "Fifth built-in writable target. It writes sync results into S3 or compatible object storage and currently uses normal object upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为对象存储桶、备份桶或云原生归档目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a target for object-storage buckets, backup buckets, or cloud-native archives. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
    "seafile": {
        "key": "seafile",
        "label": "Seafile",
        "label_zh": "Seafile 目标端",
        "auth_mode": "seafile url + token or username/password + repo",
        "token_refresh": "login token reusable",
        "auto_create_dir": True,
        "fast_upload_hashes": [],
        "fallback_modes": ["download_upload", "stream_upload"],
        "description": {
            "zh": "第六个正式可写目标端。用于把同步结果写入 Seafile 资料库目录，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Sixth built-in writable target. It writes sync results into Seafile libraries and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为团队资料库、私有云文档库或 Seafile 归档目录目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a target for team libraries, private cloud document vaults, or Seafile archive directories. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
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
            "zh": "第十个正式可写目标端。用于把同步结果写入 Azure Blob 容器，当前只按普通对象上传/覆盖处理，不承诺元数据秒传。",
            "en": "Tenth built-in writable target. It writes sync results into Azure Blob containers and currently uses normal object upload/overwrite only, without any metadata-based fast-upload promise.",
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
            "zh": "第七个正式可写目标端。用于把同步结果写入 SMB 共享目录，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Seventh built-in writable target. It writes sync results into SMB share directories and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
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
            "zh": "第八个正式可写目标端。用于把同步结果写入 FTP 存储，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Eighth built-in writable target. It writes sync results into FTP storage and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
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
            "zh": "第九个正式可写目标端。用于把同步结果写入 SFTP 存储，当前只按普通上传/覆盖处理，不承诺元数据秒传。",
            "en": "Ninth built-in writable target. It writes sync results into SFTP storage and currently uses normal upload/overwrite only, without any metadata-based fast-upload promise.",
        },
        "research_notes": {
            "zh": "适合作为 Linux 主机、NAS 或云服务器目录型目标端；当前能力定位仍是保守上传链路，不宣传成跨盘秒传。",
            "en": "Useful as a directory-style target for Linux hosts, NAS systems, or cloud servers. The current capability remains a conservative upload path rather than cross-cloud fast upload.",
        },
    },
}

