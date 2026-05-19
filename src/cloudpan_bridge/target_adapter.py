from __future__ import annotations

import ftplib
import hashlib
import shutil
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Protocol
from urllib.parse import urlparse

import httpx

from .guangya import GuangyaService
from .openlist import OpenListClient
from .models import DirectImportResult
from .config import AppConfig
from .models import SyncState


class TargetAdapter(Protocol):
    def ensure_auth(self) -> None: ...
    def export_state(self) -> dict[str, str]: ...
    def close(self) -> None: ...
    def ensure_target_dir(self, path: str) -> str: ...
    def remove_target_path(self, path: str) -> bool: ...
    def delete_if_exists(self, parent_id: str, name: str) -> bool: ...
    def try_fast_upload(self, file_name: str, file_size: int, parent_id: str, md5_hex: str = "", gcid: str = "") -> DirectImportResult: ...
    def upload_local_file(self, local_path: Path, target_parent_id: str, target_name: str) -> dict[str, Any]: ...
    def verify_local_md5(self, local_path: Path, md5_hex: str) -> None: ...


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
    return ["guangya", "openlist", "localfs", "webdav", "s3", "ftp", "sftp", "smb"]


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
