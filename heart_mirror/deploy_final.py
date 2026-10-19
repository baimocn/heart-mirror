import paramiko
import os
import time

# 服务器信息
SERVER_IP = '8.136.152.54'
SERVER_USER = 'root'
SERVER_PASSWORD = 'Fms613728'
SERVER_PROJECT_PATH = '/var/www/heart_mirror'

# 本地项目路径
LOCAL_PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

def ssh_exec(client, command):
    """执行SSH命令"""
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if error:
        print(f"错误: {error}")
    return output

def sftp_put_dir(sftp, local_dir, remote_dir):
    """递归上传目录"""
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = os.path.join(remote_dir, item).replace('\\', '/')
        if os.path.isdir(local_path):
            # 创建远程目录
            try:
                sftp.mkdir(remote_path)
            except:
                pass
            # 递归上传
            sftp_put_dir(sftp, local_path, remote_path)
        else:
            # 上传文件
            print(f"上传: {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)

def main():
    print("开始部署项目...")
    
    # 连接服务器
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, 22, SERVER_USER, SERVER_PASSWORD)
    print("连接服务器成功")
    
    # 创建项目目录
    ssh_exec(client, f'mkdir -p {SERVER_PROJECT_PATH}')
    
    # 上传项目文件
    sftp = client.open_sftp()
    sftp_put_dir(sftp, LOCAL_PROJECT_PATH, SERVER_PROJECT_PATH)
    sftp.close()
    print("项目文件上传完成")
    
    # 安装依赖
    print("安装依赖...")
    ssh_exec(client, f'cd {SERVER_PROJECT_PATH} && python3 -m venv venv && venv/bin/pip install -r requirements.txt')
    
    # 初始化数据库
    print("初始化数据库...")
    ssh_exec(client, f'cd {SERVER_PROJECT_PATH} && venv/bin/python -c "from models import init_db; init_db()"')
    
    # 初始化超级管理员账号
    print("初始化超级管理员账号...")
    ssh_exec(client, f'cd {SERVER_PROJECT_PATH} && venv/bin/python init_admin.py')
    
    # 创建Gunicorn配置文件
    print("创建Gunicorn配置文件...")
    gunicorn_config = '''bind = '0.0.0.0:8000'
workers = 3
threads = 2
timeout = 120'''
    sftp = client.open_sftp()
    with sftp.open(f'{SERVER_PROJECT_PATH}/gunicorn_config.py', 'w') as f:
        f.write(gunicorn_config)
    sftp.close()
    
    # 创建systemd服务文件
    print("创建systemd服务文件...")
    service_file = f'''
[Unit]
Description=Heart Mirror Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory={SERVER_PROJECT_PATH}
ExecStart={SERVER_PROJECT_PATH}/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
'''
    sftp = client.open_sftp()
    with sftp.open('/etc/systemd/system/heart_mirror.service', 'w') as f:
        f.write(service_file)
    sftp.close()
    
    # 创建Nginx配置文件
    print("创建Nginx配置文件...")
    nginx_config = f'''
server {{
    listen 80;
    server_name {SERVER_IP};

    location / {{
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
'''
    sftp = client.open_sftp()
    with sftp.open('/etc/nginx/sites-available/heart_mirror', 'w') as f:
        f.write(nginx_config)
    sftp.close()
    
    # 启用Nginx配置
    print("启用Nginx配置...")
    ssh_exec(client, 'ln -s /etc/nginx/sites-available/heart_mirror /etc/nginx/sites-enabled/')
    
    # 重启服务
    print("重启服务...")
    ssh_exec(client, 'systemctl daemon-reload')
    ssh_exec(client, 'systemctl start heart_mirror')
    ssh_exec(client, 'systemctl enable heart_mirror')
    ssh_exec(client, 'systemctl restart nginx')
    
    # 检查服务状态
    print("检查服务状态...")
    time.sleep(5)  # 等待服务启动
    ssh_exec(client, 'systemctl status heart_mirror')
    ssh_exec(client, 'systemctl status nginx')
    
    # 测试访问
    print("测试访问...")
    ssh_exec(client, f'curl -I http://{SERVER_IP}')
    
    # 关闭连接
    client.close()
    print("部署完成！")

if __name__ == "__main__":
    main()
