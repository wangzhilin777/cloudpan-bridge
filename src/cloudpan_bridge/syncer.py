from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Callable

from .config import AppConfig
from .guangya import extract_access_token
from .models import PendingFileState, QueueItemState, SourceEntry, SyncFileState, SyncPlanItem, SyncState, normalize_posix_path
from .openlist import OpenListClient
from .target_adapter import GuangyaTargetAdapter, TargetAdapter

LogFn = Callable[[str], None]


def load_state(path: Path) -> SyncState:
    if not path.exists():
        return SyncState()
    return SyncState.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_state(path: Path, state: SyncState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_plan(entries: list[SourceEntry], state: SyncState) -> tuple[list[SyncPlanItem], list[str]]:
    plan: list[SyncPlanItem] = []
    current_paths = {entry.path for entry in entries}
    removed_paths = sorted(path for path in state.files if path not in current_paths)
    for entry in sorted(entries, key=lambda item: item.path):
        previous = state.files.get(entry.path)
        if previous and previous.md5 == entry.md5 and previous.size == entry.size and previous.last_op_time == entry.last_op_time:
            continue
        is_new = previous is None
        plan.append(
            SyncPlanItem(
                source=entry,
                action="create" if is_new else "update",
                reason="新增文件" if is_new else "源文件已修改",
            )
        )
    return plan, removed_paths


def relative_target_path(source_root: str, source_path: str, target_root: str) -> str:
    root = PurePosixPath("/" + source_root.lstrip("/"))
    source = PurePosixPath("/" + source_path.lstrip("/"))
    relative = source.relative_to(root)
    return str(PurePosixPath("/" + target_root.lstrip("/")) / relative)


def render_tree(paths: list[str]) -> str:
    lines = []
    for path in sorted(paths):
        depth = max(len(PurePosixPath(path).parts) - 1, 0)
        lines.append(f"{'  ' * depth}- {PurePosixPath(path).name}")
    return "\n".join(lines)


def serialize_source_entry(entry: SourceEntry) -> dict[str, object]:
    return {
        "path": entry.path,
        "md5": entry.md5,
        "etag": entry.etag,
        "size": entry.size,
        "lastOpTime": entry.last_op_time,
        "sourceId": entry.source_id,
        "providerFileId": entry.provider_file_id,
        "provider": entry.provider,
        "hashType": entry.hash_type,
        "gcid": entry.gcid,
        "sha1": entry.sha1,
        "crc64": entry.crc64,
        "pickcode": entry.pickcode,
        "extraHashes": dict(entry.extra_hashes or {}),
        "rawHashInfo": dict(entry.raw_hash_info or {}),
    }


def summarize_source_entries(entries: list[SourceEntry]) -> dict[str, object]:
    provider_counts: dict[str, int] = {}
    hash_type_counts: dict[str, int] = {}
    gcid_ready = 0
    md5_ready = 0
    sha1_ready = 0
    missing_md5 = 0
    missing_fast_upload = 0
    fast_upload_ready = 0
    total_size = 0
    for entry in entries:
        provider_counts[entry.provider] = provider_counts.get(entry.provider, 0) + 1
        hash_type_counts[entry.hash_type] = hash_type_counts.get(entry.hash_type, 0) + 1
        total_size += int(entry.size)
        if entry.gcid:
            gcid_ready += 1
        if entry.md5:
            md5_ready += 1
        else:
            missing_md5 += 1
        if entry.sha1:
            sha1_ready += 1
        if entry.has_fast_upload_fingerprint:
            fast_upload_ready += 1
        else:
            missing_fast_upload += 1
    return {
        "total": len(entries),
        "total_size": total_size,
        "provider_counts": provider_counts,
        "hash_type_counts": hash_type_counts,
        "md5_ready": md5_ready,
        "gcid_ready": gcid_ready,
        "sha1_ready": sha1_ready,
        "fast_upload_ready": fast_upload_ready,
        "missing_md5": missing_md5,
        "missing_fast_upload": missing_fast_upload,
    }


def build_source_miaochuan_payload(
    entries: list[SourceEntry],
    source_root: str,
) -> dict[str, object]:
    normalized_root = normalize_posix_path(source_root or "/")
    files: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for entry in sorted(entries, key=lambda item: item.path):
        relative = str(PurePosixPath("/") / PurePosixPath(entry.path).relative_to(PurePosixPath(normalized_root)))
        record = {
            "path": relative,
            "size": str(entry.size),
            "provider": entry.provider,
            "hashType": entry.hash_type,
            "sourceId": entry.source_id,
            "providerFileId": entry.provider_file_id,
        }
        if entry.md5:
            record["etag"] = entry.md5.lower()
        if entry.gcid:
            record["gcid"] = entry.gcid
        if entry.sha1:
            record["sha1"] = entry.sha1
        if entry.crc64:
            record["crc64"] = entry.crc64
        if entry.pickcode:
            record["pickcode"] = entry.pickcode
        if entry.extra_hashes:
            record["extraHashes"] = dict(entry.extra_hashes)
        if entry.md5 or entry.gcid:
            files.append(record)
        else:
            skipped.append({"path": entry.path, "reason": "missing md5/gcid"})
    return {
        "scriptVersion": "cloudpan-bridge-source-export-2026.05.16",
        "commonPath": "",
        "totalFilesCount": len(files),
        "totalSize": sum(int(item["size"]) for item in files),
        "files": files,
        "skipped": skipped,
        "sourceRoot": normalized_root,
    }


@dataclass(slots=True)
class SyncSummary:
    source_path: str = ""
    total: int = 0
    direct_success: int = 0
    downloaded_success: int = 0
    skipped: int = 0
    failed: int = 0
    pending_downloads: list[str] | None = None

    def to_dict(self) -> dict[str, int | list[str] | None]:
        return {
            "source_path": self.source_path,
            "total": self.total,
            "direct_success": self.direct_success,
            "downloaded_success": self.downloaded_success,
            "skipped": self.skipped,
            "failed": self.failed,
            "pending_downloads": self.pending_downloads,
        }


class SyncRunner:
    def __init__(self, config: AppConfig, log: LogFn | None = None, source_root_for_target: str | None = None):
        self.config = config
        self.source_root_for_target = normalize_posix_path(source_root_for_target or config.source_path)
        self.source = OpenListClient(
            base_url=config.openlist_url,
            token=config.openlist_token,
            username=config.openlist_username,
            password=config.openlist_password,
            on_progress=log,
            page_size=config.openlist_page_size,
            request_interval_ms=config.openlist_request_interval_ms,
        )
        self.log = log or print

    def _guangya_access_token(self, state: SyncState) -> str:
        return (
            state.guangya_tokens.get("access_token", "")
            or self.config.guangya_access_token
            or extract_access_token(getattr(self.config, "guangya_authorization", ""))
        )

    def _build_target_adapter(self, state: SyncState) -> TargetAdapter:
        return GuangyaTargetAdapter(
            access_token=self._guangya_access_token(state),
            refresh_token=state.guangya_tokens.get("refresh_token", "") or self.config.guangya_refresh_token,
            device_id=state.guangya_tokens.get("device_id", "") or self.config.guangya_device_id,
            phone_number=self.config.guangya_phone,
        )

    def run(self, allow_download_upload: bool | None = None, dry_run: bool = False) -> SyncSummary:
        self.config.ensure_parent_dirs()
        state = load_state(self.config.state_file)
        target: TargetAdapter | None = None

        try:
            self.source.ensure_login()
            entries = self.source.export_tree(self.config.source_path)
            self.config.export_file.write_text(
                "\n".join(
                    json.dumps(
                        serialize_source_entry(entry),
                        ensure_ascii=False,
                    )
                    for entry in entries
                ) + ("\n" if entries else ""),
                encoding="utf-8",
            )
            plan, removed_paths = build_plan(entries, state)
            summary = SyncSummary(source_path=self.config.source_path, total=len(plan))

            self.log(f"源文件总数: {len(entries)}")
            self.log(f"待同步文件数: {len(plan)}")
            self.log(f"源端已删除文件数: {len(removed_paths)}")

            if not plan and not removed_paths:
                self.log("没有检测到需要同步的变更。")
                return summary

            if removed_paths:
                self.log("以下文件在 OpenList 源目录已不存在:")
                self.log(render_tree(removed_paths))
                if self.config.delete_removed:
                    self.log("配置开启了 delete_removed，后续会尝试从同步状态移除这些文件。")
                else:
                    self.log("当前不会自动删除光鸭中的旧文件，只会提示。")

            if dry_run:
                self.log("dry-run 模式，不执行实际同步。")
                return summary

            target = self._build_target_adapter(state)
            target.ensure_auth()
            state.guangya_tokens = target.export_state()

            need_download: list[SyncPlanItem] = []
            for item in plan:
                if self._try_direct_metadata_sync(item, target, state):
                    summary.direct_success += 1
                elif self._should_auto_download(item):
                    try:
                        self.log(
                            f"[自动补传] {item.source.path} 命中小文件阈值 "
                            f"({self.config.auto_download_threshold_mb} MB)，改走下载后上传"
                        )
                        self._sync_download_then_upload(item, target, state)
                        summary.downloaded_success += 1
                    except Exception as exc:  # noqa: BLE001
                        summary.failed += 1
                        self.log(f"[失败] {item.source.path}: {exc}")
                else:
                    need_download.append(item)

            if need_download:
                self.log("以下文件未命中元数据秒传库存:")
                self.log(render_tree([item.source.path for item in need_download]))
                if allow_download_upload is None:
                    answer = input("\n是否继续执行“先下载到本地临时目录，再上传到光鸭云盘”？[y/N]: ").strip().lower()
                    allow_download_upload = answer in {"y", "yes"}
                if allow_download_upload:
                    for item in need_download:
                        try:
                            self._sync_download_then_upload(item, target, state)
                            summary.downloaded_success += 1
                        except Exception as exc:  # noqa: BLE001
                            summary.failed += 1
                            self.log(f"[失败] {item.source.path}: {exc}")
                else:
                    summary.skipped += len(need_download)
                    self.log("已跳过下载后上传步骤。")

            if self.config.delete_removed:
                for removed in removed_paths:
                    state.files.pop(removed, None)

            save_state(self.config.state_file, state)
            self.log(f"同步完成: {summary.to_dict()}")
            return summary
        finally:
            if target is not None:
                target.close()
            self.source.close()

    def analyze(self) -> tuple[list[SourceEntry], list[SyncPlanItem], list[str]]:
        self.config.ensure_parent_dirs()
        state = load_state(self.config.state_file)
        self.source.ensure_login()
        self.log(f"开始扫描源目录树: {self.config.source_path}")
        entries = self.source.export_tree(self.config.source_path)
        self.log(f"源目录扫描完成，累计文件数: {len(entries)}")
        plan, removed_paths = build_plan(entries, state)
        self.config.export_file.write_text(
            "\n".join(
                json.dumps(
                    serialize_source_entry(entry),
                    ensure_ascii=False,
                )
                for entry in entries
            ) + ("\n" if entries else ""),
            encoding="utf-8",
        )
        return entries, plan, removed_paths

    def run_direct_phase(self) -> SyncSummary:
        self.config.ensure_parent_dirs()
        state = load_state(self.config.state_file)
        target: TargetAdapter | None = None
        try:
            entries, plan, removed_paths = self.analyze()
            summary = SyncSummary(total=len(plan), pending_downloads=[])
            summary.source_path = self.config.source_path
            self.log(f"源文件总数: {len(entries)}")
            self.log(f"待同步文件数: {len(plan)}")
            self.log(f"源端已删除文件数: {len(removed_paths)}")
            if not plan and not removed_paths:
                self.log("没有检测到需要同步的变更。")
                return summary

            target = self._build_target_adapter(state)
            target.ensure_auth()
            state.guangya_tokens = target.export_state()

            pending: list[str] = []
            for item in plan:
                if self._try_direct_metadata_sync(item, target, state):
                    summary.direct_success += 1
                elif self._should_auto_download(item):
                    try:
                        self.log(
                            f"[自动补传] {item.source.path} 命中小文件阈值 "
                            f"({self.config.auto_download_threshold_mb} MB)，改走下载后上传"
                        )
                        self._sync_download_then_upload(item, target, state)
                        summary.downloaded_success += 1
                    except Exception as exc:  # noqa: BLE001
                        summary.failed += 1
                        pending.append(item.source.path)
                        self._record_pending(item, state, reason=f"自动补传失败: {exc}")
                        self.log(f"[失败] {item.source.path}: {exc}")
                else:
                    pending.append(item.source.path)
                    self._record_pending(item, state)
            summary.pending_downloads = pending
            self._prune_pending_for_source(self.config.source_path, keep_paths=set(pending), state=state)
            self._update_queue_item(
                state,
                self.config.source_path,
                last_status="completed" if not summary.failed else "partial",
                last_summary=summary.to_dict(),
                last_error="",
            )
            save_state(self.config.state_file, state)
            self.log(f"秒传阶段完成: 成功 {summary.direct_success}，待补传 {len(pending)}")
            if pending:
                self.log(render_tree(pending))
            return summary
        finally:
            if target is not None:
                target.close()
            self.source.close()

    def run_selected_downloads(self, selected_paths: list[str]) -> SyncSummary:
        self.config.ensure_parent_dirs()
        state = load_state(self.config.state_file)
        target: TargetAdapter | None = None
        try:
            target = self._build_target_adapter(state)
            target.ensure_auth()
            state.guangya_tokens = target.export_state()
            self.source.ensure_login()

            summary = SyncSummary(source_path=self.config.source_path, total=len(selected_paths), pending_downloads=[])
            for path in selected_paths:
                pending = state.pending_files.get(path)
                if not pending:
                    summary.failed += 1
                    self._mark_pending_missing(path, state)
                    self.log(f"[失败] 待补传记录不存在: {path}")
                    continue
                entry = SourceEntry(
                    path=pending.path,
                    md5=pending.md5,
                    size=pending.size,
                    last_op_time=pending.last_op_time,
                    source_id=pending.source_id,
                    provider=pending.provider,
                    hash_type=pending.hash_type,
                    gcid=pending.gcid,
                )
                item = SyncPlanItem(source=entry, action="update", reason="手动补传")
                try:
                    self._sync_download_then_upload(item, target, state, source_root_override=pending.source_root or self.source_root_for_target)
                    summary.downloaded_success += 1
                    state.pending_files.pop(path, None)
                except Exception as exc:  # noqa: BLE001
                    summary.failed += 1
                    summary.pending_downloads.append(path)
                    self._record_pending(item, state, reason=f"补传失败: {exc}")
                    self.log(f"[失败] {path}: {exc}")
            self._update_queue_item(
                state,
                self.config.source_path,
                last_status="completed" if not summary.failed else "partial",
                last_summary=summary.to_dict(),
                last_error="",
            )
            save_state(self.config.state_file, state)
            self.log(f"补传阶段完成: {summary.to_dict()}")
            return summary
        finally:
            if target is not None:
                target.close()
            self.source.close()

    def _resolve_target_path(self, source_path: str, source_root_override: str | None = None) -> str:
        return relative_target_path(source_root_override or self.source_root_for_target, source_path, self.config.target_path)

    def _try_direct_metadata_sync(self, item: SyncPlanItem, target: TargetAdapter, state: SyncState) -> bool:
        if not item.source.has_fast_upload_fingerprint:
            self.log(f"[无秒传指纹] {item.source.path}: 缺少 MD5/GCID，改走降级路径。")
            return False
        target_path = self._resolve_target_path(item.source.path)
        target_parent = str(PurePosixPath(target_path).parent)
        target_parent_id = target.ensure_target_dir(target_parent)
        target.delete_if_exists(target_parent_id, item.source.name)

        result = target.try_fast_upload(
            file_name=item.source.name,
            file_size=item.source.size,
            parent_id=target_parent_id,
            md5_hex=item.source.md5,
            gcid=item.source.gcid,
        )
        if result.success:
            self.log(f"[元数据秒传成功] {item.source.path} -> {target_path} ({result.reason})")
            self._record_success(item.source, target_path, state)
            return True
        self.log(f"[元数据秒传未命中] {item.source.path}: {result.reason}")
        return False

    def _sync_download_then_upload(
        self,
        item: SyncPlanItem,
        target: TargetAdapter,
        state: SyncState,
        source_root_override: str | None = None,
    ) -> None:
        target_path = self._resolve_target_path(item.source.path, source_root_override)
        target_parent = str(PurePosixPath(target_path).parent)
        target_parent_id = target.ensure_target_dir(target_parent)
        target.delete_if_exists(target_parent_id, item.source.name)

        local_path = self.source.download_file(item.source.path, self.config.temp_dir)
        if item.source.md5:
            target.verify_local_md5(local_path, item.source.md5)
        else:
            self.log(f"[跳过 MD5 校验] {item.source.path}: 源端未提供 MD5，仅保留 GCID/其它元数据。")
        self.log(f"[下载补传] {item.source.path} -> {target_path}")
        target.upload_local_file(local_path, target_parent_id, item.source.name)
        try:
            local_path.unlink(missing_ok=True)
            self.log(f"[清理临时文件] {local_path}")
        except Exception as exc:  # noqa: BLE001
            self.log(f"[警告] 上传成功，但删除临时文件失败: {local_path} ({exc})")
        self._record_success(item.source, target_path, state)

    def _should_auto_download(self, item: SyncPlanItem) -> bool:
        threshold_mb = max(0, int(self.config.auto_download_threshold_mb))
        if threshold_mb <= 0:
            return False
        return item.source.size <= threshold_mb * 1024 * 1024

    @staticmethod
    def _record_success(entry: SourceEntry, target_path: str, state: SyncState) -> None:
        state.files[entry.path] = SyncFileState(
            path=entry.path,
            md5=entry.md5,
            size=entry.size,
            last_op_time=entry.last_op_time,
            synced_at=datetime.now().isoformat(timespec="seconds"),
            target_path=target_path,
            source_id=entry.source_id,
            provider=entry.provider,
            hash_type=entry.hash_type,
            gcid=entry.gcid,
            etag=entry.etag,
            sha1=entry.sha1,
            crc64=entry.crc64,
            pickcode=entry.pickcode,
            extra_hashes=dict(entry.extra_hashes or {}),
        )
        state.pending_files.pop(entry.path, None)

    def _record_pending(self, item: SyncPlanItem, state: SyncState, reason: str | None = None) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        existing = state.pending_files.get(item.source.path)
        state.pending_files[item.source.path] = PendingFileState(
            path=item.source.path,
            md5=item.source.md5,
            size=item.source.size,
            last_op_time=item.source.last_op_time,
            source_root=self.source_root_for_target,
            reason=reason or item.reason or "未命中秒传库存",
            target_path="",
            discovered_at=existing.discovered_at if existing else now,
            updated_at=now,
            source_id=item.source.source_id,
            provider=item.source.provider,
            hash_type=item.source.hash_type,
            gcid=item.source.gcid,
        )

    @staticmethod
    def _mark_pending_missing(path: str, state: SyncState) -> None:
        item = state.pending_files.get(path)
        if item:
            item.reason = "源端已不存在"
            item.updated_at = datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _prune_pending_for_source(source_root: str, keep_paths: set[str], state: SyncState) -> None:
        normalized_root = str(PurePosixPath("/" + source_root.lstrip("/")))
        to_remove = [
            path for path, item in state.pending_files.items()
            if path.startswith(normalized_root.rstrip("/") + "/") and path not in keep_paths
        ]
        for path in to_remove:
            state.pending_files.pop(path, None)

    @staticmethod
    def _update_queue_item(
        state: SyncState,
        source_path: str,
        *,
        last_status: str,
        last_summary: dict[str, object],
        last_error: str,
    ) -> None:
        normalized = str(PurePosixPath("/" + source_path.lstrip("/")))
        now = datetime.now().isoformat(timespec="seconds")
        for item in state.source_queue:
            if item.source_path == normalized:
                item.last_status = last_status
                item.last_summary = dict(last_summary)
                item.last_error = last_error
                item.last_run_at = now
                return
        state.source_queue.append(
            QueueItemState(
                source_path=normalized,
                last_status=last_status,
                last_summary=dict(last_summary),
                last_error=last_error,
                last_run_at=now,
            )
        )
