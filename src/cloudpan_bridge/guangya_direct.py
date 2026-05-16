from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

import httpx

from .models import normalize_posix_path

GUANGYA_CODE_RES_TOKEN_INSTANT = 156
GUANGYA_CODE_DIR_EXISTS = 159


def normalize_guangya_authorization(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text.lower().startswith("bearer "):
        return "Bearer " + text[7:].strip()
    return "Bearer " + text


def extract_access_token(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text.lower().startswith("bearer "):
        return text[7:].strip()
    return text


def _find_first_value_by_keys(node: Any, keys: set[str]) -> Any:
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).lower() in keys and value not in ("", None):
                return value
        for value in node.values():
            found = _find_first_value_by_keys(value, keys)
            if found not in ("", None):
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_first_value_by_keys(item, keys)
            if found not in ("", None):
                return found
    return None


def _extract_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[Any] = []
    data = response.get("data")
    if isinstance(data, list):
        candidates.append(data)
    elif isinstance(data, dict):
        for key in ("fileList", "list", "rows", "records", "items", "content"):
            value = data.get(key)
            if isinstance(value, list):
                candidates.append(value)
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                candidates.append(value)
    for items in candidates:
        if items:
            return items
    return []


def _is_dir(item: dict[str, Any]) -> bool:
    for key in ("isFolder", "isDir", "folder"):
        if key in item:
            return bool(item[key])
    if str(item.get("dirType", "")) not in ("", "0"):
        return True
    if str(item.get("type", "")).lower() in ("dir", "folder"):
        return True
    return False


def _normalize_md5(value: str) -> str:
    text = str(value or "").strip().strip('"').upper()
    return text if len(text) == 32 and all(ch in "0123456789ABCDEF" for ch in text) else ""


@dataclass(slots=True)
class MiaochuanFile:
    path: str
    size: int
    etag: str = ""
    gcid: str = ""
    provider: str = ""
    hash_type: str = ""


@dataclass(slots=True)
class DirectImportSummary:
    total: int = 0
    success: int = 0
    transfer_fail: int = 0
    mkdir_fail: int = 0
    skipped: int = 0
    target_root: str = "/"
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "success": self.success,
            "transfer_fail": self.transfer_fail,
            "mkdir_fail": self.mkdir_fail,
            "skipped": self.skipped,
            "target_root": self.target_root,
            "failures": self.failures,
        }


class GuangyaMiaochuanImporter:
    def __init__(self, authorization: str, *, timeout: float = 45.0) -> None:
        self.authorization = normalize_guangya_authorization(authorization)
        if not self.authorization:
            raise RuntimeError("缺少光鸭 Authorization，无法执行秒传 JSON 直导。")
        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=utf-8",
                "Authorization": self.authorization,
                "dt": "4",
            },
        )
        self.dir_cache: dict[tuple[str, str], str] = {}

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "GuangyaMiaochuanImporter":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def _post(
        self,
        url: str,
        body: dict[str, Any],
        *,
        allowed_codes: set[int] | None = None,
    ) -> dict[str, Any]:
        response = self.client.post(url, json=body)
        response.raise_for_status()
        payload = response.json()
        code = payload.get("code")
        if code is None:
            return payload
        if int(code) == 0:
            return payload
        if allowed_codes and int(code) in allowed_codes:
            return payload
        raise RuntimeError(str(payload.get("msg") or payload.get("message") or payload))

    def _extract_created_dir_id(self, payload: dict[str, Any]) -> str:
        value = _find_first_value_by_keys(payload, {"dirid", "dir_id", "fileid", "folderid", "folder_id", "id"})
        return "" if value in ("", None) else str(value)

    def _find_child_directory_id(self, parent_id: str, name: str) -> str:
        page = 0
        while True:
            payload = self._post(
                "https://api.guangyapan.com/userres/v1/file/get_file_list",
                {
                    "parentId": str(parent_id or ""),
                    "page": page,
                    "pageSize": 200,
                    "orderBy": 0,
                    "sortType": 0,
                },
            )
            items = _extract_items(payload)
            if not items:
                return ""
            for item in items:
                item_name = str(
                    item.get("fileName")
                    or item.get("name")
                    or item.get("dirName")
                    or ""
                ).strip()
                if item_name == name and _is_dir(item):
                    value = item.get("fileId") or item.get("id")
                    return "" if value in ("", None) else str(value)
            if len(items) < 200:
                return ""
            page += 1

    def ensure_directory_path(self, path: str, summary: DirectImportSummary | None = None, sample_path: str = "") -> str | None:
        normalized = normalize_posix_path(path)
        if normalized == "/":
            return ""
        current_parent = ""
        full_path = ""
        for segment in PurePosixPath(normalized).parts[1:]:
            full_path = f"{full_path}/{segment}" if full_path else f"/{segment}"
            cache_key = (current_parent, full_path)
            if cache_key in self.dir_cache:
                current_parent = self.dir_cache[cache_key]
                continue
            payload = self._post(
                "https://api.guangyapan.com/nd.bizuserres.s/v1/file/create_dir",
                {
                    "dirName": segment,
                    "parentId": str(current_parent or ""),
                    "failIfNameExist": False,
                },
                allowed_codes={GUANGYA_CODE_DIR_EXISTS},
            )
            dir_id = self._extract_created_dir_id(payload)
            if not dir_id:
                dir_id = self._find_child_directory_id(current_parent, segment)
            if not dir_id:
                if summary is not None:
                    summary.mkdir_fail += 1
                    summary.failures.append(
                        f"{sample_path or full_path}：创建目录失败（目录={full_path}，未返回目录 ID）"
                    )
                return None
            self.dir_cache[cache_key] = dir_id
            current_parent = dir_id
        return current_parent

    @staticmethod
    def normalize_payload(payload: str | dict[str, Any]) -> list[MiaochuanFile]:
        raw = json.loads(payload) if isinstance(payload, str) else payload
        rows = raw.get("files") if isinstance(raw, dict) else None
        if not isinstance(rows, list):
            raise RuntimeError("秒传 JSON 缺少 files 数组。")
        common_path = ""
        if isinstance(raw, dict):
            common_path = normalize_posix_path(str(raw.get("commonPath") or "").strip()) if str(raw.get("commonPath") or "").strip() else ""
        files: list[MiaochuanFile] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            path = normalize_posix_path(str(row.get("path") or row.get("name") or "").strip())
            if common_path and path and path != common_path:
                common_prefix = common_path.rstrip("/") + "/"
                if not path.startswith(common_prefix):
                    path = normalize_posix_path(str(PurePosixPath(common_path) / path.lstrip("/")))
            try:
                size = int(str(row.get("size") or "").strip())
            except Exception:  # noqa: BLE001
                size = -1
            etag = _normalize_md5(str(row.get("etag") or row.get("md5") or ""))
            gcid = str(row.get("gcid") or "").strip().upper()
            if not path or size < 0 or (not etag and not gcid):
                raise RuntimeError(f"第 {index} 项缺少有效的 path / size / etag(gcid)。")
            files.append(
                MiaochuanFile(
                    path=path,
                    size=size,
                    etag=etag,
                    gcid=gcid,
                    provider=str(row.get("provider") or ""),
                    hash_type=str(row.get("hashType") or ("md5" if etag else "gcid")),
                )
            )
        if not files:
            raise RuntimeError("秒传 JSON 没有可导入文件。")
        return files

    @classmethod
    def diagnose_payload(cls, payload: str | dict[str, Any]) -> dict[str, Any]:
        files = cls.normalize_payload(payload)
        total_size = 0
        md5_count = 0
        gcid_count = 0
        provider_counts: dict[str, int] = {}
        sample: list[dict[str, Any]] = []
        for item in files:
            total_size += int(item.size)
            if item.etag:
                md5_count += 1
            if item.gcid:
                gcid_count += 1
            provider_key = item.provider or "unknown"
            provider_counts[provider_key] = provider_counts.get(provider_key, 0) + 1
            if len(sample) < 30:
                sample.append(
                    {
                        "path": item.path,
                        "size": item.size,
                        "etag": item.etag,
                        "gcid": item.gcid,
                        "provider": item.provider,
                        "hashType": item.hash_type,
                    }
                )
        return {
            "total": len(files),
            "total_size": total_size,
            "md5_count": md5_count,
            "gcid_count": gcid_count,
            "provider_counts": provider_counts,
            "sample": sample,
        }

    def import_payload(self, payload: str | dict[str, Any], target_root: str = "/") -> DirectImportSummary:
        files = self.normalize_payload(payload)
        summary = DirectImportSummary(total=len(files), target_root=normalize_posix_path(target_root or "/"))
        target_root_id = self.ensure_directory_path(summary.target_root, summary)
        if target_root_id is None and summary.target_root != "/":
            return summary
        target_root_id = target_root_id or ""
        self.dir_cache[("", summary.target_root)] = target_root_id

        for item in files:
            target_path = normalize_posix_path(str(PurePosixPath(summary.target_root) / item.path.lstrip("/")))
            target_parent = str(PurePosixPath(target_path).parent)
            target_name = PurePosixPath(target_path).name or "file"
            target_parent_id = self.ensure_directory_path(target_parent, summary, item.path)
            if target_parent_id is None:
                continue
            body: dict[str, Any] = {
                "capacity": 1,
                "name": target_name,
                "parentId": str(target_parent_id or ""),
                "res": {"fileSize": item.size},
            }
            if item.etag:
                body["res"]["md5"] = item.etag
            try:
                result = self._post(
                    "https://api.guangyapan.com/nd.bizuserres.s/v1/get_res_center_token",
                    body,
                    allowed_codes={GUANGYA_CODE_RES_TOKEN_INSTANT},
                )
                code = int(result.get("code", 0))
                if code == GUANGYA_CODE_RES_TOKEN_INSTANT:
                    summary.success += 1
                    continue
                task_id = _find_first_value_by_keys(result, {"taskid", "task_id"})
                if item.gcid and task_id:
                    check = self._post(
                        "https://api.guangyapan.com/nd.bizuserres.s/v1/check_can_flash_upload",
                        {"taskId": str(task_id), "gcid": item.gcid},
                    )
                    if bool(((check.get("data") or {}) if isinstance(check.get("data"), dict) else {}).get("canFlashUpload")):
                        summary.success += 1
                        continue
                if task_id:
                    try:
                        self._post(
                            "https://api.guangyapan.com/nd.bizuserres.s/v1/file/delete_upload_task",
                            {"taskIds": [str(task_id)]},
                        )
                    except Exception:  # noqa: BLE001
                        pass
                summary.transfer_fail += 1
                summary.failures.append(f"{item.path}：未命中秒传库存")
            except Exception as exc:  # noqa: BLE001
                summary.transfer_fail += 1
                summary.failures.append(f"{item.path}：秒传接口失败（{exc}）")
        return summary
