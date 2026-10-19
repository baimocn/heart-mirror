from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from models import add_user, get_user_by_username, get_user_by_email, verify_password, get_user_by_account, get_user_admin_level
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
            # 检查用户是否为管理员（admin_level >= 1）
            if not isinstance(current_user, dict) or current_user.get('admin_level', 0) < 1:
                return jsonify({'error': '权限不足'}), 403
        except Exception as e:
            return jsonify({'error': '未授权访问'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 超级管理员认证装饰器
def super_admin_required(f):
    """超级管理员认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            # 检查用户是否为超级管理员（admin_level == 1）
            if not isinstance(current_user, dict) or current_user.get('admin_level', 0) != 1:
                return jsonify({'error': '权限不足'}), 403
        except Exception as e:
            return jsonify({'error': '未授权访问'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 管理员账号验证接口
@app.route('/api/admin/verify_account', methods=['POST'])
def verify_admin_account():
    """验证管理员账号"""
    data = request.json
    account_number = data.get('account_number')
    
    if not account_number:
        return jsonify({'error': '账号不能为空'}), 400
    
    # 检查账号是否存在且为管理员
    user = get_user_by_account(account_number)
    if not user:
        return jsonify({'error': '账号不存在'}), 404
    
    admin_level = get_user_admin_level(account_number)
    if admin_level == 0:
        return jsonify({'error': '该账号不是管理员'}), 403
    
    # 返回管理员级别
    return jsonify({'admin_level': admin_level, 'message': '验证成功'}), 200

# 管理员登录接口
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录接口"""
    data = request.json
    account_number = data.get('account_number')
    password = data.get('password')
    
    if not account_number or not password:
        return jsonify({'error': '账号和密码不能为空'}), 400
    
    # 检查账号是否存在且为管理员
    user = get_user_by_account(account_number)
    if not user:
        return jsonify({'error': '账号不存在'}), 404
    
    admin_level = get_user_admin_level(account_number)
    if admin_level == 0:
        return jsonify({'error': '该账号不是管理员'}), 403
    
    # 验证密码（超级管理员需要密码，受限管理员不需要）
    if admin_level == 1:
        # 超级管理员需要密码验证
        # 使用预设密码 "Fms613728"
        if password != "Fms613728":
            return jsonify({'error': '密码错误'}), 401
    
    # 创建访问令牌
    user_info = {
        'id': user['id'],
        'account_number': account_number,
        'admin_level': admin_level
    }
    access_token = create_access_token(identity=user_info)
    
    # 设置cookie存储令牌
    response = jsonify({'access_token': access_token, 'token_type': 'Bearer', 'admin_level': admin_level})
    response.set_cookie(
        'admin_token',
        access_token,
        httponly=True,
        secure=False,  # 在开发环境中设置为False，生产环境中设置为True
        samesite='Lax',
        max_age=7200  # 2小时过期
    )
    return response, 200

# 测试接口
@app.route('/api/admin/test')
@admin_required
def admin_test():
    """测试管理员认证"""
    return jsonify({'message': '管理员认证成功！', 'user': get_jwt_identity()}), 200

# 获取当前管理员信息接口
@app.route('/api/admin/me')
@admin_required
def get_admin_info():
    """获取当前管理员信息"""
    current_user = get_jwt_identity()
    return jsonify({'user': current_user}), 200

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
