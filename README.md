# PalAdminPanel

PalAdminPanel 是面向 Windows 原生 PalServer 的本地 Web 管理后台。它运行在管理员自己的 Windows 电脑上，通过 PalDefender REST API 和 RCON 管理同一局域网内的服务器。

> 当前版本按 PalDefender 1.8.3 和 Palworld Dedicated Server 的接口完成。其他版本可能需要调整指令或权限名称。

## 功能

- 管理员登录、密码哈希、8 小时会话和登录限速
- CSRF 校验、输入白名单、危险操作二次确认
- 查看服务器状态、在线玩家和 PalDefender 版本
- Kick / Ban 玩家，发送全服公告，保存世界
- 异步发放物品、帕鲁和经验，无需刷新页面
- 可搜索、可分类的中英文物品与帕鲁目录
- 玩家选择器支持玩家名、UserId、PlayerUID 和公会筛选
- 从服务器读取 RCON 指令，并显示中文用途和参数说明
- 独立命令执行记录，支持复制或插入玩家 ID
- 帕鲁蛋 EggId + PalId 参数生成器
- 游戏内 `/AdminPassword`、`/adminlogin` 命令模板
- 轮换保存的本地操作审计日志
- 桌面和手机浏览器自适应界面

项目不附带第三方游戏图片。物品与帕鲁页面使用分类、文字和内部 ID 展示，避免将本机游戏资源或未经授权的图片上传到仓库。

## 运行结构

```text
管理员电脑                                  PalServer 电脑
127.0.0.1:5000                            <服务器局域网IP>:17993
浏览器 → PalAdminPanel ── REST + Bearer ──→ PalDefender
                     └── RCON 25575 ──────→ 保存世界与指令中心
```

- PalAdminPanel 只需要安装在管理员电脑上。
- PalServer 电脑不需要安装 Python，也不需要复制整个项目。
- 默认只监听 `127.0.0.1:5000`，局域网内其他设备无法打开管理后台。
- REST 与 RCON 只应开放给可信局域网设备，切勿映射到公网。

## 环境要求

- Windows 10 或 Windows 11
- Python 3.11，并确保 Windows Python Launcher `py` 可用
- Windows 原生 PalServer
- PalDefender 1.8.3，已启用 REST API
- 管理员电脑能访问服务器的 TCP 17993 和 TCP 25575

## 快速开始

1. 下载或克隆本仓库，进入 `PalAdminPanel` 文件夹。
2. 双击 `start_admin.bat`，或在命令提示符中运行：

   ```bat
   cmd.exe /c start_admin.bat
   ```

3. 首次启动按提示输入：

   - 服务器显示名称
   - PalServer 的局域网 IPv4 地址，例如 `192.168.1.100`
   - RCON / `AdminPassword`
   - PalDefender REST Bearer Token
   - 后台登录用户名和至少 10 位的密码

4. 浏览器打开 [http://127.0.0.1:5000](http://127.0.0.1:5000)。

启动脚本会创建独立的 `.runtime` Python 3.11 环境并安装依赖，不使用 IDE 的 `.venv`，也会隔离外部 `PYTHONHOME`、`PYTHONPATH` 等变量。

如需手动准备配置，可复制 `config.example.json` 为 `config.json`，但推荐运行 `setup_config.py`，让程序自动生成 Web 密码哈希和随机会话密钥。示例文件中的地址和 `CHANGE_ME` 值都必须替换。

## PalServer RCON 配置

编辑服务器的 `PalWorldSettings.ini`：

```ini
RCONEnabled=True
RCONPort=25575
AdminPassword="请设置强密码"
```

重启 PalServer 后生效。Windows 防火墙只允许管理员电脑的局域网 IP 访问 TCP 25575。RCON 流量本身不加密，只能在可信局域网中使用。

## PalDefender REST API 配置

在管理员电脑运行：

```bat
cmd.exe /c prepare_server_rest.bat
```

脚本会生成 `server_setup\AdminPanel.json`，并把同一个随机 Token 写入本机 `config.json`。把生成的文件复制到服务器：

```text
Pal\Binaries\Win64\PalDefender\RESTAPI\Tokens\AdminPanel.json
```

然后编辑服务器上的：

```text
Pal\Binaries\Win64\PalDefender\RESTAPI\RESTConfig.json
```

保留原 JSON 结构并确认：

```json
{
  "Enabled": true,
  "Address": "0.0.0.0",
  "Port": 17993
}
```

`Address` 使用 `0.0.0.0` 才能接受其他局域网设备的连接。服务器防火墙只向管理员电脑开放 TCP 17993，随后重启 PalServer。不要把 Token 写入截图、Issue、聊天记录或 Git 提交。

玩家列表、发放、经验、公告、Kick 和 Ban 使用 REST API；保存世界和动态指令中心使用 RCON。REST 返回的真实 `UserId` 或 `PlayerUID` 会直接用于后续操作，不会根据 SteamID 猜测标识。

## 更新物品与帕鲁目录

仓库已包含 `data/items.json` 和 `data/pals.json`。需要更新时运行：

```bat
cmd.exe /c refresh_catalogs.bat
```

内部 ID 目录来自 PalDefender 文档推荐的 Paldeck；物品导入只保留 `legal_in_game=true` 的记录。简体中文名来自 `zaigie/palworld-server-tool` 的 Palworld 本地化目录。来源和刷新时间记录在 `data/catalog_meta.json`。

## 常见问题

### 页面显示“无法连接 PalDefender REST API”

检查 `config.json` 中的 `rest_host` 和 `rest_port`、服务器防火墙、`RESTConfig.json` 的 `Enabled/Address/Port`，以及 PalDefender 启动日志中是否出现 REST API 已运行的信息。

### RCON connection timed out

检查 `PalWorldSettings.ini` 是否启用 RCON、TCP 25575 是否只对管理员电脑放行，以及 `rcon_host` 是否填写服务器的局域网 IPv4 地址。

### Failed to find player by UserId

玩家操作应优先使用 REST API 返回的真实 `UserId` 或 `PlayerUID`。不要手动把 SteamID 拼成 UserId。

### Python 报错 `No module named 'encodings'`

关闭后台，将项目里的 `.runtime` 文件夹改名或删除后重新运行 `start_admin.bat`。仍然失败时重新安装官方 Python 3.11，并勾选 Python Launcher。

## 安全与隐私

- `config.json` 保存真实 RCON 密码、REST Token、Web 密码哈希和会话密钥，已被 `.gitignore` 排除。
- `server_setup/AdminPanel.json` 保存 REST Token，已被 `.gitignore` 排除。
- `logs/` 可能包含玩家名、UserId、IP 和管理操作，仅保留空目录标记进入 Git。
- `.runtime`、`.venv`、IDE 配置、缓存和本机测试目录均不进入发布仓库。
- 管理后台默认只监听 `127.0.0.1`。除非你已经增加 HTTPS、额外认证和访问控制，否则不要改成 `0.0.0.0`。
- 任何凭据一旦误提交或发送给他人，应立即更换 RCON 密码、REST Token 和后台密码；仅删除文件不足以消除泄露。

更多发布前检查见 [SECURITY.md](SECURITY.md)。

## 项目结构

```text
PalAdminPanel/
├─ app.py                    Flask 后端与路由
├─ palworld.py               Palworld REST/RCON 业务层
├─ rest_client.py            PalDefender REST 客户端
├─ rcon_client.py            Source RCON 客户端
├─ setup_config.py           首次安全配置向导
├─ prepare_server_rest.py    REST Token 文件生成器
├─ data/                     物品、帕鲁与来源元数据
├─ static/                   前端样式与交互
├─ templates/                HTML 模板
├─ server_setup/README.txt   服务端配置说明
└─ logs/.gitkeep             运行日志目录占位
```

## 免责声明

本项目是非官方社区工具，与 Pocketpair 或 PalDefender 项目维护者无隶属关系。请先备份存档，并在你有权管理的服务器上使用。
