from __future__ import annotations

import json
import re
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
    docker_daemon_available: bool = False
    docker_image: str = ""
    docker_container_name: str = ""
    docker_container_exists: bool = False

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
            "docker_daemon_available": self.docker_daemon_available,
            "docker_image": self.docker_image,
            "docker_container_name": self.docker_container_name,
            "docker_container_exists": self.docker_container_exists,
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
        docker_image: str = "openlistteam/openlist:latest",
        docker_container_name: str = "cloudpan-bridge-openlist",
    ) -> None:
        self.mode = str(mode or "external_local")
        self.configured_url = str(configured_url or "").rstrip("/")
        self.data_dir = Path(data_dir)
        self.binary_path = str(binary_path or "").strip()
        self.port = int(port or 0)
        self.init_admin_username = str(init_admin_username or "admin").strip() or "admin"
        self.init_admin_password = str(init_admin_password or "")
        self.docker_image = str(docker_image or "openlistteam/openlist:latest").strip() or "openlistteam/openlist:latest"
        self.docker_container_name = str(docker_container_name or "cloudpan-bridge-openlist").strip() or "cloudpan-bridge-openlist"
        self.process: subprocess.Popen[str] | None = None
        self.effective_admin_username = "admin"
        self.effective_admin_password = ""
        self.admin_token = ""
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
            "managed_docker": "托管模式（Docker）",
        }
        return labels.get(self.normalized_mode(), self.normalized_mode())

    def _run_docker(self, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
        docker_cli = shutil.which("docker")
        if not docker_cli:
            raise RuntimeError("未检测到 Docker CLI。")
        command = [docker_cli, *args]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if check and completed.returncode != 0:
            message = (completed.stderr or completed.stdout or "").strip() or f"docker {' '.join(args)} 执行失败"
            raise RuntimeError(message)
        return completed

    def _docker_daemon_available(self) -> bool:
        docker_cli = shutil.which("docker")
        if not docker_cli:
            return False
        try:
            result = self._run_docker("version", "--format", "{{.Server.Version}}")
        except Exception:
            return False
        return result.returncode == 0 and bool((result.stdout or "").strip())

    def _docker_inspect(self) -> dict[str, Any] | None:
        try:
            result = self._run_docker("inspect", self.docker_container_name)
        except Exception:
            return None
        if result.returncode != 0:
            return None
        try:
            data = json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            return None
        return data[0] if isinstance(data, list) and data else None

    def _docker_volume_spec(self) -> str:
        return f"{self.data_dir.resolve()}:/opt/openlist/data"

    def _docker_port_key(self) -> str:
        return "5244/tcp"

    def _docker_container_matches(self, inspect_data: dict[str, Any] | None) -> bool:
        if not inspect_data:
            return False
        config = inspect_data.get("Config") or {}
        host_config = inspect_data.get("HostConfig") or {}
        image = str(config.get("Image") or "")
        binds = [str(item or "") for item in (host_config.get("Binds") or [])]
        expected_bind = self._docker_volume_spec()
        port_bindings = (host_config.get("PortBindings") or {}).get(self._docker_port_key()) or []
        host_ports = {str(item.get("HostPort") or "") for item in port_bindings if isinstance(item, dict)}
        return image == self.docker_image and expected_bind in binds and str(self.port) in host_ports

    def _docker_container_running(self, inspect_data: dict[str, Any] | None) -> bool:
        if not inspect_data:
            return False
        state = inspect_data.get("State") or {}
        return bool(state.get("Running"))

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

    def config_path(self) -> Path:
        return self.data_dir / "config.json"

    def _managed_command(self, binary: str, *args: str) -> list[str]:
        return [
            binary,
            *args,
            "--data",
            str(self.data_dir),
            "--config",
            str(self.config_path()),
            "--no-prefix",
        ]

    def _run_managed_cli(self, binary: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            self._managed_command(binary, *args),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            cwd=str(self.data_dir),
        )

    def _extract_generated_password(self, output: str) -> str:
        text = str(output or "")
        patterns = [
            r"initial password is:\s*([^\r\n]+)",
            r"password:\s*([^\r\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return str(match.group(1) or "").strip()
        return ""

    def _prepare_managed_admin(self, binary: str) -> None:
        configured_password = str(self.init_admin_password or "").strip()
        self.effective_admin_username = "admin"
        self.effective_admin_password = configured_password
        self.admin_token = ""

        if configured_password:
            completed = self._run_managed_cli(binary, "admin", "set", configured_password)
            if completed.returncode != 0:
                message = (completed.stderr or completed.stdout or "").strip() or "OpenList admin set 失败"
                raise RuntimeError(message)
        else:
            completed = self._run_managed_cli(binary, "admin", "random")
            if completed.returncode != 0:
                message = (completed.stderr or completed.stdout or "").strip() or "OpenList admin random 失败"
                raise RuntimeError(message)
            generated = self._extract_generated_password(completed.stdout or completed.stderr or "")
            self.effective_admin_password = generated

        token_result = self._run_managed_cli(binary, "admin", "token")
        if token_result.returncode == 0:
            token_output = str(token_result.stdout or token_result.stderr or "")
            token_match = re.search(r"Admin token:\s*([^\r\n]+)", token_output, re.IGNORECASE)
            if token_match:
                self.admin_token = str(token_match.group(1) or "").strip()

    def _ensure_managed_config(self) -> None:
        path = self.config_path()
        payload: dict[str, Any] = {}
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        scheme = dict(payload.get("scheme") or {})
        scheme["address"] = "127.0.0.1"
        scheme["http_port"] = int(self.port or 5244)
        payload["scheme"] = scheme

        database = dict(payload.get("database") or {})
        if not database.get("type"):
            database["type"] = "sqlite3"
        if not database.get("db_file"):
            database["db_file"] = str((self.data_dir / "data.db").resolve())
        payload["database"] = database

        if not payload.get("temp_dir"):
            payload["temp_dir"] = str((self.data_dir / "temp").resolve())
        if not payload.get("bleve_dir"):
            payload["bleve_dir"] = str((self.data_dir / "bleve").resolve())

        log_payload = dict(payload.get("log") or {})
        if not log_payload.get("name"):
            log_payload["name"] = str((self.data_dir / "log" / "log.log").resolve())
        if "enable" not in log_payload:
            log_payload["enable"] = True
        payload["log"] = log_payload

        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

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
        docker_daemon_available = self._docker_daemon_available() if docker_available else False
        docker_inspect = self._docker_inspect() if docker_daemon_available else None
        docker_container_exists = bool(docker_inspect)
        docker_running = self._docker_container_running(docker_inspect)
        if self.normalized_mode() == "managed_docker":
            running = docker_running and self._is_alive(active_url)
            pid = 0
            if not docker_available:
                message = "当前未检测到本机 Docker CLI，无法使用 Docker 托管 OpenList。"
                suggested_action = "请先安装并启动 Docker Desktop / Docker Engine，验证 docker version / docker info 后再试。"
            elif not docker_daemon_available:
                message = "已检测到 Docker CLI，但当前 Docker daemon 不可用。"
                suggested_action = "请先启动 Docker Desktop 或修复 Docker daemon，再重新检查托管状态。"
            elif running:
                message = "Docker 托管 OpenList 已运行。"
                suggested_action = "当前可直接使用托管 OpenList，或调整端口/卷目录后重新创建容器。"
            elif docker_container_exists and not self._docker_container_matches(docker_inspect):
                message = "已检测到同名 Docker 容器，但其镜像、端口或卷目录与当前配置不一致。"
                suggested_action = "重新启动时将自动重建该容器，使其与当前托管配置一致。"
            else:
                message = "Docker 托管 OpenList 尚未启动。"
                suggested_action = "Docker 环境就绪后，可直接点击启动托管 OpenList 容器。"
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
        if self.is_managed_mode() and self.init_admin_username.strip() and self.init_admin_username.strip() != "admin":
            suggested_action = (
                "当前 OpenList CLI 已验证可稳定设置管理员密码，但管理员用户名仍按底层程序限制保持为 admin。"
            )
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
            runtime_profile=self.normalized_mode() if self.is_managed_mode() else self.normalized_mode(),
            init_admin_username=self.init_admin_username,
            init_admin_password_set=bool(self.effective_admin_password or self.init_admin_password),
            install_download_url=install_download_url,
            install_filename=install_filename,
            data_dir=str(self.data_dir),
            docker_available=docker_available,
            docker_cli=docker_cli,
            docker_daemon_available=docker_daemon_available,
            docker_image=self.docker_image,
            docker_container_name=self.docker_container_name,
            docker_container_exists=docker_container_exists,
        )

    def start(self) -> ManagedOpenListStatus:
        if self.normalized_mode() == "managed_docker":
            return self._start_docker()
        if self.normalized_mode() != "managed_binary":
            return self.status()
        if self.process and self.process.poll() is not None:
            self.process = None
        status = self.status()
        if status.running:
            return status
        binary = status.binary
        if not binary:
            return status
        active_url = self.active_url()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._prepare_managed_admin(binary)
        self._ensure_managed_config()
        command = self._managed_command(binary, "server", "--force-bin-dir", str(self.data_dir))
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

    def _start_docker(self) -> ManagedOpenListStatus:
        status = self.status()
        if status.running:
            return status
        if not status.docker_available:
            return status
        if not status.docker_daemon_available:
            return status
        self.data_dir.mkdir(parents=True, exist_ok=True)
        inspect_data = self._docker_inspect()
        recreate = inspect_data is not None and not self._docker_container_matches(inspect_data)
        if recreate:
            self._run_docker("rm", "-f", self.docker_container_name, check=True)
            inspect_data = None
        if inspect_data is None:
            self._run_docker(
                "run",
                "-d",
                "--restart",
                "unless-stopped",
                "--name",
                self.docker_container_name,
                "-p",
                f"{self.port}:5244",
                "-v",
                self._docker_volume_spec(),
                self.docker_image,
                check=True,
            )
        elif not self._docker_container_running(inspect_data):
            self._run_docker("start", self.docker_container_name, check=True)
        deadline = time.time() + 45
        active_url = self.active_url()
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
