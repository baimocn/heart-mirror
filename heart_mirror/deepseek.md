## 📋 给 Trae CN 的终极修复指令（复制即用）

> **目标**：让「心镜」项目在阿里云 Linux 服务器（公网 IP：`8.136.152.54`，操作系统：Ubuntu 24.04）上通过 **80 端口（Nginx + Gunicorn）** 完全运行，所有功能（测试、捐款、道德困惑墙、管理员后台等）与本地测试时完全一致。

### 第一步：诊断当前服务器状态（CN 需要先获取信息）

请 CN 在回答中**提供以下命令的输出**（由用户在服务器上执行后粘贴给你），或者**提供一套完整的服务器端诊断脚本**让用户运行：

```bash
# 1. 检查服务状态
systemctl status heart_mirror --no-pager
systemctl status nginx --no-pager

# 2. 检查 Nginx 配置
cat /etc/nginx/sites-available/heart_mirror

# 3. 检查 Gunicorn 服务文件
cat /etc/systemd/system/heart_mirror.service

# 4. 检查项目文件权限
ls -la /var/www/heart_mirror/
ls -la /var/www/heart_mirror/static/
ls -la /var/www/heart_mirror/database/

# 5. 查看最新的错误日志
journalctl -u heart_mirror -n 50 --no-pager
tail -30 /var/log/nginx/error.log

# 6. 测试静态文件是否可访问
curl -I http://localhost/static/style.css

# 7. 测试 API 是否可访问（以 /api/stats 为例）
curl -I http://localhost/api/stats
```

> 如果 CN 无法直接获得这些输出，请 CN 给出**用户需要在服务器上执行的完整命令列表**，用户执行后把结果贴给 CN。

### 第二步：根据诊断结果，CN 需要逐一修复以下常见问题

**问题 A：静态文件 404（页面只有文字，无样式）**
- **修复方法**：确保 Nginx 配置中包含以下 location 块：
  ```nginx
  location /static {
      alias /var/www/heart_mirror/static;
      expires 30d;
  }
  ```
- 然后执行 `nginx -t && systemctl restart nginx`
- **CN 必须提供完整的 `heart_mirror` Nginx 配置文件内容**。

**问题 B：前端 JavaScript 中的 API 请求地址错误**
- **原因**：本地测试时 `fetch('/api/xxx')` 会向 `localhost` 请求，部署后应该向当前域名请求。但如果代码中使用了绝对路径（如 `http://localhost:5000/api/xxx`），会导致失败。
- **修复**：检查 `script.js` 中所有 `fetch` 调用，确保使用**相对路径**（例如 `'/api/submit'`）。如果使用了绝对路径，CN 必须给出修改后的 `script.js`。

**问题 C：管理员功能无法使用（如 `/admin` 页面或登录）**
- **可能原因**：
  1. 管理员密码验证方式在服务器环境中失败（比如使用了硬编码密码但环境变量未设置）。
  2. 相关路由未注册或路径错误。
  3. 会话管理问题（如 Flask 的 secret_key 未设置）。
- **修复**：CN 必须提供以下代码的修改方案：
  - 在 `app.py` 中设置 `app.secret_key` 或 `app.config['SECRET_KEY']`（从环境变量读取）。
  - 确保所有管理员相关的路由（如 `/admin`, `/api/admin/stats` 等）正常工作。
  - 提供前端管理员页面的 HTML 和 JS 是否正确加载。

**问题 D：数据库权限导致无法写入（测试提交、捐款等失败）**
- **修复**：CN 应给出命令：
  ```bash
  chmod 777 /var/www/heart_mirror/database
  chmod 777 /var/www/heart_mirror/database/heart_mirror.db
  ```
- 并在 `models.py` 中确保数据库路径使用 `os.path.join` 构建绝对路径，避免相对路径问题。

**问题 E：环境变量缺失（例如 SECRET_KEY、ADMIN_PASSWORD）**
- **修复**：CN 应给出修改 `heart_mirror.service` 文件的指令，添加：
  ```ini
  Environment="SECRET_KEY=your-strong-secret-key"
  Environment="ADMIN_PASSWORD=admin123"   # 按需修改
  ```
- 然后 `systemctl daemon-reload && systemctl restart heart_mirror`。

**问题 F：Gunicorn 启动命令不匹配**
- 确认服务文件中 `ExecStart` 使用的是正确的入口文件（例如 `app:app` 或 `wsgi:app`）。CN 应提供正确的服务文件内容。

**问题 G：前端代码中可能存在针对 `localhost` 的硬编码（例如 WebSocket 或绝对 URL）**
- CN 必须搜索 `script.js` 中所有出现 `localhost`、`127.0.0.1` 的地方，并将其改为相对路径或使用 `window.location.origin`。

### 第三步：CN 需要输出完整的修复方案，包括：

1. **修改后的文件列表**（例如 `app.py`, `script.js`, `nginx.conf`, `heart_mirror.service` 等）的完整内容。
2. **需要在服务器上执行的命令序列**（从停止服务、备份、替换文件、修改权限、重启服务等一系列步骤）。
3. **验证方法**：用户如何测试每个功能（例如访问 `/admin` 能否看到管理面板、提交一道测试题能否成功、捐款是否记录等）。

### 第四步：CN 必须承诺不偷懒，逐项检查

- 不要只输出“请检查 XXX”的文字建议，而是**直接给出可以复制粘贴到项目中的代码和命令**。
- 不要假设本地运行正常就代表线上正常，必须考虑生产环境和开发环境的差异（如路径、权限、端口、环境变量）。
- 如果 CN 无法直接修复，请提供**最小的可重现步骤**和**用户需要提供的额外信息**。

### 第五步：如果问题依然存在

CN 应要求用户在服务器上执行以下诊断脚本，并把输出发回：

```bash
#!/bin/bash
echo "=== 系统信息 ==="
uname -a
echo "=== 项目文件列表 ==="
ls -laR /var/www/heart_mirror --hide=venv
echo "=== Nginx 错误日志（最后20行） ==="
tail -20 /var/log/nginx/error.log
echo "=== Gunicorn 日志 ==="
journalctl -u heart_mirror -n 30 --no-pager
echo "=== 测试 API ==="
curl -v http://localhost/api/stats
echo "=== 测试静态文件 ==="
curl -I http://localhost/static/style.css
echo "=== 数据库文件权限 ==="
ls -la /var/www/heart_mirror/database/
```

根据输出的具体错误，CN 再针对性地修复。

---

## 📌 总结

“**请逐条回答，不要跳过任何一项。如果某些信息缺失，请直接告诉我需要用户提供什么。**”

