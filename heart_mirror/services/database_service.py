import sqlite3
import os
import json
from datetime import datetime

# 使用绝对路径连接数据库
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')

class DatabaseService:
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """确保数据库目录存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """初始化数据库"""
        conn = self._get_connection()
        c = conn.cursor()
        
        # 统计表（只有一行记录）
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                participants INTEGER DEFAULT 0,
                donations INTEGER DEFAULT 0,
                total_donation_amount REAL DEFAULT 0,
                dilemma_posts INTEGER DEFAULT 0,
                task_completions INTEGER DEFAULT 0
            )
        ''')
        # 插入默认记录
        c.execute('INSERT OR IGNORE INTO stats (id) VALUES (1)')
        
        # 捐款表
        c.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                amount REAL,
                nickname TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 用户表
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 为users表添加account_number和device_id列（如果不存在）
        try:
            c.execute('ALTER TABLE users ADD COLUMN account_number TEXT')
        except sqlite3.OperationalError:
            pass  # 列已存在
        try:
            c.execute('ALTER TABLE users ADD COLUMN device_id TEXT')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        # 测试历史表
        c.execute('''
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                fingerprint TEXT,
                scores_json TEXT,
                title TEXT,
                answers_json TEXT,
                patterns_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 为test_history表添加user_id列（如果不存在）
        try:
            c.execute('ALTER TABLE test_history ADD COLUMN user_id INTEGER')
        except sqlite3.OperationalError:
            pass  # 列已存在
        

        
        # 时间胶囊表
        c.execute('''
            CREATE TABLE IF NOT EXISTS time_capsules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                title TEXT,
                scores_json TEXT,
                mood_tags TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 道德困惑表
        c.execute('''
            CREATE TABLE IF NOT EXISTS moral_dilemmas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                content TEXT,
                options TEXT,
                is_anonymous INTEGER DEFAULT 1,
                votes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 每日任务表
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                category TEXT,
                points INTEGER,
                description TEXT
            )
        ''')
        
        # 用户任务表
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                task_id INTEGER,
                status TEXT DEFAULT 'assigned',
                completed_at TIMESTAMP
            )
        ''')
        
        # 社区评论表
        c.execute('''
            CREATE TABLE IF NOT EXISTS community_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                nickname TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 留言表（善行回音壁）
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                content TEXT,
                author TEXT,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 留言点赞表
        c.execute('''
            CREATE TABLE IF NOT EXISTS message_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                device_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_id, device_id)
            )
        ''')
        
        # 善款流向表
        c.execute('''
            CREATE TABLE IF NOT EXISTS donation_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT,
                amount REAL,
                purpose TEXT,
                date TEXT,
                description TEXT,
                images TEXT
            )
        ''')
        
        # 善款批次表
        c.execute('''
            CREATE TABLE IF NOT EXISTS donation_batches (
                id TEXT PRIMARY KEY,
                name TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT 'active',
                total_amount REAL DEFAULT 0,
                description TEXT,
                images TEXT
            )
        ''')
        
        # 知识文章表
        c.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 用户表
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """获取统计数据"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT participants, donations, total_donation_amount, dilemma_posts, task_completions FROM stats WHERE id = 1')
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'participants': row[0],
                'donations': row[1],
                'total_donation_amount': row[2],
                'dilemma_posts': row[3],
                'task_completions': row[4]
            }
        return {
            'participants': 0,
            'donations': 0,
            'total_donation_amount': 0,
            'dilemma_posts': 0,
            'task_completions': 0
        }
    
    def increment_participant(self):
        """增加参与者计数"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE stats SET participants = participants + 1 WHERE id = 1')
        conn.commit()
        conn.close()
    
    def add_donation(self, device_id, amount, nickname, status='pending'):
        """添加捐款记录"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO donations (device_id, amount, nickname, status) VALUES (?, ?, ?, ?)',
                  (device_id, amount, nickname, status))
        if status == 'confirmed':
            c.execute('UPDATE stats SET donations = donations + 1, total_donation_amount = total_donation_amount + ? WHERE id = 1', (amount,))
        conn.commit()
        conn.close()
    
    def get_donation_list(self):
        """获取捐款列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, device_id, amount, nickname, status, created_at FROM donations ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'device_id': row[1],
            'amount': row[2],
            'nickname': row[3],
            'status': row[4],
            'created_at': row[5]
        } for row in rows]
    
    def add_user(self, username, email, password):
        """添加用户"""
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                  (username, email, password_hash))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, email, password_hash FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3]
            }
        return None
    
    def get_user_by_email(self, email):
        """根据邮箱获取用户"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, email, password_hash FROM users WHERE email = ?', (email,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3]
            }
        return None
    
    def verify_password(self, stored_password, provided_password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(stored_password, provided_password)
    
    def add_question_stat(self, question_id, option_index):
        """添加题目统计"""
        pass  # 未实现
    
    def increment_question_stat(self, question_id, option_index):
        """增加题目统计"""
        pass  # 未实现
    
    def add_option_stat(self, question_id, option_index):
        """添加选项统计"""
        pass  # 未实现
    
    def get_question_stats(self, question_id):
        """获取题目统计"""
        pass  # 未实现
    
    def get_option_stats(self, question_id, option_index):
        """获取选项统计"""
        pass  # 未实现
    
    def get_admin_stats(self):
        """获取管理员统计"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT participants, donations, total_donation_amount, dilemma_posts, task_completions FROM stats WHERE id = 1')
        stats_row = c.fetchone()
        
        c.execute('SELECT COUNT(*) FROM users')
        users_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM moral_dilemmas')
        dilemmas_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM knowledge_articles')
        articles_count = c.fetchone()[0]
        
        conn.close()
        
        if stats_row:
            return {
                'participants': stats_row[0],
                'donations': stats_row[1],
                'total_donation_amount': stats_row[2],
                'dilemma_posts': stats_row[3],
                'task_completions': stats_row[4],
                'users_count': users_count,
                'dilemmas_count': dilemmas_count,
                'articles_count': articles_count
            }
        return {
            'participants': 0,
            'donations': 0,
            'total_donation_amount': 0,
            'dilemma_posts': 0,
            'task_completions': 0,
            'users_count': 0,
            'dilemmas_count': 0,
            'articles_count': 0
        }
    
    def get_user_by_account(self, account_number):
        """根据账号数字获取用户"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, account_number, device_id, created_at FROM users WHERE account_number = ?', (account_number,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'account_number': row[1],
                'device_id': row[2],
                'created_at': row[3]
            }
        return None
    
    def create_user(self, account_number, device_id):
        """创建新用户"""
        conn = self._get_connection()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (account_number, device_id, username, email, password_hash) VALUES (?, ?, ?, ?, ?)', 
                      (account_number, device_id, account_number, f'{account_number}@example.com', ''))
            user_id = c.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            # 账号已存在
            return None
        finally:
            conn.close()
    
    def update_user_device_id(self, user_id, device_id):
        """更新用户设备ID"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE users SET device_id = ? WHERE id = ?', (device_id, user_id))
        conn.commit()
        conn.close()
    
    def get_test_history(self, device_id=None, user_id=None):
        """获取测试历史"""
        conn = self._get_connection()
        c = conn.cursor()
        
        if user_id:
            c.execute('SELECT id, scores_json, title, created_at FROM test_history WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        elif device_id:
            c.execute('SELECT id, scores_json, title, created_at FROM test_history WHERE device_id = ? ORDER BY created_at DESC', (device_id,))
        else:
            c.execute('SELECT id, scores_json, title, created_at FROM test_history ORDER BY created_at DESC')
        
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'scores': json.loads(row[1]),
            'title': row[2],
            'created_at': row[3]
        } for row in rows]
    
    def add_donation_flow(self, batch_id, amount, purpose, date, description, images):
        """添加善款流向"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO donation_flows (batch_id, amount, purpose, date, description, images) VALUES (?, ?, ?, ?, ?, ?)',
                  (batch_id, amount, purpose, date, description, images))
        flow_id = c.lastrowid
        conn.commit()
        conn.close()
        return flow_id
    
    def get_donation_flows(self):
        """获取善款流向列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, batch_id, amount, purpose, date, description, images FROM donation_flows ORDER BY id DESC')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'batch_id': row[1],
            'amount': row[2],
            'purpose': row[3],
            'date': row[4],
            'description': row[5],
            'images': json.loads(row[6]) if row[6] else []
        } for row in rows]
    
    def get_donation_flow_by_id(self, flow_id):
        """根据ID获取善款流向"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, batch_id, amount, purpose, date, description, images FROM donation_flows WHERE id = ?', (flow_id,))
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
                'images': json.loads(row[6]) if row[6] else []
            }
        return None
    
    def update_donation_flow(self, flow_id, amount, purpose, date, description, images):
        """更新善款流向"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE donation_flows SET amount = ?, purpose = ?, date = ?, description = ?, images = ? WHERE id = ?',
                  (amount, purpose, date, description, images, flow_id))
        conn.commit()
        conn.close()
    
    def delete_donation_flow(self, flow_id):
        """删除善款流向"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM donation_flows WHERE id = ?', (flow_id,))
        conn.commit()
        conn.close()
    
    def add_donation_batch(self, batch_id, name, start_date, end_date, description, images):
        """添加善款批次"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO donation_batches (id, name, start_date, end_date, description, images) VALUES (?, ?, ?, ?, ?, ?)',
                  (batch_id, name, start_date, end_date, description, images))
        conn.commit()
        conn.close()
        return batch_id
    
    def get_donation_batches(self):
        """获取善款批次列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, name, start_date, end_date, status, total_amount, description, images FROM donation_batches ORDER BY id DESC')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'name': row[1],
            'start_date': row[2],
            'end_date': row[3],
            'status': row[4],
            'total_amount': row[5],
            'description': row[6],
            'images': json.loads(row[7]) if row[7] else []
        } for row in rows]
    
    def get_donation_batch_by_id(self, batch_id):
        """根据ID获取善款批次"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, name, start_date, end_date, status, total_amount, description, images FROM donation_batches WHERE id = ?', (batch_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'status': row[4],
                'total_amount': row[5],
                'description': row[6],
                'images': json.loads(row[7]) if row[7] else []
            }
        return None
    
    def update_donation_batch(self, batch_id, name, start_date, end_date, status, description, images):
        """更新善款批次"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE donation_batches SET name = ?, start_date = ?, end_date = ?, status = ?, description = ?, images = ? WHERE id = ?',
                  (name, start_date, end_date, status, description, images, batch_id))
        conn.commit()
        conn.close()
    
    def delete_donation_batch(self, batch_id):
        """删除善款批次"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM donation_batches WHERE id = ?', (batch_id,))
        conn.commit()
        conn.close()
    
    def update_batch_total_amount(self, batch_id):
        """更新批次总金额"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM donations WHERE status = \'confirmed\'')
        total = c.fetchone()[0] or 0
        c.execute('UPDATE donation_batches SET total_amount = ? WHERE id = ?', (total, batch_id))
        conn.commit()
        conn.close()
    
    def add_time_capsule(self, device_id, title, scores_json, mood_tags, email):
        """添加时间胶囊"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO time_capsules (device_id, title, scores_json, mood_tags, email) VALUES (?, ?, ?, ?, ?)',
                  (device_id, title, scores_json, mood_tags, email))
        capsule_id = c.lastrowid
        conn.commit()
        conn.close()
        return capsule_id
    
    def get_time_capsules(self, device_id):
        """获取时间胶囊列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, title, scores_json, mood_tags, email, created_at FROM time_capsules WHERE device_id = ? ORDER BY created_at DESC', (device_id,))
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'title': row[1],
            'scores': json.loads(row[2]),
            'mood_tags': json.loads(row[3]),
            'email': row[4],
            'created_at': row[5]
        } for row in rows]
    
    def delete_time_capsule(self, capsule_id):
        """删除时间胶囊"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM time_capsules WHERE id = ?', (capsule_id,))
        conn.commit()
        conn.close()
    
    def add_moral_dilemma(self, device_id, content, options, is_anonymous):
        """添加道德困惑"""
        conn = self._get_connection()
        c = conn.cursor()
        # 初始化投票数组
        votes = json.dumps([0] * len(options))
        c.execute('INSERT INTO moral_dilemmas (device_id, content, options, is_anonymous, votes) VALUES (?, ?, ?, ?, ?)',
                  (device_id, content, json.dumps(options), is_anonymous, votes))
        dilemma_id = c.lastrowid
        c.execute('UPDATE stats SET dilemma_posts = dilemma_posts + 1 WHERE id = 1')
        conn.commit()
        conn.close()
        return dilemma_id
    
    def get_moral_dilemmas(self):
        """获取道德困惑列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, device_id, content, options, is_anonymous, votes, created_at FROM moral_dilemmas ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'device_id': row[1],
            'content': row[2],
            'options': json.loads(row[3]),
            'is_anonymous': row[4],
            'votes': json.loads(row[5]),
            'created_at': row[6]
        } for row in rows]
    
    def get_moral_dilemma_by_id(self, dilemma_id):
        """根据ID获取道德困惑"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, device_id, content, options, is_anonymous, votes, created_at FROM moral_dilemmas WHERE id = ?', (dilemma_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'device_id': row[1],
                'content': row[2],
                'options': json.loads(row[3]),
                'is_anonymous': row[4],
                'votes': json.loads(row[5]),
                'created_at': row[6]
            }
        return None
    
    def update_moral_dilemma_votes(self, dilemma_id, option_index):
        """更新道德困惑投票"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT votes FROM moral_dilemmas WHERE id = ?', (dilemma_id,))
        votes_str = c.fetchone()[0]
        votes = json.loads(votes_str)
        if 0 <= option_index < len(votes):
            votes[option_index] += 1
            c.execute('UPDATE moral_dilemmas SET votes = ? WHERE id = ?', (json.dumps(votes), dilemma_id))
            conn.commit()
        conn.close()
    
    def delete_moral_dilemma(self, dilemma_id):
        """删除道德困惑"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM moral_dilemmas WHERE id = ?', (dilemma_id,))
        conn.commit()
        conn.close()
    
    def add_daily_task(self, content, category, points, description):
        """添加每日任务"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO daily_tasks (content, category, points, description) VALUES (?, ?, ?, ?)',
                  (content, category, points, description))
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_daily_tasks(self, category=None):
        """获取每日任务列表"""
        conn = self._get_connection()
        c = conn.cursor()
        if category:
            c.execute('SELECT id, content, category, points, description FROM daily_tasks WHERE category = ?', (category,))
        else:
            c.execute('SELECT id, content, category, points, description FROM daily_tasks')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'content': row[1],
            'category': row[2],
            'points': row[3],
            'description': row[4]
        } for row in rows]
    
    def get_task_by_id(self, task_id):
        """根据ID获取任务"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, content, category, points, description FROM daily_tasks WHERE id = ?', (task_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'content': row[1],
                'category': row[2],
                'points': row[3],
                'description': row[4]
            }
        return None
    
    def assign_task_to_user(self, device_id, task_id):
        """分配任务给用户"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO user_tasks (device_id, task_id) VALUES (?, ?)', (device_id, task_id))
        user_task_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_task_id
    
    def get_user_tasks(self, device_id, status=None):
        """获取用户任务列表"""
        conn = self._get_connection()
        c = conn.cursor()
        if status:
            c.execute('SELECT ut.id, t.content, t.category, t.points, ut.status, ut.completed_at FROM user_tasks ut JOIN daily_tasks t ON ut.task_id = t.id WHERE ut.device_id = ? AND ut.status = ?', (device_id, status))
        else:
            c.execute('SELECT ut.id, t.content, t.category, t.points, ut.status, ut.completed_at FROM user_tasks ut JOIN daily_tasks t ON ut.task_id = t.id WHERE ut.device_id = ?', (device_id,))
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'content': row[1],
            'category': row[2],
            'points': row[3],
            'status': row[4],
            'completed_at': row[5]
        } for row in rows]
    
    def complete_task(self, user_task_id):
        """完成任务"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE user_tasks SET status = \'completed\', completed_at = CURRENT_TIMESTAMP WHERE id = ?', (user_task_id,))
        c.execute('UPDATE stats SET task_completions = task_completions + 1 WHERE id = 1')
        conn.commit()
        conn.close()
    
    def get_user_points(self, device_id):
        """获取用户积分"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT SUM(t.points) FROM user_tasks ut JOIN daily_tasks t ON ut.task_id = t.id WHERE ut.device_id = ? AND ut.status = \'completed\'', (device_id,))
        total = c.fetchone()[0] or 0
        conn.close()
        return total
    
    def init_daily_tasks(self):
        """初始化每日任务"""
        conn = self._get_connection()
        c = conn.cursor()
        # 检查是否已有任务
        c.execute('SELECT COUNT(*) FROM daily_tasks')
        if c.fetchone()[0] == 0:
            # 添加默认任务
            default_tasks = [
                ('今天对至少一个人说一声谢谢', 'gratitude', 5, '表达感谢是培养同理心的重要方式'),
                ('主动帮助一位需要帮助的人', 'altruism', 10, '小小的帮助可能会给他人带来巨大的改变'),
                ('今天反思一次自己的行为是否符合道德标准', 'self_reflection', 8, '自我反思是道德成长的关键'),
                ('阅读一篇关于道德哲学的文章', 'learning', 7, '知识是道德判断的基础'),
                ('今天尝试从他人的角度思考问题', 'empathy', 6, '理解他人是建立良好关系的前提'),
                ('为慈善事业捐款（哪怕是很小的金额）', 'charity', 12, '给予是最纯粹的善举'),
                ('今天避免说负面或伤人的话', 'kindness', 5, '语言的力量比我们想象的更大'),
                ('学习一项新的技能或知识', 'growth', 9, '个人成长也是道德成长的一部分'),
                ('今天花时间陪伴家人或朋友', 'relationships', 8, '良好的关系是幸福的基础'),
                ('做一件你一直想做但不敢做的正确的事', 'courage', 15, '勇气是道德行动的重要品质')
            ]
            c.executemany('INSERT INTO daily_tasks (content, category, points, description) VALUES (?, ?, ?, ?)', default_tasks)
            conn.commit()
        conn.close()
    
    def add_comment(self, device_id, nickname, content):
        """添加评论"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO community_comments (device_id, nickname, content) VALUES (?, ?, ?)',
                  (device_id, nickname, content))
        comment_id = c.lastrowid
        conn.commit()
        conn.close()
        return comment_id
    
    def get_comments(self):
        """获取评论列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, device_id, nickname, content, created_at FROM community_comments ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'device_id': row[1],
            'nickname': row[2],
            'content': row[3],
            'created_at': row[4]
        } for row in rows]
    
    def get_messages(self, device_id=None):
        """获取留言列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, device_id, content, author, likes, created_at FROM messages ORDER BY created_at DESC')
        rows = c.fetchall()
        
        # 获取用户的点赞记录
        liked_message_ids = set()
        if device_id:
            c.execute('SELECT message_id FROM message_likes WHERE device_id = ?', (device_id,))
            like_rows = c.fetchall()
            liked_message_ids = {row[0] for row in like_rows}
        
        conn.close()
        
        return [{
            'id': row[0],
            'device_id': row[1],
            'content': row[2],
            'author': row[3],
            'likes': row[4],
            'liked': row[0] in liked_message_ids,
            'time': row[5]
        } for row in rows]
    
    def add_message(self, device_id, content, author):
        """添加留言"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO messages (device_id, content, author) VALUES (?, ?, ?)',
                  (device_id, content, author))
        message_id = c.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    def like_message(self, message_id, device_id):
        """点赞留言"""
        conn = self._get_connection()
        c = conn.cursor()
        try:
            # 开始事务
            conn.execute('BEGIN TRANSACTION')
            
            # 插入点赞记录
            c.execute('INSERT OR IGNORE INTO message_likes (message_id, device_id) VALUES (?, ?)',
                      (message_id, device_id))
            
            # 更新留言的点赞数
            c.execute('UPDATE messages SET likes = (SELECT COUNT(*) FROM message_likes WHERE message_id = ?) WHERE id = ?',
                      (message_id, message_id))
            
            # 提交事务
            conn.commit()
            return True
        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"Error liking message: {e}")
            return False
        finally:
            conn.close()
    
    def add_knowledge_article(self, title, content, category):
        """添加知识文章"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO knowledge_articles (title, content, category) VALUES (?, ?, ?)',
                  (title, content, category))
        article_id = c.lastrowid
        conn.commit()
        conn.close()
        return article_id
    
    def get_knowledge_articles(self, category=None):
        """获取知识文章列表"""
        conn = self._get_connection()
        c = conn.cursor()
        if category:
            c.execute('SELECT id, title, content, category, views, created_at FROM knowledge_articles WHERE category = ? ORDER BY created_at DESC', (category,))
        else:
            c.execute('SELECT id, title, content, category, views, created_at FROM knowledge_articles ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'category': row[3],
            'views': row[4],
            'created_at': row[5]
        } for row in rows]
    
    def get_knowledge_article_by_id(self, article_id):
        """根据ID获取知识文章"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT id, title, content, category, views, created_at FROM knowledge_articles WHERE id = ?', (article_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'views': row[4],
                'created_at': row[5]
            }
        return None
    
    def increment_knowledge_article_views(self, article_id):
        """增加知识文章浏览量"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE knowledge_articles SET views = views + 1 WHERE id = ?', (article_id,))
        conn.commit()
        conn.close()
    
    def get_knowledge_categories(self):
        """获取知识分类列表"""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT DISTINCT category FROM knowledge_articles')
        rows = c.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_personalized_recommendations(self, device_id, scores):
        """获取个性化推荐"""
        # 这里可以根据用户的道德评分生成个性化推荐
        # 暂时返回默认推荐
        return [
            {
                'type': 'article',
                'title': '如何培养同理心',
                'description': '同理心是道德判断的重要组成部分',
                'score': scores[3]  # 共情力
            },
            {
                'type': 'task',
                'title': '今天尝试从他人的角度思考问题',
                'description': '理解他人是建立良好关系的前提',
                'score': scores[3]  # 共情力
            },
            {
                'type': 'article',
                'title': '正义与公平的哲学思考',
                'description': '探索正义的本质和实践方法',
                'score': scores[0]  # 正义感
            }
        ]

# 创建全局数据库服务实例
db_service = DatabaseService()
