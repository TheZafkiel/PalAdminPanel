from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from typing import Callable, Any

from rcon_client import SourceRconClient
from rest_client import PalDefenderRestClient


SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,96}$")
SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_-]{3,96}$")


@dataclass(frozen=True)
class Player:
    name: str
    player_uid: str
    platform_id: str
    status: str = ""
    guild_name: str = ""
    online: bool = False

    @property
    def paldefender_id(self) -> str:
        value = self.platform_id.strip()
        if value.isdigit() and len(value) >= 15:
            return f"steam_{value}"
        return value or self.player_uid

    @property
    def admin_id(self) -> str:
        value = self.platform_id.strip()
        if value.lower().startswith("steam_"):
            return value[6:]
        return value or self.player_uid


def parse_showplayers(response: str) -> list[Player]:
    """Parse Palworld's CSV-like ShowPlayers response."""
    clean = response.lstrip("\ufeff").strip()
    if not clean:
        return []
    rows = list(csv.reader(io.StringIO(clean)))
    if not rows:
        return []

    header = [cell.strip().lower().replace(" ", "") for cell in rows[0]]
    has_header = "name" in header and any("uid" in item or "steam" in item for item in header)
    data_rows = rows[1:] if has_header else rows
    players: list[Player] = []
    for row in data_rows:
        if len(row) < 2 or not any(cell.strip() for cell in row):
            continue
        padded = [cell.strip() for cell in row] + [""] * (3 - len(row))
        players.append(Player(name=padded[0], player_uid=padded[1], platform_id=padded[2]))
    return players


def validate_identifier(value: str, label: str = "ID") -> str:
    value = value.strip()
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"{label} 只能包含字母、数字、下划线和短横线")
    return value


def validate_user_id(value: str) -> str:
    value = value.strip()
    if not SAFE_USER_ID.fullmatch(value):
        raise ValueError("玩家 ID 格式无效")
    return value


def validate_positive_int(value: str | int, label: str, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}必须是整数") from exc
    if not 1 <= number <= maximum:
        raise ValueError(f"{label}必须在 1 到 {maximum} 之间")
    return number


class PalworldService:
    def __init__(
        self,
        rest_client: PalDefenderRestClient,
        rcon_client_factory: Callable[[], SourceRconClient],
    ):
        self._rest = rest_client
        self._rcon_client_factory = rcon_client_factory

    def command(self, command: str) -> str:
        return self._rcon_client_factory().run(command)

    def optional_response_command(self, command: str) -> str:
        return self._rcon_client_factory().run(command, allow_no_response=True)

    def rcon_commands(self) -> list[dict[str, Any]]:
        """Return the command list advertised by the running PalDefender server."""
        raw = self.command("getrconcmds")
        commands: list[dict[str, Any]] = []
        for entry in raw.split(";"):
            name, separator, argument_count = entry.strip().partition(":")
            if not separator or not SAFE_ID.fullmatch(name):
                continue
            try:
                count = int(argument_count)
            except ValueError:
                continue
            if count < 0:
                continue
            commands.append({"name": name, "argument_count": count})
        if not commands:
            raise ValueError("服务器没有返回可用的 PalDefender RCON 指令。")
        return commands

    def execute_rcon(self, command_name: str, arguments: str = "") -> str:
        command_name = validate_identifier(command_name, "指令名称")
        available = {item["name"] for item in self.rcon_commands()}
        if command_name not in available:
            raise ValueError("该指令不在服务器当前公布的指令清单中。")
        arguments = arguments.strip()
        if len(arguments) > 500 or any(char in arguments for char in "\r\n\0"):
            raise ValueError("指令参数不能超过 500 个字符，也不能包含换行或空字符。")
        command_line = command_name if not arguments else f"{command_name} {arguments}"
        return self.command(command_line)

    def info(self) -> str:
        return self.command("Info")

    def players(self) -> list[Player]:
        payload = self._rest.players()
        raw_players = payload.get("Players", [])
        if not isinstance(raw_players, list):
            return []
        players: list[Player] = []
        for item in raw_players:
            if not isinstance(item, dict):
                continue
            status = str(item.get("Status", ""))
            online = status.casefold() == "online" or bool(item.get("IP"))
            players.append(
                Player(
                    name=str(item.get("Name", "未知玩家")),
                    player_uid=str(item.get("PlayerUID", "")),
                    platform_id=str(item.get("UserId", "")),
                    status=status,
                    guild_name=str(item.get("GuildName", "")),
                    online=online,
                )
            )
        return players

    def defender_version(self) -> dict[str, str]:
        payload = self._rest.version()
        version = payload.get("Version", {})
        if not isinstance(version, dict):
            version = {}
        return {
            "game": "REST API",
            "paldefender": str(
                version.get("VersionLong") or version.get("Version") or "未知"
            ),
        }

    @staticmethod
    def _result(label: str, payload: dict[str, Any]) -> str:
        granted = payload.get("Granted")
        if isinstance(granted, dict) and granted:
            summary = "、".join(f"{key}={value}" for key, value in granted.items())
            return f"{label}成功：{summary}"
        return f"{label}成功。"

    def give_item(self, user_id: str, item_id: str, amount: int) -> str:
        user_id = validate_user_id(user_id)
        item_id = validate_identifier(item_id, "物品 ID")
        amount = validate_positive_int(amount, "数量", 999999)
        return self._result("发放物品", self._rest.give_items(user_id, item_id, amount))

    def give_pal(self, user_id: str, pal_id: str, level: int) -> str:
        user_id = validate_user_id(user_id)
        pal_id = validate_identifier(pal_id, "帕鲁 ID")
        level = validate_positive_int(level, "等级", 255)
        return self._result("发放帕鲁", self._rest.give_pals(user_id, pal_id, level))

    def give_experience(self, user_id: str, amount: int) -> str:
        user_id = validate_user_id(user_id)
        amount = validate_positive_int(amount, "经验值", 2_000_000_000)
        return self._result("发放经验", self._rest.give_experience(user_id, amount))

    def broadcast(self, message: str) -> str:
        message = " ".join(message.strip().splitlines())
        if not message or len(message) > 200:
            raise ValueError("公告内容长度必须在 1 到 200 个字符之间")
        self._rest.broadcast(message)
        return "公告发送成功。"

    def save(self) -> str:
        self.optional_response_command("Save")
        return "保存命令已发送。"

    def kick(self, player_id: str) -> str:
        self._rest.kick(validate_user_id(player_id))
        return "玩家已踢出。"

    def ban(self, player_id: str) -> str:
        self._rest.ban(validate_user_id(player_id))
        return "玩家已封禁。"
