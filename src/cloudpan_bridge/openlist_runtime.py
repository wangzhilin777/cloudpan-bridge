from __future__ import annotations

import json
import platform
import shutil
import socket
import subprocess
import time
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass(slots=True)
class ManagedOpenListStatus:
    mode: str
    configured_url: str
    active_url: str
    port: int
    running: bool
    binary: str
    pid: int = 0
    message: str = ""
    binary_exists: bool = False
    mode_label: str = ""
    install_required: bool = False
    can_start: bool = False
    suggested_action: str = ""
    runtime_profile: str = ""
    init_admin_username: str = ""
    init_admin_password_set: bool = False
    install_download_url: str = ""
    install_filename: str = ""
    data_dir: str = ""
    docker_available: bool = False
    docker_cli: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "configured_url": self.configured_url,
            "active_url": self.active_url,
            "port": self.port,
            "running": self.running,
            "binary": self.binary,
            "pid": self.pid,
            "message": self.message,
            "binary_exists": self.binary_exists,
            "mode_label": self.mode_label,
            "install_required": self.install_required,
            "can_start": self.can_start,
            "suggested_action": self.suggested_action,
            "runtime_profile": self.runtime_profile,
            "init_admin_username": self.init_admin_username,
            "init_admin_password_set": self.init_admin_password_set,
            "install_download_url": self.install_download_url,
            "install_filename": self.install_filename,
            "data_dir": self.data_dir,
            "docker_available": self.docker_available,
            "docker_cli": self.docker_cli,
        }


class ManagedOpenListRuntime:
    def __init__(
        self,
        *,
        mode: str,
        configured_url: str,
        data_dir: Path,
        binary_path: str = "",
        port: int = 0,
        init_admin_username: str = "admin",
        init_admin_password: str = "",
    ) -> None:
        self.mode = str(mode or "external_local")
        self.configured_url = str(configured_url or "").rstrip("/")
        self.data_dir = Path(data_dir)
        self.binary_path = str(binary_path or "").strip()
        self.port = int(port or 0)
        self.init_admin_username = str(init_admin_username or "admin").strip() or "admin"
        self.init_admin_password = str(init_admin_password or "")
        self.process: subprocess.Popen[str] | None = None
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def normalized_mode(self) -> str:
        normalized = str(self.mode or "").strip().lower()
        if normalized == "external":
            return "external_local"
        if normalized == "managed":
            return "managed_binary"
        return normalized or "external_local"

    def is_managed_mode(self) -> bool:
        return self.normalized_mode().startswith("managed_")

    def mode_label(self) -> str:
        labels = {
            "external_local": "外部模式（本机）",
            "external_remote": "外部模式（远程）",
            "managed_binary": "托管模式（本机二进制）",
            "managed_docker_placeholder": "托管模式（Docker 预留）",
        }
        return labels.get(self.normalized_mode(), self.normalized_mode())

    def _detect_binary(self) -> str:
        candidates = [
            self.binary_path,
            str((self.data_dir / "openlist.exe").resolve()),
            str((self.data_dir / "alist.exe").resolve()),
            "openlist.exe",
            "alist.exe",
            "openlist",
            "alist",
        ]
        for candidate in candidates:
            text = str(candidate or "").strip()
            if not text:
                continue
            if Path(text).exists():
                return text
            if "\\" not in text and "/" not in text and shutil.which(text):
                return text
        return ""

    def install_download_info(self) -> tuple[str, str]:
        machine = platform.machine().lower()
        filename = "openlist-windows-amd64.zip"
        if "arm64" in machine or machine == "aarch64":
            filename = "openlist-windows-arm64.zip"
        elif machine in {"x86", "i386", "i686"}:
            filename = "openlist-windows-386.zip"
        return ("https://api.github.com/repos/OpenListTeam/OpenList/releases/latest", filename)

    def active_url(self) -> str:
        if not self.is_managed_mode():
            return self.configured_url
        port = self.port or _pick_free_port()
        self.port = port
        return f"http://127.0.0.1:{port}"

    def status(self) -> ManagedOpenListStatus:
        binary = self._detect_binary()
        active_url = self.active_url()
        running = self._is_alive(active_url)
        pid = self.process.pid if self.process else 0
        message = ""
        install_required = False
        suggested_action = ""
        install_download_url = ""
        install_filename = ""
        docker_cli = shutil.which("docker") or ""
        docker_available = bool(docker_cli)
        if self.normalized_mode() == "managed_docker_placeholder":
            if docker_available:
                message = "已检测到本机 Docker 环境，但 Docker 托管当前仍仅预留状态，不会真正自动创建 OpenList 容器。"
                suggested_action = "当前可继续使用外部模式或本机二进制托管；后续若落地 Docker 托管，可复用当前 Docker 环境。"
            else:
                message = "当前未检测到本机 Docker 环境，且 Docker 托管仍仅预留状态。"
                suggested_action = "如需后续使用 Docker 托管，请先完成 docker version / docker info 验证；当前请改用外部模式或本机二进制托管。"
        elif self.is_managed_mode() and not binary:
            message = "未找到可用的 OpenList/Alist 可执行文件。可选择先拉取本机运行时；如果不拉取，请改用外部模式。"
            install_required = True
            suggested_action = "可先拉取本机 OpenList 运行时，或切换到外部本机/远程模式。"
            _, install_filename = self.install_download_info()
        elif self.is_managed_mode() and not running and self.process is None:
            message = "托管 OpenList 尚未启动。"
            suggested_action = "运行时已就绪后，可直接点击启动托管 OpenList。"
        elif not self.is_managed_mode() and not running:
            message = "当前外部 OpenList 不可访问。"
            suggested_action = "请检查 URL、端口和登录凭证，或切换到托管模式。"
        if self.is_managed_mode() and not self.init_admin_password and not suggested_action:
            suggested_action = "当前只负责启动进程；若底层程序不支持启动时初始化管理员密码，请在 OpenList 首次进入后自行确认或重设管理员密码。"
        return ManagedOpenListStatus(
            mode=self.normalized_mode(),
            configured_url=self.configured_url,
            active_url=active_url,
            port=self.port,
            running=running,
            binary=binary,
            pid=pid,
            message=message,
            binary_exists=bool(binary),
            mode_label=self.mode_label(),
            install_required=install_required,
            can_start=bool(binary) and self.normalized_mode() == "managed_binary",
            suggested_action=suggested_action,
            runtime_profile="managed_binary" if self.is_managed_mode() else self.normalized_mode(),
            init_admin_username=self.init_admin_username,
            init_admin_password_set=bool(self.init_admin_password),
            install_download_url=install_download_url,
            install_filename=install_filename,
            data_dir=str(self.data_dir),
            docker_available=docker_available,
            docker_cli=docker_cli,
        )

    def start(self) -> ManagedOpenListStatus:
        if self.normalized_mode() != "managed_binary":
            return self.status()
        status = self.status()
        if status.running:
            return status
        binary = status.binary
        if not binary:
            return status
        active_url = self.active_url()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        command = [
            binary,
            "server",
            "--data",
            str(self.data_dir),
            "--force-bin-dir",
            str(self.data_dir),
            "--no-prefix",
        ]
        self.process = subprocess.Popen(
            command,
            cwd=str(self.data_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            if self._is_alive(active_url):
                return self.status()
            time.sleep(1)
        return self.status()

    def install_binary(self) -> ManagedOpenListStatus:
        if self.normalized_mode() != "managed_binary":
            return self.status()
        status = self.status()
        if status.binary_exists:
            return status
        api_url, expected_asset = self.install_download_info()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        release: dict[str, Any] = {}
        asset_url = ""
        asset_name = ""
        archive_response: httpx.Response | None = None
        request_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "CloudPan-Bridge/managed-runtime",
        }
        last_error: Exception | None = None
        for verify in (True, False):
            try:
                with httpx.Client(timeout=60.0, follow_redirects=True, verify=verify) as client:
                    response = client.get(api_url, headers=request_headers)
                    response.raise_for_status()
                    release = json.loads(response.text)
                    for asset in release.get("assets", []):
                        name = str(asset.get("name") or "")
                        if name == expected_asset:
                            asset_url = str(asset.get("browser_download_url") or "")
                            asset_name = name
                            break
                    if not asset_url:
                        raise RuntimeError(f"OpenList release 中未找到适用于当前环境的资产：{expected_asset}")
                    archive_response = client.get(asset_url, headers={"User-Agent": request_headers["User-Agent"]})
                    archive_response.raise_for_status()
                    break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                archive_response = None
                asset_url = ""
                asset_name = ""
                continue
        if archive_response is None:
            raise RuntimeError(f"拉取 OpenList runtime 失败: {last_error}") from last_error
        archive_bytes = BytesIO(archive_response.content)
        with zipfile.ZipFile(archive_bytes) as archive:
            candidate_names = [name for name in archive.namelist() if name.lower().endswith("openlist.exe")]
            if not candidate_names:
                candidate_names = [name for name in archive.namelist() if name.lower().endswith(".exe")]
            if not candidate_names:
                raise RuntimeError(f"下载的 OpenList 归档 {asset_name} 中没有可执行文件。")
            target_name = candidate_names[0]
            archive.extract(target_name, path=self.data_dir)
            extracted = self.data_dir / target_name
            final_path = self.data_dir / "openlist.exe"
            if extracted.resolve() != final_path.resolve():
                final_path.write_bytes(extracted.read_bytes())
                extracted.unlink()
                parent = extracted.parent
                if parent != self.data_dir and parent.exists():
                    try:
                        parent.rmdir()
                    except OSError:
                        pass
            self.binary_path = str(final_path.resolve())
        return self.status()

    def _is_alive(self, base_url: str) -> bool:
        if not base_url:
            return False
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{base_url}/api/public/settings")
                return response.status_code < 500
        except Exception:
            return False
