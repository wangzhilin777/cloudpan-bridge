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

    def __post_init__(self) -> None:
        self.path = normalize_posix_path(self.path)
        self.md5 = self.md5.upper()
        self.size = int(self.size)

    @property
    def parent_path(self) -> str:
        return str(PurePosixPath(self.path).parent)

    @property
    def name(self) -> str:
        return PurePosixPath(self.path).name

    def signature(self) -> str:
        return f"{self.md5}:{self.size}:{self.last_op_time}"


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
        return cls(
            version=int(payload.get("version", 1)),
            guangya_tokens=dict(payload.get("guangya_tokens", {})),
            files=files,
            pending_files=pending_files,
            source_queue=source_queue,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "guangya_tokens": self.guangya_tokens,
            "files": {path: item.to_dict() for path, item in self.files.items()},
            "pending_files": {path: item.to_dict() for path, item in self.pending_files.items()},
            "source_queue": [item.to_dict() for item in self.source_queue],
        }


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
