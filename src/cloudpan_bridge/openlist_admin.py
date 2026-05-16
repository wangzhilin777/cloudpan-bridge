from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class OpenListDriverField:
    name: str
    type: str = "string"
    default: str = ""
    options: str = ""
    required: bool = False
    help: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "OpenListDriverField":
        return cls(
            name=str(payload.get("name") or ""),
            type=str(payload.get("type") or "string"),
            default=str(payload.get("default") or ""),
            options=str(payload.get("options") or ""),
            required=_to_bool(payload.get("required")),
            help=str(payload.get("help") or ""),
        )


@dataclass(slots=True)
class OpenListDriverInfo:
    name: str
    common: list[OpenListDriverField]
    additional: list[OpenListDriverField]
    config: dict[str, Any]


class OpenListAdminClient:
    def __init__(self, base_url: str, token: str = "", timeout: float = 45.0) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.token = str(token or "").strip()
        self.client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "OpenListAdminClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def _headers(self) -> dict[str, str]:
        headers = {"content-type": "application/json"}
        if self.token:
            headers["authorization"] = self.token
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self.client.request(
            method,
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=json_body,
            params=params,
        )
        response.raise_for_status()
        payload = response.json()
        code = int(payload.get("code", 500))
        if code != 200:
            raise RuntimeError(str(payload.get("message") or payload.get("msg") or payload))
        return payload

    def driver_names(self) -> list[str]:
        payload = self._request("GET", "/api/admin/driver/names")
        data = payload.get("data") or []
        return [str(item) for item in data if str(item).strip()]

    def driver_info(self, driver: str) -> OpenListDriverInfo:
        payload = self._request("GET", "/api/admin/driver/info", params={"driver": driver})
        data = payload.get("data") or {}
        common = [OpenListDriverField.from_dict(item) for item in data.get("common", []) if isinstance(item, dict)]
        additional = [OpenListDriverField.from_dict(item) for item in data.get("additional", []) if isinstance(item, dict)]
        config = dict(data.get("config") or {})
        return OpenListDriverInfo(
            name=str(config.get("name") or driver),
            common=common,
            additional=additional,
            config=config,
        )

    def storage_list(self, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        return self._request("GET", "/api/admin/storage/list", params={"page": int(page), "per_page": int(per_page)})

    def create_storage(self, driver: str, values: dict[str, Any]) -> dict[str, Any]:
        payload = self._request(
            "POST",
            "/api/admin/storage/create",
            json_body={
                "driver": driver,
                **values,
            },
        )
        return payload


def build_storage_payload(
    driver_info: OpenListDriverInfo,
    values: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    common_names = {field.name for field in driver_info.common}
    addition: dict[str, Any] = {}

    for field in driver_info.common:
        raw = values.get(field.name, field.default)
        if raw in ("", None) and field.required:
            raise RuntimeError(f"缺少必填字段: {field.name}")
        if raw not in ("", None):
            payload[field.name] = _normalize_field_value(field, raw)

    for field in driver_info.additional:
        raw = values.get(field.name, field.default)
        if raw in ("", None) and field.required:
            raise RuntimeError(f"缺少必填字段: {field.name}")
        if raw not in ("", None):
            addition[field.name] = _normalize_field_value(field, raw)

    for key, value in values.items():
        if key in common_names or any(field.name == key for field in driver_info.additional):
            continue
        if value not in ("", None):
            addition[key] = value

    payload["addition"] = json.dumps(addition, ensure_ascii=False)
    return payload


def _normalize_field_value(field: OpenListDriverField, value: Any) -> Any:
    field_type = field.type.lower()
    if field_type == "bool":
        return _to_bool(value)
    if field_type == "number":
        try:
            return int(value)
        except (TypeError, ValueError):
            return float(value)
    return value
