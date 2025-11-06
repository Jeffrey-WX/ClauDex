[English](COLLABORATIVE_MODE.md) | [简体中文](COLLABORATIVE_MODE.zh-CN.md)

# 协同模式：Claude Code + Codex

## 概述

协同模式允许 Claude Code 和 Codex 分工协作修复bug和实现功能：
- **Claude Code**: 分析、搜索、推理
- **Codex**: 执行、修改、实现

这避免了重复分析，充分发挥各自优势。

## 工作流程

```
用户需求
   ↓
Claude Code 分析
   ↓ (传递结构化上下文)
Codex 执行修复
   ↓
自动运行测试
   ↓
返回结果给 Claude Code
   ↓
展示给用户
```

## 使用方法

### 标准模式 (简单任务)

```typescript
// Claude Code 直接调用
invoke_codex({
  task: "创建一个用户登录API",
  projectPath: "/path/to/project"
})
```

### 协同模式 (复杂bug修复)

```typescript
// Claude Code 先分析，再调用
invoke_codex({
  task: "修复token过期bug",
  projectPath: "/path/to/project",
  context: {
    analysis: "问题定位在 auth.ts:45，缺少token刷新逻辑。当前实现只在初始化时获取token，未处理过期场景。",
    relatedFiles: [
      "src/auth/auth.ts",
      "src/middleware/auth-middleware.ts",
      "src/utils/token.ts"
    ],
    suggestedFix: "在auth.ts添加自动刷新机制，检测token即将过期时主动刷新。同时在middleware中添加过期检查和重试逻辑。",
    errorDetails: "Error: jwt expired\\n  at verify (/node_modules/jsonwebtoken/verify.js:224:19)",
    testCommand: "npm test -- auth"  // 可选：修复后自动运行
  }
})
```

## 协同上下文字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `analysis` | string | ✅ | Claude Code的分析结果 |
| `relatedFiles` | string[] | ❌ | 相关文件列表 |
| `suggestedFix` | string | ❌ | 建议的修复方案 |
| `errorDetails` | string | ❌ | 错误信息或日志 |
| `testCommand` | string | ❌ | 修复后运行的测试命令 |

## 返回结果

```typescript
{
  result: "修复完成描述",
  executionLog: [
    { tool: "write_file", args: {...}, timestamp: "..." }
  ],
  iterations: 1,
  testResult: {  // 如果提供了testCommand
    success: true,
    output: "All tests passed",
    exitCode: 0
  }
}
```

## 实际示例

### 示例 1: 修复API bug

```typescript
// 1. 用户报告："POST /api/users 返回500错误"

// 2. Claude Code 操作
//    - 搜索代码找到 routes/users.ts
//    - 阅读代码发现缺少错误处理
//    - 检查相关的 controllers/user-controller.ts

// 3. Claude Code 调用 Codex
invoke_codex({
  task: "修复 POST /api/users 的500错误",
  context: {
    analysis: "routes/users.ts:23 调用 createUser 时未捕获异常。当数据库连接失败时直接抛出未处理的错误导致500。",
    relatedFiles: [
      "routes/users.ts",
      "controllers/user-controller.ts"
    ],
    suggestedFix: "在routes/users.ts添加try-catch，返回适当的错误码和消息。",
    testCommand: "npm test -- routes/users"
  }
})

// 4. Codex 执行修复

// 5. 自动运行测试验证

// 6. 返回结果给用户
```

### 示例 2: 性能优化

```typescript
invoke_codex({
  task: "优化用户列表查询性能",
  context: {
    analysis: "users.service.ts:45 的 getAllUsers 方法使用了N+1查询。每个用户都单独查询关联的profile数据，导致1000个用户就有1000次数据库查询。",
    relatedFiles: [
      "services/users.service.ts",
      "models/user.model.ts",
      "models/profile.model.ts"
    ],
    suggestedFix: "使用JOIN或eager loading一次性加载所有数据",
    testCommand: "npm run test:performance"
  }
})
```

## 优势

✅ **避免重复分析** - Codex直接基于Claude的分析执行
✅ **充分发挥优势** - Claude擅长分析，Codex擅长实现
✅ **自动化验证** - 可选的测试命令确保修复有效
✅ **减少token消耗** - 不重复分析相同的代码
✅ **提高成功率** - 结构化上下文让Codex更精准

## 何时使用协同模式

**适合场景：**
- 跨文件的复杂bug
- 需要深入分析的性能问题
- 涉及多个模块的重构
- 错误信息不明确的问题

**不适合场景：**
- 简单的单文件修改
- 明确的新功能添加
- 代码格式化等机械性任务

## 超时配置

协同模式支持自定义超时时间（默认 30 分钟）：

```typescript
invoke_codex({
  task: "修复认证 bug",
  context: {
    analysis: "...",
    relatedFiles: ["auth.ts"],
    suggestedFix: "...",
    testCommand: "npm test -- auth"
  },
  timeout: 1200  // 20 分钟
})
```

**推荐超时**：
- 简单 bug 修复：10-15 分钟
- 复杂重构：20-30 分钟
- 大规模修改：30-60 分钟

如果任务经常超时，考虑：
1. 拆分为更小的子任务
2. 简化 `suggestedFix`，提供更明确的方向
3. 减少 `relatedFiles` 数量，只保留核心文件

## 注意事项

1. **Claude的分析应该准确** - Codex会信任并执行建议
2. **提供足够上下文** - 相关文件列表和错误详情很重要
3. **测试命令应该快速** - 避免运行整个测试套件（2 分钟超时）
4. **不是"互审"** - 这是协作，不是Claude审查Codex的代码
5. **合理设置超时** - 根据任务复杂度调整，避免过长或过短

## 对比：标准模式 vs 协同模式

| 维度 | 标准模式 | 协同模式 |
|------|---------|---------|
| 分析 | Codex自己分析 | Claude提供分析 |
| 适用 | 简单任务 | 复杂bug |
| Token | Codex需要更多 | 总体更优化 |
| 准确性 | 取决于Codex | 结合两者优势 |
| 验证 | 手动 | 可自动测试 |
