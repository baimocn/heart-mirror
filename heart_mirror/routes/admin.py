from flask import request, jsonify, render_template
from models import get_admin_stats, get_user_by_account, get_test_history, create_user, set_admin_level
from app import app, admin_required, super_admin_required
import json
import os
import sqlite3

# 管理员路由
@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    stats = get_admin_stats()
    return jsonify(stats), 200

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/admin/questions')
@admin_required
def admin_questions():
    return render_template('admin_questions.html')

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def question_detail_get(question_id):
    # 加载题目数据
    questions_file = os.path.join(os.path.dirname(__file__), '..', 'static', 'questions.json')
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    questions = questions_data['questions']
    
    # 获取题目详情
    for q in questions:
        if q.get('id') == question_id:
            return jsonify(q), 200
    return jsonify({'error': '题目不存在'}), 404

@app.route('/api/questions/<int:question_id>', methods=['PUT', 'DELETE'])
@admin_required
def question_detail_modify(question_id):
    # 加载题目数据
    questions_file = os.path.join(os.path.dirname(__file__), '..', 'static', 'questions.json')
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    questions = questions_data['questions']
    
    if request.method == 'PUT':
        # 更新题目
        data = request.json
        for i, q in enumerate(questions):
            if q.get('id') == question_id:
                questions[i] = data
                # 保存到文件
                with open(questions_file, 'w', encoding='utf-8') as f:
                    json.dump(questions_data, f, ensure_ascii=False, indent=2)
                return jsonify({'message': '题目更新成功'}), 200
        return jsonify({'error': '题目不存在'}), 404
    elif request.method == 'DELETE':
        # 删除题目
        for i, q in enumerate(questions):
            if q.get('id') == question_id:
                questions.pop(i)
                # 保存到文件
                with open(questions_file, 'w', encoding='utf-8') as f:
                    json.dump(questions_data, f, ensure_ascii=False, indent=2)
                return jsonify({'message': '题目删除成功'}), 200
        return jsonify({'error': '题目不存在'}), 404

@app.route('/api/questions', methods=['POST'])
@admin_required
def add_question():
    data = request.json
    # 加载题目数据
    questions_file = os.path.join(os.path.dirname(__file__), '..', 'static', 'questions.json')
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    questions = questions_data['questions']
    # 生成新的题目ID
    new_id = max([q.get('id', 0) for q in questions]) + 1
    data['id'] = new_id
    questions.append(data)
    # 保存到文件
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
    return jsonify({'message': '题目添加成功', 'id': new_id}), 201

# 测试人员数据管理API

@app.route('/api/admin/test_users', methods=['GET'])
@admin_required
def get_test_users():
    """获取所有测试人员数据"""
    try:
        # 连接数据库
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # 查询所有用户
        c.execute('SELECT id, account_number, device_id, admin_level, created_at FROM users')
        users = c.fetchall()
        
        # 整理用户数据
        users_data = []
        for user in users:
            user_dict = {
                'id': user['id'],
                'account_number': user['account_number'],
                'device_id': user['device_id'],
                'admin_level': user['admin_level'],
                'created_at': user['created_at']
            }
            
            # 查询用户的测试历史
            c.execute('SELECT id, scores_json, title, created_at FROM test_history WHERE user_id = ? ORDER BY created_at DESC', (user['id'],))
            test_history = c.fetchall()
            
            user_dict['test_history'] = []
            for test in test_history:
                user_dict['test_history'].append({
                    'id': test['id'],
                    'scores': json.loads(test['scores_json']) if test['scores_json'] else [],
                    'title': test['title'],
                    'created_at': test['created_at']
                })
            
            users_data.append(user_dict)
        
        conn.close()
        return jsonify(users_data), 200
    except Exception as e:
        print(f"Error getting test users: {e}")
        return jsonify({'error': '获取测试人员数据失败'}), 500

@app.route('/api/admin/test_users/<int:user_id>', methods=['PUT'])
@super_admin_required
def update_test_user(user_id):
    """修改测试人员数据"""
    try:
        data = request.json
        
        # 连接数据库
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 更新用户信息
        if 'account_number' in data:
            c.execute('UPDATE users SET account_number = ? WHERE id = ?', (data['account_number'], user_id))
        if 'device_id' in data:
            c.execute('UPDATE users SET device_id = ? WHERE id = ?', (data['device_id'], user_id))
        if 'admin_level' in data:
            c.execute('UPDATE users SET admin_level = ? WHERE id = ?', (data['admin_level'], user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '测试人员数据更新成功'}), 200
    except Exception as e:
        print(f"Error updating test user: {e}")
        return jsonify({'error': '更新测试人员数据失败'}), 500

# 受限管理员管理API

@app.route('/api/admin/limited_admins', methods=['GET'])
@admin_required
def get_limited_admins():
    """获取受限管理员列表"""
    try:
        # 连接数据库
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # 查询所有受限管理员（admin_level = 2）
        c.execute('SELECT id, account_number, device_id, created_at FROM users WHERE admin_level = 2')
        admins = c.fetchall()
        
        # 整理数据
        admins_data = []
        for admin in admins:
            admins_data.append({
                'id': admin['id'],
                'account_number': admin['account_number'],
                'device_id': admin['device_id'],
                'created_at': admin['created_at']
            })
        
        conn.close()
        return jsonify(admins_data), 200
    except Exception as e:
        print(f"Error getting limited admins: {e}")
        return jsonify({'error': '获取受限管理员列表失败'}), 500

@app.route('/api/admin/limited_admins', methods=['POST'])
@super_admin_required
def add_limited_admin():
    """添加受限管理员"""
    try:
        data = request.json
        account_number = data.get('account_number')
        device_id = data.get('device_id')
        
        if not account_number:
            return jsonify({'error': '数字账号不能为空'}), 400
        
        if not device_id:
            return jsonify({'error': '设备ID不能为空'}), 400
        
        # 检查账号是否已存在
        existing_user = get_user_by_account(account_number)
        if existing_user:
            # 如果账号已存在，更新为受限管理员
            success = set_admin_level(account_number, 2)
            if success:
                return jsonify({'message': '受限管理员添加成功'}), 200
            else:
                return jsonify({'error': '添加失败'}), 500
        else:
            # 如果账号不存在，创建新用户并设置为受限管理员
            user_id = create_user(account_number, device_id, 2)
            if user_id:
                return jsonify({'message': '受限管理员添加成功'}), 201
            else:
                return jsonify({'error': '添加失败'}), 500
    except Exception as e:
        print(f"Error adding limited admin: {e}")
        return jsonify({'error': '添加受限管理员失败'}), 500

@app.route('/api/admin/limited_admins/<int:admin_id>', methods=['DELETE'])
@super_admin_required
def delete_limited_admin(admin_id):
    """删除受限管理员"""
    try:
        # 连接数据库
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 将管理员级别设置为普通用户（0）
        c.execute('UPDATE users SET admin_level = 0 WHERE id = ? AND admin_level = 2', (admin_id,))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'message': '受限管理员删除成功'}), 200
        else:
            conn.close()
            return jsonify({'error': '删除失败，该用户不是受限管理员'}), 400
    except Exception as e:
        print(f"Error deleting limited admin: {e}")
        return jsonify({'error': '删除受限管理员失败'}), 500
