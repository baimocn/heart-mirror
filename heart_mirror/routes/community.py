from flask import request, jsonify, render_template
from models import get_moral_dilemmas, add_moral_dilemma, get_moral_dilemma_by_id, delete_moral_dilemma, update_moral_dilemma_votes, get_comments, add_comment, get_messages as get_messages_model, add_message, like_message as like_message_model, add_dilemma_comment, get_dilemma_comments, like_dilemma, unlike_dilemma, is_dilemma_liked, favorite_dilemma, unfavorite_dilemma, is_dilemma_favorited, follow_dilemma, unfollow_dilemma, is_dilemma_followed, like_comment, unlike_comment, is_comment_liked
from app import app

# 道德困惑墙相关路由
@app.route('/dilemmas')
def dilemmas():
    return render_template('dilemmas.html')

@app.route('/api/dilemmas', methods=['GET', 'POST'])
def moral_dilemmas():
    if request.method == 'GET':
        sort_by = request.args.get('sort_by', 'latest')
        category = request.args.get('category')
        dilemmas = get_moral_dilemmas(sort_by, category)
        return jsonify(dilemmas), 200
    elif request.method == 'POST':
        data = request.json
        device_id = data.get('device_id')
        title = data.get('title')
        content = data.get('content')
        description = data.get('description', '')
        background = data.get('background', '')
        options = data.get('options', [])
        category = data.get('category', '其他')
        is_anonymous = data.get('is_anonymous', 1)
        
        if not device_id or not title or not content or len(options) < 2:
            return jsonify({'error': 'device_id, title, content, and at least 2 options are required'}), 400
        
        dilemma_id = add_moral_dilemma(device_id, title, content, description, background, options, category, is_anonymous)
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

# 道德困惑评论相关路由
@app.route('/api/dilemmas/<int:dilemma_id>/comments', methods=['GET', 'POST'])
def dilemma_comments(dilemma_id):
    if request.method == 'GET':
        comments = get_dilemma_comments(dilemma_id)
        return jsonify(comments), 200
    elif request.method == 'POST':
        data = request.json
        device_id = data.get('device_id')
        nickname = data.get('nickname', '匿名用户')
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not device_id or not content:
            return jsonify({'error': 'device_id and content are required'}), 400
        
        comment_id = add_dilemma_comment(dilemma_id, device_id, nickname, content, parent_id)
        return jsonify({'message': '评论发布成功', 'id': comment_id}), 201

# 道德困惑点赞相关路由
@app.route('/api/dilemmas/<int:dilemma_id>/like', methods=['POST'])
def dilemma_like(dilemma_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = like_dilemma(dilemma_id, device_id)
    if success:
        return jsonify({'message': '点赞成功'}), 200
    else:
        return jsonify({'error': '点赞失败'}), 500

@app.route('/api/dilemmas/<int:dilemma_id>/unlike', methods=['POST'])
def dilemma_unlike(dilemma_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = unlike_dilemma(dilemma_id, device_id)
    if success:
        return jsonify({'message': '取消点赞成功'}), 200
    else:
        return jsonify({'error': '取消点赞失败'}), 500

@app.route('/api/dilemmas/<int:dilemma_id>/is_liked', methods=['GET'])
def dilemma_is_liked(dilemma_id):
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    is_liked = is_dilemma_liked(dilemma_id, device_id)
    return jsonify({'is_liked': is_liked}), 200

# 道德困惑收藏相关路由
@app.route('/api/dilemmas/<int:dilemma_id>/favorite', methods=['POST'])
def dilemma_favorite(dilemma_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = favorite_dilemma(dilemma_id, device_id)
    if success:
        return jsonify({'message': '收藏成功'}), 200
    else:
        return jsonify({'error': '收藏失败'}), 500

@app.route('/api/dilemmas/<int:dilemma_id>/unfavorite', methods=['POST'])
def dilemma_unfavorite(dilemma_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = unfavorite_dilemma(dilemma_id, device_id)
    if success:
        return jsonify({'message': '取消收藏成功'}), 200
    else:
        return jsonify({'error': '取消收藏失败'}), 500

@app.route('/api/dilemmas/<int:dilemma_id>/is_favorited', methods=['GET'])
def dilemma_is_favorited(dilemma_id):
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    is_favorited = is_dilemma_favorited(dilemma_id, device_id)
    return jsonify({'is_favorited': is_favorited}), 200

# 道德困惑关注相关路由
@app.route('/api/dilemmas/<int:dilemma_id>/follow', methods=['POST'])
def dilemma_follow(dilemma_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = follow_dilemma(dilemma_id, device_id)
    if success:
        return jsonify({'message': '关注成功'}), 200
    else:
        return jsonify({'error': '关注失败'}), 500

@app.route('/api/dilemmas/<int:dilemma_id>/unfollow', methods=['POST'])
def dilemma_unfollow(dilemma_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = unfollow_dilemma(dilemma_id, device_id)
    if success:
        return jsonify({'message': '取消关注成功'}), 200
    else:
        return jsonify({'error': '取消关注失败'}), 500

@app.route('/api/dilemmas/<int:dilemma_id>/is_followed', methods=['GET'])
def dilemma_is_followed(dilemma_id):
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    is_followed = is_dilemma_followed(dilemma_id, device_id)
    return jsonify({'is_followed': is_followed}), 200

# 评论点赞相关路由
@app.route('/api/comments/<int:comment_id>/like', methods=['POST'])
def comment_like(comment_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = like_comment(comment_id, device_id)
    if success:
        return jsonify({'message': '点赞成功'}), 200
    else:
        return jsonify({'error': '点赞失败'}), 500

@app.route('/api/comments/<int:comment_id>/unlike', methods=['POST'])
def comment_unlike(comment_id):
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    success = unlike_comment(comment_id, device_id)
    if success:
        return jsonify({'message': '取消点赞成功'}), 200
    else:
        return jsonify({'error': '取消点赞失败'}), 500

@app.route('/api/comments/<int:comment_id>/is_liked', methods=['GET'])
def comment_is_liked(comment_id):
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    is_liked = is_comment_liked(comment_id, device_id)
    return jsonify({'is_liked': is_liked}), 200
