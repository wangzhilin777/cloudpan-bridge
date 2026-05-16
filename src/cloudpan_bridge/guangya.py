from __future__ import annotations

from base64 import b64encode
from hashlib import md5
from pathlib import Path, PurePosixPath
from time import sleep
from typing import Any

from httpx import HTTPStatusError
from guangyaclient import GuangyaClient

from .models import DirectImportResult, TargetNode


def _extract_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[Any] = []
    data = response.get("data")
    if isinstance(data, list):
        candidates.append(data)
    elif isinstance(data, dict):
        for key in ("fileList", "list", "rows", "records", "items"):
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


def _first(item: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            return str(value)
    return default


def _is_dir(item: dict[str, Any]) -> bool:
    for key in ("isFolder", "isDir", "folder"):
        if key in item:
            return bool(item[key])
    if str(item.get("dirType", "")) not in ("", "0"):
        return True
    if str(item.get("type", "")).lower() in ("dir", "folder"):
        return True
    return False


def md5_hex_to_base64(md5_hex: str) -> str:
    return b64encode(bytes.fromhex(md5_hex)).decode("ascii")


def extract_access_token(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text.lower().startswith("bearer "):
        return text[7:].strip()
    return text


class GuangyaService:
    def __init__(
        self,
        access_token: str = "",
        refresh_token: str = "",
        device_id: str = "",
    ) -> None:
        self.client = GuangyaClient(
            access_token=extract_access_token(access_token) or None,
            refresh_token=refresh_token or None,
            device_id=device_id or None,
        )
        self.dir_cache: dict[str, str] = {"/": ""}
        self.children_cache: dict[str, dict[str, TargetNode]] = {}

    def login_if_needed(self, phone_number: str = "") -> None:
        if self.client.token:
            return
        if not phone_number:
            raise RuntimeError("光鸭云盘未配置 access_token，也没有手机号可用于短信登录。")
        self.client.login_sms(phone_number)

    def export_tokens(self) -> dict[str, str]:
        return {
            "access_token": self.client.token,
            "refresh_token": self.client.refresh_token_value or "",
            "device_id": self.client.device_id,
        }

    def close(self) -> None:
        self.client.close()

    def _load_children(self, parent_id: str) -> dict[str, TargetNode]:
        if parent_id in self.children_cache:
            return self.children_cache[parent_id]
        page = 0
        by_name: dict[str, TargetNode] = {}
        while True:
            response = self.client.fs_files(parent_id=parent_id, page=page, page_size=200)
            items = _extract_items(response)
            if not items:
                break
            for item in items:
                node = TargetNode(
                    file_id=_first(item, "fileId", "id"),
                    parent_id=_first(item, "parentId", default=parent_id),
                    name=_first(item, "fileName", "name", "dirName"),
                    is_dir=_is_dir(item),
                    raw=item,
                )
                if node.name:
                    by_name[node.name] = node
            if len(items) < 200:
                break
            page += 1
        self.children_cache[parent_id] = by_name
        return by_name

    def ensure_directory(self, path: str) -> str:
        path_obj = PurePosixPath("/" + path.lstrip("/"))
        if str(path_obj) == "/":
            return ""
        current_id = ""
        current_path = PurePosixPath("/")
        for part in path_obj.parts[1:]:
            current_path = current_path / part
            current_key = str(current_path)
            if current_key in self.dir_cache:
                current_id = self.dir_cache[current_key]
                continue
            children = self._load_children(current_id)
            existing = children.get(part)
            if existing and existing.is_dir:
                current_id = existing.file_id
            else:
                parent_cache_id = current_id
                created = self.client.fs_create_dir(part, parent_id=current_id or None)
                file_id = _first(created.get("data", {}), "fileId", "id")
                if not file_id:
                    children = self._load_children(current_id)
                    existing = children.get(part)
                    if not existing or not existing.is_dir:
                        raise RuntimeError(f"无法创建或定位光鸭目录: {current_key}")
                    file_id = existing.file_id
                current_id = file_id
                self.children_cache.pop(parent_cache_id, None)
            self.dir_cache[current_key] = current_id
        return current_id

    def get_node(self, parent_id: str, name: str) -> TargetNode | None:
        return self._load_children(parent_id).get(name)

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        node = self.get_node(parent_id, name)
        if not node:
            return False
        self.client.fs_delete([node.file_id])
        self.children_cache.pop(parent_id, None)
        return True

    def try_metadata_import(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        res_payload: dict[str, Any] = {"fileSize": file_size}
        used_hash = ""
        if md5_hex:
            res_payload["md5"] = md5_hex_to_base64(md5_hex)
            used_hash = "md5"
        body = {
            "capacity": 1,
            "res": res_payload,
            "name": file_name,
            "parentId": "" if parent_id in ("", None) else str(parent_id),
        }
        response = self.client.request(
            "https://api.guangyapan.com/nd.bizuserres.s/v1/get_res_center_token",
            method="POST",
            json=body,
        ).json()
        if int(response.get("code", 0)) == 156:
            return DirectImportResult(True, "命中光鸭秒传库存", used_hash=used_hash or "gcid")

        data = response.get("data", {})
        task_id = _first(data, "taskId")
        if gcid and task_id:
            check = self.client.check_can_flash_upload(task_id, gcid)
            if check.get("data", {}).get("canFlashUpload"):
                return DirectImportResult(True, "命中 GCID 秒传库存", used_hash="gcid", task_id=task_id)
        if task_id:
            return DirectImportResult(False, "未命中秒传库存", used_hash=used_hash, task_id=task_id)
        return DirectImportResult(False, str(response.get("msg") or response.get("message") or "秒传失败"), used_hash=used_hash)

    def instant_upload_small_file(self, file_name: str, file_size: int, md5_hex: str, parent_id: str) -> bool:
        result = self.try_metadata_import(
            file_name=file_name,
            file_size=file_size,
            parent_id=parent_id,
            md5_hex=md5_hex,
        )
        return result.success

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        parent_id = str(target_parent_id) if target_parent_id not in ("", None) else None
        try:
            return self.client.file_upload(
                str(local_path),
                name=target_name,
                parent_id=parent_id,
            )
        except HTTPStatusError as exc:
            if exc.response.status_code != 400:
                raise RuntimeError(self._format_http_error("光鸭上传失败", exc)) from exc
            try:
                return self._upload_local_file_force_multipart(local_path, parent_id, target_name)
            except HTTPStatusError as fallback_exc:
                raise RuntimeError(
                    self._format_http_error(
                        "光鸭上传兜底失败",
                        fallback_exc,
                        extra={
                            "target_name": target_name,
                            "parent_id": parent_id,
                            "size": local_path.stat().st_size,
                        },
                    )
                ) from fallback_exc

    def _upload_local_file_force_multipart(
        self,
        local_path: Path,
        parent_id: str | None,
        target_name: str,
    ) -> dict[str, Any]:
        file_size = local_path.stat().st_size
        token_resp = self.client.upload_token(target_name, file_size, parent_id)
        token_data = token_resp["data"]
        task_id = token_data["taskId"]

        flash_resp = self.client.check_can_flash_upload(task_id, local_path)
        if flash_resp.get("data", {}).get("canFlashUpload"):
            return self.client.upload_info(task_id)

        self.client.cdn_upload(local_path, token_data, content_type="application/octet-stream")
        for _ in range(3):
            resp = self.client.upload_info(task_id)
            if resp.get("msg", "") == "文件上传中":
                sleep(2)
            else:
                return resp
        return self.client.upload_info(task_id)

    @staticmethod
    def _format_http_error(message: str, exc: HTTPStatusError, extra: dict[str, Any] | None = None) -> str:
        body = ""
        try:
            body = exc.response.text.strip()
        except Exception:  # noqa: BLE001
            body = ""
        parts = [message, f"{exc.response.status_code} {exc.response.reason_phrase}", str(exc.request.url)]
        if extra:
            parts.append(str(extra))
        if body:
            body = body[:500]
            parts.append(body)
        return " | ".join(parts)

    @staticmethod
    def verify_local_md5(local_path: Path, md5_hex: str) -> None:
        hasher = md5()
        with local_path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                hasher.update(chunk)
        digest = hasher.hexdigest().upper()
        if digest != md5_hex.upper():
            raise RuntimeError(f"下载校验失败: {local_path}")
