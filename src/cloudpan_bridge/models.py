from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath
from typing import Any


def normalize_posix_path(value: str) -> str:
    parts: list[str] = []
    for part in PurePosixPath("/" + value.lstrip("/")).parts:
        if part in ("", "/"):
            continue
        if part == ".":
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/" + "/".join(parts)


def normalize_fingerprint_value(value: Any, *, uppercase: bool = True) -> str:
    text = str(value or "").strip()
    return text.upper() if uppercase else text


@dataclass(slots=True)
class SourceEntry:
    path: str
    md5: str
    size: int
    last_op_time: str = ""
    source_id: str = ""
    provider: str = "openlist"
    hash_type: str = "md5"
    gcid: str = ""
    etag: str = ""
    sha1: str = ""
    sha256: str = ""
    crc64: str = ""
    pre_hash: str = ""
    slice_md5: str = ""
    pickcode: str = ""
    content_hash: str = ""
    extra_hashes: dict[str, str] = field(default_factory=dict)
    provider_specific: dict[str, str] = field(default_factory=dict)
    raw_hash_info: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.path = normalize_posix_path(self.path)
        self.md5 = normalize_fingerprint_value(self.md5)
        self.etag = normalize_fingerprint_value(self.etag)
        self.sha1 = normalize_fingerprint_value(self.sha1)
        self.sha256 = normalize_fingerprint_value(self.sha256)
        self.crc64 = normalize_fingerprint_value(self.crc64)
        self.gcid = normalize_fingerprint_value(self.gcid)
        self.pre_hash = normalize_fingerprint_value(self.pre_hash)
        self.slice_md5 = normalize_fingerprint_value(self.slice_md5)
        self.content_hash = normalize_fingerprint_value(self.content_hash)
        self.pickcode = normalize_fingerprint_value(self.pickcode, uppercase=False)
        self.size = int(self.size)
        self.extra_hashes = {str(key): normalize_fingerprint_value(value, uppercase=False) for key, value in dict(self.extra_hashes or {}).items() if str(value or "").strip()}
        self.provider_specific = {str(key): normalize_fingerprint_value(value, uppercase=False) for key, value in dict(self.provider_specific or {}).items() if str(value or "").strip()}

    @property
    def parent_path(self) -> str:
        return str(PurePosixPath(self.path).parent)

    @property
    def name(self) -> str:
        return PurePosixPath(self.path).name

    def signature(self) -> str:
        return f"{self.md5}:{self.size}:{self.last_op_time}"

    @property
    def provider_file_id(self) -> str:
        return self.source_id

    @property
    def mtime(self) -> str:
        return self.last_op_time

    @property
    def has_fast_upload_fingerprint(self) -> bool:
        return bool(self.md5 or self.gcid)

    def to_fingerprint_dict(self) -> dict[str, Any]:
        return {
            "size": self.size,
            "md5": self.md5,
            "sha1": self.sha1,
            "sha256": self.sha256,
            "gcid": self.gcid,
            "etag": self.etag,
            "crc64": self.crc64,
            "pre_hash": self.pre_hash,
            "slice_md5": self.slice_md5,
            "pickcode": self.pickcode,
            "content_hash": self.content_hash,
            "provider_specific": dict(self.provider_specific or {}),
        }


@dataclass(slots=True)
class DirectImportResult:
    success: bool
    reason: str
    used_hash: str = ""
    task_id: str = ""


@dataclass(slots=True)
class SyncFileState:
    path: str
    md5: str
    size: int
    last_op_time: str = ""
    synced_at: str = ""
    target_path: str = ""
    source_id: str = ""
    provider: str = "openlist"
    hash_type: str = "md5"
    gcid: str = ""
    etag: str = ""
    sha1: str = ""
    sha256: str = ""
    crc64: str = ""
    pre_hash: str = ""
    slice_md5: str = ""
    pickcode: str = ""
    extra_hashes: dict[str, str] = field(default_factory=dict)
    content_hash: str = ""
    provider_specific: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PendingFileState:
    path: str
    md5: str
    size: int
    last_op_time: str = ""
    source_root: str = ""
    reason: str = ""
    target_path: str = ""
    discovered_at: str = ""
    updated_at: str = ""
    source_id: str = ""
    provider: str = "openlist"
    hash_type: str = "md5"
    gcid: str = ""
    etag: str = ""
    sha1: str = ""
    sha256: str = ""
    crc64: str = ""
    pre_hash: str = ""
    slice_md5: str = ""
    pickcode: str = ""
    extra_hashes: dict[str, str] = field(default_factory=dict)
    content_hash: str = ""
    provider_specific: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class QueueItemState:
    source_path: str
    source_root_for_target: str = ""
    enabled: bool = True
    last_status: str = "idle"
    last_summary: dict[str, Any] = field(default_factory=dict)
    last_error: str = ""
    last_run_at: str = ""

    def __post_init__(self) -> None:
        self.source_path = normalize_posix_path(self.source_path)
        if self.source_root_for_target:
            self.source_root_for_target = normalize_posix_path(self.source_root_for_target)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SyncState:
    version: int = 1
    guangya_tokens: dict[str, str] = field(default_factory=dict)
    target_states: dict[str, dict[str, str]] = field(default_factory=dict)
    files: dict[str, SyncFileState] = field(default_factory=dict)
    pending_files: dict[str, PendingFileState] = field(default_factory=dict)
    source_queue: list[QueueItemState] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SyncState":
        files = {
            path: SyncFileState(**item)
            for path, item in payload.get("files", {}).items()
        }
        pending_files = {
            path: PendingFileState(**item)
            for path, item in payload.get("pending_files", {}).items()
        }
        source_queue = [
            QueueItemState(**item)
            for item in payload.get("source_queue", [])
            if isinstance(item, dict) and item.get("source_path")
        ]
        legacy_guangya_tokens = dict(payload.get("guangya_tokens", {}))
        target_states = {
            str(key): dict(value or {})
            for key, value in dict(payload.get("target_states", {}) or {}).items()
            if isinstance(value, dict)
        }
        if legacy_guangya_tokens and "guangya" not in target_states:
            target_states["guangya"] = dict(legacy_guangya_tokens)
        return cls(
            version=int(payload.get("version", 1)),
            guangya_tokens=legacy_guangya_tokens,
            target_states=target_states,
            files=files,
            pending_files=pending_files,
            source_queue=source_queue,
        )

    def to_dict(self) -> dict[str, Any]:
        target_states = {
            str(key): dict(value or {})
            for key, value in dict(self.target_states or {}).items()
            if isinstance(value, dict)
        }
        if self.guangya_tokens:
            target_states.setdefault("guangya", dict(self.guangya_tokens))
        return {
            "version": self.version,
            "guangya_tokens": dict(self.guangya_tokens),
            "target_states": target_states,
            "files": {path: item.to_dict() for path, item in self.files.items()},
            "pending_files": {path: item.to_dict() for path, item in self.pending_files.items()},
            "source_queue": [item.to_dict() for item in self.source_queue],
        }

    def get_target_state(self, target_key: str) -> dict[str, str]:
        normalized = str(target_key or "").strip().lower()
        if not normalized:
            return {}
        if normalized == "guangya" and self.guangya_tokens:
            return dict(self.target_states.get(normalized) or self.guangya_tokens)
        return dict(self.target_states.get(normalized) or {})

    def set_target_state(self, target_key: str, state: dict[str, str] | None) -> None:
        normalized = str(target_key or "").strip().lower()
        if not normalized:
            return
        next_state = dict(state or {})
        self.target_states[normalized] = next_state
        if normalized == "guangya":
            self.guangya_tokens = dict(next_state)


@dataclass(slots=True)
class SyncPlanItem:
    source: SourceEntry
    action: str
    reason: str
    requires_download: bool = False


@dataclass(slots=True)
class TargetNode:
    file_id: str
    parent_id: str
    name: str
    is_dir: bool
    raw: dict[str, Any]
