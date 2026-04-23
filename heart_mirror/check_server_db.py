import sqlite3
import os

db_path = '/var/www/heart_mirror/database/heart_mirror.db'

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
try:
    c.execute("SELECT * FROM users WHERE account_number = '001'")
    user = c.fetchone()
    if user:
        print(f"  User found: {user}")
    else:
        print("  User not found")
except Exception as e:
    print(f"  Error: {e}")

# 关闭连接
conn.close()