from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ensure", action="store_true")
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        return 0
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    existing = str(data.get("rest_token", "")).strip()
    if args.ensure and existing and existing != "CHANGE_ME_REST_TOKEN":
        return 0

    print("\nPalDefender REST API 配置")
    print("请先在服务器启用 REST API，并创建 AdminPanel Token。\n")
    default_host = str(data.get("rcon_host", "192.168.1.100"))
    host = input(f"REST API 地址 [{default_host}]: ").strip() or default_host
    raw_port = input("REST API 端口 [17993]: ").strip() or "17993"
    try:
        port = int(raw_port)
    except ValueError:
        print("端口必须是整数。")
        return 1
    if not 1 <= port <= 65535:
        print("端口必须在 1 到 65535 之间。")
        return 1
    token = getpass.getpass("REST Bearer Token: ").strip()
    if len(token) < 16:
        print("Token 为空或过短，没有更新配置。")
        return 1

    data.update(
        {
            "rest_host": host,
            "rest_port": port,
            "rest_token": token,
            "rest_timeout": 8.0,
        }
    )
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REST 配置已保存，Token 未显示在屏幕上。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
