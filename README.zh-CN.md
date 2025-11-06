[English](README.md) | [简体中文](README.zh-CN.md)

# Codex MCP Server

连接 Claude Code 和本地 Codex CLI 的 MCP 服务器，实现协同编程。

## 功能特性

- 🤖 **本地 Codex CLI 集成**: 直接在本地机器上执行 Codex 命令
- 🤝 **协同模式**: Claude Code 负责分析，Codex 负责执行 - 发挥各自优势
- 📁 **完整文件系统访问**: Codex 可以读取、写入、创建项目文件
- ⚙️ **命令执行**: 自动运行测试、构建等命令
- ✅ **自动测试验证**: 可选的修复后测试执行
- 📊 **执行日志**: 详细追踪所有操作
- 🔒 **本地安全**: 所有操作通过本地 Codex CLI 执行

## 架构说明

```
Claude Code
    ↓ MCP Protocol
codex-mcp-server
    ├── invoke_codex (标准模式)
    │   └── 简单任务
    └── invoke_codex (协同模式)
        ├── Claude 的分析
        ├── Codex 的执行
        └── 自动测试验证
            ↓
    本地 Codex CLI
        └── 真实文件修改
```

## 新特性：协同模式

详细文档请查看 [COLLABORATIVE_MODE.zh-CN.md](./COLLABORATIVE_MODE.zh-CN.md)

**快速示例：**
```typescript
// Claude Code 先分析，然后调用：
invoke_codex({
  task: "修复认证bug",
  context: {
    analysis: "auth.ts:45 缺少token刷新逻辑",
    relatedFiles: ["auth.ts", "middleware.ts"],
    testCommand: "npm test -- auth"
  }
})
```

## 安装配置

### 前置要求

- Node.js 18+
- **Codex CLI** 已安装并配置 (https://codex.anthropic.com)
- Claude Code

### 1. 安装依赖

```bash
cd codex-mcp
npm install
npm run build
```

### 2. 添加到 Claude Code

> **注意：CLI vs GUI 配置**
> - **Claude CLI**（命令行 `claude` 工具）使用配置文件：`~/.claude.json`
> - **Claude Code GUI**（桌面应用）使用配置文件：`~/.claude/.claude.json`
> - 自动化脚本默认支持两者（`--target auto`），会自动检测并配置所有存在的配置文件

有两种方式为项目添加 MCP 配置：

#### 方式 A：自动化脚本（推荐）

使用提供的脚本快速添加项目配置：

```bash
# 自动检测并配置 CLI 和 GUI（默认）
./add-project.sh add /你的/项目/路径

# 只配置 Claude CLI
./add-project.sh add --target cli /你的/项目/路径

# 只配置 Claude Code GUI
./add-project.sh add --target gui /你的/项目/路径

# 列出所有已配置的项目
./add-project.sh list

# 移除项目配置
./add-project.sh remove /你的/项目/路径
```

脚本会自动：
- ✅ 检测 CLI 和 GUI 配置文件
- ✅ 验证项目路径
- ✅ 备份现有配置
- ✅ 添加 MCP Server 配置
- ✅ 检查是否重复配置

#### 方式 B：手动编辑配置

**对于 Claude CLI**，编辑 `~/.claude.json`：

```json
{
  "projects": {
    "/你的/项目/路径": {
      "mcpServers": {
        "codex": {
          "command": "node",
          "args": ["/codex-mcp的绝对路径/dist/index.js"]
        }
      }
    }
  }
}
```

**对于 Claude Code GUI**，编辑 `~/.claude/.claude.json`（内容相同）。

将 `/codex-mcp的绝对路径` 替换为本项目的实际绝对路径（如 `/mnt/c/Users/95321/codex-mcp`）。

### 3. 重启 Claude Code

- **Claude CLI**: 无需重启，下次运行 `claude` 命令时自动加载
- **Claude Code GUI**: 需要重启桌面应用以加载新的 MCP 服务器

## 使用方法

### 基础示例

在 Claude Code 中，可以调用 Codex：

```typescript
// 示例调用
invoke_codex({
  task: "审查 src/auth.ts 中的认证代码，查找安全漏洞",
  projectPath: "/你的项目路径"
})
```

### 使用场景

#### 1. 代码审查

```typescript
invoke_codex({
  task: "审查 src/ 目录下所有 TypeScript 文件，查找潜在bug和安全问题",
  projectPath: "/项目路径",
  context: "重点关注输入验证和错误处理"
})
```

#### 2. 实现功能

```typescript
invoke_codex({
  task: "实现带邮件验证的密码重置功能",
  projectPath: "/项目路径",
  context: "使用现有的 UserService 和 EmailService 类"
})
```

#### 3. 修复 Bug

```typescript
invoke_codex({
  task: "修复 tests/auth.test.ts 中失败的测试",
  projectPath: "/项目路径"
})
```

#### 4. 重构代码

```typescript
invoke_codex({
  task: "重构数据库连接代码以使用连接池",
  projectPath: "/项目路径",
  context: "保持现有API接口不变"
})
```

#### 5. 生成测试

```typescript
invoke_codex({
  task: "为 src/services/payment.service.ts 创建全面的单元测试",
  projectPath: "/项目路径"
})
```

### 超时配置

**默认超时**: 30 分钟（1800 秒）

根据任务复杂度自定义超时：

```typescript
// 简单任务 - 5 分钟
invoke_codex({
  task: "格式化所有 TypeScript 文件",
  projectPath: "/项目路径",
  timeout: 300  // 5 分钟
})

// 中等任务 - 使用默认 30 分钟
invoke_codex({
  task: "重构认证模块",
  projectPath: "/项目路径"
  // timeout 省略，使用默认值 1800 秒
})

// 复杂任务 - 60 分钟
invoke_codex({
  task: "将整个项目从 JavaScript 迁移到 TypeScript",
  projectPath: "/项目路径",
  timeout: 3600  // 60 分钟
})
```

**推荐超时时间**：
- 代码审查、格式化：5-10 分钟
- 单文件实现、简单重构：10-20 分钟
- 多文件重构、功能实现：20-30 分钟（默认）
- 大规模迁移、全项目重构：30-60 分钟

**注意**：
- 超时时间过长可能掩盖死循环问题
- 建议将超大任务拆分为多个小任务
- `maxIterations` 参数（默认 15）也会限制执行时间

## 工作原理

### 1. 接收用户请求

```
用户: "让 Codex 实现一个登录功能"
```

### 2. 通过 MCP 调用 Codex

```typescript
invoke_codex({
  task: "在 src/auth/ 中实现基于 JWT 的登录功能",
  projectPath: "/home/user/my-app",
  context: "使用 bcrypt 进行密码哈希"
})
```

### 3. Codex 自主执行任务

Codex 将：
1. 读取现有文件
2. 理解代码库结构
3. 创建新文件
4. 修改现有文件
5. 运行测试
6. 迭代直到完成

### 4. 接收执行结果

```json
{
  "result": "登录功能实现成功...",
  "iterations": 1,
  "toolCallsExecuted": 5,
  "executionLog": [...]
}
```

## 两种工作模式

### 标准模式

**适用场景：** 简单任务、明确需求

```typescript
invoke_codex({
  task: "创建一个用户登录 API",
  projectPath: "/项目路径"
})
```

**特点：**
- Codex 自己分析和执行
- 适合单文件或明确任务

### 协同模式

**适用场景：** 复杂bug修复、跨文件重构

```typescript
invoke_codex({
  task: "修复 token 过期bug",
  projectPath: "/项目路径",
  context: {
    analysis: "auth.ts:45 缺少刷新逻辑，当前实现只在初始化时获取token",
    relatedFiles: ["auth.ts", "middleware.ts", "token.ts"],
    suggestedFix: "添加自动刷新机制，检测token即将过期时主动刷新",
    errorDetails: "Error: jwt expired",
    testCommand: "npm test -- auth"
  }
})
```

**特点：**
- Claude Code 先分析，Codex 直接执行
- 避免 Codex 重复分析
- 可选的自动测试验证
- 充分发挥两者优势

详细说明请参考 [COLLABORATIVE_MODE.zh-CN.md](./COLLABORATIVE_MODE.zh-CN.md)

## 工具参数

```typescript
interface InvokeCodexParams {
  task: string;              // 必需：任务描述
  projectPath: string;       // 必需：项目绝对路径
  context?: string | CollaborativeContext;  // 可选：额外上下文或协同上下文
  maxIterations?: number;    // 可选：最大迭代次数（默认：15）
}
```

### 协同上下文结构

```typescript
interface CollaborativeContext {
  analysis: string;          // Claude Code 的分析结果
  relatedFiles?: string[];   // 相关文件列表
  suggestedFix?: string;     // 建议的修复方案
  errorDetails?: string;     // 错误信息或日志
  testCommand?: string;      // 修复后运行的测试命令
}
```

## 使用示例

### 场景 1：协同修复 Bug

```
用户: "登录时会话一直过期，帮我修复一下"

Claude Code（内部分析）:
1. 搜索代码找到 auth.ts, session.ts
2. 分析发现session超时设置为60秒（太短）
3. 相关文件还有 middleware.ts

Claude Code（调用 Codex）:
[协同模式调用，传递分析结果]

Codex:
- 根据分析修改 session.ts 的超时时间
- 更新 middleware.ts 的session检查逻辑
- 运行测试验证

Claude Code（返回用户）:
"已修复session过期问题。Codex将超时时间从60秒改为30分钟，
并更新了中间件逻辑。所有测试通过。"
```

### 场景 2：自主实现功能

```
用户: "实现一个用户注册功能"

Claude Code:
[调用 Codex 标准模式]

Codex:
1. 创建 src/auth/register.service.ts
2. 创建 src/routes/register.routes.ts
3. 添加邮件验证
4. 创建测试文件
5. 运行测试：全部通过 ✓

Claude Code:
"注册功能已实现完成。Codex创建了注册服务、路由和测试。
包含邮件验证功能，所有测试通过。"
```

## 项目结构

```
codex-mcp/
├── src/
│   ├── index.ts                    # MCP 服务器入口
│   ├── types/
│   │   └── index.ts                # TypeScript 类型定义
│   └── tools/
│       ├── codex-cli-executor.ts   # Codex CLI 执行器
│       ├── invoke-codex.ts         # 主工具封装
│       ├── backup-manager.ts       # （未使用）
│       ├── command-executor.ts     # （未使用）
│       └── file-operations.ts      # （未使用）
├── dist/                           # 编译输出目录
├── COLLABORATIVE_MODE.zh-CN.md     # 协同模式文档
├── CLAUDE.zh-CN.md                 # 项目配置文档
├── README.md                       # 英文文档
├── README.zh-CN.md                 # 本文件
├── package.json
└── tsconfig.json
```

## 开发相关

### 构建

```bash
npm run build
```

### 开发模式（监听文件变化）

```bash
npm run dev
```

### 测试

```bash
npm test  # （待实现）
```

## 常见问题

**Q: Codex 可以访问项目目录外的文件吗？**
A: 不可以。Codex CLI 有内置沙箱保护，只能访问指定的项目目录。

**Q: 如果 Codex 出错怎么办？**
A: Codex CLI 会创建自动备份。出错后可以回滚或重新执行任务。

**Q: 使用成本如何？**
A: 取决于你使用的 Codex API。本地 CLI 调用你自己配置的 API endpoint。

**Q: 可以不用 Claude Code 单独使用吗？**
A: 不可以。MCP 服务器需要 MCP 客户端（如 Claude Code）才能工作，不能直接从命令行调用。

**Q: 是否适合生产代码？**
A: 可以，但需要注意：
- 始终审查 Codex 的修改再提交
- 使用版本控制（git）
- 充分测试
- 监控 API 使用成本

**Q: 如何调试问题？**
A: 检查 `invoke_codex` 返回的执行日志，它显示了每个操作和结果。

## 配置说明

### 无需环境变量

当前版本使用本地 Codex CLI，**不需要**配置 OpenAI API 密钥。
Codex CLI 使用你自己配置的 API endpoint。

### 配置 Codex CLI

确保本地 Codex CLI 已正确配置：

```bash
# 检查 Codex CLI 是否可用
codex --version

# 测试 Codex CLI
codex exec --help
```

Codex CLI 的配置文件位于 `~/.codex/config.toml`

## 故障排除

### "codex 命令未找到"

确保 Codex CLI 已安装并在 PATH 中：
```bash
which codex
```

### "项目不在 git 仓库中"

Codex CLI 默认需要 git 仓库。如果项目不是 git 仓库，CLI 会自动使用 `--skip-git-repo-check` 参数。

### "MCP 服务器未加载"

1. 检查配置文件路径是否正确
2. 确保使用绝对路径
3. 重启 Claude Code
4. 检查 `dist/index.js` 是否存在

### "任务执行超时"

Codex CLI 执行有 5 分钟超时。对于复杂任务：
- 拆分为多个小任务
- 增加 `maxIterations` 参数
- 查看执行日志了解进度

## 许可证

MIT

## 贡献

欢迎贡献！请提交 Issue 或 Pull Request。

## 支持

遇到问题请提交 GitHub Issue，并附上：
- 错误信息
- 任务描述
- 执行日志（如有）
- 环境信息（操作系统、Node 版本）

---

**项目地址**: `/mnt/c/Users/95321/codex-mcp/`
**文档**: 查看 [CLAUDE.zh-CN.md](./CLAUDE.zh-CN.md) 了解项目架构和开发规范
**协同模式**: 查看 [COLLABORATIVE_MODE.zh-CN.md](./COLLABORATIVE_MODE.zh-CN.md) 了解详细用法
