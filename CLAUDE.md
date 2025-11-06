# Codex MCP Server - Project Configuration

> MCP server connecting Claude Code with the local Codex CLI for collaborative programming.

**Languages**: [English](./CLAUDE.md) · [简体中文](./CLAUDE.zh-CN.md)

## Project Overview

### Objectives
Provide an MCP (Model Context Protocol) server that lets Claude Code call the local Codex CLI to execute coding tasks, enabling the two AIs to collaborate.

### Core Value Proposition
- **Collaborative Specialization**: Claude excels at analysis, Codex excels at execution.
- **Local Execution**: Everything runs locally for safety and control.
- **Automated Verification**: Optional test commands automatically validate fixes.
- **No Redundant Work**: Reduces repeated analysis and optimizes token usage.

## Architecture

### Tech Stack
- **Language**: TypeScript 5.7+
- **Runtime**: Node.js 18+
- **Protocol**: MCP (Model Context Protocol)
- **Transport**: stdio (standard input/output)
- **Dependencies**:
  - `@modelcontextprotocol/sdk` - MCP protocol implementation
  - `glob` - file matching utility

### Directory Layout
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

### Data Flow

```
User request
   ↓
Claude Code (analysis, decision-making)
   ↓ MCP Protocol (stdio JSON-RPC)
codex-mcp-server
   ├─ Standard mode: pass the task through
   └─ Collaborative mode: format the analysis output
   ↓
Codex CLI (codex exec --full-auto --json)
   ↓
Local file system (real modifications)
   ↓
Optional: automatic test run
   ↓
Return results
   ↓
Claude Code (present results to user)
```

## Module Overview

### 1. index.ts - MCP Server
**Responsibilities**:
- Implement the MCP protocol server.
- Register the `invoke_codex` tool.
- Handle tool invocation requests.
- Format returned results.

**Key Logic**:
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

### 2. codex-cli-executor.ts - Core Executor
**Responsibilities**:
- Run the local `codex exec` command.
- Parse JSONL event output.
- Handle collaborative context.
- Execute test commands.

**Key Methods**:
- `invoke()` - main execution method.
- `formatCollaborativePrompt()` - format the collaborative prompt.
- `executeCodexCLI()` - run the CLI command.
- `runTestCommand()` - execute tests.

**Codex CLI Parameters**:
```bash
codex exec \
    --full-auto \           # 自动执行，无交互
    --skip-git-repo-check \ # 允许非git目录
    --json \                # JSONL输出
    -C <projectPath> \      # 工作目录
    "<task + context>"      # 任务描述
```

### 3. types/index.ts - Type System
**Key Types**:

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

## Working Modes

### Standard Mode
**Use When**: straightforward tasks with clear requirements.

```typescript
invoke_codex({
    task: "创建一个用户登录API",
    projectPath: "/path/to/project"
})
```

**Traits**:
- Codex performs its own analysis and execution.
- Best for single-file or well-defined tasks.
- Higher token usage but usually completes in one pass.

### Collaborative Mode
**Use When**: complex bugs or cross-file refactors.

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

**Traits**:
- Claude analyzes first; Codex executes immediately.
- Avoids redundant analysis by Codex.
- Optional automatic test verification.
- Leverages both agents' strengths.

See also: [COLLABORATIVE_MODE.md](./COLLABORATIVE_MODE.md)

## Development Guidelines

### TypeScript Guidelines
- Every public API must include type annotations.
- Use `interface` to define data structures.
- Avoid `any`; prefer `unknown` or specific types.
- Export types for external usage.

### Error Handling
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

### Logging Guidelines
- **stdout**: JSON-RPC messages only (MCP requirement).
- **stderr**: all logs and debug information.
- Use `console.error()` for logging.
- Tag key events with emojis (🤖 ✅ ❌ 🧪).

### Security Considerations
- **Path validation**: Codex CLI has a sandbox, but still validate paths.
- **Command injection**: use array parameters for bash commands instead of string concatenation.
- **Timeout guard**: Codex CLI calls timeout after 5 minutes.
- **Test timeout**: test commands timeout after 2 minutes.

## Development Workflow

### Local Development
```bash
# Install dependencies
npm install

# Development mode (watch files)
npm run dev

# Build
npm run build

# Run
npm start
```

### Testing
```bash
# Unit tests (TBD)
npm test

# Manual test: call the CLI directly
node dist/index.js

# Then send a JSON-RPC request (use test script if available)
```

### Release Process
1. Update the version number (`package.json`).
2. Update the CHANGELOG (TBD).
3. Run tests (TBD).
4. Build: `npm run build`.
5. Create a Git tag: `git tag v1.x.x`.
6. Commit the code.

### Claude Code Integration
Edit `~/.claude/.claude.json`:
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

Restart Claude Code to apply changes.

## Design Principles

### 1. Favor Simplicity
- Initial designs included backup and security modules that proved unnecessary.
- Codex CLI already supplies sandboxing and safety.
- Keep the MCP server focused on bridging Claude Code and the Codex CLI.

### 2. Collaboration Over Competition
- Not "Claude reviews Codex" (no objective rubric).
- Instead "Claude analyzes + Codex executes" (play to strengths).
- Test results provide the objective validation.

### 3. Local First
- Switched from remote API to local CLI.
- Safer, faster, and more controllable.
- Produces actual file changes rather than simulations.

### 4. Backward Compatible
- Collaborative mode extends standard mode.
- The `context` parameter accepts both strings and objects.
- Existing invocation patterns continue to work.

## FAQ

### Q: Why not use the OpenAI API?
A: We initially used the API, but third-party keys lacked function calling, and remote execution could not edit files for real. Switching to the local Codex CLI resolved those issues.

### Q: Why are backup-manager and similar modules unused?
A: Early iterations expected the MCP server to manipulate files directly and needed backups. After delegating to the Codex CLI, those safeguards belong inside the CLI, so the MCP layer no longer duplicates them.

### Q: Why does the collaborative mode `testCommand` sometimes not run?
A: The `context` may be serialized as a JSON string, causing type checks to fail. We are working on improvements.

### Q: How do I debug the MCP server?
A: MCP relies on stdio, so stdout is reserved. Send all debugging output to stderr, then inspect Claude Code logs or redirect stderr to a file.

## Future Improvements

### Short Term
- [ ] Implement unit tests.
- [ ] Fix the `testCommand` detection logic.
- [ ] Add more usage examples.

### Mid Term
- [ ] Support streaming output (show Codex progress in real time).
- [ ] Capture performance metrics.
- [ ] Smart cost tuning (auto-select mode).

### Long Term
- [ ] Context memory (learn project structure).
- [ ] Automatic task decomposition.
- [ ] Run multiple Codex instances in parallel.

---

**Project Location**: `/mnt/c/Users/95321/codex-mcp/`
**Last Updated**: 2025-11-05
**Maintainers**: Claude Code + Codex collaborative team
