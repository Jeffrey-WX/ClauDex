# Codex MCP Server - 项目配置

> MCP服务器，连接Claude Code与本地Codex CLI实现协同编程

**语言**: [English](./CLAUDE.md) · [简体中文](./CLAUDE.zh-CN.md)

## 项目概述

### 目标
提供一个MCP (Model Context Protocol) 服务器，使Claude Code能够调用本地Codex CLI来执行编程任务，实现两个AI的协同工作。

### 核心价值
- **分工协作**: Claude擅长分析，Codex擅长执行
- **本地执行**: 所有操作在本地进行，安全可控
- **自动化验证**: 可选的测试命令自动验证修复
- **避免重复**: 减少重复分析，优化token消耗

## 架构设计

### 技术栈
- **语言**: TypeScript 5.7+
- **运行时**: Node.js 18+
- **协议**: MCP (Model Context Protocol)
- **传输**: stdio (标准输入输出)
- **依赖**:
  - `@modelcontextprotocol/sdk` - MCP协议实现
  - `glob` - 文件匹配工具

### 目录结构
```
codex-mcp/
├── src/
│   ├── index.ts                    # MCP服务器入口
│   ├── types/
│   │   └── index.ts                # 类型定义
│   └── tools/
│       ├── codex-cli-executor.ts   # Codex CLI执行器
│       ├── invoke-codex.ts         # 主工具封装
│       ├── backup-manager.ts       # 备份管理（未使用）
│       ├── command-executor.ts     # 命令执行（未使用）
│       └── file-operations.ts      # 文件操作（未使用）
├── dist/                           # 编译输出
├── COLLABORATIVE_MODE.md           # 协同模式文档
├── README.md                       # 项目说明
└── CLAUDE.md                       # 本文件
```

### 数据流

```
用户请求
   ↓
Claude Code (分析、决策)
   ↓ MCP Protocol (stdio JSON-RPC)
codex-mcp-server
   ├─ 标准模式: 直接传递任务
   └─ 协同模式: 格式化分析结果
   ↓
Codex CLI (codex exec --full-auto --json)
   ↓
本地文件系统 (真实修改)
   ↓
可选: 自动运行测试
   ↓
返回结果
   ↓
Claude Code (展示给用户)
```

## 模块说明

### 1. index.ts - MCP服务器
**职责**:
- 实现MCP协议服务器
- 注册 `invoke_codex` 工具
- 处理工具调用请求
- 格式化返回结果

**关键逻辑**:
```typescript
// 工具定义
{
    name: 'invoke_codex',
    inputSchema: {
        task: string,           // 必需
        projectPath: string,    // 必需
        context?: string | CollaborativeContext,  // 可选
        maxIterations?: number  // 可选
    }
}
```

### 2. codex-cli-executor.ts - 核心执行器
**职责**:
- 执行本地 `codex exec` 命令
- 解析JSONL输出事件
- 处理协同上下文
- 运行测试命令

**关键方法**:
- `invoke()` - 主执行方法
- `formatCollaborativePrompt()` - 格式化协同prompt
- `executeCodexCLI()` - 执行CLI命令
- `runTestCommand()` - 运行测试

**Codex CLI参数**:
```bash
codex exec \
    --full-auto \           # 自动执行，无交互
    --skip-git-repo-check \ # 允许非git目录
    --json \                # JSONL输出
    -C <projectPath> \      # 工作目录
    "<task + context>"      # 任务描述
```

### 3. types/index.ts - 类型系统
**核心类型**:

```typescript
// 调用参数
interface InvokeCodexParams {
    task: string;
    context?: string | CollaborativeContext;
    projectPath: string;
    maxIterations?: number;
}

// 协同上下文（结构化）
interface CollaborativeContext {
    analysis: string;           // Claude的分析
    relatedFiles?: string[];    // 相关文件
    suggestedFix?: string;      // 修复建议
    errorDetails?: string;      // 错误信息
    testCommand?: string;       // 测试命令
}

// 返回结果
interface InvokeCodexResult {
    result: string;             // Codex的输出
    executionLog: ToolExecution[];
    iterations: number;
    backups?: string[];
    testResult?: {              // 测试结果（如果有）
        success: boolean;
        output: string;
        exitCode: number;
    };
}
```

## 工作模式

### 标准模式
**适用**: 简单任务、明确需求

```typescript
invoke_codex({
    task: "创建一个用户登录API",
    projectPath: "/path/to/project"
})
```

**特点**:
- Codex自己分析和执行
- 适合单文件或明确任务
- token消耗较多但一次完成

### 协同模式
**适用**: 复杂bug、跨文件重构

```typescript
invoke_codex({
    task: "修复token过期bug",
    projectPath: "/path/to/project",
    context: {
        analysis: "auth.ts:45缺少刷新逻辑...",
        relatedFiles: ["auth.ts", "middleware.ts"],
        suggestedFix: "添加自动刷新机制",
        errorDetails: "Error: jwt expired...",
        testCommand: "npm test -- auth"
    }
})
```

**特点**:
- Claude先分析，Codex直接执行
- 避免Codex重复分析
- 可选的自动测试验证
- 充分发挥两者优势

详见: [COLLABORATIVE_MODE.md](./COLLABORATIVE_MODE.md)

## 开发规范

### TypeScript规范
- 所有公开API必须有类型注解
- 使用 `interface` 定义数据结构
- 避免 `any`，使用 `unknown` 或具体类型
- 导出类型以便外部使用

### 错误处理
```typescript
// ✅ 正确：捕获并记录
try {
    const result = await executor.invoke(params);
    return result;
} catch (error: any) {
    console.error(`Error: ${error.message}`);
    executionLog.push({
        tool: 'codex_cli',
        error: error.message,
        timestamp: new Date().toISOString()
    });
    return { result: `Error: ${error.message}`, ... };
}
```

### 日志规范
- **stdout**: 仅JSON-RPC消息（MCP协议要求）
- **stderr**: 所有日志和调试信息
- 使用 `console.error()` 输出日志
- 关键事件添加emoji标识（🤖 ✅ ❌ 🧪）

### 安全考虑
- **路径验证**: 虽然Codex CLI有沙箱，仍需注意
- **命令注入**: bash命令使用数组参数，避免字符串拼接
- **超时保护**: Codex CLI执行5分钟超时
- **测试超时**: 测试命令2分钟超时

## 开发工作流

### 本地开发
```bash
# 安装依赖
npm install

# 开发模式（监听文件变化）
npm run dev

# 构建
npm run build

# 运行
npm start
```

### 测试
```bash
# 单元测试（待实现）
npm test

# 手动测试：直接调用CLI
node dist/index.js

# 然后发送JSON-RPC请求（可用测试脚本）
```

### 发布流程
1. 更新版本号（`package.json`）
2. 更新 CHANGELOG（待创建）
3. 运行测试（待实现）
4. 构建: `npm run build`
5. Git标签: `git tag v1.x.x`
6. 提交代码

### Claude Code集成
编辑 `~/.claude/.claude.json`:
```json
{
    "projects": {
        "/your/project": {
            "mcpServers": {
                "codex": {
                    "command": "node",
                    "args": ["/path/to/codex-mcp/dist/index.js"]
                }
            }
        }
    }
}
```

重启Claude Code生效。

## 设计原则

### 1. 简单优于复杂
- 最初设计包含backup、security等模块，但实际不需要
- Codex CLI已有沙箱和安全机制
- 保持MCP服务器职责单一：桥接Claude Code和Codex CLI

### 2. 协同而非竞争
- 不是"Claude审查Codex"（缺乏客观标准）
- 而是"Claude分析 + Codex执行"（发挥优势）
- 测试结果是客观验证标准

### 3. 本地优先
- 从远程API改为本地CLI
- 更安全、更快、更可控
- 真实文件修改而非模拟

### 4. 向后兼容
- 协同模式是标准模式的增强
- `context` 参数同时支持string和object
- 不影响现有调用方式

## 常见问题

### Q: 为什么不使用OpenAI API？
A: 最初使用API，但发现用户的第三方API不支持function calling，且远程执行无法真实修改文件。改用本地Codex CLI后问题解决。

### Q: backup-manager等模块为什么没用到？
A: 最初计划MCP服务器直接操作文件，需要备份保护。改为调用Codex CLI后，这些功能由CLI内部处理，MCP层无需重复实现。

### Q: 协同模式的testCommand为什么有时不执行？
A: 可能是context被序列化为JSON字符串导致类型检测失败。正在改进中。

### Q: 如何调试MCP服务器？
A: MCP使用stdio协议，stdout被占用。所有调试信息输出到stderr，可以查看Claude Code的日志或重定向stderr到文件。

## 未来改进

### 短期
- [ ] 实现单元测试
- [ ] 修复testCommand检测问题
- [ ] 添加更多示例

### 中期
- [ ] 支持流式输出（实时显示Codex进度）
- [ ] 添加性能指标收集
- [ ] 智能成本优化（自动选择模式）

### 长期
- [ ] 上下文记忆（学习项目结构）
- [ ] 自动任务分解
- [ ] 多Codex并行执行

---

**项目地址**: `/mnt/c/Users/95321/codex-mcp/`
**最后更新**: 2025-11-05
**维护者**: Claude Code + Codex 协同开发
