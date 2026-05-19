from __future__ import annotations

import hashlib
import shutil
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

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


def supported_target_keys() -> list[str]:
    return ["guangya", "openlist", "localfs"]


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
    raise NotImplementedError(f"目标端暂未实现: {normalized}")
