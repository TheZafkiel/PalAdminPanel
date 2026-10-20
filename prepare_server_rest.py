from __future__ import annotations

import json
import secrets
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
OUTPUT_DIR = BASE_DIR / "server_setup"
TOKEN_PATH = OUTPUT_DIR / "AdminPanel.json"

PERMISSIONS = [
    "REST.Version.Read",
    "REST.Players.Read",
    "REST.Items.Give",
    "REST.Pals.Give",
    "REST.Progression.Give",
    "REST.Messages.Broadcast",
    "REST.Punishments.Kick",
    "REST.Punishments.Ban",
]


def main() -> int:
    if not CONFIG_PATH.exists():
        print("请先运行 start_admin.bat 完成基础配置。")
        return 1
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    token = str(config.get("rest_token", "")).strip()
    if not token or token == "CHANGE_ME_REST_TOKEN":
        token = secrets.token_urlsafe(48)

    host = str(config.get("rcon_host", "192.168.1.100"))
    config.update(
        {
            "rest_host": host,
            "rest_port": 17993,
            "rest_token": token,
            "rest_timeout": 8.0,
        }
    )
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    OUTPUT_DIR.mkdir(exist_ok=True)
    token_file = {"Name": "PalAdminPanel", "Token": token, "Permissions": PERMISSIONS}
    TOKEN_PATH.write_text(json.dumps(token_file, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REST Token 已安全生成并写入本机配置。")
    print(f"请将此文件复制到 PalServer：{TOKEN_PATH}")
    print("Token 没有显示在终端中。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
