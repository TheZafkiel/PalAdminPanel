from __future__ import annotations

import getpass
import json
import secrets
from pathlib import Path

from werkzeug.security import generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"


def prompt_nonempty(label: str, default: str | None = None, secret: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    prompt = f"{label}{suffix}: "
    while True:
        value = getpass.getpass(prompt) if secret else input(prompt)
        value = value.strip()
        if value:
            return value
        if default is not None:
            return default
        print("此项不能为空。")


def main() -> None:
    print("\nPalAdminPanel 首次配置\n")
    if CONFIG_PATH.exists():
        answer = input("config.json 已存在，是否覆盖？输入 YES 继续: ").strip()
        if answer != "YES":
            print("已取消。")
            return

    server_name = prompt_nonempty("服务器名称", "Palworld 局域网服务器")
    rcon_host = prompt_nonempty("PalServer 局域网地址", "192.168.1.100")
    rcon_password = prompt_nonempty("RCON / AdminPassword", secret=True)
    rest_token = prompt_nonempty("PalDefender REST Bearer Token", secret=True)
    web_username = prompt_nonempty("后台登录用户名", "admin")
    while True:
        password = prompt_nonempty("后台登录密码（至少 10 位）", secret=True)
        confirm = prompt_nonempty("再次输入后台登录密码", secret=True)
        if password != confirm:
            print("两次密码不一致，请重试。")
        elif len(password) < 10:
            print("密码至少需要 10 位。")
        else:
            break

    config = {
        "server_name": server_name,
        "rcon_host": rcon_host,
        "rcon_port": 25575,
        "rcon_password": rcon_password,
        "rcon_timeout": 3.0,
        "rest_host": rcon_host,
        "rest_port": 17993,
        "rest_token": rest_token,
        "rest_timeout": 8.0,
        "web_host": "127.0.0.1",
        "web_port": 5000,
        "web_username": web_username,
        "web_password_hash": generate_password_hash(password),
        "secret_key": secrets.token_urlsafe(48),
        "max_players": 32,
        "session_hours": 8,
    }
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n配置完成。本机访问地址：http://127.0.0.1:5000")


if __name__ == "__main__":
    main()
