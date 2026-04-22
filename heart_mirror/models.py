import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 使用绝对路径连接数据库
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 删除旧表（如果存在）
    c.execute('DROP TABLE IF EXISTS stats')
    # 统计表（只有一行记录）
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            participants INTEGER DEFAULT 0,
            donation REAL DEFAULT 0.0
        )
    ''')
    # 确保初始行存在
    c.execute('INSERT OR IGNORE INTO stats (id, participants, donation) VALUES (1, 0, 0.0)')

    # 捐款记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            nickname TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',   -- pending, confirmed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP
        )
    ''')
    
    # 测试历史表
    c.execute('''
        CREATE TABLE IF NOT EXISTS test_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            scores_json TEXT,
            title TEXT,
            answers_json TEXT,          -- 存储每道题的选项索引、耗时、切换次数
            patterns_json TEXT          -- 存储检测到的模式（如连续功利）
        )
    ''')
    
    # 道德日记表
    c.execute('''
        CREATE TABLE IF NOT EXISTS moral_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            result_snapshot TEXT,
            user_note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 群体规范表
    c.execute('''
        CREATE TABLE IF NOT EXISTS global_norms (
            id INTEGER PRIMARY KEY CHECK (id=1),
            total_users INTEGER DEFAULT 0,
            sum_justice REAL DEFAULT 0,
            sum_altruism REAL DEFAULT 0,
            sum_rule REAL DEFAULT 0,
            sum_empathy REAL DEFAULT 0,
            sum_utilitarian REAL DEFAULT 0,
            sum_punish REAL DEFAULT 0
        )
    ''')
    c.execute('INSERT OR IGNORE INTO global_norms (id) VALUES (1)')
    
    # 用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 题目统计表
    c.execute('''
        CREATE TABLE IF NOT EXISTS question_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            category TEXT,
            selected_count INTEGER DEFAULT 0,
            avg_duration REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 选项统计表
    c.execute('''
        CREATE TABLE IF NOT EXISTS option_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            option_index INTEGER,
            selected_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 善款批次表
    c.execute('''
        CREATE TABLE IF NOT EXISTS donation_batch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT UNIQUE,
            name TEXT,
            total_amount REAL DEFAULT 0,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'pending',
            description TEXT,
            images TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 时间胶囊表
    c.execute('''
        CREATE TABLE IF NOT EXISTS time_capsule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            title TEXT,
            scores_json TEXT,
            mood_tags TEXT,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reminder_date TEXT
        )
    ''')
    
    # 道德困惑墙表
    c.execute('''
        CREATE TABLE IF NOT EXISTS moral_dilemma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            content TEXT,
            options TEXT,
            votes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_anonymous INTEGER DEFAULT 1
        )
    ''')
    
    # 每日微行动表
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            category TEXT,
            difficulty INTEGER,
            points INTEGER
        )
    ''')
    
    # 用户任务记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            task_id INTEGER,
            status TEXT DEFAULT 'pending',
            completed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 用户积分表
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            points INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 善款流向表
    c.execute('''
        CREATE TABLE IF NOT EXISTS donation_flow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT,
            amount REAL,
            purpose TEXT,
            date TEXT,
            description TEXT,
            images TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES donation_batch(batch_id)
        )
    ''')
    
    # 社区评论表
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            user_id INTEGER,
            nickname TEXT,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 道德知识库表
    c.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            category TEXT,
            author TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT participants, donation FROM stats WHERE id = 1')
    row = c.fetchone()
    conn.close()
    return {'participants': row[0], 'total_donation': round(row[1], 2)}

def increment_participant():
    """每次完成测试，参与人数+1，公益金额+0.01元"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE stats SET participants = participants + 1, donation = donation + 0.01 WHERE id = 1')
    conn.commit()
    conn.close()

def get_donation_list(limit=20):
    """获取已确认的善行榜"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT nickname, amount, confirmed_at FROM donations
        WHERE status = 'confirmed'
        ORDER BY confirmed_at DESC LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return [{'nickname': r[0], 'amount': r[1], 'time': r[2]} for r in rows]

def add_donation(device_id, amount, nickname, user_id=None, status='confirmed'):
    """添加捐款记录（演示模式直接确认）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO donations (device_id, user_id, nickname, amount, status, created_at, confirmed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (device_id, user_id, nickname, amount, status, now, now if status == 'confirmed' else None))
    # 同时更新总捐款额
    c.execute('UPDATE stats SET donation = donation + ? WHERE id = 1', (amount,))
    conn.commit()
    conn.close()

def add_user(username, email, password):
    """添加用户"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    password_hash = generate_password_hash(password)
    c.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    ''', (username, email, password_hash))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_username(username):
    """根据用户名获取用户"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4]}
    return None

def get_user_by_email(email):
    """根据邮箱获取用户"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4]}
    return None

def verify_password(password_hash, password):
    """验证密码"""
    return check_password_hash(password_hash, password)

def add_question_stat(question_id, category):
    """添加题目统计记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO question_stats (question_id, category)
        VALUES (?, ?)
    ''', (question_id, category))
    conn.commit()
    conn.close()

def increment_question_stat(question_id, duration):
    """增加题目统计"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 先获取当前统计
    c.execute('SELECT selected_count, avg_duration FROM question_stats WHERE question_id = ?', (question_id,))
    row = c.fetchone()
    if row:
        new_count = row[0] + 1
        new_avg = (row[1] * row[0] + duration) / new_count
        c.execute('UPDATE question_stats SET selected_count = ?, avg_duration = ? WHERE question_id = ?',
                  (new_count, new_avg, question_id))
    conn.commit()
    conn.close()

def add_option_stat(question_id, option_index):
    """增加选项统计"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO option_stats (question_id, option_index)
        VALUES (?, ?)
    ''', (question_id, option_index))
    c.execute('UPDATE option_stats SET selected_count = selected_count + 1 WHERE question_id = ? AND option_index = ?',
              (question_id, option_index))
    conn.commit()
    conn.close()

def get_question_stats():
    """获取题目统计"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM question_stats ORDER BY selected_count DESC')
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'question_id': r[1], 'category': r[2], 'selected_count': r[3], 'avg_duration': r[4], 'created_at': r[5]} for r in rows]

def get_option_stats(question_id):
    """获取选项统计"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM option_stats WHERE question_id = ? ORDER BY option_index', (question_id,))
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'question_id': r[1], 'option_index': r[2], 'selected_count': r[3], 'created_at': r[4]} for r in rows]

def get_admin_stats():
    """获取管理员统计数据"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 今日参与人数
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(*) FROM test_history WHERE timestamp LIKE ?', (today + '%',))
    today_participants = c.fetchone()[0]
    # 本周参与人数
    c.execute('SELECT COUNT(*) FROM test_history WHERE timestamp >= date(now, -7 days)')
    week_participants = c.fetchone()[0]
    # 今日捐款总额
    c.execute('SELECT SUM(amount) FROM donations WHERE created_at LIKE ? AND status = "confirmed"', (today + '%',))
    today_donation = c.fetchone()[0] or 0
    # 本周捐款总额
    c.execute('SELECT SUM(amount) FROM donations WHERE created_at >= date(now, -7 days) AND status = "confirmed"')
    week_donation = c.fetchone()[0] or 0
    # 平均测试完成率 (假设完成的测试)
    c.execute('SELECT COUNT(*) FROM test_history')
    total_tests = c.fetchone()[0]
    # 最受欢迎的题目
    c.execute('SELECT question_id, selected_count FROM question_stats ORDER BY selected_count DESC LIMIT 5')
    popular_questions = c.fetchall()
    # 捐款转化率
    c.execute('SELECT COUNT(*) FROM test_history')
    total_tests = c.fetchone()[0]
    c.execute('SELECT COUNT(DISTINCT device_id) FROM donations WHERE status = "confirmed"')
    unique_donors = c.fetchone()[0]
    conversion_rate = (unique_donors / total_tests * 100) if total_tests > 0 else 0
    conn.close()
    return {
        'today_participants': today_participants,
        'week_participants': week_participants,
        'today_donation': today_donation,
        'week_donation': week_donation,
        'popular_questions': popular_questions,
        'conversion_rate': conversion_rate
    }

def get_test_history(device_id):
    """获取用户的测试历史记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT timestamp, scores_json, title FROM test_history WHERE device_id = ? ORDER BY timestamp DESC', (device_id,))
    rows = c.fetchall()
    conn.close()
    history = []
    for row in rows:
        history.append({
            'timestamp': row[0],
            'scores': json.loads(row[1]) if row[1] else [],
            'title': row[2]
        })
    return history

def add_donation_flow(batch_id, amount, purpose, date, description, images):
    """添加善款流向记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO donation_flow (batch_id, amount, purpose, date, description, images)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (batch_id, amount, purpose, date, description, images))
    flow_id = c.lastrowid
    conn.commit()
    conn.close()
    return flow_id

def get_donation_flows():
    """获取所有善款流向记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM donation_flow ORDER BY date DESC')
    rows = c.fetchall()
    conn.close()
    flows = []
    for row in rows:
        flows.append({
            'id': row[0],
            'batch_id': row[1],
            'amount': row[2],
            'purpose': row[3],
            'date': row[4],
            'description': row[5],
            'images': json.loads(row[6]) if row[6] else [],
            'created_at': row[7]
        })
    return flows

def get_donation_flow_by_id(flow_id):
    """根据ID获取善款流向记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM donation_flow WHERE id = ?', (flow_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'batch_id': row[1],
            'amount': row[2],
            'purpose': row[3],
            'date': row[4],
            'description': row[5],
            'images': json.loads(row[6]) if row[6] else [],
            'created_at': row[7]
        }
    return None

def update_donation_flow(flow_id, amount, purpose, date, description, images):
    """更新善款流向记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE donation_flow
        SET amount = ?, purpose = ?, date = ?, description = ?, images = ?
        WHERE id = ?
    ''', (amount, purpose, date, description, images, flow_id))
    conn.commit()
    conn.close()

def delete_donation_flow(flow_id):
    """删除善款流向记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM donation_flow WHERE id = ?', (flow_id,))
    conn.commit()
    conn.close()

def add_donation_batch(batch_id, name, start_date, end_date, description, images):
    """添加善款批次"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO donation_batch (batch_id, name, start_date, end_date, description, images)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (batch_id, name, start_date, end_date, description, images))
    batch_id = c.lastrowid
    conn.commit()
    conn.close()
    return batch_id

def get_donation_batches():
    """获取所有善款批次"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM donation_batch ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    batches = []
    for row in rows:
        batches.append({
            'id': row[0],
            'batch_id': row[1],
            'name': row[2],
            'total_amount': row[3],
            'start_date': row[4],
            'end_date': row[5],
            'status': row[6],
            'description': row[7],
            'images': json.loads(row[8]) if row[8] else [],
            'created_at': row[9]
        })
    return batches

def get_donation_batch_by_id(batch_id):
    """根据ID获取善款批次"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM donation_batch WHERE batch_id = ?', (batch_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'batch_id': row[1],
            'name': row[2],
            'total_amount': row[3],
            'start_date': row[4],
            'end_date': row[5],
            'status': row[6],
            'description': row[7],
            'images': json.loads(row[8]) if row[8] else [],
            'created_at': row[9]
        }
    return None

def update_donation_batch(batch_id, name, start_date, end_date, status, description, images):
    """更新善款批次"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE donation_batch
        SET name = ?, start_date = ?, end_date = ?, status = ?, description = ?, images = ?
        WHERE batch_id = ?
    ''', (name, start_date, end_date, status, description, images, batch_id))
    conn.commit()
    conn.close()

def delete_donation_batch(batch_id):
    """删除善款批次"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM donation_batch WHERE batch_id = ?', (batch_id,))
    conn.commit()
    conn.close()

def update_batch_total_amount(batch_id):
    """更新批次总金额"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 计算批次总金额
    c.execute('SELECT SUM(amount) FROM donation_flow WHERE batch_id = ?', (batch_id,))
    total = c.fetchone()[0] or 0
    # 更新批次总金额
    c.execute('UPDATE donation_batch SET total_amount = ? WHERE batch_id = ?', (total, batch_id))
    conn.commit()
    conn.close()

def add_time_capsule(device_id, title, scores_json, mood_tags, email):
    """添加时间胶囊"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 计算一年后的提醒日期
    import datetime
    reminder_date = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    c.execute('''
        INSERT INTO time_capsule (device_id, title, scores_json, mood_tags, email, reminder_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (device_id, title, scores_json, mood_tags, email, reminder_date))
    capsule_id = c.lastrowid
    conn.commit()
    conn.close()
    return capsule_id

def get_time_capsules(device_id):
    """获取用户的时间胶囊"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM time_capsule WHERE device_id = ? ORDER BY created_at DESC', (device_id,))
    rows = c.fetchall()
    conn.close()
    capsules = []
    for row in rows:
        capsules.append({
            'id': row[0],
            'device_id': row[1],
            'user_id': row[2],
            'title': row[3],
            'scores': json.loads(row[4]) if row[4] else [],
            'mood_tags': json.loads(row[5]) if row[5] else [],
            'email': row[6],
            'created_at': row[7],
            'reminder_date': row[8]
        })
    return capsules

def delete_time_capsule(capsule_id):
    """删除时间胶囊"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM time_capsule WHERE id = ?', (capsule_id,))
    conn.commit()
    conn.close()

def add_moral_dilemma(device_id, content, options, is_anonymous=1):
    """添加道德困惑"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 初始化投票数据
    votes = {}
    for i in range(len(options)):
        votes[str(i)] = 0
    c.execute('''
        INSERT INTO moral_dilemma (device_id, content, options, votes, is_anonymous)
        VALUES (?, ?, ?, ?, ?)
    ''', (device_id, content, json.dumps(options), json.dumps(votes), is_anonymous))
    dilemma_id = c.lastrowid
    conn.commit()
    conn.close()
    return dilemma_id

def get_moral_dilemmas():
    """获取所有道德困惑"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM moral_dilemma ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    dilemmas = []
    for row in rows:
        dilemmas.append({
            'id': row[0],
            'device_id': row[1],
            'user_id': row[2],
            'content': row[3],
            'options': json.loads(row[4]) if row[4] else [],
            'votes': json.loads(row[5]) if row[5] else {},
            'created_at': row[6],
            'is_anonymous': row[7]
        })
    return dilemmas

def get_moral_dilemma_by_id(dilemma_id):
    """根据ID获取道德困惑"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM moral_dilemma WHERE id = ?', (dilemma_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'device_id': row[1],
            'user_id': row[2],
            'content': row[3],
            'options': json.loads(row[4]) if row[4] else [],
            'votes': json.loads(row[5]) if row[5] else {},
            'created_at': row[6],
            'is_anonymous': row[7]
        }
    return None

def update_moral_dilemma_votes(dilemma_id, option_index):
    """更新道德困惑投票"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 获取当前投票数据
    c.execute('SELECT votes FROM moral_dilemma WHERE id = ?', (dilemma_id,))
    row = c.fetchone()
    if row:
        votes = json.loads(row[0]) if row[0] else {}
        # 增加投票
        if str(option_index) in votes:
            votes[str(option_index)] += 1
        else:
            votes[str(option_index)] = 1
        # 更新投票数据
        c.execute('UPDATE moral_dilemma SET votes = ? WHERE id = ?', (json.dumps(votes), dilemma_id))
        conn.commit()
    conn.close()

def delete_moral_dilemma(dilemma_id):
    """删除道德困惑"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM moral_dilemma WHERE id = ?', (dilemma_id,))
    conn.commit()
    conn.close()

def add_daily_task(title, description, category, difficulty, points):
    """添加每日任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO daily_task (title, description, category, difficulty, points)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, category, difficulty, points))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_daily_tasks(category=None):
    """获取每日任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if category:
        c.execute('SELECT * FROM daily_task WHERE category = ?', (category,))
    else:
        c.execute('SELECT * FROM daily_task')
    rows = c.fetchall()
    conn.close()
    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'category': row[3],
            'difficulty': row[4],
            'points': row[5]
        })
    return tasks

def get_task_by_id(task_id):
    """根据ID获取任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM daily_task WHERE id = ?', (task_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'category': row[3],
            'difficulty': row[4],
            'points': row[5]
        }
    return None

def assign_task_to_user(device_id, task_id):
    """分配任务给用户"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO user_task (device_id, task_id, status)
        VALUES (?, ?, ?)
    ''', (device_id, task_id, 'pending'))
    user_task_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_task_id

def get_user_tasks(device_id, status=None):
    """获取用户的任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if status:
        c.execute('SELECT * FROM user_task WHERE device_id = ? AND status = ? ORDER BY created_at DESC', (device_id, status))
    else:
        c.execute('SELECT * FROM user_task WHERE device_id = ? ORDER BY created_at DESC', (device_id,))
    rows = c.fetchall()
    conn.close()
    tasks = []
    for row in rows:
        task = get_task_by_id(row[3])
        if task:
            tasks.append({
                'id': row[0],
                'task_id': row[3],
                'status': row[4],
                'completed_at': row[5],
                'created_at': row[6],
                'task': task
            })
    return tasks

def complete_task(user_task_id):
    """完成任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 获取任务信息
    c.execute('SELECT device_id, task_id FROM user_task WHERE id = ?', (user_task_id,))
    row = c.fetchone()
    if row:
        device_id, task_id = row
        # 更新任务状态
        c.execute('UPDATE user_task SET status = ?, completed_at = ? WHERE id = ?', ('completed', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_task_id))
        # 获取任务积分
        task = get_task_by_id(task_id)
        if task:
            # 更新用户积分
            c.execute('SELECT * FROM user_points WHERE device_id = ?', (device_id,))
            points_row = c.fetchone()
            if points_row:
                # 更新现有积分
                new_points = points_row[3] + task['points']
                c.execute('UPDATE user_points SET points = ?, last_updated = ? WHERE id = ?', (new_points, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), points_row[0]))
            else:
                # 创建新积分记录
                c.execute('INSERT INTO user_points (device_id, points) VALUES (?, ?)', (device_id, task['points']))
    conn.commit()
    conn.close()

def get_user_points(device_id):
    """获取用户积分"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM user_points WHERE device_id = ?', (device_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[3]
    return 0

def init_daily_tasks():
    """初始化每日任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 检查是否已有任务
    c.execute('SELECT COUNT(*) FROM daily_task')
    count = c.fetchone()[0]
    if count == 0:
        # 添加初始任务
        tasks = [
            {'title': '对陌生人微笑', 'description': '今天对至少3个陌生人微笑并问好', 'category': 'empathy', 'difficulty': 1, 'points': 10},
            {'title': '帮助他人', 'description': '今天帮助至少1个人，无论是小事情还是大事情', 'category': 'altruism', 'difficulty': 2, 'points': 15},
            {'title': '遵守规则', 'description': '今天严格遵守所有规则，包括交通规则、工作规则等', 'category': 'rule', 'difficulty': 2, 'points': 12},
            {'title': '反思自己', 'description': '今天花10分钟反思自己的行为，看看是否有需要改进的地方', 'category': 'justice', 'difficulty': 1, 'points': 8},
            {'title': '保护环境', 'description': '今天至少做一件保护环境的事情，比如垃圾分类、节约用水等', 'category': 'utilitarian', 'difficulty': 1, 'points': 10},
            {'title': '控制情绪', 'description': '今天遇到任何事情都保持冷静，不发脾气', 'category': 'punish', 'difficulty': 3, 'points': 20},
            {'title': '倾听他人', 'description': '今天认真倾听至少1个人的倾诉，不打断，不评判', 'category': 'empathy', 'difficulty': 2, 'points': 15},
            {'title': '分享快乐', 'description': '今天分享至少一件让你快乐的事情给他人', 'category': 'altruism', 'difficulty': 1, 'points': 10},
            {'title': '学习新知识', 'description': '今天学习至少一个新的道德知识或概念', 'category': 'justice', 'difficulty': 2, 'points': 12},
            {'title': '原谅他人', 'description': '今天原谅一个曾经伤害过你的人', 'category': 'punish', 'difficulty': 3, 'points': 25},
            {'title': '节约资源', 'description': '今天尽量节约资源，比如减少使用一次性物品、节约用电等', 'category': 'utilitarian', 'difficulty': 1, 'points': 8},
            {'title': '遵守承诺', 'description': '今天严格遵守所有承诺，不食言', 'category': 'rule', 'difficulty': 2, 'points': 15}
        ]
        for task in tasks:
            c.execute('''
                INSERT INTO daily_task (title, description, category, difficulty, points)
                VALUES (?, ?, ?, ?, ?)
            ''', (task['title'], task['description'], task['category'], task['difficulty'], task['points']))
        conn.commit()
    conn.close()

# 社区评论相关函数
def add_comment(device_id, nickname, content, user_id=None):
    """添加社区评论"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO comments (device_id, user_id, nickname, content)
        VALUES (?, ?, ?, ?)
    ''', (device_id, user_id, nickname, content))
    comment_id = c.lastrowid
    conn.commit()
    conn.close()
    return comment_id

def get_comments(limit=50):
    """获取社区评论"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, device_id, user_id, nickname, content, created_at FROM comments
        ORDER BY created_at DESC LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    comments = []
    for row in rows:
        comments.append({
            'id': row[0],
            'device_id': row[1],
            'user_id': row[2],
            'nickname': row[3],
            'content': row[4],
            'created_at': row[5]
        })
    return comments

# 道德知识库相关函数
def add_knowledge_article(title, content, category, author):
    """添加道德知识库文章"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO knowledge_base (title, content, category, author)
        VALUES (?, ?, ?, ?)
    ''', (title, content, category, author))
    article_id = c.lastrowid
    conn.commit()
    conn.close()
    return article_id

def get_knowledge_articles(category=None, limit=20):
    """获取道德知识库文章列表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if category:
        c.execute('''
            SELECT id, title, category, author, created_at, views FROM knowledge_base
            WHERE category = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (category, limit))
    else:
        c.execute('''
            SELECT id, title, category, author, created_at, views FROM knowledge_base
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
    rows = c.fetchall()
    conn.close()
    articles = []
    for row in rows:
        articles.append({
            'id': row[0],
            'title': row[1],
            'category': row[2],
            'author': row[3],
            'created_at': row[4],
            'views': row[5]
        })
    return articles

def get_knowledge_article_by_id(article_id):
    """根据ID获取道德知识库文章"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, title, content, category, author, created_at, views FROM knowledge_base
        WHERE id = ?
    ''', (article_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'category': row[3],
            'author': row[4],
            'created_at': row[5],
            'views': row[6]
        }
    return None

def increment_knowledge_article_views(article_id):
    """增加道德知识库文章浏览量"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE knowledge_base SET views = views + 1 WHERE id = ?
    ''', (article_id,))
    conn.commit()
    conn.close()

def get_knowledge_categories():
    """获取道德知识库所有分类"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT DISTINCT category FROM knowledge_base
    ''')
    rows = c.fetchall()
    conn.close()
    categories = []
    for row in rows:
        categories.append(row[0])
    return categories

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