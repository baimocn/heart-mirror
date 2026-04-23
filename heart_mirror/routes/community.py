from flask import request, jsonify, render_template
from models import get_moral_dilemmas, add_moral_dilemma, get_moral_dilemma_by_id, delete_moral_dilemma, update_moral_dilemma_votes, get_comments, add_comment, get_messages as get_messages_model, add_message, like_message as like_message_model
from app import app

# 道德困惑墙相关路由
@app.route('/dilemmas')
def dilemmas():
    return render_template('dilemmas.html')

@app.route('/api/dilemmas', methods=['GET', 'POST'])
def moral_dilemmas():
    if request.method == 'GET':
        dilemmas = get_moral_dilemmas()
        return jsonify(dilemmas), 200
    elif request.method == 'POST':
        data = request.json
        device_id = data.get('device_id')
        content = data.get('content')
        options = data.get('options', [])
        is_anonymous = data.get('is_anonymous', 1)
        
        if not device_id or not content or len(options) < 2:
            return jsonify({'error': 'device_id, content, and at least 2 options are required'}), 400
        
        dilemma_id = add_moral_dilemma(device_id, content, options, is_anonymous)
        return jsonify({'message': '道德困惑发布成功', 'id': dilemma_id}), 201

@app.route('/api/dilemmas/<int:dilemma_id>', methods=['GET', 'DELETE'])
def moral_dilemma_detail(dilemma_id):
    if request.method == 'GET':
        dilemma = get_moral_dilemma_by_id(dilemma_id)
        if dilemma:
            return jsonify(dilemma), 200
        return jsonify({'error': '道德困惑不存在'}), 404
    elif request.method == 'DELETE':
        delete_moral_dilemma(dilemma_id)
        return jsonify({'message': '道德困惑删除成功'}), 200

@app.route('/api/dilemmas/<int:dilemma_id>/vote', methods=['POST'])
def vote_dilemma(dilemma_id):
    data = request.json
    option_index = data.get('option_index')
    
    if option_index is None:
        return jsonify({'error': 'option_index is required'}), 400
    
    update_moral_dilemma_votes(dilemma_id, option_index)
    return jsonify({'message': '投票成功'}), 200

# 社区评论相关路由
@app.route('/api/comments', methods=['GET', 'POST'])
def community_comments():
    if request.method == 'GET':
        comments = get_comments()
        return jsonify(comments), 200
    elif request.method == 'POST':
        data = request.json
        device_id = data.get('device_id')
        nickname = data.get('nickname', '匿名用户')
        content = data.get('content')
        
        if not device_id or not content:
            return jsonify({'error': 'device_id and content are required'}), 400
        
        comment_id = add_comment(device_id, nickname, content)
        return jsonify({'status': 'ok', 'message': '评论发布成功', 'id': comment_id}), 201

@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/api/messages', methods=['GET', 'POST'])
def api_messages():
    """获取留言列表或发布新留言"""
    if request.method == 'GET':
        device_id = request.args.get('device_id')
        messages = get_messages_model(device_id)
        return jsonify({'messages': messages}), 200
    elif request.method == 'POST':
        data = request.json
        device_id = data.get('device_id')
        content = data.get('content')
        author = data.get('author', '匿名用户')
        
        if not device_id or not content:
            return jsonify({'error': 'device_id and content are required'}), 400
        
        message_id = add_message(device_id, content, author)
        return jsonify({'message': '留言发布成功', 'id': message_id}), 201

@app.route('/api/messages/like', methods=['POST'])
def api_like_message():
    """点赞留言"""
    data = request.json
    message_id = data.get('message_id')
    device_id = data.get('device_id')
    
    if not message_id or not device_id:
        return jsonify({'error': 'message_id and device_id are required'}), 400
    
    success = like_message_model(message_id, device_id)
    if success:
        return jsonify({'message': '点赞成功'}), 200
    else:
        return jsonify({'error': '点赞失败'}), 500
