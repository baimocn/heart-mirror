# 时间胶囊与锚点数字账号关联功能 - 实现计划

## [ ] Task 1: 修改时间胶囊表结构，添加user_id字段
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修改database_service.py中的时间胶囊表创建语句，添加user_id字段
  - 确保字段添加不会影响现有数据
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 时间胶囊表成功添加user_id字段
  - `programmatic` TR-1.2: 现有时间胶囊数据不受影响
- **Notes**: 使用ALTER TABLE语句添加字段，处理可能的异常

## [ ] Task 2: 修改数据库服务层，支持时间胶囊与用户关联
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 修改add_time_capsule函数，支持传递user_id参数
  - 修改get_time_capsules函数，支持通过user_id查询
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: add_time_capsule函数能够接收并存储user_id
  - `programmatic` TR-2.2: get_time_capsules函数能够通过user_id查询
- **Notes**: 保持向后兼容，user_id参数可选

## [ ] Task 3: 修改时间胶囊API路由，支持用户关联
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 修改/api/time_capsule POST路由，支持接收user_id参数
  - 修改/api/time_capsules GET路由，支持通过user_id查询
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: POST /api/time_capsule能够接收并处理user_id参数
  - `programmatic` TR-3.2: GET /api/time_capsules能够通过user_id参数查询
- **Notes**: 保持向后兼容，user_id参数可选

## [ ] Task 4: 修改前端保存逻辑，传递用户信息
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 修改saveTimeCapsule函数，从localStorage获取已绑定的用户信息
  - 在API请求中传递user_id参数（如果已绑定）
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 已绑定数字账号的用户保存时间胶囊时传递user_id
  - `programmatic` TR-4.2: 未绑定数字账号的用户仍可正常保存
- **Notes**: 从localStorage.getItem('anchor_user')获取用户信息

## [ ] Task 5: 测试验证
- **Priority**: P1
- **Depends On**: Task 4
- **Description**: 
  - 测试已绑定数字账号的用户保存时间胶囊
  - 测试未绑定数字账号的用户保存时间胶囊
  - 验证时间胶囊数据与用户账号正确关联
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 已绑定用户保存的时间胶囊包含正确的user_id
  - `programmatic` TR-5.2: 未绑定用户保存的时间胶囊仍可通过设备ID查询
  - `human-judgment` TR-5.3: 功能使用流程顺畅，无错误提示
- **Notes**: 测试时需要先绑定数字账号