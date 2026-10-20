# 安全与隐私说明

PalAdminPanel 能执行服务器管理命令，请把它当作管理员工具而不是普通网页应用。

## 永远不要提交的文件

- `config.json`：包含 RCON 密码、REST Token、Web 密码哈希和会话密钥
- `server_setup/*.json`：包含 PalDefender REST Token
- `logs/`：可能包含玩家名、UserId、PlayerUID、IP 和管理操作
- `.env*`、私钥、证书、本机运行环境、IDE 配置和缓存

这些路径已由 `.gitignore` 排除。提交前仍应运行 `git status --short` 和 `git diff --cached`，逐项确认暂存内容。

## 推荐部署边界

- Web 后台保持监听 `127.0.0.1`。
- RCON 与 PalDefender REST 只允许可信局域网设备访问。
- Windows 防火墙按来源 IP 放行 TCP 25575 和 TCP 17993。
- 不要在路由器上把这些端口映射到公网。
- 为 RCON、REST Token 和 Web 登录使用不同的高强度凭据。
- 定期备份 Palworld 存档，并在升级 PalServer 或 PalDefender 后先验证接口兼容性。

## 凭据意外泄露

1. 立即更换 Palworld `AdminPassword`。
2. 删除并重新生成 PalDefender REST Token 文件。
3. 重新运行 `setup_config.py` 更换后台密码和会话密钥。
4. 检查 Git 历史、日志、截图和聊天记录；只删除当前文件不能撤销已经发生的泄露。
5. 检查服务器日志中是否有异常连接或管理操作。

## 报告安全问题

请在私有仓库中创建 Issue，并只描述复现步骤和影响。不要粘贴真实密码、Token、玩家个人信息或完整运行日志。
