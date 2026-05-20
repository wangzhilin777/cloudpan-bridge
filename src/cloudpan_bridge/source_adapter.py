from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Protocol

from .config import AppConfig
from .models import SourceEntry, SyncState
from .openlist import OpenListClient


class SourceProvider(Protocol):
    def ensure_auth(self) -> None: ...
    def close(self) -> None: ...
    def list_roots(self) -> list[str]: ...
    def list_dir(self, path: str) -> dict[str, Any]: ...
    def walk_tree(self, source_root: str) -> list[SourceEntry]: ...
    def walk_leaf_dirs(self, root_path: str) -> Iterable[str]: ...
    def get_file_fingerprints(self, path: str) -> list[SourceEntry]: ...
    def download_stream(self, source_path: str, temp_dir: Path) -> Path: ...
    def get_auth_state(self) -> dict[str, str]: ...
    def get_provider_key(self) -> str: ...


class OpenListSourceProvider:
    def __init__(
        self,
        base_url: str,
        token: str = "",
        username: str = "",
        password: str = "",
        page_size: int = 200,
        request_interval_ms: int = 300,
        on_progress: Any | None = None,
    ) -> None:
        self.client = OpenListClient(
            base_url=base_url,
            token=token,
            username=username,
            password=password,
            on_progress=on_progress,
            page_size=page_size,
            request_interval_ms=request_interval_ms,
        )

    def ensure_auth(self) -> None:
        self.client.ensure_login()

    def close(self) -> None:
        self.client.close()

    def list_roots(self) -> list[str]:
        self.ensure_auth()
        listing = self.client.list_directories("/")
        directories = list(listing.get("directories") or [])
        roots = [str(item.get("path") or "").strip() for item in directories if str(item.get("path") or "").strip()]
        return roots or ["/"]

    def list_dir(self, path: str) -> dict[str, Any]:
        self.ensure_auth()
        return self.client.list_directories(path)

    def walk_tree(self, source_root: str) -> list[SourceEntry]:
        self.ensure_auth()
        return self.client.export_tree(source_root)

    def walk_leaf_dirs(self, root_path: str) -> Iterable[str]:
        self.ensure_auth()
        yield from self.client.iter_leaf_directories(root_path)

    def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
        self.ensure_auth()
        return self.client.export_tree(path)

    def download_stream(self, source_path: str, temp_dir: Path) -> Path:
        self.ensure_auth()
        return self.client.download_file(source_path, temp_dir)

    def get_auth_state(self) -> dict[str, str]:
        return {
            "base_url": self.client.base_url,
            "token": self.client.token,
            "username": self.client.username,
        }

    def get_provider_key(self) -> str:
        return "openlist"


def create_source_provider(
    config: AppConfig,
    state: SyncState | None = None,
    *,
    on_progress: Any | None = None,
) -> SourceProvider:
    _ = state
    return OpenListSourceProvider(
        base_url=config.openlist_url,
        token=config.openlist_token,
        username=config.openlist_username,
        password=config.openlist_password,
        page_size=config.openlist_page_size,
        request_interval_ms=config.openlist_request_interval_ms,
        on_progress=on_progress,
    )
