from __future__ import annotations

import ftplib
import hashlib
import shutil
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Protocol
from urllib.parse import quote, urlparse

import httpx

from .guangya import GuangyaService
from .openlist import OpenListClient
from .models import DirectImportResult
from .config import AppConfig
from .models import SyncState
from .provider_registry_data import TARGET_PROFILES


class TargetAdapter(Protocol):
    def ensure_auth(self) -> None: ...
    def export_state(self) -> dict[str, str]: ...
    def preflight_capability(self) -> dict[str, Any]: ...
    def close(self) -> None: ...
    def ensure_target_dir(self, path: str) -> str: ...
    def remove_target_path(self, path: str) -> bool: ...
    def delete_if_enabled(self, parent_id: str, name: str) -> bool: ...
    def delete_if_exists(self, parent_id: str, name: str) -> bool: ...
    def try_fast_upload(self, file_name: str, file_size: int, parent_id: str, md5_hex: str = "", gcid: str = "") -> DirectImportResult: ...
    def upload_stream(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]: ...
    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]: ...
    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None: ...


def target_delete_if_enabled(target: TargetAdapter, parent_id: str, name: str) -> bool:
    if hasattr(target, "delete_if_enabled"):
        return target.delete_if_enabled(parent_id, name)  # type: ignore[call-arg]
    return target.delete_if_exists(parent_id, name)  # type: ignore[call-arg]


def target_upload_stream(target: TargetAdapter, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
    if hasattr(target, "upload_stream"):
        return target.upload_stream(local_path, target_parent_id, target_name)  # type: ignore[call-arg]
    return target.upload_local_file(local_path, target_parent_id, target_name)  # type: ignore[call-arg]


def _build_target_capability(
    target_key: str,
    *,
    configured: bool,
    missing_fields: list[str] | None = None,
    message: str = "",
    write_mode: str = "upload_overwrite",
    auth_state_fields: list[str] | None = None,
) -> dict[str, Any]:
    profile = dict(TARGET_PROFILES.get(target_key, {}) or {})
    fast_upload_hashes = list(profile.get("fast_upload_hashes") or [])
    fallback_modes = list(profile.get("fallback_modes") or [])
    supports_fast_upload = bool(fast_upload_hashes)
    return {
        "target_key": target_key,
        "configured": configured,
        "missing_fields": list(missing_fields or []),
        "supports_fast_upload": supports_fast_upload,
        "fast_upload_hashes": fast_upload_hashes,
        "fallback_modes": fallback_modes,
        "supports_delete": True,
        "auto_create_dir": bool(profile.get("auto_create_dir", True)),
        "auth_mode": str(profile.get("auth_mode") or ""),
        "write_mode": write_mode,
        "auth_state_fields": list(auth_state_fields or []),
        "message": message,
    }


class GuangyaTargetAdapter:
    def __init__(
        self,
        access_token: str = "",
        refresh_token: str = "",
        device_id: str = "",
        phone_number: str = "",
    ) -> None:
        self.phone_number = phone_number
        self.service = GuangyaService(
            access_token=access_token,
            refresh_token=refresh_token,
            device_id=device_id,
        )

    def ensure_auth(self) -> None:
        self.service.login_if_needed(self.phone_number)

    def export_state(self) -> dict[str, str]:
        return self.service.export_tokens()

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.service.client.token or self.service.client.refresh_token_value)
        missing_fields = [] if configured else ["access_token_or_refresh_token"]
        return _build_target_capability(
            "guangya",
            configured=configured,
            missing_fields=missing_fields,
            message="Guangya 目标端支持元数据秒传，未命中时可降级补传。" if configured else "请先提供 Guangya 登录态后再执行同步。",
            write_mode="metadata_import",
            auth_state_fields=["access_token", "refresh_token", "device_id"],
        )

    def close(self) -> None:
        self.service.close()

    def ensure_target_dir(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return self.service.ensure_directory(normalized)

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        return self.service.delete_if_exists(parent_id, name)

    def remove_target_path(self, path: str) -> bool:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        target_name = PurePosixPath(normalized).name
        parent_path = str(PurePosixPath(normalized).parent)
        parent_id = self.service.find_directory_id(parent_path)
        if parent_id is None:
            return False
        return self.service.delete_if_exists(parent_id, target_name)

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return self.service.try_metadata_import(
            file_name=file_name,
            file_size=file_size,
            parent_id=parent_id,
            md5_hex=md5_hex,
            gcid=gcid,
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        return self.service.upload_local_file(local_path, target_parent_id, target_name)

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        self.service.verify_local_md5(local_path, md5_hex)


class OpenListTargetAdapter:
    def __init__(
        self,
        base_url: str,
        token: str = "",
        username: str = "",
        password: str = "",
        page_size: int = 200,
        request_interval_ms: int = 300,
    ) -> None:
        self.client = OpenListClient(
            base_url=base_url,
            token=token,
            username=username,
            password=password,
            page_size=page_size,
            request_interval_ms=request_interval_ms,
        )

    def ensure_auth(self) -> None:
        self.client.ensure_login()

    def export_state(self) -> dict[str, str]:
        return {"token": self.client.token}

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.client.base_url and (self.client.token or self.client.username))
        missing_fields: list[str] = []
        if not self.client.base_url:
            missing_fields.append("openlist_url")
        if not (self.client.token or self.client.username):
            missing_fields.append("openlist_token_or_username")
        return _build_target_capability(
            "openlist",
            configured=configured,
            missing_fields=missing_fields,
            message="OpenList 目标端当前只支持普通上传/覆盖，不支持跨盘元数据秒传。" if configured else "请先补齐 OpenList 目标端连接信息。",
            write_mode="upload_overwrite",
            auth_state_fields=["token"],
        )

    def close(self) -> None:
        self.client.close()

    def ensure_target_dir(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return self.client.ensure_directory(normalized)

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        return self.client.delete_path_if_exists(parent_id, name)

    def remove_target_path(self, path: str) -> bool:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        target_name = PurePosixPath(normalized).name
        parent_path = str(PurePosixPath(normalized).parent)
        return self.client.delete_path_if_exists(parent_path, target_name)

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="OpenList 目标端当前只支持普通上传，不支持跨盘元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        return self.client.upload_local_file(local_path, target_parent_id, target_name)

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class LocalFsTargetAdapter:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir).expanduser()

    def ensure_auth(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def export_state(self) -> dict[str, str]:
        return {"root": str(self.root_dir)}

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(str(self.root_dir))
        return _build_target_capability(
            "localfs",
            configured=configured,
            missing_fields=[] if configured else ["local_target_root"],
            message="本地文件系统目标端使用复制覆盖写入，不支持元数据秒传。" if configured else "请先配置本地目标目录。",
            write_mode="local_copy",
            auth_state_fields=["root"],
        )

    def close(self) -> None:
        return None

    def ensure_target_dir(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        if normalized == "/":
            target_dir = self.root_dir
        else:
            target_dir = self.root_dir.joinpath(*PurePosixPath(normalized).parts[1:])
        target_dir.mkdir(parents=True, exist_ok=True)
        return str(target_dir)

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = Path(parent_id) / name
        if not target_path.exists():
            return False
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        return True

    def remove_target_path(self, path: str) -> bool:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        if normalized == "/":
            return False
        target_path = self.root_dir.joinpath(*PurePosixPath(normalized).parts[1:])
        if not target_path.exists():
            return False
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        return True

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="LocalFS 目标端当前只支持普通写入/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        target_dir = Path(target_parent_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / target_name
        shutil.copy2(local_path, destination)
        return {
            "path": str(destination),
            "size": destination.stat().st_size,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        expected = str(md5_hex or "").strip().upper()
        if not expected:
            return None
        digest = hashlib.md5(local_path.read_bytes()).hexdigest().upper()
        if digest != expected:
            raise RuntimeError(f"本地文件 MD5 校验失败: expected={expected}, actual={digest}")
        return None


class WebDavTargetAdapter:
    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.username = username
        self.password = password
        self.client = client or httpx.Client(timeout=60.0, follow_redirects=True)

    def ensure_auth(self) -> None:
        if not self.base_url:
            raise RuntimeError("WebDAV 目标端未配置 URL。")

    def export_state(self) -> dict[str, str]:
        return {
            "url": self.base_url,
            "username": self.username,
        }

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.base_url)
        return _build_target_capability(
            "webdav",
            configured=configured,
            missing_fields=[] if configured else ["webdav_target_url"],
            message="WebDAV 目标端支持普通上传/覆盖与自动建目录，不支持元数据秒传。" if configured else "请先配置 WebDAV URL。",
            write_mode="stream_upload",
            auth_state_fields=["url", "username"],
        )

    def close(self) -> None:
        self.client.close()

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _build_url(self, path: str) -> str:
        normalized = self._normalize_path(path)
        return f"{self.base_url}{normalized}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        request_headers = dict(headers or {})
        auth = None
        if self.username:
            auth = (self.username, self.password)
        response = self.client.request(
            method,
            self._build_url(path),
            auth=auth,
            headers=request_headers,
            content=content,
        )
        return response

    def ensure_target_dir(self, path: str) -> str:
        normalized = self._normalize_path(path)
        if normalized == "/":
            return normalized
        current = PurePosixPath("/")
        for part in PurePosixPath(normalized).parts[1:]:
            current = current / part
            response = self._request("MKCOL", str(current))
            if response.status_code not in {200, 201, 204, 301, 302, 405}:
                raise RuntimeError(f"WebDAV 创建目录失败: {current} -> {response.status_code} {response.text}")
        return normalized

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        response = self._request("DELETE", normalized)
        if response.status_code in {200, 202, 204}:
            return True
        if response.status_code == 404:
            return False
        raise RuntimeError(f"WebDAV 删除失败: {normalized} -> {response.status_code} {response.text}")

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="WebDAV 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        target_path = str(PurePosixPath(self._normalize_path(target_parent_id)) / target_name)
        response = self._request(
            "PUT",
            target_path,
            content=local_path.read_bytes(),
            headers={"content-type": "application/octet-stream"},
        )
        if response.status_code not in {200, 201, 204}:
            raise RuntimeError(f"WebDAV 上传失败: {target_path} -> {response.status_code} {response.text}")
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class S3TargetAdapter:
    def __init__(
        self,
        endpoint: str,
        bucket: str,
        access_key: str = "",
        secret_key: str = "",
        region: str = "",
        prefix: str = "",
        *,
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.endpoint = str(endpoint or "").strip()
        self.bucket = str(bucket or "").strip()
        self.access_key = str(access_key or "").strip()
        self.secret_key = str(secret_key or "").strip()
        self.region = str(region or "").strip()
        self.prefix = str(prefix or "").strip().strip("/")
        self._client_factory = client_factory or self._default_client_factory
        self.client: Any | None = None

    def _default_client_factory(self, **kwargs: Any) -> Any:
        try:
            import boto3  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised through runtime selection
            raise RuntimeError("S3 目标端需要先安装 boto3：pip install boto3") from exc
        return boto3.client("s3", **kwargs)

    def ensure_auth(self) -> None:
        if not self.endpoint:
            raise RuntimeError("S3 目标端未配置 endpoint。")
        if not self.bucket:
            raise RuntimeError("S3 目标端未配置 bucket。")
        if self.client is not None:
            return
        kwargs: dict[str, Any] = {
            "endpoint_url": self.endpoint,
        }
        if self.access_key:
            kwargs["aws_access_key_id"] = self.access_key
        if self.secret_key:
            kwargs["aws_secret_access_key"] = self.secret_key
        if self.region:
            kwargs["region_name"] = self.region
        self.client = self._client_factory(**kwargs)

    def export_state(self) -> dict[str, str]:
        return {
            "endpoint": self.endpoint,
            "bucket": self.bucket,
            "prefix": self.prefix,
            "region": self.region,
        }

    def preflight_capability(self) -> dict[str, Any]:
        missing_fields: list[str] = []
        if not self.endpoint:
            missing_fields.append("s3_target_endpoint")
        if not self.bucket:
            missing_fields.append("s3_target_bucket")
        configured = not missing_fields
        return _build_target_capability(
            "s3",
            configured=configured,
            missing_fields=missing_fields,
            message="S3 目标端支持普通上传/覆盖，不支持元数据秒传。" if configured else "请先补齐 S3 endpoint 与 bucket。",
            write_mode="stream_upload",
            auth_state_fields=["endpoint", "bucket", "prefix", "region"],
        )

    def close(self) -> None:
        client = self.client
        if client is not None and hasattr(client, "close"):
            try:
                client.close()
            except Exception:
                pass
        self.client = None

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _build_key(self, path: str) -> str:
        normalized = self._normalize_path(path)
        path_part = normalized.lstrip("/")
        if self.prefix and path_part:
            return f"{self.prefix}/{path_part}"
        if self.prefix:
            return self.prefix
        return path_part

    def ensure_target_dir(self, path: str) -> str:
        self.ensure_auth()
        return self._normalize_path(path)

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        self.ensure_auth()
        assert self.client is not None
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        key = self._build_key(normalized)
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="S3 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        self.ensure_auth()
        assert self.client is not None
        target_path = str(PurePosixPath(self._normalize_path(target_parent_id)) / target_name)
        key = self._build_key(target_path)
        self.client.upload_file(str(local_path), self.bucket, key)
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
            "bucket": self.bucket,
            "key": key,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class SeafileTargetAdapter:
    def __init__(
        self,
        base_url: str,
        token: str = "",
        username: str = "",
        password: str = "",
        repo_id: str = "",
        repo_name: str = "",
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.token = str(token or "").strip()
        self.username = username
        self.password = password
        self.repo_id = str(repo_id or "").strip()
        self.repo_name = str(repo_name or "").strip()
        self.client = client or httpx.Client(timeout=60.0, follow_redirects=True)

    def ensure_auth(self) -> None:
        if not self.base_url:
            raise RuntimeError("Seafile 目标端未配置 URL。")
        if not self.token:
            if not self.username:
                raise RuntimeError("Seafile 目标端未配置 token，也未提供用户名。")
            response = self.client.post(
                f"{self.base_url}/api2/auth-token/",
                data={"username": self.username, "password": self.password},
            )
            if response.status_code != 200:
                raise RuntimeError(f"Seafile 登录失败: {response.status_code} {response.text}")
            payload = response.json()
            token = str(payload.get("token") or "").strip()
            if not token:
                raise RuntimeError("Seafile 登录成功但未返回 token。")
            self.token = token
        if not self.repo_id:
            self.repo_id = self._resolve_repo_id()

    def export_state(self) -> dict[str, str]:
        return {
            "url": self.base_url,
            "token": self.token,
            "repo_id": self.repo_id,
            "repo_name": self.repo_name,
            "username": self.username,
        }

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.base_url and (self.token or self.username))
        missing_fields: list[str] = []
        if not self.base_url:
            missing_fields.append("seafile_target_url")
        if not (self.token or self.username):
            missing_fields.append("seafile_target_token_or_username")
        return _build_target_capability(
            "seafile",
            configured=configured,
            missing_fields=missing_fields,
            message="Seafile 目标端支持普通上传/覆盖与自动建目录，不支持元数据秒传。" if configured else "请先补齐 Seafile 连接信息。",
            write_mode="stream_upload",
            auth_state_fields=["url", "token", "repo_id", "repo_name", "username"],
        )

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _auth_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def _resolve_repo_id(self) -> str:
        headers = self._auth_headers()
        if self.repo_name:
            response = self.client.get(f"{self.base_url}/api2/repos/", headers=headers)
            if response.status_code != 200:
                raise RuntimeError(f"Seafile 获取资料库列表失败: {response.status_code} {response.text}")
            for item in list(response.json() or []):
                current_name = str(item.get("name") or "")
                if current_name == self.repo_name:
                    repo_id = str(item.get("repo_id") or item.get("id") or "").strip()
                    if repo_id:
                        return repo_id
            raise RuntimeError(f"Seafile 未找到名为 {self.repo_name} 的资料库。")
        response = self.client.get(f"{self.base_url}/api2/default-repo/", headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Seafile 获取默认资料库失败: {response.status_code} {response.text}")
        payload = response.json()
        repo_id = str(payload.get("repo_id") or payload.get("id") or "").strip()
        if not repo_id:
            raise RuntimeError("Seafile 默认资料库响应里缺少 repo_id。")
        return repo_id

    def _dir_exists(self, path: str) -> bool:
        assert self.repo_id
        normalized = self._normalize_path(path)
        response = self.client.get(
            f"{self.base_url}/api/v2.1/repos/{self.repo_id}/dir/detail/",
            params={"path": normalized},
            headers=self._auth_headers(),
        )
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        raise RuntimeError(f"Seafile 查询目录失败: {normalized} -> {response.status_code} {response.text}")

    def _create_dir(self, path: str) -> None:
        assert self.repo_id
        normalized = self._normalize_path(path)
        encoded = quote(normalized, safe="/")
        response = self.client.post(
            f"{self.base_url}/api2/repos/{self.repo_id}/dir/?p={encoded}",
            data={"operation": "mkdir"},
            headers=self._auth_headers(),
        )
        if response.status_code not in {200, 201}:
            raise RuntimeError(f"Seafile 创建目录失败: {normalized} -> {response.status_code} {response.text}")

    def ensure_target_dir(self, path: str) -> str:
        self.ensure_auth()
        normalized = self._normalize_path(path)
        if normalized == "/":
            return normalized
        current = PurePosixPath("/")
        for part in PurePosixPath(normalized).parts[1:]:
            current = current / part
            current_path = str(current)
            if not self._dir_exists(current_path):
                self._create_dir(current_path)
        return normalized

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        self.ensure_auth()
        assert self.repo_id
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        response = self.client.delete(
            f"{self.base_url}/api2/repos/{self.repo_id}/file/",
            params={"p": normalized},
            headers=self._auth_headers(),
        )
        if response.status_code in {200, 202, 204}:
            return True
        if response.status_code == 404:
            return False
        raise RuntimeError(f"Seafile 删除失败: {normalized} -> {response.status_code} {response.text}")

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="Seafile 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        self.ensure_auth()
        assert self.repo_id
        parent_path = self.ensure_target_dir(target_parent_id)
        encoded = quote(parent_path, safe="/")
        link_response = self.client.get(
            f"{self.base_url}/api2/repos/{self.repo_id}/upload-link/",
            params={"p": parent_path},
            headers=self._auth_headers(),
        )
        if link_response.status_code != 200:
            raise RuntimeError(f"Seafile 获取上传链接失败: {parent_path} -> {link_response.status_code} {link_response.text}")
        try:
            upload_link = link_response.json()
        except Exception:
            upload_link = link_response.text
        upload_url = str(upload_link or "").strip().strip('"')
        if not upload_url:
            raise RuntimeError("Seafile 上传链接为空。")
        if upload_url.startswith("/"):
            upload_url = f"{self.base_url}{upload_url}"
        with local_path.open("rb") as handle:
            response = self.client.post(
                upload_url,
                data={"parent_dir": parent_path, "replace": "1"},
                files={"file": (target_name, handle, "application/octet-stream")},
                headers=self._auth_headers(),
            )
        if response.status_code not in {200, 201}:
            raise RuntimeError(f"Seafile 上传失败: {parent_path} -> {response.status_code} {response.text}")
        target_path = str(PurePosixPath(parent_path) / target_name)
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
            "repo_id": self.repo_id,
            "repo_name": self.repo_name,
            "upload_link_path": encoded,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class SmbTargetAdapter:
    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        *,
        client_module: Any | None = None,
    ) -> None:
        self.base_url = str(base_url or "").strip()
        self.username = username
        self.password = password
        self.client_module = client_module
        self._registered = False
        parsed = urlparse(self.base_url if "://" in self.base_url else f"smb://{self.base_url.lstrip('/')}")
        self.host = parsed.hostname or ""
        self.share = ""
        self.root_path = "/"
        parsed_path = str(parsed.path or "").lstrip("/")
        if parsed_path:
            parts = PurePosixPath("/" + parsed_path).parts[1:]
            if parts:
                self.share = str(parts[0])
                self.root_path = "/" + "/".join(parts[1:]) if len(parts) > 1 else "/"

    def _load_client_module(self) -> Any:
        if self.client_module is not None:
            return self.client_module
        try:
            import smbclient  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised through runtime selection
            raise RuntimeError("SMB 目标端需要先安装 smbprotocol：pip install smbprotocol") from exc
        self.client_module = smbclient
        return smbclient

    def ensure_auth(self) -> None:
        if not self.host:
            raise RuntimeError("SMB 目标端未配置 URL。")
        if not self.share:
            raise RuntimeError("SMB 目标端未配置共享名。")
        client = self._load_client_module()
        if not self._registered:
            client.register_session(self.host, username=self.username, password=self.password)
            self._registered = True

    def export_state(self) -> dict[str, str]:
        return {
            "url": self.base_url,
            "username": self.username,
        }

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.host and self.share)
        missing_fields: list[str] = []
        if not self.host:
            missing_fields.append("smb_target_url")
        if not self.share:
            missing_fields.append("smb_share")
        return _build_target_capability(
            "smb",
            configured=configured,
            missing_fields=missing_fields,
            message="SMB 目标端支持普通上传/覆盖，不支持元数据秒传。" if configured else "请先补齐 SMB URL 与共享名。",
            write_mode="stream_upload",
            auth_state_fields=["url", "username"],
        )

    def close(self) -> None:
        return None

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _build_unc_path(self, path: str) -> str:
        normalized = self._normalize_path(path)
        remote = normalized.lstrip("/")
        base_parts = [self.share]
        root = str(self.root_path or "/").strip("/")
        if root:
            base_parts.append(root)
        if remote:
            base_parts.extend(part for part in remote.split("/") if part)
        unc_tail = "\\".join(part for part in base_parts if part)
        return f"\\\\{self.host}\\{unc_tail}"

    def ensure_target_dir(self, path: str) -> str:
        self.ensure_auth()
        client = self._load_client_module()
        normalized = self._normalize_path(path)
        current = PurePosixPath("/")
        for part in PurePosixPath(normalized).parts[1:]:
            current = current / part
            unc = self._build_unc_path(str(current))
            try:
                client.mkdir(unc)
            except Exception:
                pass
        return normalized

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        self.ensure_auth()
        client = self._load_client_module()
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        unc = self._build_unc_path(normalized)
        try:
            client.remove(unc)
            return True
        except Exception:
            try:
                client.rmdir(unc)
                return True
            except Exception:
                return False

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="SMB 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        self.ensure_auth()
        client = self._load_client_module()
        target_path = str(PurePosixPath(self._normalize_path(target_parent_id)) / target_name)
        unc = self._build_unc_path(target_path)
        with local_path.open("rb") as src, client.open_file(unc, mode="wb") as dst:
            shutil.copyfileobj(src, dst)
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class AzureBlobTargetAdapter:
    def __init__(
        self,
        account_url: str,
        container: str,
        account_name: str = "",
        account_key: str = "",
        prefix: str = "",
        *,
        service_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.account_url = str(account_url or "").strip()
        self.container = str(container or "").strip()
        self.account_name = str(account_name or "").strip()
        self.account_key = str(account_key or "").strip()
        self.prefix = str(prefix or "").strip().strip("/")
        self._service_factory = service_factory or self._default_service_factory
        self.service_client: Any | None = None
        self.container_client: Any | None = None

    def _default_service_factory(self, **kwargs: Any) -> Any:
        try:
            from azure.storage.blob import BlobServiceClient  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised through runtime selection
            raise RuntimeError("Azure Blob 目标端需要先安装 azure-storage-blob：pip install azure-storage-blob") from exc
        return BlobServiceClient(**kwargs)

    def ensure_auth(self) -> None:
        if not self.account_url:
            raise RuntimeError("Azure Blob 目标端未配置 account_url。")
        if not self.container:
            raise RuntimeError("Azure Blob 目标端未配置 container。")
        if self.container_client is not None:
            return
        kwargs: dict[str, Any] = {"account_url": self.account_url}
        if self.account_key:
            kwargs["credential"] = self.account_key
        self.service_client = self._service_factory(**kwargs)
        self.container_client = self.service_client.get_container_client(self.container)

    def export_state(self) -> dict[str, str]:
        return {
            "account_url": self.account_url,
            "container": self.container,
            "prefix": self.prefix,
            "account_name": self.account_name,
        }

    def preflight_capability(self) -> dict[str, Any]:
        missing_fields: list[str] = []
        if not self.account_url:
            missing_fields.append("azureblob_target_account_url")
        if not self.container:
            missing_fields.append("azureblob_target_container")
        configured = not missing_fields
        return _build_target_capability(
            "azureblob",
            configured=configured,
            missing_fields=missing_fields,
            message="Azure Blob 目标端支持普通上传/覆盖，不支持元数据秒传。" if configured else "请先补齐 Azure Blob account_url 与 container。",
            write_mode="stream_upload",
            auth_state_fields=["account_url", "container", "prefix", "account_name"],
        )

    def close(self) -> None:
        self.container_client = None
        self.service_client = None

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _build_blob_name(self, path: str) -> str:
        normalized = self._normalize_path(path)
        path_part = normalized.lstrip("/")
        if self.prefix and path_part:
            return f"{self.prefix}/{path_part}"
        if self.prefix:
            return self.prefix
        return path_part

    def ensure_target_dir(self, path: str) -> str:
        self.ensure_auth()
        return self._normalize_path(path)

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        self.ensure_auth()
        assert self.container_client is not None
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        blob_name = self._build_blob_name(normalized)
        try:
            self.container_client.delete_blob(blob_name)
            return True
        except Exception:
            return False

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="Azure Blob 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        self.ensure_auth()
        assert self.container_client is not None
        target_path = str(PurePosixPath(self._normalize_path(target_parent_id)) / target_name)
        blob_name = self._build_blob_name(target_path)
        with local_path.open("rb") as handle:
            self.container_client.upload_blob(blob_name, handle, overwrite=True)
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
            "container": self.container,
            "blob_name": blob_name,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class FtpTargetAdapter:
    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        *,
        ftp_factory: Callable[[], ftplib.FTP] | None = None,
    ) -> None:
        self.base_url = str(base_url or "").strip()
        self.username = username
        self.password = password
        self._ftp_factory = ftp_factory or ftplib.FTP
        self.ftp: ftplib.FTP | None = None
        parsed = urlparse(self.base_url if "://" in self.base_url else f"ftp://{self.base_url.lstrip('/')}")
        self.host = parsed.hostname or ""
        self.port = int(parsed.port or 21)
        self.root_path = str(PurePosixPath("/" + parsed.path.lstrip("/")))

    def ensure_auth(self) -> None:
        if not self.host:
            raise RuntimeError("FTP 目标端未配置 URL。")
        if self.ftp is not None:
            return
        ftp = self._ftp_factory()
        ftp.connect(self.host, self.port)
        ftp.login(self.username or "anonymous", self.password or "")
        self.ftp = ftp

    def export_state(self) -> dict[str, str]:
        return {
            "url": self.base_url,
            "username": self.username,
        }

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.host)
        return _build_target_capability(
            "ftp",
            configured=configured,
            missing_fields=[] if configured else ["ftp_target_url"],
            message="FTP 目标端支持普通上传/覆盖，不支持元数据秒传。" if configured else "请先配置 FTP URL。",
            write_mode="stream_upload",
            auth_state_fields=["url", "username"],
        )

    def close(self) -> None:
        if self.ftp is None:
            return
        try:
            self.ftp.quit()
        except Exception:
            try:
                self.ftp.close()
            except Exception:
                pass
        self.ftp = None

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _build_remote_path(self, path: str) -> str:
        normalized = self._normalize_path(path)
        if self.root_path == "/":
            return normalized
        if normalized == "/":
            return self.root_path
        return str(PurePosixPath(self.root_path) / normalized.lstrip("/"))

    def ensure_target_dir(self, path: str) -> str:
        self.ensure_auth()
        assert self.ftp is not None
        normalized = self._normalize_path(path)
        remote = self._build_remote_path(normalized)
        current = PurePosixPath("/")
        for part in PurePosixPath(remote).parts[1:]:
            current = current / part
            try:
                self.ftp.mkd(str(current))
            except Exception:
                # Most FTP servers return an error if the directory already exists.
                pass
        return normalized

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        self.ensure_auth()
        assert self.ftp is not None
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        remote = self._build_remote_path(normalized)
        try:
            self.ftp.delete(remote)
            return True
        except Exception:
            try:
                self.ftp.rmd(remote)
                return True
            except Exception:
                return False

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="FTP 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        self.ensure_auth()
        assert self.ftp is not None
        target_path = str(PurePosixPath(self._normalize_path(target_parent_id)) / target_name)
        remote = self._build_remote_path(target_path)
        with local_path.open("rb") as handle:
            self.ftp.storbinary(f"STOR {remote}", handle)
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


class SftpTargetAdapter:
    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        *,
        connect_factory: Callable[[str, int, str, str], tuple[Any, Any]] | None = None,
    ) -> None:
        self.base_url = str(base_url or "").strip()
        self.username = username
        self.password = password
        self._connect_factory = connect_factory or self._default_connect_factory
        self.transport: Any | None = None
        self.sftp: Any | None = None
        parsed = urlparse(self.base_url if "://" in self.base_url else f"sftp://{self.base_url.lstrip('/')}")
        self.host = parsed.hostname or ""
        self.port = int(parsed.port or 22)
        self.root_path = str(PurePosixPath("/" + parsed.path.lstrip("/")))

    def _default_connect_factory(self, host: str, port: int, username: str, password: str) -> tuple[Any, Any]:
        try:
            import paramiko  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised through runtime selection
            raise RuntimeError("SFTP 目标端需要先安装 paramiko：pip install paramiko") from exc
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return transport, sftp

    def ensure_auth(self) -> None:
        if not self.host:
            raise RuntimeError("SFTP 目标端未配置 URL。")
        if self.sftp is not None:
            return
        transport, sftp = self._connect_factory(self.host, self.port, self.username, self.password)
        self.transport = transport
        self.sftp = sftp

    def export_state(self) -> dict[str, str]:
        return {
            "url": self.base_url,
            "username": self.username,
        }

    def preflight_capability(self) -> dict[str, Any]:
        configured = bool(self.host)
        return _build_target_capability(
            "sftp",
            configured=configured,
            missing_fields=[] if configured else ["sftp_target_url"],
            message="SFTP 目标端支持普通上传/覆盖，不支持元数据秒传。" if configured else "请先配置 SFTP URL。",
            write_mode="stream_upload",
            auth_state_fields=["url", "username"],
        )

    def close(self) -> None:
        if self.sftp is not None:
            try:
                self.sftp.close()
            except Exception:
                pass
        if self.transport is not None:
            try:
                self.transport.close()
            except Exception:
                pass
        self.sftp = None
        self.transport = None

    def _normalize_path(self, path: str) -> str:
        normalized = str(PurePosixPath("/" + str(path or "/").lstrip("/")))
        return "/" if normalized == "." else normalized

    def _build_remote_path(self, path: str) -> str:
        normalized = self._normalize_path(path)
        if self.root_path == "/":
            return normalized
        if normalized == "/":
            return self.root_path
        return str(PurePosixPath(self.root_path) / normalized.lstrip("/"))

    def ensure_target_dir(self, path: str) -> str:
        self.ensure_auth()
        assert self.sftp is not None
        normalized = self._normalize_path(path)
        remote = self._build_remote_path(normalized)
        current = PurePosixPath("/")
        for part in PurePosixPath(remote).parts[1:]:
            current = current / part
            try:
                self.sftp.mkdir(str(current))
            except Exception:
                pass
        return normalized

    def delete_if_exists(self, parent_id: str, name: str) -> bool:
        target_path = str(PurePosixPath(self._normalize_path(parent_id)) / name)
        return self.remove_target_path(target_path)

    def remove_target_path(self, path: str) -> bool:
        self.ensure_auth()
        assert self.sftp is not None
        normalized = self._normalize_path(path)
        if normalized == "/":
            return False
        remote = self._build_remote_path(normalized)
        try:
            self.sftp.remove(remote)
            return True
        except Exception:
            try:
                self.sftp.rmdir(remote)
                return True
            except Exception:
                return False

    def try_fast_upload(
        self,
        file_name: str,
        file_size: int,
        parent_id: str,
        md5_hex: str = "",
        gcid: str = "",
    ) -> DirectImportResult:
        return DirectImportResult(
            success=False,
            reason="SFTP 目标端当前只支持普通上传/覆盖，不支持元数据秒传。",
        )

    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]:
        self.ensure_auth()
        assert self.sftp is not None
        target_path = str(PurePosixPath(self._normalize_path(target_parent_id)) / target_name)
        remote = self._build_remote_path(target_path)
        self.sftp.put(str(local_path), remote)
        return {
            "path": target_path,
            "size": local_path.stat().st_size,
        }

    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None:
        return None


def supported_target_keys() -> list[str]:
    return ["guangya", "openlist", "localfs", "webdav", "s3", "seafile", "azureblob", "ftp", "sftp", "smb"]


def build_target_preflight_capability(config: AppConfig, state: SyncState, target_key: str = "") -> dict[str, Any]:
    normalized = str(target_key or config.target_key or "guangya").strip().lower() or "guangya"
    if normalized not in supported_target_keys():
        profile = dict(TARGET_PROFILES.get(normalized, {}) or {})
        return {
            "target_key": normalized,
            "configured": False,
            "missing_fields": [],
            "supports_fast_upload": bool(profile.get("fast_upload_hashes")),
            "fast_upload_hashes": list(profile.get("fast_upload_hashes") or []),
            "fallback_modes": list(profile.get("fallback_modes") or []),
            "supports_delete": False,
            "auto_create_dir": bool(profile.get("auto_create_dir", False)),
            "auth_mode": str(profile.get("auth_mode") or ""),
            "write_mode": "unavailable",
            "auth_state_fields": [],
            "message": f"目标端 {normalized} 当前还没有可执行适配器。",
        }
    adapter = create_target_adapter(config, state, normalized)
    try:
        return adapter.preflight_capability()
    finally:
        adapter.close()


def create_target_adapter(config: AppConfig, state: SyncState, target_key: str = "") -> TargetAdapter:
    normalized = str(target_key or config.target_key or "guangya").strip().lower() or "guangya"
    if normalized == "guangya":
        target_state = state.get_target_state("guangya")
        access_token = (
            target_state.get("access_token", "")
            or config.guangya_access_token
            or ""
        )
        from .guangya import extract_access_token

        return GuangyaTargetAdapter(
            access_token=access_token or extract_access_token(getattr(config, "guangya_authorization", "")),
            refresh_token=target_state.get("refresh_token", "") or config.guangya_refresh_token,
            device_id=target_state.get("device_id", "") or config.guangya_device_id,
            phone_number=config.guangya_phone,
        )
    if normalized == "openlist":
        target_state = state.get_target_state("openlist")
        return OpenListTargetAdapter(
            base_url=config.openlist_url,
            token=target_state.get("token", "") or config.openlist_token,
            username=config.openlist_username,
            password=config.openlist_password,
            page_size=config.openlist_page_size,
            request_interval_ms=config.openlist_request_interval_ms,
        )
    if normalized == "localfs":
        return LocalFsTargetAdapter(config.local_target_root)
    if normalized == "webdav":
        return WebDavTargetAdapter(
            base_url=config.webdav_target_url,
            username=config.webdav_target_username,
            password=config.webdav_target_password,
        )
    if normalized == "s3":
        return S3TargetAdapter(
            endpoint=config.s3_target_endpoint,
            bucket=config.s3_target_bucket,
            access_key=config.s3_target_access_key,
            secret_key=config.s3_target_secret_key,
            region=config.s3_target_region,
            prefix=config.s3_target_prefix,
        )
    if normalized == "seafile":
        target_state = state.get_target_state("seafile")
        return SeafileTargetAdapter(
            base_url=config.seafile_target_url,
            token=target_state.get("token", "") or config.seafile_target_token,
            username=config.seafile_target_username,
            password=config.seafile_target_password,
            repo_id=target_state.get("repo_id", "") or config.seafile_target_repo_id,
            repo_name=config.seafile_target_repo_name,
        )
    if normalized == "azureblob":
        return AzureBlobTargetAdapter(
            account_url=config.azureblob_target_account_url,
            container=config.azureblob_target_container,
            account_name=config.azureblob_target_account_name,
            account_key=config.azureblob_target_account_key,
            prefix=config.azureblob_target_prefix,
        )
    if normalized == "smb":
        return SmbTargetAdapter(
            base_url=config.smb_target_url,
            username=config.smb_target_username,
            password=config.smb_target_password,
        )
    if normalized == "ftp":
        return FtpTargetAdapter(
            base_url=config.ftp_target_url,
            username=config.ftp_target_username,
            password=config.ftp_target_password,
        )
    if normalized == "sftp":
        return SftpTargetAdapter(
            base_url=config.sftp_target_url,
            username=config.sftp_target_username,
            password=config.sftp_target_password,
        )
    raise NotImplementedError(f"目标端暂未实现: {normalized}")
