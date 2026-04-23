# 导入数据库服务
from services.database_service import db_service
import json

# 数据库操作函数 - 委托给数据库服务层
def init_db():
    """初始化数据库"""
    db_service.init_db()

def get_stats():
    """获取统计数据"""
    stats = db_service.get_stats()
    return {'participants': stats['participants'], 'total_donation': round(stats['total_donation_amount'], 2)}

def increment_participant():
    """每次完成测试，参与人数+1，公益金额+0.01元"""
    db_service.increment_participant()

def get_donation_list(limit=20):
    """获取已确认的善行榜"""
    donations = db_service.get_donation_list()
    confirmed_donations = [d for d in donations if d['status'] == 'confirmed'][:limit]
    return [{'nickname': d['nickname'], 'amount': d['amount'], 'time': d['created_at']} for d in confirmed_donations]

def add_donation(device_id, amount, nickname, user_id=None, status='confirmed'):
    """添加捐款记录（演示模式直接确认）"""
    db_service.add_donation(device_id, amount, nickname, status)

def add_user(username, email, password):
    """添加用户"""
    return db_service.add_user(username, email, password)

def get_user_by_username(username):
    """根据用户名获取用户"""
    user = db_service.get_user_by_username(username)
    if user:
        user['created_at'] = user.get('created_at', None)
    return user

def get_user_by_email(email):
    """根据邮箱获取用户"""
    user = db_service.get_user_by_email(email)
    if user:
        user['created_at'] = user.get('created_at', None)
    return user

def verify_password(password_hash, password):
    """验证密码"""
    return db_service.verify_password(password_hash, password)

def add_question_stat(question_id, category):
    """添加题目统计记录"""
    db_service.add_question_stat(question_id, category)

def increment_question_stat(question_id, duration):
    """增加题目统计"""
    db_service.increment_question_stat(question_id, duration)

def add_option_stat(question_id, option_index):
    """增加选项统计"""
    db_service.add_option_stat(question_id, option_index)

def get_question_stats():
    """获取题目统计"""
    return db_service.get_question_stats()

def get_option_stats(question_id):
    """获取选项统计"""
    return db_service.get_option_stats(question_id)

def get_admin_stats():
    """获取管理员统计数据"""
    return db_service.get_admin_stats()

def get_user_by_account(account_number):
    """根据账号数字获取用户"""
    return db_service.get_user_by_account(account_number)

def create_user(account_number, device_id):
    """创建新用户"""
    return db_service.create_user(account_number, device_id)

def update_user_device_id(user_id, device_id):
    """更新用户设备ID"""
    db_service.update_user_device_id(user_id, device_id)

def get_test_history(device_id=None, user_id=None):
    """获取用户的测试历史记录"""
    history = db_service.get_test_history(device_id, user_id)
    return [{
        'timestamp': h['created_at'],
        'scores': h['scores'],
        'title': h['title']
    } for h in history]

def add_donation_flow(batch_id, amount, purpose, date, description, images):
    """添加善款流向记录"""
    return db_service.add_donation_flow(batch_id, amount, purpose, date, description, images)

def get_donation_flows():
    """获取所有善款流向记录"""
    flows = db_service.get_donation_flows()
    for flow in flows:
        flow['created_at'] = flow.get('created_at', None)
    return flows

def get_donation_flow_by_id(flow_id):
    """根据ID获取善款流向记录"""
    flow = db_service.get_donation_flow_by_id(flow_id)
    if flow:
        flow['created_at'] = flow.get('created_at', None)
    return flow

def update_donation_flow(flow_id, amount, purpose, date, description, images):
    """更新善款流向记录"""
    db_service.update_donation_flow(flow_id, amount, purpose, date, description, images)

def delete_donation_flow(flow_id):
    """删除善款流向记录"""
    db_service.delete_donation_flow(flow_id)

def add_donation_batch(batch_id, name, start_date, end_date, description, images):
    """添加善款批次"""
    return db_service.add_donation_batch(batch_id, name, start_date, end_date, description, images)

def get_donation_batches():
    """获取所有善款批次"""
    batches = db_service.get_donation_batches()
    for batch in batches:
        batch['created_at'] = batch.get('created_at', None)
    return batches

def get_donation_batch_by_id(batch_id):
    """根据ID获取善款批次"""
    batch = db_service.get_donation_batch_by_id(batch_id)
    if batch:
        batch['created_at'] = batch.get('created_at', None)
    return batch

def update_donation_batch(batch_id, name, start_date, end_date, status, description, images):
    """更新善款批次"""
    db_service.update_donation_batch(batch_id, name, start_date, end_date, status, description, images)

def delete_donation_batch(batch_id):
    """删除善款批次"""
    db_service.delete_donation_batch(batch_id)

def update_batch_total_amount(batch_id):
    """更新批次总金额"""
    db_service.update_batch_total_amount(batch_id)

def add_time_capsule(device_id, title, scores_json, mood_tags, email):
    """添加时间胶囊"""
    return db_service.add_time_capsule(device_id, title, scores_json, mood_tags, email)

def get_time_capsules(device_id):
    """获取用户的时间胶囊"""
    capsules = db_service.get_time_capsules(device_id)
    for capsule in capsules:
        capsule['reminder_date'] = capsule.get('reminder_date', None)
    return capsules

def delete_time_capsule(capsule_id):
    """删除时间胶囊"""
    db_service.delete_time_capsule(capsule_id)

def add_moral_dilemma(device_id, content, options, is_anonymous=1):
    """添加道德困惑"""
    return db_service.add_moral_dilemma(device_id, content, options, is_anonymous)

def get_moral_dilemmas():
    """获取所有道德困惑"""
    dilemmas = db_service.get_moral_dilemmas()
    for dilemma in dilemmas:
        dilemma['user_id'] = dilemma.get('user_id', None)
    return dilemmas

def get_moral_dilemma_by_id(dilemma_id):
    """根据ID获取道德困惑"""
    dilemma = db_service.get_moral_dilemma_by_id(dilemma_id)
    if dilemma:
        dilemma['user_id'] = dilemma.get('user_id', None)
    return dilemma

def update_moral_dilemma_votes(dilemma_id, option_index):
    """更新道德困惑投票"""
    db_service.update_moral_dilemma_votes(dilemma_id, option_index)

def delete_moral_dilemma(dilemma_id):
    """删除道德困惑"""
    db_service.delete_moral_dilemma(dilemma_id)

def add_daily_task(title, description, category, difficulty, points):
    """添加每日任务"""
    return db_service.add_daily_task(title, description, category, points)

def get_daily_tasks(category=None):
    """获取每日任务"""
    tasks = db_service.get_daily_tasks(category)
    for task in tasks:
        task['title'] = task['content']  # 适配字段名
        task['difficulty'] = task.get('difficulty', 1)
    return tasks

def get_task_by_id(task_id):
    """根据ID获取任务"""
    task = db_service.get_task_by_id(task_id)
    if task:
        task['title'] = task['content']  # 适配字段名
        task['difficulty'] = task.get('difficulty', 1)
    return task

def assign_task_to_user(device_id, task_id):
    """分配任务给用户"""
    return db_service.assign_task_to_user(device_id, task_id)

def get_user_tasks(device_id, status=None):
    """获取用户的任务"""
    tasks = db_service.get_user_tasks(device_id, status)
    formatted_tasks = []
    for task in tasks:
        formatted_task = {
            'id': task['id'],
            'task_id': task.get('task_id', None),
            'status': task['status'],
            'completed_at': task['completed_at'],
            'created_at': task.get('created_at', None),
            'task': {
                'id': task['id'],
                'title': task['content'],
                'description': task['description'],
                'category': task['category'],
                'difficulty': task.get('difficulty', 1),
                'points': task['points']
            }
        }
        formatted_tasks.append(formatted_task)
    return formatted_tasks

def complete_task(user_task_id):
    """完成任务"""
    db_service.complete_task(user_task_id)

def get_user_points(device_id):
    """获取用户积分"""
    return db_service.get_user_points(device_id)

def init_daily_tasks():
    """初始化每日任务"""
    db_service.init_daily_tasks()

# 社区评论相关函数
def add_comment(device_id, nickname, content, user_id=None):
    """添加社区评论"""
    return db_service.add_comment(device_id, nickname, content)

def get_comments(limit=50):
    """获取社区评论"""
    comments = db_service.get_comments()[:limit]
    for comment in comments:
        comment['user_id'] = comment.get('user_id', None)
    return comments

# 留言相关函数
def get_messages(device_id=None):
    """获取留言列表"""
    return db_service.get_messages(device_id)

def add_message(device_id, content, author):
    """添加留言"""
    return db_service.add_message(device_id, content, author)

def like_message(message_id, device_id):
    """点赞留言"""
    return db_service.like_message(message_id, device_id)

# 道德知识库相关函数
def add_knowledge_article(title, content, category, author):
    """添加道德知识库文章"""
    return db_service.add_knowledge_article(title, content, category)

def get_knowledge_articles(category=None, limit=20):
    """获取道德知识库文章列表"""
    articles = db_service.get_knowledge_articles(category)[:limit]
    for article in articles:
        article['author'] = article.get('author', '管理员')
    return articles

def get_knowledge_article_by_id(article_id):
    """根据ID获取道德知识库文章"""
    article = db_service.get_knowledge_article_by_id(article_id)
    if article:
        article['author'] = article.get('author', '管理员')
    return article

def increment_knowledge_article_views(article_id):
    """增加道德知识库文章浏览量"""
    db_service.increment_knowledge_article_views(article_id)

def get_knowledge_categories():
    """获取道德知识库所有分类"""
    return db_service.get_knowledge_categories()

# 个性化推荐相关函数
def get_personalized_recommendations(device_id, scores):
    """根据用户测试结果生成个性化推荐"""
    recommendations = {
        'moral_challenges': [],
        'micro_actions': [],
        'knowledge_articles': []
    }
    
    # 根据得分生成道德挑战推荐
    if scores[0] < 40:  # 低正义感
        recommendations['moral_challenges'].append({
            'title': '勇敢发声',
            'description': '当你看到不公平时，尝试勇敢地站出来发声，即使可能会面临压力',
            'difficulty': 3,
            'points': 30
        })
    elif scores[0] > 80:  # 高正义感
        recommendations['moral_challenges'].append({
            'title': '理解他人',
            'description': '尝试理解那些你认为不正义的人的立场，寻找共同点',
            'difficulty': 2,
            'points': 25
        })
    
    if scores[1] < 40:  # 低利他主义
        recommendations['moral_challenges'].append({
            'title': '微小善意',
            'description': '每天做一件微小的善事，如给陌生人微笑、帮助他人开门等',
            'difficulty': 1,
            'points': 15
        })
    elif scores[1] > 80:  # 高利他主义
        recommendations['moral_challenges'].append({
            'title': '自我关怀',
            'description': '在帮助他人的同时，也要学会照顾自己的需求，避免 burnout',
            'difficulty': 2,
            'points': 20
        })
    
    if scores[2] < 40:  # 低规则遵从
        recommendations['moral_challenges'].append({
            'title': '规则意识',
            'description': '尝试严格遵守一天的所有规则，观察自己的感受',
            'difficulty': 2,
            'points': 20
        })
    elif scores[2] > 80:  # 高规则遵从
        recommendations['moral_challenges'].append({
            'title': '灵活变通',
            'description': '在适当的情况下，尝试打破规则，为了更高的价值',
            'difficulty': 3,
            'points': 25
        })
    
    if scores[3] < 40:  # 低共情力
        recommendations['moral_challenges'].append({
            'title': '倾听练习',
            'description': '认真倾听一个人的故事，不打断，不评判',
            'difficulty': 2,
            'points': 20
        })
    elif scores[3] > 80:  # 高共情力
        recommendations['moral_challenges'].append({
            'title': '情感边界',
            'description': '学习设定情感边界，避免过度吸收他人的情绪',
            'difficulty': 2,
            'points': 20
        })
    
    if scores[4] < 40:  # 低功利倾向
        recommendations['moral_challenges'].append({
            'title': '结果思考',
            'description': '在做决策时，尝试分析不同选择的长期结果',
            'difficulty': 2,
            'points': 20
        })
    elif scores[4] > 80:  # 高功利倾向
        recommendations['moral_challenges'].append({
            'title': '过程价值',
            'description': '尝试享受过程本身的价值，而不仅仅关注结果',
            'difficulty': 2,
            'points': 20
        })
    
    if scores[5] < 40:  # 低惩罚欲
        recommendations['moral_challenges'].append({
            'title': '责任意识',
            'description': '当他人犯错时，尝试帮助他们承担责任，而不是简单原谅',
            'difficulty': 2,
            'points': 20
        })
    elif scores[5] > 80:  # 高惩罚欲
        recommendations['moral_challenges'].append({
            'title': '宽恕练习',
            'description': '尝试宽恕一个曾经伤害过你的人，释放内心的愤怒',
            'difficulty': 3,
            'points': 30
        })
    
    # 推荐每日微行动
    tasks = get_daily_tasks()
    # 根据得分选择最适合的任务
    if scores[0] > 60:  # 高正义感
        recommendations['micro_actions'].extend([t for t in tasks if t['category'] == 'justice'][:2])
    if scores[1] > 60:  # 高利他主义
        recommendations['micro_actions'].extend([t for t in tasks if t['category'] == 'altruism'][:2])
    if scores[3] > 60:  # 高共情力
        recommendations['micro_actions'].extend([t for t in tasks if t['category'] == 'empathy'][:2])
    
    # 推荐知识库文章
    articles = get_knowledge_articles(limit=10)
    # 根据得分选择相关文章
    if scores[0] > 70:  # 高正义感
        recommendations['knowledge_articles'].extend([a for a in articles if '正义' in a['category'] or '公正' in a['category']][:3])
    if scores[1] > 70:  # 高利他主义
        recommendations['knowledge_articles'].extend([a for a in articles if '利他' in a['category'] or '慈善' in a['category']][:3])
    if scores[3] > 70:  # 高共情力
        recommendations['knowledge_articles'].extend([a for a in articles if '共情' in a['category'] or '情感' in a['category']][:3])
    
    return recommendations