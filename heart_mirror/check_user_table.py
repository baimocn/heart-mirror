import sqlite3
import os

# 连接数据库
db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查users表的结构
print("=== users表结构 ===")
c.execute('PRAGMA table_info(users)')
columns = c.fetchall()
for column in columns:
    print(f"ID: {column[0]}, 名称: {column[1]}, 类型: {column[2]}, 非空: {column[3]}, 默认值: {column[4]}, 主键: {column[5]}")

# 检查test_history表的结构
print("\n=== test_history表结构 ===")
c.execute('PRAGMA table_info(test_history)')
columns = c.fetchall()
for column in columns:
    print(f"ID: {column[0]}, 名称: {column[1]}, 类型: {column[2]}, 非空: {column[3]}, 默认值: {column[4]}, 主键: {column[5]}")

# 关闭连接
conn.close()
