from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable

import httpx

from .models import SourceEntry


class OpenListClient:
    def __init__(
        self,
        base_url: str,
        token: str = "",
        username: str = "",
        password: str = "",
        on_progress: Callable[[str], None] | None = None,
        page_size: int = 200,
        request_interval_ms: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.username = username.strip()
        self.password = password
        self.on_progress = on_progress
        self.page_size = max(1, int(page_size))
        self.request_interval_ms = max(0, int(request_interval_ms))
        self.client = httpx.Client(timeout=60.0)

    def close(self) -> None:
        self.client.close()

    def _headers(self) -> dict[str, str]:
        headers = {"content-type": "application/json"}
        if self.token:
            headers["authorization"] = self.token
        return headers

    @staticmethod
    def _is_auth_failure(response: httpx.Response, payload: dict[str, Any] | None = None) -> bool:
        if response.status_code in {401, 403}:
            return True
        if not isinstance(payload, dict):
            return False
        message = str(payload.get("message") or payload.get("msg") or "").lower()
        return any(key in message for key in ("token", "login", "unauthorized", "auth", "expired"))

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        allow_reauth: bool = True,
    ) -> dict[str, Any]:
        response = self.client.request(
            method,
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=json_body,
        )
        payload: dict[str, Any] | None = None
        try:
            payload = response.json()
        except Exception:
            payload = None
        if allow_reauth and self.token and self.username and self.password and self._is_auth_failure(response, payload):
            self.token = ""
            self.ensure_login()
            return self._request_json(method, path, json_body=json_body, allow_reauth=False)
        response.raise_for_status()
        if isinstance(payload, dict):
            return payload
        raise RuntimeError(f"OpenList 返回了非 JSON 响应: {path}")

    def ensure_login(self) -> None:
        if self.token:
            return
        if not self.base_url or not self.username or not self.password:
            raise RuntimeError("OpenList 未配置 token，且缺少用户名/密码。")
        errors: list[str] = []
        for strategy in (
            ("明文登录", self._login_plain),
            ("新 hash 登录", lambda: self._login_hash(self._hash_password_with_suffix(self.password))),
            ("旧 hash 登录", lambda: self._login_hash(hashlib.sha256(self.password.encode("utf-8")).hexdigest())),
        ):
            label, handler = strategy
            try:
                token = handler()
                if token:
                    self.token = token
                    return
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{label}: {exc}")
        raise RuntimeError("OpenList 登录失败；已尝试明文登录、新 hash 登录、旧 hash 登录。 " + " | ".join(errors))

    def _login_plain(self) -> str:
        response = self.client.post(
            f"{self.base_url}/api/auth/login",
            headers={"content-type": "application/json"},
            json={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        return self._extract_token(response.json(), "OpenList 明文登录失败")

    def _login_hash(self, hashed_password: str) -> str:
        response = self.client.post(
            f"{self.base_url}/api/auth/login/hash",
            headers={"content-type": "application/json"},
            json={"username": self.username, "password": hashed_password},
        )
        response.raise_for_status()
        return self._extract_token(response.json(), "OpenList hash 登录失败")

    @staticmethod
    def _hash_password_with_suffix(password: str) -> str:
        salted = f"{password}-https://github.com/alist-org/alist"
        return hashlib.sha256(salted.encode("utf-8")).hexdigest()

    @staticmethod
    def _extract_token(payload: dict[str, Any], default_error: str) -> str:
        if int(payload.get("code", 500)) != 200:
            raise RuntimeError(payload.get("message") or payload.get("msg") or default_error)
        token = str(payload.get("data", {}).get("token", "")).strip()
        if not token:
            raise RuntimeError("登录成功但未返回 token")
        return token

    def export_tree(self, source_root: str) -> list[SourceEntry]:
        self.ensure_login()
        entries: list[SourceEntry] = []
        self._walk(source_root, entries)
        return entries

    def list_directories(self, path: str) -> dict[str, Any]:
        self.ensure_login()
        normalized = self._normalize_dir(path)
        payload = self._request_json(
            "POST",
            "/api/fs/list",
            json_body={
                "path": normalized,
                "password": "",
                "page": 1,
                "per_page": 1000,
                "refresh": False,
            },
        )
        if int(payload.get("code", 500)) != 200:
            raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 列表读取失败: {normalized}")
        data = payload.get("data") or {}
        if not isinstance(data, dict):
            data = {}
        content = data.get("content") or []
        if not isinstance(content, list):
            content = []
        directories: list[dict[str, str]] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if not item.get("is_dir"):
                continue
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            child_path = self._join(normalized, name)
            directories.append({"name": name, "path": child_path})
        directories.sort(key=lambda item: item["name"])
        return {
            "path": normalized,
            "parent_path": self._parent(normalized),
            "directories": directories,
        }

    def collect_leaf_directories(self, root_path: str) -> list[str]:
        self.ensure_login()
        normalized = self._normalize_dir(root_path)
        units: list[str] = []
        self._collect_leaf_directories(normalized, units)
        return units

    def iter_leaf_directories(self, root_path: str):  # type: ignore[no-untyped-def]
        self.ensure_login()
        normalized = self._normalize_dir(root_path)
        yield from self._iter_leaf_directories(normalized)

    def _walk(self, path: str, entries: list[SourceEntry]) -> None:
        page = 1
        per_page = self.page_size
        while True:
            if page > 1:
                self._sleep_between_requests()
            if self.on_progress:
                self.on_progress(f"[扫描源目录] {path} (page={page})")
            payload = self._request_json(
                "POST",
                "/api/fs/list",
                json_body={
                    "path": path,
                    "password": "",
                    "page": page,
                    "per_page": per_page,
                    "refresh": False,
                },
            )
            if int(payload.get("code", 500)) != 200:
                raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 列表读取失败: {path}")
            data = payload.get("data") or {}
            if not isinstance(data, dict):
                data = {}
            content = data.get("content") or []
            if not isinstance(content, list):
                content = []
            total = int(data.get("total") or 0)
            for item in content:
                if not isinstance(item, dict):
                    continue
                child_path = self._join(path, str(item.get("name", "")))
                if item.get("is_dir"):
                    self._walk(child_path, entries)
                    continue
                hash_fields = self._extract_hash_fields(item)
                entries.append(
                    SourceEntry(
                        path=child_path,
                        md5=hash_fields["md5"],
                        size=int(item.get("size") or 0),
                        last_op_time=str(item.get("modified") or item.get("created") or ""),
                        source_id=self._extract_source_id(item),
                        provider=self._extract_provider(item),
                        hash_type=hash_fields["hash_type"],
                        gcid=hash_fields["gcid"],
                        etag=hash_fields["etag"],
                        sha1=hash_fields["sha1"],
                        crc64=hash_fields["crc64"],
                        pickcode=hash_fields["pickcode"],
                        extra_hashes=dict(hash_fields["extra_hashes"] or {}),
                        raw_hash_info=dict(hash_fields["raw_hash_info"] or {}),
                    )
                )
            has_more = data.get("has_more")
            if has_more is None:
                has_more = page * per_page < total
            if not bool(has_more):
                break
            page += 1

    def _collect_leaf_directories(self, path: str, units: list[str]) -> None:
        for item in self._iter_leaf_directories(path):
            units.append(item)

    def _iter_leaf_directories(self, path: str):  # type: ignore[no-untyped-def]
        page = 1
        per_page = self.page_size
        child_dirs: list[str] = []
        has_file = False
        while True:
            if page > 1:
                self._sleep_between_requests()
            if self.on_progress:
                self.on_progress(f"[扫描叶子目录] {path} (page={page})")
            payload = self._request_json(
                "POST",
                "/api/fs/list",
                json_body={
                    "path": path,
                    "password": "",
                    "page": page,
                    "per_page": per_page,
                    "refresh": False,
                },
            )
            if int(payload.get("code", 500)) != 200:
                raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 列表读取失败: {path}")
            data = payload.get("data") or {}
            if not isinstance(data, dict):
                data = {}
            content = data.get("content") or []
            if not isinstance(content, list):
                content = []
            total = int(data.get("total") or 0)
            for item in content:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                if not name:
                    continue
                if item.get("is_dir"):
                    child_dirs.append(self._join(path, name))
                else:
                    has_file = True
            has_more = data.get("has_more")
            if has_more is None:
                has_more = page * per_page < total
            if not bool(has_more):
                break
            page += 1
        if not child_dirs:
            if has_file:
                yield path
            return
        for child in child_dirs:
            yield from self._iter_leaf_directories(child)

    def _sleep_between_requests(self) -> None:
        if self.request_interval_ms > 0:
            time.sleep(self.request_interval_ms / 1000)

    def get_download_url(self, path: str) -> str:
        self.ensure_login()
        payload = self._request_json(
            "POST",
            "/api/fs/get",
            json_body={"path": path, "password": ""},
        )
        if int(payload.get("code", 500)) != 200:
            raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 获取下载链接失败: {path}")
        raw_url = str(payload.get("data", {}).get("raw_url", "")).strip()
        if not raw_url:
            raise RuntimeError(f"OpenList 返回了空下载链接: {path}")
        return raw_url

    def download_file(self, source_path: str, temp_dir: Path) -> Path:
        temp_dir.mkdir(parents=True, exist_ok=True)
        local_path = temp_dir / source_path.lstrip("/").replace("/", "\\")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        raw_url = self.get_download_url(source_path)
        with self.client.stream("GET", raw_url, follow_redirects=True) as response:
            response.raise_for_status()
            with local_path.open("wb") as handle:
                for chunk in response.iter_bytes():
                    handle.write(chunk)
        return local_path

    def list_entries(self, path: str) -> list[dict[str, Any]]:
        self.ensure_login()
        normalized = self._normalize_dir(path)
        payload = self._request_json(
            "POST",
            "/api/fs/list",
            json_body={
                "path": normalized,
                "password": "",
                "page": 1,
                "per_page": 1000,
                "refresh": False,
            },
        )
        if int(payload.get("code", 500)) != 200:
            raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 列表读取失败: {normalized}")
        data = payload.get("data") or {}
        if not isinstance(data, dict):
            data = {}
        content = data.get("content") or []
        if not isinstance(content, list):
            return []
        return [item for item in content if isinstance(item, dict)]

    def ensure_directory(self, path: str) -> str:
        self.ensure_login()
        normalized = self._normalize_dir(path)
        if normalized == "/":
            return normalized
        current = "/"
        for part in [part for part in normalized.strip("/").split("/") if part]:
            current = self._join(current, part)
            self._mkdir_if_needed(current)
        return normalized

    def delete_path_if_exists(self, parent_path: str, name: str) -> bool:
        self.ensure_login()
        normalized_parent = self._normalize_dir(parent_path)
        normalized_name = str(name or "").strip().strip("/")
        if not normalized_name:
            return False
        entries = self.list_entries(normalized_parent)
        if normalized_name not in {str(item.get("name") or "").strip() for item in entries}:
            return False
        payload = self._request_json(
            "POST",
            "/api/fs/remove",
            json_body={
                "dir": normalized_parent,
                "names": [normalized_name],
            },
        )
        if int(payload.get("code", 500)) != 200:
            raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 删除失败: {normalized_parent}/{normalized_name}")
        return True

    def upload_local_file(self, local_path: Path, target_parent_path: str, target_name: str) -> dict[str, Any]:
        self.ensure_login()
        normalized_parent = self.ensure_directory(target_parent_path)
        normalized_name = str(target_name or "").strip()
        if not normalized_name:
            raise RuntimeError("OpenList 上传失败: 缺少目标文件名")
        with local_path.open("rb") as handle:
            response = self.client.put(
                f"{self.base_url}/api/fs/form",
                headers={"authorization": self.token} if self.token else {},
                data={
                    "path": normalized_parent,
                },
                files={
                    "file": (normalized_name, handle, "application/octet-stream"),
                },
            )
        response.raise_for_status()
        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("OpenList 上传返回了非 JSON 响应") from exc
        if int(payload.get("code", 500)) != 200:
            raise RuntimeError(payload.get("message") or payload.get("msg") or f"OpenList 上传失败: {normalized_parent}/{normalized_name}")
        return payload

    def _mkdir_if_needed(self, path: str) -> None:
        payload = self._request_json(
            "POST",
            "/api/fs/mkdir",
            json_body={"path": path},
        )
        code = int(payload.get("code", 500))
        if code == 200:
            return
        message = str(payload.get("message") or payload.get("msg") or "")
        lowered = message.lower()
        if any(keyword in lowered for keyword in ("exist", "exists", "already", "重复", "已存在")):
            return
        raise RuntimeError(message or f"OpenList 创建目录失败: {path}")

    @staticmethod
    def _extract_hash_fields(item: dict[str, Any]) -> dict[str, Any]:
        md5_hex = ""
        gcid = ""
        etag = ""
        sha1 = ""
        crc64 = ""
        pickcode = ""
        extra_hashes: dict[str, str] = {}
        raw_hash_info: dict[str, Any] = {}
        hash_info = item.get("hash_info") or {}
        if isinstance(hash_info, dict):
            raw_hash_info.update({str(key): value for key, value in hash_info.items()})
            for key, value in hash_info.items():
                key_lower = str(key).lower()
                if key_lower == "md5" and value:
                    md5_hex = str(value).upper()
                elif key_lower == "gcid" and value:
                    gcid = str(value).upper()
                elif key_lower == "etag" and value:
                    etag = str(value).upper()
                elif key_lower == "sha1" and value:
                    sha1 = str(value).upper()
                elif key_lower == "crc64" and value:
                    crc64 = str(value).upper()
                elif key_lower == "pickcode" and value:
                    pickcode = str(value)
                elif value not in ("", None):
                    extra_hashes[key_lower] = str(value)
        hash_info_str = str(item.get("hashinfo") or "").strip()
        if hash_info_str:
            try:
                payload = json.loads(hash_info_str)
                if isinstance(payload, dict):
                    raw_hash_info.update({str(key): value for key, value in payload.items()})
                    for key, value in payload.items():
                        key_lower = str(key).lower()
                        if key_lower == "md5" and value and not md5_hex:
                            md5_hex = str(value).upper()
                        elif key_lower == "gcid" and value and not gcid:
                            gcid = str(value).upper()
                        elif key_lower == "etag" and value and not etag:
                            etag = str(value).upper()
                        elif key_lower == "sha1" and value and not sha1:
                            sha1 = str(value).upper()
                        elif key_lower == "crc64" and value and not crc64:
                            crc64 = str(value).upper()
                        elif key_lower == "pickcode" and value and not pickcode:
                            pickcode = str(value)
                        elif value not in ("", None):
                            extra_hashes.setdefault(key_lower, str(value))
            except json.JSONDecodeError:
                pass
        if not md5_hex:
            for key in ("md5", "etag", "file_md5", "content_md5"):
                value = item.get(key)
                if value:
                    md5_hex = str(value).upper()
                    break
        if not etag:
            value = item.get("etag")
            if value:
                etag = str(value).upper()
        if not gcid:
            for key in ("gcid", "file_gcid"):
                value = item.get(key)
                if value:
                    gcid = str(value).upper()
                    break
        if not sha1:
            value = item.get("sha1")
            if value:
                sha1 = str(value).upper()
        if not crc64:
            value = item.get("crc64")
            if value:
                crc64 = str(value).upper()
        if not pickcode:
            value = item.get("pickcode")
            if value:
                pickcode = str(value)
        hash_type = "md5" if md5_hex else "gcid" if gcid else "sha1" if sha1 else "none"
        if md5_hex and not etag:
            etag = md5_hex
        extra_hashes = {
            key: value
            for key, value in extra_hashes.items()
            if key not in {"md5", "gcid", "etag", "sha1", "crc64", "pickcode"}
        }
        return {
            "md5": md5_hex,
            "gcid": gcid,
            "etag": etag,
            "sha1": sha1,
            "crc64": crc64,
            "pickcode": pickcode,
            "extra_hashes": extra_hashes,
            "raw_hash_info": raw_hash_info,
            "hash_type": hash_type,
        }

    @staticmethod
    def _extract_source_id(item: dict[str, Any]) -> str:
        for key in ("id", "file_id", "fileId", "fid"):
            value = item.get(key)
            if value not in ("", None):
                return str(value)
        return ""

    @staticmethod
    def _extract_provider(item: dict[str, Any]) -> str:
        for key in ("provider", "driver", "storage", "storage_driver"):
            value = item.get(key)
            if value not in ("", None):
                return str(value)
        return "openlist"

    @staticmethod
    def _join(parent: str, name: str) -> str:
        if parent == "/":
            return "/" + name.strip("/")
        return parent.rstrip("/") + "/" + name.strip("/")

    @staticmethod
    def _normalize_dir(path: str) -> str:
        cleaned = "/" + str(path or "/").strip()
        cleaned = cleaned.replace("\\", "/")
        while "//" in cleaned:
            cleaned = cleaned.replace("//", "/")
        return cleaned.rstrip("/") or "/"

    @staticmethod
    def _parent(path: str) -> str | None:
        normalized = OpenListClient._normalize_dir(path)
        if normalized == "/":
            return None
        parts = normalized.rstrip("/").split("/")
        if len(parts) <= 2:
            return "/"
        return "/".join(parts[:-1]) or "/"
