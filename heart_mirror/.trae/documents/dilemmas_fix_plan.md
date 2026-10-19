# 道德困惑墙页面修复计划

## 项目分析

通过对现有的 `dilemmas.html` 文件进行分析，发现以下问题需要修复：

1. **发布困惑功能**：
   - 表单字段与API要求不匹配（当前包含title、description、background、category字段，而API只需要content、options、is_anonymous）
   - 缺少字符长度限制
   - 缺少提交加载状态显示
   - 错误处理机制需要完善

2. **困惑列表展示**：
   - API调用格式不正确（当前使用了sort_by和category参数，需要调整）
   - 发布时间格式化显示需要优化（如"X分钟前"、"X小时前"）
   - 需要确保按created_at倒序排列

3. **投票功能**：
   - 需要确保与API正确交互
   - 投票加载状态需要实现

4. **技术实现**：
   - 需要实现getDeviceId()函数
   - 代码组织需要优化
   - 需要确保使用原生HTML/CSS/JavaScript

## 修复计划

### 1. HTML结构调整

- 简化发布表单，只保留必要字段：
  - 困惑内容文本域（textarea）
  - 选项输入组件（初始2个，最多5个）
  - 匿名发布复选框
  - 提交按钮
- 优化困惑卡片结构，确保包含所有必要元素
- 确保语义化HTML结构

### 2. CSS样式优化

- 保持现有的视觉风格（柔和圆角、暖色调、毛玻璃效果）
- 优化响应式设计，确保在移动端和桌面端都有良好表现
- 添加加载状态样式
- 优化表单元素和卡片的视觉效果

### 3. JavaScript逻辑修复

- 实现getDeviceId()函数，用于获取设备ID
- 修复API调用：
  - GET /api/dilemmas：获取所有困惑
  - POST /api/dilemmas：创建困惑
  - POST /api/dilemmas/{id}/vote：为特定困惑投票
- 实现表单验证（内容不为空，选项数量2-5个）
- 实现投票限制机制（使用localStorage）
- 优化发布时间格式化显示
- 添加错误处理和用户反馈
- 优化代码组织，按功能模块化

### 4. 功能测试

- 测试发布困惑功能
- 测试困惑列表展示
- 测试投票功能
- 测试错误处理
- 测试响应式设计

## 技术实现细节

### 1. 设备ID生成

```javascript
function getDeviceId() {
  let id = localStorage.getItem('deviceId');
  if (!id) {
    id = 'device_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('deviceId', id);
  }
  return id;
}
```

### 2. 已投票记录管理

```javascript
// 获取已投票记录
function getVotedDilemmas() {
  return JSON.parse(localStorage.getItem('voted_dilemmas') || '{}');
}

// 记录已投票的困惑ID
function setVotedDilemma(dilemmaId) {
  const votedDilemmas = getVotedDilemmas();
  votedDilemmas[dilemmaId] = true;
  localStorage.setItem('voted_dilemmas', JSON.stringify(votedDilemmas));
}

// 检查困惑是否已投票
function hasVoted(dilemmaId) {
  const votedDilemmas = getVotedDilemmas();
  return !!votedDilemmas[dilemmaId];
}
```

### 3. API调用函数

```javascript
// 获取困惑列表
async function fetchDilemmas() {
  try {
    const response = await fetch('/api/dilemmas');
    const data = await response.json();
    return data.data || [];
  } catch (error) {
    console.error('获取困惑列表失败', error);
    return [];
  }
}

// 发布困惑
async function createDilemma(content, options, isAnonymous) {
  try {
    const response = await fetch('/api/dilemmas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id: getDeviceId(),
        content,
        options,
        is_anonymous: isAnonymous ? 1 : 0
      })
    });
    return await response.json();
  } catch (error) {
    console.error('发布困惑失败', error);
    throw error;
  }
}

// 投票
async function voteDilemma(dilemmaId, optionIndex) {
  try {
    const response = await fetch(`/api/dilemmas/${dilemmaId}/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ option_index: optionIndex })
    });
    return await response.json();
  } catch (error) {
    console.error('投票失败', error);
    throw error;
  }
}
```

### 4. 时间格式化函数

```javascript
function formatTime(timestamp) {
  const now = new Date();
  const past = new Date(timestamp);
  const diffInSeconds = Math.floor((now - past) / 1000);

  if (diffInSeconds < 60) {
    return '刚刚';
  } else if (diffInSeconds < 3600) {
    return `${Math.floor(diffInSeconds / 60)}分钟前`;
  } else if (diffInSeconds < 86400) {
    return `${Math.floor(diffInSeconds / 3600)}小时前`;
  } else if (diffInSeconds < 604800) {
    return `${Math.floor(diffInSeconds / 86400)}天前`;
  } else {
    return past.toLocaleDateString('zh-CN');
  }
}
```

## 预期成果

修复后的道德困惑墙页面应具备以下功能：

1. **发布困惑**：用户可以填写困惑内容，添加2-5个选项，选择是否匿名发布
2. **困惑列表**：按时间倒序显示所有困惑，包含完整内容、选项、投票数、发布时间等信息
3. **投票功能**：用户可以为困惑投票，已投票的困惑会被标记并禁用投票
4. **响应式设计**：在桌面端和移动端都有良好的显示效果
5. **用户反馈**：提供加载状态、成功/错误提示等反馈
6. **错误处理**：妥善处理网络错误、服务器错误等异常情况

修复后的页面将完全符合后端API规范，确保所有功能正常工作。