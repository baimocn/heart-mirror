from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from models import init_db, get_stats, increment_participant, add_donation, get_donation_list, add_user, get_user_by_username, get_user_by_email, verify_password, add_question_stat, increment_question_stat, add_option_stat, get_question_stats, get_option_stats, get_admin_stats, get_test_history, add_donation_flow, get_donation_flows, get_donation_flow_by_id, update_donation_flow, delete_donation_flow, add_donation_batch, get_donation_batches, get_donation_batch_by_id, update_donation_batch, delete_donation_batch, update_batch_total_amount, add_time_capsule, get_time_capsules, delete_time_capsule, add_moral_dilemma, get_moral_dilemmas, get_moral_dilemma_by_id, update_moral_dilemma_votes, delete_moral_dilemma, add_daily_task, get_daily_tasks, get_task_by_id, assign_task_to_user, get_user_tasks, complete_task, get_user_points, init_daily_tasks, add_comment, get_comments, add_knowledge_article, get_knowledge_articles, get_knowledge_article_by_id, increment_knowledge_article_views, get_knowledge_categories, get_personalized_recommendations
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

app = Flask(__name__)
CORS(app)

# JWT配置
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
    seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 7200))
)
jwt = JWTManager(app)

# 数据库连接
DB_PATH = os.environ.get('DB_PATH', 'database/heart_mirror.db')

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

# 模拟 AI 回响：根据题目和选项内容，组合模板生成
def mock_ai_reflection(question_text, option_text, user_context=None):
    # 提取关键词
    keywords = []
    if "揭发" in option_text or "举报" in option_text:
        keywords.append("勇气")
        templates = [
            "你选择了直面冲突。有没有想过，对方可能会因此记恨你？但正义从不许诺安全。",
            "勇敢的一步。有时真相需要代价，你愿意承受吗？",
            "你的内心有一团火。它温暖你，也可能灼伤靠近的人。"
        ]
    elif "沉默" in option_text or "当作没看见" in option_text:
        keywords.append("隐忍")
        templates = [
            "沉默有时是金，有时是锈。你听见内心那个微弱的声音了吗？",
            "你保护了自己，但那份不安会停留多久？",
            "不是所有战场都要冲锋，但退让之后，你会如何定义自己？"
        ]
    elif "牺牲" in question_text and "救" in option_text:
        keywords.append("牺牲")
        templates = [
            "你愿意为他人承受损失。这份善意是否也会让你疲惫？",
            "在救人与自救之间，你找到了自己的平衡点。",
            "这种选择很重。请记得，你的生命同样珍贵。"
        ]
    else:
        templates = [
            "这个选择背后，藏着怎样的故事？",
            "如果时间倒流，你还会这样选吗？",
            "有趣。你的道德罗盘指向了一个独特的方向。"
        ]
    return random.choice(templates)

# 初始化数据库
init_db()
# 初始化每日任务
init_daily_tasks()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questions', methods=['GET'])
def get_questions():
    # 使用绝对路径读取文件
    import os
    questions_file = os.path.join(os.path.dirname(__file__), 'static', 'questions.json')
    # 尝试使用utf-8-sig编码直接读取文件
    try:
        with open(questions_file, 'r', encoding='utf-8-sig') as f:
            questions_data = json.load(f)
    except Exception as e:
        # 如果失败，尝试其他编码
        try:
            with open(questions_file, 'r', encoding='gbk') as f:
                questions_data = json.load(f)
        except Exception as e:
            # 如果仍然失败，返回一个默认的问题列表
            questions_data = {
                "categories": ["justice", "altruism", "rule", "empathy", "utilitarian", "punish"],
                "questions": [
                    {
                        "id": 1,
                        "category": "altruism",
                        "text": "周五下午6点，你赶着去接发烧的女儿放学。路上看到一位老人在雨中摔倒了，周围没人。你停车帮忙的话，女儿要多等30分钟。你会？",
                        "mood": "self_sacrifice",
                        "options": [
                            {
                                "text": "立刻停车，扶起老人并叫救护车，然后通知妻子去接女儿。",
                                "icon": "fa-hand-holding-heart",
                                "increments": {"justice": 1, "altruism": 2, "rule": 0, "empathy": 2, "utilitarian": -2, "punish": 0},
                                "reflection": "你选择了先照顾陌生人，哪怕家人会失望。",
                                "inner_voice": ["女儿会理解吗？", "你的心在颤抖，但行动没有犹豫。"],
                                "consequence": "⏰ 女儿多等30分钟，老人得到及时救助。",
                                "ai_trigger": True
                            },
                            {
                                "text": "先打电话给120，然后快速拍照留证，再去接女儿。",
                                "icon": "fa-phone",
                                "increments": {"justice": 1, "altruism": 1, "rule": 1, "empathy": 1, "utilitarian": 0, "punish": 0},
                                "reflection": "你尝试兼顾两头，但可能都不完美。",
                                "inner_voice": ["尽力了就好。"],
                                "consequence": "📞 老人被救护车接走，但你未亲自陪伴。女儿等了20分钟。",
                                "ai_trigger": False
                            },
                            {
                                "text": "装作没看见，直接去接女儿，但事后会内疚很久。",
                                "icon": "fa-eye-slash",
                                "increments": {"justice": -1, "altruism": -2, "rule": -1, "empathy": -2, "utilitarian": 2, "punish": -1},
                                "reflection": "你选择了家庭优先，但良心不安。",
                                "inner_voice": ["你保护了女儿，却失去了自己的平静。"],
                                "consequence": "👧 女儿准时接到，但你整晚失眠。",
                                "ai_trigger": True
                            }
                        ]
                    }
                ]
            }
    print(f"Loaded {len(questions_data.get('questions', []))} questions")
    response = jsonify(questions_data)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        device_id = data.get('device_id')
        scores = data.get('scores', [])        # list of 6 floats
        title = data.get('title', '')
        answers_detail = data.get('answers', [])  # [{q_id, selected_idx, duration, switches}]
        patterns = data.get('patterns', [])       # 检测到的模式列表
        
        # 验证必要的字段
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
        
        # 使用绝对路径连接数据库
        db_path = os.path.join(app.root_path, 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 更新统计
        c.execute('UPDATE stats SET participants = participants+1, donation = donation+0.01 WHERE id=1')
        
        # 获取fingerprint
        fingerprint = data.get('fingerprint', '')
        
        # 插入历史
        c.execute('INSERT INTO test_history (device_id, fingerprint, scores_json, title, answers_json, patterns_json) VALUES (?,?,?,?,?,?)',
                  (device_id, fingerprint, json.dumps(scores), title, json.dumps(answers_detail), json.dumps(patterns)))
        
        # 检查并创建global_norms表
        c.execute('''CREATE TABLE IF NOT EXISTS global_norms (
            id INTEGER PRIMARY KEY CHECK (id=1),
            total_users INTEGER DEFAULT 0,
            sum_justice REAL DEFAULT 0,
            sum_altruism REAL DEFAULT 0,
            sum_rule REAL DEFAULT 0,
            sum_empathy REAL DEFAULT 0,
            sum_utilitarian REAL DEFAULT 0,
            sum_punish REAL DEFAULT 0
        )''')
        
        # 插入默认记录
        c.execute('INSERT OR IGNORE INTO global_norms (id) VALUES (1)')
        
        # 更新global_norms
        if len(scores) == 6:
            c.execute('''UPDATE global_norms SET 
                total_users = total_users + 1,
                sum_justice = sum_justice + ?,
                sum_altruism = sum_altruism + ?,
                sum_rule = sum_rule + ?,
                sum_empathy = sum_empathy + ?,
                sum_utilitarian = sum_utilitarian + ?,
                sum_punish = sum_punish + ?
                WHERE id = 1''', scores)
        
        conn.commit()
        conn.close()
        return jsonify({'ok': True})
    except Exception as e:
        print(f"Error in submit: {e}")
        return jsonify({'error': '提交失败，请稍后重试'}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify(get_stats())

@app.route('/api/donations', methods=['GET'])
def donations():
    return jsonify(get_donation_list())

@app.route('/api/donate', methods=['POST'])
def donate():
    """模拟捐款：直接确认，更新总额"""
    data = request.json
    device_id = data.get('device_id', '')
    nickname = data.get('nickname', '匿名用户')
    amount = float(data.get('amount', 1.0))
    if amount <= 0:
        return jsonify({'error': '金额必须大于0'}), 400
    add_donation(device_id, amount, nickname, status='confirmed')
    return jsonify({'status': 'ok', 'message': '感谢您的善意！'})

@app.route('/api/norms', methods=['GET'])
def get_norms():
    """获取群体平均数据"""
    conn = sqlite3.connect('database/heart_mirror.db')
    c = conn.cursor()
    c.execute('''SELECT total_users, sum_justice, sum_altruism, sum_rule, sum_empathy, sum_utilitarian, sum_punish 
                FROM global_norms WHERE id=1''')
    row = c.fetchone()
    conn.close()
    
    if not row or row[0] == 0:
        return jsonify({'avg': [50, 50, 50, 50, 50, 50], 'count': 0})
    
    total = row[0]
    avg = [row[1]/total, row[2]/total, row[3]/total, row[4]/total, row[5]/total, row[6]/total]
    return jsonify({'avg': avg, 'count': total})

@app.route('/api/journal', methods=['POST', 'GET'])
def journal():
    device_id = request.args.get('device_id') if request.method == 'GET' else request.json.get('device_id')
    if request.method == 'POST':
        data = request.json
        conn = sqlite3.connect('database/heart_mirror.db')
        c = conn.cursor()
        c.execute('INSERT INTO moral_journal (device_id, result_snapshot, user_note) VALUES (?,?,?)',
                  (data['device_id'], data['snapshot'], data['note']))
        conn.commit()
        conn.close()
        return jsonify({'ok': True})
    else:
        conn = sqlite3.connect('database/heart_mirror.db')
        c = conn.cursor()
        rows = c.execute('SELECT result_snapshot, user_note, created_at FROM moral_journal WHERE device_id = ? ORDER BY created_at DESC', (device_id,)).fetchall()
        conn.close()
        return jsonify([{'snapshot': r[0], 'note': r[1], 'date': r[2]} for r in rows])

@app.route('/api/ai_reflection', methods=['POST'])
def ai_reflection():
    data = request.json
    question = data.get('question', '')
    option = data.get('option', '')
    # 可选：用户历史倾向摘要（用于个性化）
    user_tendency = data.get('user_tendency', '')
    
    # 使用模拟 AI（可替换为真实 API）
    reflection = mock_ai_reflection(question, option, user_tendency)
    return jsonify({'reflection': reflection})

# 生成详细报告
def generate_detailed_report(scores, title):
    # scores: list of 6 floats 0-100
    # 确定每个维度的档位 low/mid/high
    levels = []
    for s in scores:
        if s < 33: levels.append('low')
        elif s < 67: levels.append('mid')
        else: levels.append('high')
    
    dim_names = ['正义感', '利他主义', '规则遵从', '共情力', '功利倾向', '惩罚欲']
    
    # 1. 核心特质画像：根据主导维度生成
    dominant_idx = scores.index(max(scores))
    dominant = dim_names[dominant_idx]
    # 为每个维度提供多个描述选项
    dominant_desc = {
        '正义感': [
            '你心中有一把不偏不倚的尺，对错是你判断世界的首要标准。',
            '正义是你行事的指南针，你无法容忍任何形式的不公。',
            '你坚信每个人都应该得到公平对待，为此你愿意挺身而出。',
            '在你看来，维护正义是一种责任，而不仅仅是选择。'
        ],
        '利他主义': [
            '你的善意如同本能，总是不自觉地把他人的需求放在前面。',
            '你从帮助他人中获得快乐，利他对你来说是一种生活方式。',
            '你愿意为了他人的福祉牺牲自己的利益，这是你最珍贵的品质。',
            '在你眼中，每一个生命都值得被关怀，你总是伸出援手。'
        ],
        '规则遵从': [
            '秩序是你的安全绳，你相信规则能保护所有人。',
            '你尊重制度和传统，认为它们是社会稳定的基石。',
            '对规则的遵守让你感到安心，你相信这是对自己和他人的负责。',
            '你认为只有在有序的环境中，每个人才能最大限度地发挥潜能。'
        ],
        '共情力': [
            '你能轻易感受到他人的情绪，仿佛那些疼痛也发生在你身上。',
            '你的心灵如同海绵，能够吸收并理解他人的情感。',
            '你总是能够站在他人的角度思考问题，这让你成为绝佳的倾听者。',
            '对他人情绪的敏感度是你的天赋，你用它来建立深层的连接。'
        ],
        '功利倾向': [
            '你习惯计算得失，试图找到"最大多数人的最大幸福"。',
            '理性和效率是你的向导，你相信最优解往往来自冷静的分析。',
            '你擅长权衡利弊，能够做出对整体最有利的决策。',
            '在你看来，道德选择应该基于实际结果，而非纯粹的理想。'
        ],
        '惩罚欲': [
            '你相信恶必须付出代价，否则正义就成了空话。',
            '你认为对错误行为的惩罚是维护社会秩序的必要手段。',
            '你无法容忍逃避责任的行为，坚持让每个人为自己的选择负责。',
            '在你看来，适当的惩罚是对受害者的尊重，也是对恶行的警示。'
        ]
    }
    core_trait = f"你的核心驱动力是「{dominant}」。{random.choice(dominant_desc[dominant])}"
    
    # 补充次要维度影响
    second_idx = scores.index(sorted(scores)[-2])
    second = dim_names[second_idx]
    # 为次要维度提供不同的描述
    second_desc = [
        f"同时，你的「{second}」也相当突出，这让你在道德决策时多了一层考量。",
        f"此外，你在「{second}」方面的表现也很显著，这为你的人格增添了丰富的层次。",
        f"你的「{second}」特质与核心驱动力相互补充，形成了独特的道德视角。",
        f"值得注意的是，你的「{second}」也表现突出，这让你的道德判断更加全面。"
    ]
    core_trait += random.choice(second_desc)
    
    # 2. 道德优势（基于高分段维度）
    strengths = []
    strength_options = {
        0: ["你敢于维护公平，即使面对压力也不退缩。", "你是正义的守护者，从不畏惧站出来发声。", "你具有强烈的道德勇气，能够在困境中坚持正确的选择。"],
        1: ["你乐于助人，常常成为朋友的精神依靠。", "你的善意如阳光般温暖，照亮周围的人。", "你总是愿意分享自己的资源和时间，帮助那些需要帮助的人。"],
        2: ["你做事可靠，遵守承诺，让人信赖。", "你是团队中最值得依靠的人，总是能够按计划完成任务。", "你的严谨和守时让你在任何环境中都备受尊重。"],
        3: ["你善解人意，能体察到他人未说出口的需求。", "你是天生的倾听者，能够给予他人真正的理解和支持。", "你的同理心让你能够与各种人建立深厚的连接。"],
        4: ["你理性务实，能做出最有效的决策。", "你擅长分析复杂问题，找到最合理的解决方案。", "你的判断基于事实和逻辑，很少被情绪左右。"],
        5: ["你嫉恶如仇，是团队中天然的监督者。", "你对不公和欺骗零容忍，始终站在正义的一边。", "你的原则性让你成为道德底线的守护者。"]
    }
    for i, s in enumerate(scores):
        if s >= 70:
            strengths.extend(random.sample(strength_options[i], 2))  # 每个高分维度选择2个优势
    if not strengths:
        strengths = ["你善于平衡各方立场，不易走极端。", "你在复杂情境中仍能保持思考。", "你具有开放的心态，愿意考虑不同的观点。"]
    # 随机选择3个优势
    strengths = random.sample(strengths, min(3, len(strengths)))
    
    # 3. 成长盲点（基于低分段维度或高分维度过犹不及）
    blindspots = []
    # 低分段盲点
    low_blindspot_options = {
        0: ["有时可能对不公现象过于容忍，错失改变的机会。", "在面对权威时，你可能会选择沉默，而非站出来维护正义。"],
        1: ["容易优先考虑自己，可能被他人视为冷漠。", "你可能会在帮助他人和照顾自己之间感到矛盾。"],
        2: ["对规则不够敬畏，可能会无意中破坏秩序。", "你可能觉得规则限制了你的自由，有时会选择绕过它们。"],
        3: ["难以理解他人的情感，容易显得疏离。", "你可能会在情感表达上显得笨拙，难以与他人建立深层连接。"],
        4: ["可能过于理想化，忽略现实的代价。", "你可能会因为追求完美而错失实际可行的解决方案。"],
        5: ["倾向于原谅，但可能纵容恶意。", "你可能会因为过于宽容而让他人不断跨越你的边界。"]
    }
    # 高分段盲点
    high_blindspot_options = {
        0: ["过分追求正义会让你变得好斗，难以妥协。", "你可能会对他人的错误过于苛刻，缺乏宽容。"],
        1: ["过度付出可能导致自我消耗，甚至被人利用。", "你可能会忽略自己的需求，为了他人而牺牲过多。"],
        2: ["死守规则会丧失灵活性，让人感到刻板。", "你可能会因为过于坚持规则而忽视特殊情况的需要。"],
        3: ["过度共情会让你情绪透支，无法自拔。", "你可能会承担过多他人的情绪负担，影响自己的心理健康。"],
        4: ["过于功利可能让你忽视情感价值。", "你可能会因为过于关注结果而忽略过程中的人文关怀。"],
        5: ["惩罚欲过强会让你陷入报复循环。", "你可能会在惩罚他人的过程中失去对自己的控制。"]
    }
    for i, s in enumerate(scores):
        if s <= 30:
            blindspots.extend(random.sample(low_blindspot_options[i], 1))
        elif s > 85:
            blindspots.extend(random.sample(high_blindspot_options[i], 1))
    if not blindspots:
        blindspots = ["你的道德体系相对平衡，但可能缺乏鲜明的个人特色。", "注意在关键时刻不要犹豫不决。", "你可能需要更多地关注自己的内心需求，而不仅仅是外部标准。"]
    # 随机选择3个盲点
    blindspots = random.sample(blindspots, min(3, len(blindspots)))
    
    # 4. 在关系中的模样
    relationship_options = []
    if scores[3] > 70:  # 高共情
        relationship_options = [
            "在关系中，你总是第一个察觉对方情绪变化的人。你擅长倾听，给予温暖，但也容易因为过度在意他人而委屈自己。",
            "你是关系中的情感支柱，总是能够为他人提供安慰和支持。你的同理心让你成为最可靠的朋友。",
            "在亲密关系中，你注重情感的深度连接，愿意花时间理解对方的内心世界。你是一个充满爱心和耐心的伙伴。"
        ]
    elif scores[4] > 70:  # 高功利
        relationship_options = [
            "你在关系中注重实际价值，喜欢互相成就。你可能不太擅长浪漫，但绝对可靠。",
            "你是关系中的问题解决者，总是能够找到实际的方法来改善现状。你的理性让你成为困难时期的稳定力量。",
            "在关系中，你重视效率和成长，鼓励彼此成为更好的人。你相信健康的关系应该是相互促进的。"
        ]
    elif scores[0] > 70:  # 高正义
        relationship_options = [
            "你对朋友非常讲义气，但也会要求对方遵守你心中的道义。你的朋友知道你是那个会为他们出头的人。",
            "在关系中，你坚持公平和诚实，无法容忍欺骗和背叛。你的原则性让你成为值得信赖的伙伴。",
            "你是关系中的守护者，总是愿意为了保护自己所爱的人而站出来。你的勇气和正义感让你成为他人的依靠。"
        ]
    elif scores[1] > 70:  # 高利他
        relationship_options = [
            "在关系中，你总是优先考虑他人的需求，愿意为了对方的幸福而付出。你的无私让你成为最贴心的伙伴。",
            "你是关系中的给予者，总是能够发现他人的需要并主动提供帮助。你的善意让周围的人感到温暖。",
            "在亲密关系中，你注重共同成长和相互支持，愿意与对方分享生活的喜怒哀乐。"
        ]
    elif scores[2] > 70:  # 高规则
        relationship_options = [
            "在关系中，你重视承诺和责任，总是能够遵守自己的约定。你的可靠性让你成为最值得信任的伙伴。",
            "你是关系中的稳定剂，喜欢有计划和秩序的生活。你的组织能力让生活更加顺畅。",
            "在亲密关系中，你注重尊重和边界，相信健康的关系需要清晰的规则和相互的尊重。"
        ]
    elif scores[5] > 70:  # 高惩罚
        relationship_options = [
            "在关系中，你坚持原则和责任，对错误行为零容忍。你的正义感让你成为关系中的守护者。",
            "你是关系中的直言者，愿意指出问题并寻求解决。你的坦诚虽然有时尖锐，但总是出于善意。",
            "在亲密关系中，你重视诚实和 accountability，相信只有面对问题才能真正成长。"
        ]
    else:
        relationship_options = [
            "你是一个温和的伙伴，不喜冲突，愿意为了和谐而妥协。但有时也需要表达自己的真实想法。",
            "在关系中，你注重平衡和包容，能够适应不同的个性和风格。你的灵活性让你能够与各种人相处融洽。",
            "你是关系中的和平使者，总是能够找到中间地带，化解冲突。你的平和心态让周围的人感到安心。"
        ]
    relationship = random.choice(relationship_options)
    
    # 5. 适合的公益角色
    charity_role_options = []
    if scores[1] > 70:
        charity_role_options = ["直接服务型志愿者（如陪伴老人、支教）", "社区服务组织者", "人道主义援助工作者"]
    elif scores[4] > 70:
        charity_role_options = ["公益项目策划或资源整合者", "社会企业创业者", "公益战略顾问"]
    elif scores[0] > 70:
        charity_role_options = ["公益监督员或维权支持者", "法律志愿者", "社会公正倡导者"]
    elif scores[3] > 70:
        charity_role_options = ["心理咨询志愿者", "危机干预工作者", "情感支持热线接线员"]
    elif scores[2] > 70:
        charity_role_options = ["公益项目管理员", "志愿者协调员", "社区规范倡导者"]
    elif scores[5] > 70:
        charity_role_options = ["社会监督员", "公平贸易倡导者", "反歧视活动家"]
    else:
        charity_role_options = ["物资捐赠者或传播倡导者", "公益活动参与者", "社区志愿者"]
    charity_role = random.choice(charity_role_options)
    
    # 6. 寄语
    closing_options = [
        "你的每一次选择，都在塑造内心的模样。心镜不评判，只映照。愿你带着这份觉察，在真实世界中继续前行。",
        "道德不是固定的规则，而是内心的指南针。愿你在人生的旅途中，始终保持对善的追求。",
        "你的人格是独特的，你的选择是有意义的。愿你以自己的方式，为世界增添更多的光。",
        "道德成长是一生的旅程，每一步都值得珍惜。愿你在反思中不断成长，成为更好的自己。",
        "你的内心有一把属于自己的标尺，它指引着你走向真实的自我。愿你始终听从内心的声音。"
    ]
    closing = random.choice(closing_options)
    
    report = {
        "title": title,
        "core_trait": core_trait,
        "strengths": strengths,
        "blindspots": blindspots,
        "relationship": relationship,
        "charity_role": charity_role,
        "closing": closing
    }
    return report

@app.route('/api/detailed_report', methods=['POST'])
def detailed_report():
    data = request.json
    scores = data.get('scores')
    title = data.get('title')
    if not scores:
        return jsonify({'error': 'no scores'}), 400
    report = generate_detailed_report(scores, title)
    return jsonify(report)

@app.route('/api/cover_data')
def cover_data():
    # 箴言库
    quotes = [
        "你有多了解自己？—— 心镜照见真实的你。",
        "每一次选择，都是内心的一次投射。",
        "道德不是答案，而是一面镜子。",
        "你的选择，定义了你是谁。",
        "在困境中，你看见了怎样的自己？",
        "善良与正义，有时需要勇气。",
        "心镜不评判，只映照。"
    ]
    # 华丽配色方案（背景渐变色对）
    color_schemes = [
        {"bg_start": "#0f0c29", "bg_end": "#302b63", "glow": "#ffdde1"},
        {"bg_start": "#1a1a2e", "bg_end": "#16213e", "glow": "#e94560"},
        {"bg_start": "#2c3e50", "bg_end": "#3498db", "glow": "#f1c40f"},
        {"bg_start": "#0b032d", "bg_end": "#6b4e9e", "glow": "#ffb347"},
        {"bg_start": "#1e130c", "bg_end": "#9a8478", "glow": "#d4af37"}
    ]
    scheme = random.choice(color_schemes)
    return jsonify({
        "quote": random.choice(quotes),
        "bg_start": scheme["bg_start"],
        "bg_end": scheme["bg_end"],
        "glow_color": scheme["glow"]
    })

@app.route('/messages')
def messages():
    return render_template('messages.html')

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

@app.route('/api/history', methods=['GET'])
def get_history():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    history = get_test_history(device_id)
    return jsonify(history), 200

@app.route('/api/mirror_query', methods=['GET'])
def mirror_query():
    try:
        fingerprint = request.args.get('fingerprint')
        if not fingerprint:
            return jsonify({'error': 'fingerprint is required'}), 400
        
        # 使用绝对路径连接数据库
        db_path = os.path.join(app.root_path, 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT scores_json, title FROM test_history WHERE fingerprint=?', (fingerprint,))
        record = c.fetchone()
        conn.close()
        
        if not record:
            return jsonify({'error': '镜像编号不存在或无效'}), 404
        
        return jsonify({
            'fingerprint': fingerprint,
            'title': record[1],
            'scores': json.loads(record[0])
        })
    except Exception as e:
        print(f"Error in mirror_query: {e}")
        return jsonify({'error': '查询失败，请稍后重试'}), 500

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
    with open('static/questions.json', 'r', encoding='utf-8') as f:
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
    with open('static/questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    questions = questions_data['questions']
    
    if request.method == 'PUT':
        # 更新题目
        data = request.json
        for i, q in enumerate(questions):
            if q.get('id') == question_id:
                questions[i] = data
                # 保存到文件
                with open('static/questions.json', 'w', encoding='utf-8') as f:
                    json.dump(questions_data, f, ensure_ascii=False, indent=2)
                return jsonify({'message': '题目更新成功'}), 200
        return jsonify({'error': '题目不存在'}), 404
    elif request.method == 'DELETE':
        # 删除题目
        for i, q in enumerate(questions):
            if q.get('id') == question_id:
                questions.pop(i)
                # 保存到文件
                with open('static/questions.json', 'w', encoding='utf-8') as f:
                    json.dump(questions_data, f, ensure_ascii=False, indent=2)
                return jsonify({'message': '题目删除成功'}), 200
        return jsonify({'error': '题目不存在'}), 404

@app.route('/api/questions', methods=['POST'])
@admin_required
def add_question():
    data = request.json
    # 加载题目数据
    with open('static/questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    questions = questions_data['questions']
    # 生成新的题目ID
    new_id = max([q.get('id', 0) for q in questions]) + 1
    data['id'] = new_id
    questions.append(data)
    # 保存到文件
    with open('static/questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
    return jsonify({'message': '题目添加成功', 'id': new_id}), 201

# 善款流向相关路由
@app.route('/admin/flows')
@admin_required
def admin_flows():
    return render_template('admin_flows.html')

@app.route('/flows')
def flows():
    return render_template('flows.html')

# 善款批次相关路由
@app.route('/admin/batches')
@admin_required
def admin_batches():
    return render_template('admin_batches.html')

@app.route('/api/batches', methods=['GET'])
def donation_batches_get():
    batches = get_donation_batches()
    return jsonify(batches), 200

@app.route('/api/batches', methods=['POST'])
@admin_required
def donation_batches_post():
    data = request.json
    batch_id = data.get('batch_id')
    name = data.get('name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    description = data.get('description')
    images = json.dumps(data.get('images', []))
    
    batch_id = add_donation_batch(batch_id, name, start_date, end_date, description, images)
    return jsonify({'message': '善款批次添加成功', 'id': batch_id}), 201

@app.route('/api/batches/<string:batch_id>', methods=['GET'])
def donation_batch_detail_get(batch_id):
    batch = get_donation_batch_by_id(batch_id)
    if batch:
        return jsonify(batch), 200
    return jsonify({'error': '批次不存在'}), 404

@app.route('/api/batches/<string:batch_id>', methods=['PUT', 'DELETE'])
@admin_required
def donation_batch_detail_modify(batch_id):
    if request.method == 'PUT':
        data = request.json
        name = data.get('name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        status = data.get('status')
        description = data.get('description')
        images = json.dumps(data.get('images', []))
        
        update_donation_batch(batch_id, name, start_date, end_date, status, description, images)
        return jsonify({'message': '善款批次更新成功'}), 200
    elif request.method == 'DELETE':
        delete_donation_batch(batch_id)
        return jsonify({'message': '善款批次删除成功'}), 200

@app.route('/api/batches/<string:batch_id>/update_amount')
@admin_required
def update_batch_amount(batch_id):
    update_batch_total_amount(batch_id)
    return jsonify({'message': '批次金额更新成功'}), 200

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

@app.route('/api/flows', methods=['GET'])
def donation_flows_get():
    flows = get_donation_flows()
    return jsonify(flows), 200

@app.route('/api/flows', methods=['POST'])
@admin_required
def donation_flows_post():
    data = request.json
    batch_id = data.get('batch_id')
    amount = data.get('amount')
    purpose = data.get('purpose')
    date = data.get('date')
    description = data.get('description')
    images = json.dumps(data.get('images', []))
    
    flow_id = add_donation_flow(batch_id, amount, purpose, date, description, images)
    return jsonify({'message': '善款流向记录添加成功', 'id': flow_id}), 201

@app.route('/api/flows/<int:flow_id>', methods=['GET'])
def donation_flow_detail_get(flow_id):
    flow = get_donation_flow_by_id(flow_id)
    if flow:
        return jsonify(flow), 200
    return jsonify({'error': '记录不存在'}), 404

@app.route('/api/flows/<int:flow_id>', methods=['PUT', 'DELETE'])
@admin_required
def donation_flow_detail_modify(flow_id):
    if request.method == 'PUT':
        data = request.json
        amount = data.get('amount')
        purpose = data.get('purpose')
        date = data.get('date')
        description = data.get('description')
        images = json.dumps(data.get('images', []))
        
        update_donation_flow(flow_id, amount, purpose, date, description, images)
        return jsonify({'message': '善款流向记录更新成功'}), 200
    elif request.method == 'DELETE':
        delete_donation_flow(flow_id)
        return jsonify({'message': '善款流向记录删除成功'}), 200

@app.route('/api/generate_story', methods=['POST'])
def generate_story():
    """生成公益故事"""
    data = request.json
    title = data.get('title', '道德守护者')
    amount = data.get('amount', 1.0)
    
    # 公益故事模板
    templates = [
        {
            'title': '温暖传递',
            'content': f'亲爱的{title}，您的{amount}元善款已经成为温暖的种子，在需要帮助的人心中生根发芽。每一分善意都在传递着希望，每一次付出都在点亮他人的生活。感谢您的善良，让世界变得更加美好。'
        },
        {
            'title': '爱心涟漪',
            'content': f'尊敬的{title}，您的{amount}元善款如同投入湖面的石子，激起了爱的涟漪。这份善意将帮助那些处于困境中的人们，让他们感受到社会的温暖。您的行动是对人性美好的最好诠释。'
        },
        {
            'title': '希望之光',
            'content': f'亲爱的{title}，您的{amount}元善款是黑暗中的一束光，为需要帮助的人带来了希望。您的善良不仅是物质上的支持，更是精神上的鼓励。感谢您用行动诠释了什么是真正的道德。'
        },
        {
            'title': '善的力量',
            'content': f'尊敬的{title}，您的{amount}元善款展现了善的力量。这份力量将帮助那些需要帮助的人，让他们感受到人间的温情。您的行动是对道德最好的实践，是对社会最美好的贡献。'
        },
        {
            'title': '爱的传递',
            'content': f'亲爱的{title}，您的{amount}元善款是爱的传递。这份爱将温暖那些需要帮助的人，让他们感受到社会的关怀。您的善良是社会的正能量，是我们学习的榜样。'
        }
    ]
    
    # 随机选择一个模板
    story = random.choice(templates)
    
    return jsonify(story), 200

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

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取留言列表"""
    # 这里可以从数据库获取留言，暂时返回空数组
    return jsonify({'messages': []}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)