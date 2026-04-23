from flask import request, jsonify, render_template
from models import get_admin_stats
from app import app, admin_required
import json
import os

# 管理员路由
@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    stats = get_admin_stats()
    return jsonify(stats), 200

@app.route('/admin')
@admin_required
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
