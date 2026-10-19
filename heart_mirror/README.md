# 心镜 · 道德人格测试

一个基于Flask的道德人格测试系统，包含管理员功能模块。

## 功能特性

- 道德人格测试（多种测试模式）
- 管理员后台管理系统
- 数据可视化分析
- 受限管理员管理
- 测试人员数据管理

## 技术栈

- **后端**：Flask, SQLite, JWT
- **前端**：HTML, CSS, JavaScript, Chart.js
- **部署**：Gunicorn, systemd

## 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/heart_mirror.git
   cd heart_mirror
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **创建环境变量文件**
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置JWT_SECRET_KEY等配置
   ```

5. **初始化数据库**
   ```bash
   python -c "from models import init_db; init_db()"
   ```

6. **初始化超级管理员账号**
   ```bash
   python init_admin.py
   ```

7. **启动开发服务器**
   ```bash
   python app.py
   ```

8. **访问系统**
   打开浏览器访问 http://localhost:5000

### 部署到Linux云服务器

1. **准备服务器**
   - 选择一台Linux云服务器（推荐Ubuntu 20.04或更高版本）
   - 确保服务器有公网IP
   - 开放8000端口（或其他你指定的端口）

2. **上传部署脚本**
   将 `deploy.sh` 脚本上传到服务器

3. **执行部署脚本**
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

4. **访问系统**
   打开浏览器访问 http://your-server-ip:8000

## 管理员功能

### 登录流程
1. 在系统结果页面的"锚点"区域输入管理员账号
2. 超级管理员需要输入密码，受限管理员无需密码
3. 登录成功后跳转到管理员后台

### 管理员权限
- **超级管理员**：完整的管理权限，包括数据修改、受限管理员管理
- **受限管理员**：只能查看数据，不能修改

### 管理员账号
- 超级管理员账号：350524200705057715
- 超级管理员密码：Fms613728

## 项目结构

```
heart_mirror/
├── app.py              # 主应用文件
├── models.py           # 数据模型和业务逻辑
├── routes/             # API路由
│   ├── auth.py         # 认证相关路由
│   ├── admin.py        # 管理员相关路由
│   └── __init__.py     # 路由注册
├── services/           # 服务层
│   └── database_service.py  # 数据库操作服务
├── static/             # 静态文件
│   ├── style.css       # 样式文件
│   ├── script.js       # JavaScript文件
│   └── questions.json  # 测试题目数据
├── templates/          # HTML模板
│   ├── index.html      # 首页模板
│   └── admin.html      # 管理员后台模板
├── database/           # 数据库文件
├── requirements.txt    # 依赖文件
├── init_admin.py       # 初始化超级管理员账号
└── deploy.sh           # 部署脚本
```

## 注意事项

- 生产环境中请修改JWT_SECRET_KEY为随机字符串
- 生产环境中请使用HTTPS协议
- 定期备份数据库文件
- 监控服务器资源使用情况

## 许可证

MIT License
