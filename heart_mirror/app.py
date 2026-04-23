from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from models import init_db, get_stats, increment_participant, add_donation, get_donation_list, add_user, get_user_by_username, get_user_by_email, verify_password, add_question_stat, increment_question_stat, add_option_stat, get_question_stats, get_option_stats, get_admin_stats, get_test_history, add_donation_flow, get_donation_flows, get_donation_flow_by_id, update_donation_flow, delete_donation_flow, add_donation_batch, get_donation_batches, get_donation_batch_by_id, update_donation_batch, delete_donation_batch, update_batch_total_amount, add_time_capsule, get_time_capsules, delete_time_capsule, add_moral_dilemma, get_moral_dilemmas, get_moral_dilemma_by_id, update_moral_dilemma_votes, delete_moral_dilemma, add_daily_task, get_daily_tasks, get_task_by_id, assign_task_to_user, get_user_tasks, complete_task, get_user_points, init_daily_tasks, add_comment, get_comments, add_knowledge_article, get_knowledge_articles, get_knowledge_article_by_id, increment_knowledge_article_views, get_knowledge_categories, get_personalized_recommendations, get_user_by_account, create_user, update_user_device_id
import json
import os
import sqlite3
import random
import re
import bcrypt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps

# 加载环境变量
load_dotenv()

# 初始化数据库
init_db()

app = Flask(__name__)
CORS(app)

# JWT配置
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
    seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 7200))
)
jwt = JWTManager(app)

# 数据库连接
DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db'))

# 密码哈希和验证功能
def hash_password(password):
    """使用bcrypt哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password_hash(password, hashed_password):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_password_complexity(password):
    """验证密码复杂度"""
    if len(password) < 8:
        return False, "密码长度至少为8位"
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含大写字母"
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含小写字母"
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含数字"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "密码必须包含特殊字符"
    return True, "密码复杂度符合要求"

def get_admin_password_hash():
    """获取管理员密码哈希"""
    # 从环境变量读取密码，如果没有则使用默认密码
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    # 验证密码复杂度
    is_valid, message = validate_password_complexity(admin_password)
    if not is_valid:
        print(f"警告: 管理员密码不符合复杂度要求: {message}")
    # 哈希密码
    return hash_password(admin_password)

# 管理员密码哈希
ADMIN_PASSWORD_HASH = get_admin_password_hash()

# 管理员认证装饰器
def admin_required(f):
    """管理员认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user != 'admin':
                return jsonify({'error': '权限不足'}), 403
        except Exception as e:
            return jsonify({'error': '未授权访问'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 初始化数据库
init_db()
# 初始化每日任务
init_daily_tasks()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/anchor', methods=['POST'])
def api_anchor():
    """处理锚点账号验证和创建"""
    try:
        data = request.json
        account_number = data.get('account_number')
        device_id = data.get('device_id')
        
        if not account_number or not device_id:
            return jsonify({'error': 'account_number and device_id are required'}), 400
        
        # 验证账号格式
        if not account_number.isdigit():
            return jsonify({'error': 'account_number must be a number'}), 400
        
        # 查询账号是否存在
        user = get_user_by_account(account_number)
        
        if user:
            # 账号已存在，更新设备ID
            update_user_device_id(user['id'], device_id)
            user_id = user['id']
            message = '账号已存在，已关联到当前设备'
        else:
            # 账号不存在，创建新用户
            user_id = create_user(account_number, device_id)
            if not user_id:
                return jsonify({'error': '账号创建失败'}), 500
            message = '账号创建成功'
        
        # 将最近的测试数据与用户关联
        import sqlite3
        import os
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('UPDATE test_history SET user_id = ? WHERE id = (SELECT id FROM test_history WHERE device_id = ? AND user_id IS NULL ORDER BY created_at DESC LIMIT 1)', (user_id, device_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': message,
            'user': {
                'id': user_id,
                'account_number': account_number,
                'device_id': device_id
            }
        }), 200
    except Exception as e:
        print(f"Error in api_anchor: {e}")
        return jsonify({'error': '操作失败，请稍后重试'}), 500

# 导入路由模块
from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)