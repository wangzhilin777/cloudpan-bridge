from __future__ import annotations

import argparse
from pathlib import Path

from .config import AppConfig, write_example_config
from .syncer import SyncRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CloudPan Bridge: 基于 OpenList 的多源网盘到光鸭云盘桥接控制台")
    subparsers = parser.add_subparsers(dest="command", required=True)
    default_config = ".work/openlist-config.json"

    init_parser = subparsers.add_parser("init-config", help="生成示例配置文件")
    init_parser.add_argument("--path", default=default_config, help="输出配置文件路径")

    sync_parser = subparsers.add_parser("sync", help="执行同步")
    sync_parser.add_argument("--config", default=default_config, help="配置文件路径")
    sync_parser.add_argument("--yes-download-upload", action="store_true", help="直接允许下载后再上传")
    sync_parser.add_argument("--no-download-upload", action="store_true", help="禁止下载后再上传")
    sync_parser.add_argument("--dry-run", action="store_true", help="只输出计划，不真正执行")

    serve_parser = subparsers.add_parser("serve", help="启动本地页面控制台")
    serve_parser.add_argument("--config", default=default_config, help="配置文件路径")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-config":
        output = Path(args.path)
        write_example_config(output)
        print(f"已生成示例配置: {output}")
        return

    if args.command == "serve":
        config_path = Path(args.config)
        if not config_path.exists():
            write_example_config(config_path)
        config = AppConfig.load(config_path)
        from .webapp import create_app
        import uvicorn

        uvicorn.run(
            create_app(config_path),
            host=config.bind_host,
            port=config.bind_port,
        )
        return

    config = AppConfig.load(Path(args.config))
    allow_download_upload = None
    if args.yes_download_upload:
        allow_download_upload = True
    elif args.no_download_upload:
        allow_download_upload = False
    SyncRunner(config).run(
        allow_download_upload=allow_download_upload,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
