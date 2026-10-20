PalDefender 1.8.3 REST API 服务端配置
====================================

1. 停止或准备重启 PalServer。

2. 打开服务端文件：
   Pal\Binaries\Win64\PalDefender\RESTAPI\RESTConfig.json

3. 保留原 JSON 结构，只确认以下三个字段：
   "Enabled": true
   "Address": "0.0.0.0"
   "Port": 17993

   Address 若保持 127.0.0.1，客户端电脑将无法访问。

4. 在管理端运行 prepare_server_rest.bat，将本目录生成的 AdminPanel.json
   复制到服务端：
   Pal\Binaries\Win64\PalDefender\RESTAPI\Tokens\AdminPanel.json

5. 在 PalServer 所在电脑的 Windows 防火墙中允许 TCP 17993 入站。
   建议只允许运行 PalAdminPanel 的客户端电脑访问，不要做公网端口映射。

6. 重启 PalServer。日志中应出现：
   [RESTAPI] Loaded 1 Bearer token.
   [RESTAPI] Running PalDefender RESTAPI on port 17993

7. 回到管理端运行 start_admin.bat。

AdminPanel.json 和本机 config.json 都包含秘密 Token，不要上传或发给他人。
