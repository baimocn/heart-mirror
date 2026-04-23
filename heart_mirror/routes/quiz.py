from flask import request, jsonify
from models import get_stats, increment_participant, get_test_history
from app import app
import json
import os
import sqlite3
import random

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

@app.route('/api/questions', methods=['GET'])
def get_questions():
    # 使用绝对路径读取文件
    questions_file = os.path.join(os.path.dirname(__file__), '..', 'static', 'questions.json')
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
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 更新统计
        increment_participant()
        
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

@app.route('/api/history', methods=['GET'])
def get_history():
    device_id = request.args.get('device_id')
    user_id = request.args.get('user_id')
    
    if not device_id and not user_id:
        return jsonify({'error': 'device_id or user_id is required'}), 400
    
    history = get_test_history(device_id, user_id)
    return jsonify(history), 200

@app.route('/api/mirror_query', methods=['GET'])
def mirror_query():
    try:
        fingerprint = request.args.get('fingerprint')
        if not fingerprint:
            return jsonify({'error': 'fingerprint is required'}), 400
        
        # 使用绝对路径连接数据库
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
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
