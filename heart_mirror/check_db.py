import sqlite3
import os

# 导入init_db函数和sqlite3
from models import init_db
import sqlite3

# 手动添加account_number列
db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
try:
    c.execute('ALTER TABLE users ADD COLUMN account_number TEXT UNIQUE')
    conn.commit()
    print("Added account_number column successfully")
except sqlite3.OperationalError as e:
    print(f"Error adding account_number column: {e}")
finally:
    conn.close()

# 初始化数据库
init_db()

db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查users表结构
print("Users table schema:")
c.execute("PRAGMA table_info(users)")
users_schema = c.fetchall()
for column in users_schema:
    print(f"  {column[1]}: {column[2]}")

# 检查test_history表结构
print("\nTest_history table schema:")
c.execute("PRAGMA table_info(test_history)")
test_history_schema = c.fetchall()
for column in test_history_schema:
    print(f"  {column[1]}: {column[2]}")

# 检查是否存在账号001的用户
print("\nChecking if user with account_number 001 exists:")
c.execute("SELECT * FROM users WHERE account_number = '001'")
user = c.fetchone()
if user:
    print(f"  User found: {user}")
else:
    print("  User not found")

# 关闭连接
conn.close()