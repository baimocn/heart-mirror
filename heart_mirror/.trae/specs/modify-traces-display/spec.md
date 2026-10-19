# 修改"查看选择轨迹"展示方式

## Why
当前"查看选择轨迹"功能点击后会弹出一个模态框（modal），与"查看历史演化"的页面内展示方式不一致。为了提升用户体验和交互一致性，需要将其修改为在原页面内展示内容。

## What Changes
- 移除选择轨迹的模态框展示方式
- 在结果页面内添加选择轨迹展示区域（类似历史演化区域）
- 修改 `showTracesModal` 函数为 `toggleTraces` 函数，使其在原页面内显示/隐藏内容
- 添加选择轨迹区域的CSS样式

## Impact
- Affected specs: 无（交互优化）
- Affected code: 
  - `templates/index.html` - 添加选择轨迹展示区域HTML
  - `static/script.js` - 修改显示逻辑
  - `static/style.css` - 添加样式

## MODIFIED Requirements

### Requirement: 选择轨迹展示方式
**当前行为**：点击"查看选择轨迹"按钮后，弹出一个模态框显示选择轨迹内容

**修改后行为**：点击"查看选择轨迹"按钮后，在原页面内展开显示选择轨迹内容，再次点击可收起

#### Scenario: 展开选择轨迹
- **WHEN** 用户点击"查看选择轨迹"按钮
- **THEN** 在原页面内展开显示选择轨迹内容
- **AND** 按钮文字变为"收起选择轨迹"

#### Scenario: 收起选择轨迹
- **WHEN** 用户再次点击"收起选择轨迹"按钮
- **THEN** 选择轨迹内容收起
- **AND** 按钮文字变为"查看选择轨迹"

## REMOVED Requirements

### Requirement: 选择轨迹模态框
**Reason**: 改为页面内展示，不再需要模态框
**Migration**: 移除 `tracesModal` 模态框HTML，将内容迁移到页面内的专用区域
