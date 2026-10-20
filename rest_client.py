"""PalDefender 1.8.3 REST API client."""

from __future__ import annotations

import json
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class PalDefenderRestError(RuntimeError):
    """Safe, user-facing REST error that never includes the bearer token."""


class PalDefenderRestClient:
    def __init__(self, host: str, port: int, token: str, timeout: float = 8.0):
        self.base_url = f"http://{host}:{port}"
        self.token = token
        self.timeout = timeout

    @staticmethod
    def _error_message(payload: Any, fallback: str) -> str:
        if isinstance(payload, dict):
            error = payload.get("Error")
            if isinstance(error, dict):
                code = str(error.get("Code", "REST_ERROR"))
                message = str(error.get("Message", fallback))
                return f"{code}: {message}"
        return fallback

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        request = Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            raw = exc.read()
            try:
                parsed = json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                parsed = None
            message = self._error_message(parsed, f"REST API returned HTTP {exc.code}")
            if exc.code == 401:
                message = "REST Token 无效或未被服务器加载。"
            elif exc.code == 403:
                message = f"REST Token 权限不足：{message}"
            raise PalDefenderRestError(message) from exc
        except (URLError, TimeoutError, socket.timeout) as exc:
            raise PalDefenderRestError(
                f"无法连接 PalDefender REST API：{self.base_url}"
            ) from exc

        if not raw:
            return {}
        try:
            parsed = json.loads(raw.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PalDefenderRestError("PalDefender REST API 返回了无效 JSON。") from exc
        if not isinstance(parsed, dict):
            raise PalDefenderRestError("PalDefender REST API 返回格式不正确。")
        return parsed

    @staticmethod
    def player_path(identifier: str) -> str:
        return quote(identifier, safe="")

    def version(self) -> dict[str, Any]:
        return self.request("GET", "/v1/pdapi/version")

    def players(self) -> dict[str, Any]:
        return self.request("GET", "/v1/pdapi/players")

    def give_items(self, identifier: str, item_id: str, count: int) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/v1/pdapi/give/items/{self.player_path(identifier)}",
            {"Items": [{"ItemID": item_id, "Count": count}]},
        )

    def give_pals(self, identifier: str, pal_id: str, level: int) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/v1/pdapi/give/pals/{self.player_path(identifier)}",
            {"Pals": [{"PalID": pal_id, "Level": level}]},
        )

    def give_experience(self, identifier: str, amount: int) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/v1/pdapi/give/progression/{self.player_path(identifier)}",
            {"EXP": amount},
        )

    def broadcast(self, message: str) -> dict[str, Any]:
        return self.request("POST", "/v1/pdapi/Broadcast", {"Message": message})

    def kick(self, identifier: str) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/v1/pdapi/kick/{self.player_path(identifier)}",
            {"Reason": "Kicked by PalAdminPanel"},
        )

    def ban(self, identifier: str) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/v1/pdapi/ban/{self.player_path(identifier)}",
            {"Reason": "Banned by PalAdminPanel", "IP": False},
        )
