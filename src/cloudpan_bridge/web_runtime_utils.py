from __future__ import annotations

from pathlib import PurePosixPath

from .config import AppConfig
from .models import PendingFileState, normalize_posix_path


def is_rate_limit_error_message(message: str) -> bool:
    text = str(message or "").lower()
    keywords = [
        "429",
        "too many",
        "rate limit",
        "too frequent",
        "risk",
        "captcha",
        "frequency",
        "风控",
        "限流",
        "频率",
        "过于频繁",
        "稍后再试",
    ]
    return any(keyword in text for keyword in keywords)


def compute_rate_limit_cooldown_ms(config: AppConfig, source_path: str = "") -> int:
    base = {
        "safe": 180_000,
        "balanced": 90_000,
        "fast": 45_000,
        "custom": max(int(config.queue_interval_ms) * 3, 30_000),
    }.get(str(config.rate_limit_mode or "safe").lower(), 120_000)
    source = str(source_path or config.source_path or "").lower()
    if any(key in source for key in ("baidu", "189", "cloud", "thunder", "xunlei")):
        base = int(base * 1.5)
    return max(base, int(config.queue_interval_ms))


def build_pending_selected_execution_groups(
    selected_paths: list[str],
    pending_files: dict[str, PendingFileState],
) -> list[tuple[str, list[str]]]:
    normalized_selected = [normalize_posix_path(path) for path in selected_paths if str(path).strip()]
    directory_files: dict[str, list[str]] = {}
    directory_order: dict[str, int] = {}
    file_seen: set[str] = set()
    for index, path in enumerate(normalized_selected):
        pending = pending_files.get(path)
        if not pending or path in file_seen:
            continue
        file_seen.add(path)
        directory = str(PurePosixPath(path).parent)
        directory_files.setdefault(directory, []).append(path)
        directory_order.setdefault(directory, index)
    if not directory_files:
        return []

    directories = list(directory_files.keys())
    children_map: dict[str, list[str]] = {directory: [] for directory in directories}
    roots: list[str] = []
    for directory in directories:
        parent = str(PurePosixPath(directory).parent)
        nearest_selected_parent = ""
        while parent != directory:
            if parent in children_map:
                nearest_selected_parent = parent
                break
            next_parent = str(PurePosixPath(parent).parent)
            if next_parent == parent:
                break
            parent = next_parent
        if nearest_selected_parent:
            children_map[nearest_selected_parent].append(directory)
        else:
            roots.append(directory)

    def sort_key(path: str) -> tuple[int, str]:
        return (directory_order.get(path, 10**9), path)

    for key in children_map:
        children_map[key].sort(key=sort_key)
    roots.sort(key=sort_key)

    groups: list[tuple[str, list[str]]] = []

    def walk(directory: str) -> None:
        for child in children_map.get(directory, []):
            walk(child)
        file_paths = directory_files.get(directory, [])
        if file_paths:
            groups.append((directory, file_paths))

    for root in roots:
        walk(root)
    return groups
