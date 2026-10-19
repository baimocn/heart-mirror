#!/usr/bin/env python3
"""
初始化管理员账号脚本
将指定的管理员账号设置为超级管理员
"""

from models import set_admin_level, create_user, get_user_by_account

# 超级管理员账号
ADMIN_ACCOUNT = "350524200705057715"
ADMIN_LEVEL = 1  # 1: 超级管理员

# 初始化超级管理员账号
def init_admin():
    print("正在初始化超级管理员账号...")
    
    # 检查账号是否存在
    user = get_user_by_account(ADMIN_ACCOUNT)
    if user:
        print(f"账号 {ADMIN_ACCOUNT} 已存在，更新为超级管理员")
        # 更新为超级管理员
        success = set_admin_level(ADMIN_ACCOUNT, ADMIN_LEVEL)
        if success:
            print("超级管理员账号设置成功")
        else:
            print("超级管理员账号设置失败")
    else:
        print(f"账号 {ADMIN_ACCOUNT} 不存在，创建并设置为超级管理员")
        # 创建新用户并设置为超级管理员
        user_id = create_user(ADMIN_ACCOUNT, "admin_device", ADMIN_LEVEL)
        if user_id:
            print("超级管理员账号创建成功")
        else:
            print("超级管理员账号创建失败")

if __name__ == "__main__":
    init_admin()
