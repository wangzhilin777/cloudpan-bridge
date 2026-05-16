from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock


@dataclass(slots=True)
class LogRecord:
    ts: str
    level: str
    message: str


class AppLogger:
    def __init__(self, log_file: Path, keep: int = 500) -> None:
        self.log_file = log_file
        self.keep = keep
        self.records: list[LogRecord] = []
        self.lock = Lock()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, level: str, message: str) -> None:
        record = LogRecord(
            ts=datetime.now().isoformat(timespec="seconds"),
            level=level.upper(),
            message=message,
        )
        line = f"[{record.ts}] [{record.level}] {record.message}"
        with self.lock:
            self.records.append(record)
            if len(self.records) > self.keep:
                self.records = self.records[-self.keep :]
            with self.log_file.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        print(line)

    def info(self, message: str) -> None:
        self._append("info", message)

    def warning(self, message: str) -> None:
        self._append("warning", message)

    def error(self, message: str) -> None:
        self._append("error", message)

    def tail(self, limit: int = 200) -> list[dict[str, str]]:
        with self.lock:
            return [
                {"ts": record.ts, "level": record.level, "message": record.message}
                for record in self.records[-limit:]
            ]

    def clear(self) -> None:
        with self.lock:
            self.records = []
            self.log_file.write_text("", encoding="utf-8")
