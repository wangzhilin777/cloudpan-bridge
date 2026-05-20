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


def source_ensure_auth(source: SourceProvider) -> None:
    if hasattr(source, "ensure_auth"):
        source.ensure_auth()  # type: ignore[call-arg]
        return
    if hasattr(source, "ensure_login"):
        source.ensure_login()  # type: ignore[attr-defined]
        return
    raise RuntimeError("当前源端 provider 缺少 ensure_auth/ensure_login 接口。")


def source_walk_tree(source: SourceProvider, source_root: str) -> list[SourceEntry]:
    if hasattr(source, "walk_tree"):
        return source.walk_tree(source_root)  # type: ignore[call-arg]
    if hasattr(source, "export_tree"):
        return source.export_tree(source_root)  # type: ignore[attr-defined]
    raise RuntimeError("当前源端 provider 缺少 walk_tree/export_tree 接口。")


def source_download_stream(source: SourceProvider, source_path: str, temp_dir: Path) -> Path:
    if hasattr(source, "download_stream"):
        return source.download_stream(source_path, temp_dir)  # type: ignore[call-arg]
    if hasattr(source, "download_file"):
        return source.download_file(source_path, temp_dir)  # type: ignore[attr-defined]
    raise RuntimeError("当前源端 provider 缺少 download_stream/download_file 接口。")


def source_get_file_fingerprints(source: SourceProvider, path: str) -> list[SourceEntry]:
    if hasattr(source, "get_file_fingerprints"):
        return list(source.get_file_fingerprints(path) or [])  # type: ignore[call-arg]
    return []


class SourceProviderCompatMixin:
    def ensure_auth(self) -> None:
        self.ensure_login()  # type: ignore[attr-defined]

    def walk_tree(self, source_root: str) -> list[SourceEntry]:
        return self.export_tree(source_root)  # type: ignore[attr-defined]

    def download_stream(self, source_path: str, temp_dir: Path) -> Path:
        return self.download_file(source_path, temp_dir)  # type: ignore[attr-defined]

    def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
        return []


class OpenListSourceProvider(SourceProviderCompatMixin):
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

    def close(self) -> None:
        self.client.close()

    def list_roots(self) -> list[str]:
        source_ensure_auth(self)
        listing = self.client.list_directories("/")
        directories = list(listing.get("directories") or [])
        roots = [str(item.get("path") or "").strip() for item in directories if str(item.get("path") or "").strip()]
        return roots or ["/"]

    def list_dir(self, path: str) -> dict[str, Any]:
        source_ensure_auth(self)
        return self.client.list_directories(path)

    def walk_tree(self, source_root: str) -> list[SourceEntry]:
        source_ensure_auth(self)
        return self.client.export_tree(source_root)

    def walk_leaf_dirs(self, root_path: str) -> Iterable[str]:
        source_ensure_auth(self)
        yield from self.client.iter_leaf_directories(root_path)

    def get_file_fingerprints(self, path: str) -> list[SourceEntry]:
        source_ensure_auth(self)
        return self.client.get_file_fingerprints(path)

    def download_stream(self, source_path: str, temp_dir: Path) -> Path:
        source_ensure_auth(self)
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
