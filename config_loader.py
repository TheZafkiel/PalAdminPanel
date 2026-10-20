from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"


@dataclass(frozen=True)
class Settings:
    server_name: str
    rcon_host: str
    rcon_port: int
    rcon_password: str
    rcon_timeout: float
    rest_host: str
    rest_port: int
    rest_token: str
    rest_timeout: float
    web_host: str
    web_port: int
    web_username: str
    web_password_hash: str
    secret_key: str
    max_players: int
    session_hours: int


def _required(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "":
        raise RuntimeError(f"config.json is missing required setting: {key}")
    return value


def load_settings(path: Path = CONFIG_PATH) -> Settings:
    if not path.exists():
        raise RuntimeError(
            "config.json does not exist. Run setup_config.py or start_admin.bat first."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read {path.name}: {exc}") from exc

    settings = Settings(
        server_name=str(data.get("server_name", "Palworld 内网服务器")),
        rcon_host=str(data.get("rcon_host", "192.168.1.100")),
        rcon_port=int(data.get("rcon_port", 25575)),
        rcon_password=str(_required(data, "rcon_password")),
        rcon_timeout=float(data.get("rcon_timeout", 3.0)),
        rest_host=str(data.get("rest_host", data.get("rcon_host", "192.168.1.100"))),
        rest_port=int(data.get("rest_port", 17993)),
        rest_token=str(_required(data, "rest_token")),
        rest_timeout=float(data.get("rest_timeout", 8.0)),
        web_host=str(data.get("web_host", "127.0.0.1")),
        web_port=int(data.get("web_port", 5000)),
        web_username=str(_required(data, "web_username")),
        web_password_hash=str(_required(data, "web_password_hash")),
        secret_key=str(_required(data, "secret_key")),
        max_players=int(data.get("max_players", 32)),
        session_hours=int(data.get("session_hours", 8)),
    )
    if not all(1 <= port <= 65535 for port in (settings.rcon_port, settings.rest_port, settings.web_port)):
        raise RuntimeError("RCON, REST and web ports must be between 1 and 65535")
    if settings.rcon_password == "CHANGE_ME":
        raise RuntimeError("Please replace the placeholder RCON password in config.json")
    if settings.rest_token == "CHANGE_ME_REST_TOKEN":
        raise RuntimeError("Please replace the placeholder REST token in config.json")
    if settings.web_password_hash == "GENERATED_BY_SETUP_CONFIG":
        raise RuntimeError("Run setup_config.py to generate a secure web password hash")
    if settings.secret_key == "GENERATED_BY_SETUP_CONFIG":
        raise RuntimeError("Run setup_config.py to generate a secure session key")
    return settings
