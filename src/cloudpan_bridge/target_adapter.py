from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from .guangya import GuangyaService
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


def supported_target_keys() -> list[str]:
    return ["guangya"]


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
    raise NotImplementedError(f"目标端暂未实现: {normalized}")
