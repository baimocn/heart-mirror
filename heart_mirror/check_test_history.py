import sqlite3
import os

# 连接数据库
db_path = os.path.join(os.path.dirname(__file__), 'database', 'heart_mirror.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查test_history表中的user_id值
print("=== test_history表中的user_id值 ===")
c.execute('SELECT id, device_id, user_id, fingerprint, created_at FROM test_history')
test_history = c.fetchall()
for test in test_history:
    print(f"ID: {test[0]}, 设备ID: {test[1]}, 用户ID: {test[2]}, 镜像编号: {test[3]}, 创建时间: {test[4]}")

# 尝试更新test_history表中的user_id值
print("\n=== 尝试更新test_history表中的user_id值 ===")
try:
    c.execute('UPDATE test_history SET user_id = 1 WHERE device_id = "f45216e8-f267-4429-83f4-c6643033727c" AND user_id IS NULL ORDER BY created_at DESC LIMIT 1')
    conn.commit()
    print(f"更新成功，影响了 {c.rowcount} 行")
except Exception as e:
    print(f"更新失败: {e}")

# 再次检查test_history表中的user_id值
print("\n=== 更新后test_history表中的user_id值 ===")
c.execute('SELECT id, device_id, user_id, fingerprint, created_at FROM test_history')
test_history = c.fetchall()
for test in test_history:
    print(f"ID: {test[0]}, 设备ID: {test[1]}, 用户ID: {test[2]}, 镜像编号: {test[3]}, 创建时间: {test[4]}")

# 关闭连接
conn.close()
