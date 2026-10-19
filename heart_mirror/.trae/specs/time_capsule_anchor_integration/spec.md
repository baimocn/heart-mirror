# 时间胶囊与锚点数字账号关联功能 - 产品需求文档

## Overview
- **Summary**: 实现时间胶囊功能与锚点数字账号的关联，确保用户通过"保存时间胶囊"按钮提交的数据能够准确存储到与该数字账号相关联的数据库记录中。
- **Purpose**: 解决时间胶囊数据与用户数字账号关联的问题，确保数据的一致性和可追溯性。
- **Target Users**: 使用心镜·道德人格测试系统的用户，特别是已绑定数字账号的用户。

## Goals
- 实现时间胶囊表与用户表的关联，添加user_id字段
- 修改时间胶囊保存逻辑，支持通过数字账号关联存储
- 确保已绑定数字账号的用户保存的时间胶囊能够与该账号关联
- 保持现有功能的兼容性，未绑定数字账号的用户仍可通过设备ID保存时间胶囊

## Non-Goals (Out of Scope)
- 不修改时间胶囊的其他功能和界面
- 不修改锚点功能的核心逻辑
- 不涉及其他功能模块的变更

## Background & Context
- 目前时间胶囊功能仅通过设备ID存储，没有与用户数字账号关联
- 锚点功能已实现设备ID与数字账号的绑定
- 需要确保时间胶囊数据能够与用户数字账号关联，提高数据的可追溯性和一致性

## Functional Requirements
- **FR-1**: 时间胶囊表添加user_id字段，支持与用户表关联
- **FR-2**: 修改时间胶囊保存API，支持通过数字账号关联存储
- **FR-3**: 修改前端保存逻辑，传递用户信息（如果已绑定）
- **FR-4**: 保持向后兼容，未绑定数字账号的用户仍可通过设备ID保存

## Non-Functional Requirements
- **NFR-1**: 数据存储的一致性和可靠性
- **NFR-2**: API响应时间不超过500ms
- **NFR-3**: 错误处理机制完善，提供清晰的错误提示

## Constraints
- **Technical**: SQLite数据库，Flask后端，JavaScript前端
- **Business**: 保持现有功能的兼容性
- **Dependencies**: 锚点功能已实现，时间胶囊功能已存在

## Assumptions
- 锚点功能已正常工作，能够正确绑定设备ID和数字账号
- 时间胶囊表结构可修改，添加user_id字段
- 前端能够获取到已绑定的用户信息

## Acceptance Criteria

### AC-1: 时间胶囊表结构修改
- **Given**: 数据库连接正常
- **When**: 执行数据库迁移
- **Then**: 时间胶囊表添加user_id字段，支持与用户表关联
- **Verification**: `programmatic`
- **Notes**: 需确保字段添加不会影响现有数据

### AC-2: 时间胶囊保存API修改
- **Given**: API请求包含用户信息
- **When**: 调用时间胶囊保存API
- **Then**: 时间胶囊数据与用户数字账号关联存储
- **Verification**: `programmatic`

### AC-3: 前端保存逻辑修改
- **Given**: 用户已绑定数字账号
- **When**: 点击"保存时间胶囊"按钮
- **Then**: 前端传递用户信息到后端API
- **Verification**: `programmatic`

### AC-4: 向后兼容性
- **Given**: 用户未绑定数字账号
- **When**: 点击"保存时间胶囊"按钮
- **Then**: 仍可通过设备ID保存时间胶囊
- **Verification**: `programmatic`

### AC-5: 数据查询验证
- **Given**: 用户已绑定数字账号并保存时间胶囊
- **When**: 查询时间胶囊数据
- **Then**: 能够通过用户ID查询到关联的时间胶囊
- **Verification**: `programmatic`

## Open Questions
- [ ] 时间胶囊表的user_id字段是否需要设置为外键约束？
- [ ] 前端如何获取已绑定的用户信息？
- [ ] 是否需要修改时间胶囊查询API以支持通过用户ID查询？