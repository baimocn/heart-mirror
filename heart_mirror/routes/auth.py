from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from models import add_user, get_user_by_username, get_user_by_email, verify_password
from app import app, ADMIN_PASSWORD_HASH, verify_password_hash
import re

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

# 管理员登录接口
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录接口"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 验证管理员凭据
    if username != 'admin' or not verify_password_hash(password, ADMIN_PASSWORD_HASH):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 创建访问令牌
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token, 'token_type': 'Bearer'}), 200

# 测试接口
@app.route('/api/admin/test')
@admin_required
def admin_test():
    """测试管理员认证"""
    return jsonify({'message': '管理员认证成功！', 'user': get_jwt_identity()}), 200

# 用户系统路由
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
    
    if get_user_by_username(username):
        return jsonify({'error': '用户名已存在'}), 400
    
    if get_user_by_email(email):
        return jsonify({'error': '邮箱已存在'}), 400
    
    user_id = add_user(username, email, password)
    return jsonify({'message': '注册成功', 'user_id': user_id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = get_user_by_username(username)
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    access_token = create_access_token(identity=user['id'])
    return jsonify({'access_token': access_token, 'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}}), 200

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    # 这里可以根据user_id获取用户信息
    return jsonify({'message': '获取用户信息成功', 'user_id': user_id}), 200
