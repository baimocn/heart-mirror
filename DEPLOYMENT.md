# 心镜项目部署指南

## 部署到Railway平台

### 步骤1：准备工作
1. 确保项目已经推送到GitHub（已完成）
2. 确保项目包含以下配置文件：
   - `Procfile`：定义如何启动应用
   - `requirements.txt`：列出项目依赖
   - `.env`：环境变量配置

### 步骤2：通过Railway网站部署
1. **访问Railway网站**：打开 https://railway.app
2. **登录或注册**：使用GitHub账号登录
3. **创建新项目**：
   - 点击"New Project"按钮
   - 选择"GitHub Repo"选项
   - 搜索并选择"baimocn/heart-mirror"仓库
   - 点击"Import"按钮
4. **配置环境**：
   - Railway会自动检测项目类型并配置环境
   - 确保环境变量正确设置（参考.env文件）
5. **部署项目**：
   - Railway会自动开始部署过程
   - 等待部署完成
6. **查看部署状态**：
   - 点击项目查看部署状态
   - 检查日志确保无错误
7. **访问应用**：
   - Railway会为应用分配一个唯一的URL
   - 点击URL访问部署后的应用

### 步骤3：配置自动部署
1. 在Railway项目页面，点击"Settings"选项卡
2. 找到"Deployments"部分
3. 确保"Auto Deploy"选项已启用
4. 这样，当你推送代码到GitHub时，Railway会自动重新部署应用

### 步骤4：验证部署
1. 访问部署后的应用URL
2. 测试核心功能：
   - 测试页面加载
   - 测试API endpoints
   - 测试测试流程
3. 检查日志确保无错误

## 项目配置文件说明

### Procfile
```
web: gunicorn app:app
```
- 告诉Railway使用gunicorn作为WSGI服务器启动应用
- `app:app`表示从app模块中导入app对象

### requirements.txt
```
Flask==2.3.3
Flask-CORS==4.0.0
Flask-JWT-Extended==4.7.1
Werkzeug==3.1.8
PyJWT==2.12.1
gunicorn==21.2.0
```
- 列出项目所需的Python依赖

### .env
```
# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=7200

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@123

# 数据库配置
DB_PATH=database/heart_mirror.db

# 应用配置
FLASK_ENV=production
FLASK_DEBUG=False
```
- 环境变量配置
- 在生产环境中，建议修改JWT_SECRET_KEY为更安全的值

## 故障排查

### 常见问题
1. **部署失败**：检查日志中的错误信息
2. **应用无法访问**：检查端口配置和环境变量
3. **数据库连接失败**：确保DB_PATH路径正确
4. **依赖安装失败**：检查requirements.txt文件格式

### 解决方法
1. **查看部署日志**：在Railway项目页面点击"Logs"选项卡
2. **检查环境变量**：确保所有必要的环境变量已设置
3. **更新依赖**：如果依赖版本有问题，更新requirements.txt文件
4. **检查Procfile**：确保Procfile格式正确

## 联系信息

如果在部署过程中遇到问题，请联系项目维护者。