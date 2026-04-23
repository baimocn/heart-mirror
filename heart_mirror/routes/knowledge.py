from flask import request, jsonify, render_template
from models import get_knowledge_articles, add_knowledge_article, get_knowledge_article_by_id, increment_knowledge_article_views, get_knowledge_categories, add_time_capsule, get_time_capsules, delete_time_capsule, get_daily_tasks, assign_task_to_user, get_user_tasks, complete_task, get_user_points, get_personalized_recommendations
from app import app, admin_required
import json

# 道德知识库相关路由
@app.route('/api/knowledge', methods=['GET'])
def knowledge_base_get():
    category = request.args.get('category')
    articles = get_knowledge_articles(category)
    return jsonify(articles), 200

@app.route('/api/knowledge', methods=['POST'])
@admin_required
def knowledge_base_post():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')
    if not title or not content or not category:
        return jsonify({'error': 'title, content, and category are required'}), 400
    
    article_id = add_knowledge_article(title, content, category)
    return jsonify({'message': '知识文章添加成功', 'id': article_id}), 201

@app.route('/api/knowledge/<int:article_id>', methods=['GET'])
def knowledge_article_detail(article_id):
    # 增加浏览量
    increment_knowledge_article_views(article_id)
    # 获取文章详情
    article = get_knowledge_article_by_id(article_id)
    if article:
        return jsonify(article), 200
    return jsonify({'error': '文章不存在'}), 404

@app.route('/api/knowledge/categories', methods=['GET'])
def knowledge_categories():
    categories = get_knowledge_categories()
    return jsonify(categories), 200

@app.route('/knowledge')
def knowledge_page():
    return render_template('knowledge.html')

# 时间胶囊相关路由
@app.route('/api/time_capsule', methods=['POST'])
def create_time_capsule():
    data = request.json
    device_id = data.get('device_id')
    title = data.get('title')
    scores_json = json.dumps(data.get('scores', []))
    mood_tags = json.dumps(data.get('mood_tags', []))
    email = data.get('email')
    
    if not device_id or not title or not email:
        return jsonify({'error': 'device_id, title, and email are required'}), 400
    
    capsule_id = add_time_capsule(device_id, title, scores_json, mood_tags, email)
    return jsonify({'message': '时间胶囊创建成功', 'id': capsule_id}), 201

@app.route('/api/time_capsules', methods=['GET'])
def get_user_time_capsules():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    capsules = get_time_capsules(device_id)
    return jsonify(capsules), 200

@app.route('/api/time_capsules/<int:capsule_id>', methods=['DELETE'])
def delete_user_time_capsule(capsule_id):
    delete_time_capsule(capsule_id)
    return jsonify({'message': '时间胶囊删除成功'}), 200

# 每日微行动相关路由
@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    category = request.args.get('category')
    tasks = get_daily_tasks(category)
    return jsonify(tasks), 200

@app.route('/api/tasks/assign', methods=['POST'])
def assign_task():
    data = request.json
    device_id = data.get('device_id')
    task_id = data.get('task_id')
    
    if not device_id or not task_id:
        return jsonify({'error': 'device_id and task_id are required'}), 400
    
    user_task_id = assign_task_to_user(device_id, task_id)
    return jsonify({'message': '任务分配成功', 'id': user_task_id}), 201

@app.route('/api/user_tasks', methods=['GET'])
def get_user_tasks_api():
    device_id = request.args.get('device_id')
    status = request.args.get('status')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    tasks = get_user_tasks(device_id, status)
    return jsonify(tasks), 200

@app.route('/api/user_tasks/<int:user_task_id>/complete', methods=['POST'])
def complete_user_task(user_task_id):
    complete_task(user_task_id)
    return jsonify({'message': '任务完成成功'}), 200

@app.route('/api/user_points', methods=['GET'])
def get_user_points_api():
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    points = get_user_points(device_id)
    return jsonify({'points': points}), 200

# 个性化推荐API
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    device_id = data.get('device_id')
    scores = data.get('scores')
    
    if not device_id or not scores:
        return jsonify({'error': 'device_id and scores are required'}), 400
    
    recommendations = get_personalized_recommendations(device_id, scores)
    return jsonify(recommendations), 200
