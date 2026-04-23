import sqlite3
import os

# 连接数据库
db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查用户表
print("=== 用户表 ===")
c.execute('SELECT id, account_number, device_id, created_at FROM users')
users = c.fetchall()
for user in users:
    print(f"ID: {user[0]}, 账号: {user[1]}, 设备ID: {user[2]}, 创建时间: {user[3]}")

# 检查测试历史表
print("\n=== 测试历史表 ===")
c.execute('SELECT id, device_id, user_id, fingerprint, created_at FROM test_history ORDER BY created_at DESC LIMIT 10')
test_history = c.fetchall()
for test in test_history:
    print(f"ID: {test[0]}, 设备ID: {test[1]}, 用户ID: {test[2]}, 镜像编号: {test[3]}, 创建时间: {test[4]}")

# 关闭连接
conn.close()
