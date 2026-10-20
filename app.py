from __future__ import annotations

import hmac
import json
import logging
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from command_help import get_command_help, ingame_commands
from config_loader import BASE_DIR, Settings, load_settings
from palworld import PalworldService
from rcon_client import RconError, SourceRconClient
from rest_client import PalDefenderRestClient, PalDefenderRestError


EGG_NAMES = {
    "Dark": "暗属性", "Dragon": "龙属性", "Earth": "地属性",
    "Electricity": "雷属性", "Fire": "火属性", "Ice": "冰属性",
    "Leaf": "草属性", "Normal": "无属性", "Water": "水属性",
}
EGG_IDS = [
    {"id": f"PalEgg_{element}_{size:02d}", "name": f"{name}蛋 · 尺寸 {size}"}
    for element, name in EGG_NAMES.items()
    for size in range(1, 6)
]


READ_ONLY_RCON_COMMANDS = {
    "getrconcmds",
    "version",
    "getpos",
    "getnearestbase",
    "getip",
    "whitelist_get",
    "getskinids",
    "gettechids",
}


def _load_catalog(filename: str) -> list[dict[str, str]]:
    path = BASE_DIR / "data" / filename
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict) and "id" in item]
    except (OSError, json.JSONDecodeError):
        pass
    return []


def _build_audit_logger() -> logging.Logger:
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("paladmin.audit")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_dir / "admin.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def _build_command_logger() -> logging.Logger:
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("paladmin.commands")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_dir / "commands.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def _read_command_history(limit: int = 80) -> list[dict[str, Any]]:
    path = BASE_DIR / "logs" / "commands.log"
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    except OSError:
        return []
    history: list[dict[str, Any]] = []
    for line in reversed(lines):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            history.append(record)
    return history


def create_app(
    settings: Settings | None = None,
    service: PalworldService | None = None,
    testing: bool = False,
) -> Flask:
    settings = settings or load_settings()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=settings.session_hours),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=32 * 1024,
        TESTING=testing,
    )

    if service is None:
        service = PalworldService(
            PalDefenderRestClient(
                settings.rest_host,
                settings.rest_port,
                settings.rest_token,
                settings.rest_timeout,
            ),
            lambda: SourceRconClient(
                settings.rcon_host,
                settings.rcon_port,
                settings.rcon_password,
                settings.rcon_timeout,
            )
        )

    audit = _build_audit_logger()
    if testing:
        command_log = logging.getLogger("paladmin.commands.testing")
        if not command_log.handlers:
            command_log.addHandler(logging.NullHandler())
    else:
        command_log = _build_command_logger()
    attempts: dict[str, deque[float]] = defaultdict(deque)
    items = _load_catalog("items.json")
    pals = _load_catalog("pals.json")

    def csrf_token() -> str:
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return str(token)

    app.jinja_env.globals["csrf_token"] = csrf_token

    def logged_in() -> bool:
        return bool(session.get("authenticated"))

    def wants_json() -> bool:
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if not logged_in():
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped

    def write_audit(action: str, target: str = "", result: str = "ok") -> None:
        record = {
            "user": session.get("username", "anonymous"),
            "ip": request.remote_addr or "unknown",
            "action": action,
            "target": target[:120],
            "result": result.replace("\r", " ").replace("\n", " ")[:240],
        }
        audit.info(json.dumps(record, ensure_ascii=False, separators=(",", ":")))

    def run_action(action: str, target: str, callback: Callable[[], str]) -> tuple[bool, str]:
        try:
            result = callback()
        except (ValueError, RconError, PalDefenderRestError) as exc:
            message = str(exc)
            write_audit(action, target, f"error: {message}")
            if not wants_json():
                flash(message, "error")
            return False, message
        message = result or "命令已发送。"
        write_audit(action, target, message)
        if not wants_json():
            flash(message, "success")
        return True, message

    @app.before_request
    def validate_csrf() -> None:
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            expected = str(session.get("csrf_token", ""))
            received = str(request.form.get("csrf_token", ""))
            if not expected or not hmac.compare_digest(expected, received):
                abort(400, description="请求校验失败，请刷新页面后重试。")

    @app.after_request
    def secure_headers(response: Any) -> Any:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; form-action 'self'; frame-ancestors 'none'"
        )
        if logged_in():
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.context_processor
    def template_context() -> dict[str, Any]:
        return {
            "server_name": settings.server_name,
            "rcon_endpoint": f"{settings.rcon_host}:{settings.rcon_port}",
            "rest_endpoint": f"{settings.rest_host}:{settings.rest_port}",
            "is_logged_in": logged_in(),
            "current_endpoint": request.endpoint or "",
        }

    @app.route("/login", methods=["GET", "POST"])
    def login() -> Any:
        if logged_in():
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            ip = request.remote_addr or "unknown"
            now = time.monotonic()
            window = attempts[ip]
            while window and now - window[0] > 300:
                window.popleft()
            if len(window) >= 5:
                flash("登录尝试过多，请 5 分钟后再试。", "error")
                return render_template("login.html"), 429

            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            username_ok = hmac.compare_digest(username, settings.web_username)
            password_ok = check_password_hash(settings.web_password_hash, password)
            if username_ok and password_ok:
                attempts.pop(ip, None)
                session.clear()
                session["authenticated"] = True
                session["username"] = settings.web_username
                session["csrf_token"] = secrets.token_urlsafe(32)
                session.permanent = True
                write_audit("login")
                next_url = request.args.get("next", "")
                if not next_url.startswith("/") or next_url.startswith("//"):
                    next_url = url_for("dashboard")
                return redirect(next_url)
            window.append(now)
            write_audit("login", result="failed")
            flash("用户名或密码错误。", "error")
        return render_template("login.html")

    @app.post("/logout")
    @login_required
    def logout() -> Any:
        write_audit("logout")
        session.clear()
        flash("已安全退出。", "success")
        return redirect(url_for("login"))

    @app.get("/")
    @login_required
    def dashboard() -> Any:
        status: dict[str, Any] = {
            "online": False,
            "players": [],
            "info": "未连接",
            "version": {},
            "error": "",
            "players_error": "",
        }
        try:
            status["version"] = service.defender_version()
            status["online"] = True
            status["info"] = (
                f"Palworld {status['version'].get('game', '未知')} · "
                f"PalDefender {status['version'].get('paldefender', '未知')}"
            )
        except (RconError, PalDefenderRestError) as exc:
            status["error"] = str(exc)
        if status["online"]:
            try:
                status["players"] = [player for player in service.players() if player.online]
            except (RconError, PalDefenderRestError) as exc:
                status["players_error"] = str(exc)
        return render_template("dashboard.html", status=status, max_players=settings.max_players)

    @app.get("/players")
    @login_required
    def players_page() -> Any:
        try:
            player_list = service.players()
            error = ""
        except (RconError, PalDefenderRestError) as exc:
            player_list, error = [], str(exc)
        return render_template("players.html", players=player_list, error=error)

    @app.post("/players/action")
    @login_required
    def player_action() -> Any:
        action = request.form.get("action", "")
        player_id = request.form.get("player_id", "").strip()
        if action == "kick":
            run_action("kick", player_id, lambda: service.kick(player_id))
        elif action == "ban":
            if request.form.get("confirmation", "") != "BAN":
                flash("封禁确认失败，没有执行命令。", "error")
            else:
                run_action("ban", player_id, lambda: service.ban(player_id))
        else:
            abort(400, description="未知玩家操作。")
        return redirect(url_for("players_page"))

    @app.get("/grant")
    @login_required
    def grant_page() -> Any:
        try:
            player_list = service.players()
            error = ""
        except (RconError, PalDefenderRestError) as exc:
            player_list, error = [], str(exc)
        return render_template(
            "grant.html", players=player_list, error=error, items=items, pals=pals
        )

    @app.post("/grant/item")
    @login_required
    def grant_item() -> Any:
        user_id = request.form.get("custom_user_id", "").strip() or request.form.get("user_id", "")
        item_id = request.form.get("custom_item_id", "").strip() or request.form.get("item_id", "")
        amount = request.form.get("amount", "")
        success, message = run_action("give_item", f"{user_id}:{item_id}x{amount}", lambda: service.give_item(user_id, item_id, amount))
        if wants_json():
            return jsonify(success=success, message=message), 200 if success else 400
        return redirect(url_for("grant_page"))

    @app.post("/grant/pal")
    @login_required
    def grant_pal() -> Any:
        user_id = request.form.get("custom_user_id", "").strip() or request.form.get("user_id", "")
        pal_id = request.form.get("custom_pal_id", "").strip() or request.form.get("pal_id", "")
        level = request.form.get("level", "")
        success, message = run_action("give_pal", f"{user_id}:{pal_id}@{level}", lambda: service.give_pal(user_id, pal_id, level))
        if wants_json():
            return jsonify(success=success, message=message), 200 if success else 400
        return redirect(url_for("grant_page"))

    @app.post("/grant/experience")
    @login_required
    def grant_experience() -> Any:
        user_id = request.form.get("custom_user_id", "").strip() or request.form.get("user_id", "")
        amount = request.form.get("amount", "")
        success, message = run_action("give_experience", f"{user_id}:{amount}", lambda: service.give_experience(user_id, amount))
        if wants_json():
            return jsonify(success=success, message=message), 200 if success else 400
        return redirect(url_for("grant_page"))

    @app.get("/server")
    @login_required
    def server_page() -> Any:
        return render_template("server.html")

    @app.post("/server/broadcast")
    @login_required
    def server_broadcast() -> Any:
        message = request.form.get("message", "")
        run_action("broadcast", message, lambda: service.broadcast(message))
        return redirect(url_for("server_page"))

    @app.post("/server/save")
    @login_required
    def server_save() -> Any:
        run_action("save", "world", service.save)
        return redirect(url_for("server_page"))

    @app.get("/commands")
    @login_required
    def commands_page() -> Any:
        try:
            command_list = service.rcon_commands()
            error = ""
        except (ValueError, RconError) as exc:
            command_list, error = [], str(exc)
        for item in command_list:
            item["read_only"] = item["name"] in READ_ONLY_RCON_COMMANDS
            item["help"] = get_command_help(item["name"])
        try:
            player_list = service.players()
            players_error = ""
        except (RconError, PalDefenderRestError) as exc:
            player_list, players_error = [], str(exc)
        return render_template(
            "commands.html",
            commands=command_list,
            error=error,
            players=player_list,
            players_error=players_error,
            pals=pals,
            egg_ids=EGG_IDS,
            command_history=[] if testing else _read_command_history(),
        )

    @app.get("/ingame-commands")
    @login_required
    def ingame_commands_page() -> Any:
        try:
            player_list = service.players()
            players_error = ""
        except (RconError, PalDefenderRestError) as exc:
            player_list, players_error = [], str(exc)
        return render_template(
            "ingame_commands.html",
            commands=ingame_commands(),
            players=player_list,
            players_error=players_error,
            items=items,
            pals=pals,
            egg_ids=EGG_IDS,
        )

    @app.post("/commands/execute")
    @login_required
    def command_execute() -> Any:
        command_name = request.form.get("command_name", "").strip()
        arguments = request.form.get("arguments", "")
        if (
            command_name not in READ_ONLY_RCON_COMMANDS
            and request.form.get("confirmation", "") != "EXECUTE"
        ):
            message = "此指令可能修改服务器数据，确认失败，未执行。"
            if wants_json():
                return jsonify(success=False, message=message), 400
            flash(message, "error")
            return redirect(url_for("commands_page"))

        def execute() -> str:
            response = service.execute_rcon(command_name, arguments)
            if len(response) > 1600:
                return response[:1600] + "…（响应过长，已截断）"
            return response or "指令已发送。"

        command_line = f"{command_name} {arguments}".strip()
        success, message = run_action("rcon_command", command_line, execute)
        record = {
            "timestamp": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command_line[:600],
            "success": success,
            "result": message[:4000],
        }
        command_log.info(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        if wants_json():
            return jsonify(**record, message=message), 200 if success else 400
        return redirect(url_for("commands_page"))

    @app.get("/logs")
    @login_required
    def logs_page() -> Any:
        path = BASE_DIR / "logs" / "admin.log"
        lines: list[str] = []
        if path.exists():
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-250:]
                lines.reverse()
            except OSError as exc:
                flash(f"无法读取日志：{exc}", "error")
        return render_template("logs.html", lines=lines)

    @app.errorhandler(400)
    def bad_request(error: Any) -> tuple[str, int]:
        return render_template("error.html", code=400, message=getattr(error, "description", "请求无效。")), 400

    @app.errorhandler(404)
    def not_found(_error: Any) -> tuple[str, int]:
        return render_template("error.html", code=404, message="页面不存在。"), 404

    return app


if __name__ == "__main__":
    from waitress import serve

    current_settings = load_settings()
    application = create_app(current_settings)
    print(f"PalAdminPanel 已启动：http://127.0.0.1:{current_settings.web_port}")
    print(f"远程 PalServer RCON：{current_settings.rcon_host}:{current_settings.rcon_port}")
    print(f"PalDefender REST API：{current_settings.rest_host}:{current_settings.rest_port}")
    serve(
        application,
        host=current_settings.web_host,
        port=current_settings.web_port,
        threads=6,
        channel_timeout=30,
    )
