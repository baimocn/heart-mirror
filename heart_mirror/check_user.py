import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查users表中的所有记录
print("Users table records:")
c.execute("SELECT * FROM users")
users = c.fetchall()
for user in users:
    print(user)

# 检查test_history表中的记录，查看是否有user_id关联
print("\nTest_history table records with user_id:")
c.execute("SELECT id, user_id, device_id, created_at FROM test_history WHERE user_id IS NOT NULL")
test_history = c.fetchall()
for record in test_history:
    print(record)

# 关闭连接
conn.close()