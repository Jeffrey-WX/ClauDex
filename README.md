[English](README.md) | [简体中文](README.zh-CN.md)

# Codex MCP Server

An MCP server that connects Claude Code with the local Codex CLI to enable collaborative programming.

## Key Features

- 🤖 **Local Codex CLI integration**: Execute Codex commands directly on your machine
- 🤝 **Collaborative mode**: Claude Code analyzes while Codex executes so each agent plays to its strengths
- 📁 **Full filesystem access**: Codex can read, write, and create project files
- ⚙️ **Command execution**: Automatically run tests, builds, and other commands
- ✅ **Automated test verification**: Optionally execute tests after applying fixes
- 📊 **Execution logs**: Track every operation in detail
- 🔒 **Local safety**: All actions run through the local Codex CLI

## Architecture Overview

```
Claude Code
    ↓ MCP Protocol
codex-mcp-server
    ├── invoke_codex (standard mode)
    │   └── Simple tasks
    └── invoke_codex (collaborative mode)
        ├── Claude analysis
        ├── Codex execution
        └── Automated test verification
            ↓
    Local Codex CLI
        └── Real file changes
```

## New Feature: Collaborative Mode

For full documentation see [COLLABORATIVE_MODE.md](./COLLABORATIVE_MODE.md)

**Quick example:**

```typescript
// Claude Code analyzes first, then invokes:
invoke_codex({
  task: "Fix the authentication bug",
  context: {
    analysis: "auth.ts:45 is missing token refresh logic",
    relatedFiles: ["auth.ts", "middleware.ts"],
    testCommand: "npm test -- auth"
  }
})
```

## Installation & Setup

### Prerequisites

- Node.js 18+
- **Codex CLI** installed and configured (https://codex.anthropic.com)
- Claude Code

### 1. Install dependencies

```bash
cd codex-mcp
npm install
npm run build
```

### 2. Add to Claude Code

> **Note: CLI vs GUI configuration**
> - **Claude CLI** (the command-line `claude` tool) uses the config file: `~/.claude.json`
> - **Claude Code GUI** (desktop app) uses the config file: `~/.claude/.claude.json`
> - The automation script supports both (`--target auto`) and will detect and configure every available file

There are two ways to add the MCP configuration to your project:

#### Option A: Automation script (recommended)

Use the provided script to add the project quickly:

```bash
# Automatically detect and configure both CLI and GUI (default)
./add-project.sh add /path/to/your/project

# Configure Claude CLI only
./add-project.sh add --target cli /path/to/your/project

# Configure Claude Code GUI only
./add-project.sh add --target gui /path/to/your/project

# List every configured project
./add-project.sh list

# Remove a project configuration
./add-project.sh remove /path/to/your/project
```

The script automatically:
- ✅ Detects CLI and GUI config files
- ✅ Validates the project path
- ✅ Backs up existing configuration
- ✅ Adds the MCP server configuration
- ✅ Checks for duplicates

#### Option B: Manual configuration

**For Claude CLI**, edit `~/.claude.json`:

```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "codex": {
          "command": "node",
          "args": ["/absolute/path/to/codex-mcp/dist/index.js"]
        }
      }
    }
  }
}
```

**For Claude Code GUI**, edit `~/.claude/.claude.json` (same content).

Replace `/absolute/path/to/codex-mcp` with the absolute path to this project (for example `/mnt/c/Users/95321/codex-mcp`).

### 3. Restart Claude Code

- **Claude CLI**: No restart required; the next `claude` command picks up the changes automatically
- **Claude Code GUI**: Restart the desktop app to load the new MCP server

## Usage

### Basic example

In Claude Code, you can invoke Codex:

```typescript
// Example invocation
invoke_codex({
  task: "Review the authentication code in src/auth.ts and look for security issues",
  projectPath: "/path/to/your/project"
})
```

### Common scenarios

#### 1. Code review

```typescript
invoke_codex({
  task: "Review every TypeScript file in src/ for potential bugs and security issues",
  projectPath: "/path/to/your/project",
  context: "Focus on input validation and error handling"
})
```

#### 2. Feature implementation

```typescript
invoke_codex({
  task: "Implement a password reset flow with email verification",
  projectPath: "/path/to/your/project",
  context: "Reuse the existing UserService and EmailService classes"
})
```

#### 3. Bug fixing

```typescript
invoke_codex({
  task: "Fix the failing tests in tests/auth.test.ts",
  projectPath: "/path/to/your/project"
})
```

#### 4. Refactoring

```typescript
invoke_codex({
  task: "Refactor the database connection code to use a connection pool",
  projectPath: "/path/to/your/project",
  context: "Keep the existing API surface intact"
})
```

#### 5. Test generation

```typescript
invoke_codex({
  task: "Create comprehensive unit tests for src/services/payment.service.ts",
  projectPath: "/path/to/your/project"
})
```

### Timeout configuration

**Default timeout**: 30 minutes (1800 seconds)

Adjust the timeout based on task complexity:

```typescript
// Simple task - 5 minutes
invoke_codex({
  task: "Format every TypeScript file",
  projectPath: "/path/to/your/project",
  timeout: 300  // 5 minutes
})

// Medium task - use the 30 minute default
invoke_codex({
  task: "Refactor the authentication module",
  projectPath: "/path/to/your/project"
  // timeout omitted, defaults to 1800 seconds
})

// Complex task - 60 minutes
invoke_codex({
  task: "Migrate the entire project from JavaScript to TypeScript",
  projectPath: "/path/to/your/project",
  timeout: 3600  // 60 minutes
})
```

**Recommended timeouts:**
- Code review, formatting: 5–10 minutes
- Single-file implementation, small refactors: 10–20 minutes
- Multi-file refactors, feature work: 20–30 minutes (default)
- Large migrations, whole-project refactors: 30–60 minutes

**Notes:**
- Excessively long timeouts can hide infinite loop issues
- Consider breaking very large tasks into smaller ones
- The `maxIterations` parameter (default 15) also limits execution time

## How it works

### 1. Receive the user request

```
User: "Have Codex implement a login feature"
```

### 2. Invoke Codex via MCP

```typescript
invoke_codex({
  task: "Implement JWT-based login in src/auth/",
  projectPath: "/home/user/my-app",
  context: "Use bcrypt for password hashing"
})
```

### 3. Codex executes autonomously

Codex will:
1. Read existing files
2. Understand the project structure
3. Create new files
4. Modify existing files
5. Run tests
6. Iterate until the task completes

### 4. Receive the result

```json
{
  "result": "Login feature implemented successfully...",
  "iterations": 1,
  "toolCallsExecuted": 5,
  "executionLog": [...]
}
```

## Two operating modes

### Standard mode

**Best for:** Small tasks with clear requirements

```typescript
invoke_codex({
  task: "Create a user login API",
  projectPath: "/path/to/your/project"
})
```

**Characteristics:**
- Codex performs both analysis and execution
- Ideal for single-file or well-defined work

### Collaborative mode

**Best for:** Complex bug fixes and cross-file refactors

```typescript
invoke_codex({
  task: "Fix the token expiration bug",
  projectPath: "/path/to/your/project",
  context: {
    analysis: "auth.ts:45 is missing a refresh flow; the current implementation fetches the token only during initialization",
    relatedFiles: ["auth.ts", "middleware.ts", "token.ts"],
    suggestedFix: "Add an automatic refresh mechanism that proactively refreshes the token before it expires",
    errorDetails: "Error: jwt expired",
    testCommand: "npm test -- auth"
  }
})
```

**Characteristics:**
- Claude Code performs the analysis; Codex handles execution
- Avoids duplicated analysis work by Codex
- Optional automated test verification
- Lets each agent focus on its strengths

See [COLLABORATIVE_MODE.md](./COLLABORATIVE_MODE.md) for details.

## Tool parameters

```typescript
interface InvokeCodexParams {
  task: string;              // Required: task description
  projectPath: string;       // Required: absolute project path
  context?: string | CollaborativeContext;  // Optional: extra context or collaborative context
  maxIterations?: number;    // Optional: maximum iterations (default: 15)
}
```

### Collaborative context structure

```typescript
interface CollaborativeContext {
  analysis: string;          // Claude Code's analysis
  relatedFiles?: string[];   // Relevant file list
  suggestedFix?: string;     // Suggested fix strategy
  errorDetails?: string;     // Error messages or logs
  testCommand?: string;      // Tests to run after the fix
}
```

## Usage examples

### Scenario 1: Collaborative bug fix

```
User: "Sessions keep expiring during login—please fix it."

Claude Code (internal analysis):
1. Search the codebase and find auth.ts, session.ts
2. Analysis shows session timeout is set to 60 seconds (too short)
3. Related files include middleware.ts

Claude Code (invokes Codex):
[Collaborative mode call with analysis]

Codex:
- Adjusts the session timeout in session.ts
- Updates the session check logic in middleware.ts
- Runs tests to verify

Claude Code (reports back to the user):
"Session expiration issue fixed. Codex increased the timeout from 60 seconds to 30 minutes and updated the middleware logic. All tests passed."
```

### Scenario 2: Autonomous feature implementation

```
User: "Implement a user registration feature."

Claude Code:
[Standard mode invocation]

Codex:
1. Creates src/auth/register.service.ts
2. Creates src/routes/register.routes.ts
3. Adds email verification
4. Creates test files
5. Runs tests: all green ✓

Claude Code:
"Registration feature implemented. Codex created the service, routes, and tests with email verification. All tests passed."
```

## Project structure

```
codex-mcp/
├── src/
│   ├── index.ts                    # MCP server entry point
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   └── tools/
│       ├── codex-cli-executor.ts   # Codex CLI executor
│       ├── invoke-codex.ts         # Primary tool wrapper
│       ├── backup-manager.ts       # (unused)
│       ├── command-executor.ts     # (unused)
│       └── file-operations.ts      # (unused)
├── dist/                           # Build output
├── COLLABORATIVE_MODE.md           # Collaborative mode documentation
├── CLAUDE.md                       # Project configuration guide
├── README.md                       # English documentation (this file)
├── README.zh-CN.md                 # Simplified Chinese documentation
├── package.json
└── tsconfig.json
```

## Development

### Build

```bash
npm run build
```

### Watch mode

```bash
npm run dev
```

### Testing

```bash
npm test  # (to be implemented)
```

## FAQ

**Q: Can Codex access files outside the project directory?**  
A: No. The Codex CLI enforces a sandbox and can only access the specified project directory.

**Q: What if Codex encounters an error?**  
A: The Codex CLI creates automatic backups. You can roll back or rerun the task if something goes wrong.

**Q: What does it cost to use?**  
A: It depends on the Codex API you configured. The local CLI uses your own API endpoint.

**Q: Can I use this without Claude Code?**  
A: No. The MCP server requires an MCP client (such as Claude Code); it cannot be called directly from the command line.

**Q: Is it suitable for production code?**  
A: Yes, but keep in mind:
- Always review Codex's changes before committing
- Use version control (git)
- Test thoroughly
- Monitor API usage costs

**Q: How do I debug issues?**  
A: Review the `invoke_codex` execution log. It shows every action and result.

## Configuration

### No environment variables required

This version relies on the local Codex CLI, so **no** OpenAI API key configuration is needed. The Codex CLI uses the endpoint you configured locally.

### Configure the Codex CLI

Ensure the local Codex CLI is set up correctly:

```bash
# Check whether the Codex CLI is available
codex --version

# Basic Codex CLI check
codex exec --help
```

The Codex CLI configuration file is located at `~/.codex/config.toml`.

## Troubleshooting

### "codex command not found"

Make sure the Codex CLI is installed and on your PATH:

```bash
which codex
```

### "Project is not in a git repository"

The Codex CLI expects a git repository. If your project is not in git, the CLI automatically uses the `--skip-git-repo-check` flag.

### "MCP server not loaded"

1. Verify the configuration file path
2. Ensure you are using absolute paths
3. Restart Claude Code
4. Check that `dist/index.js` exists

### "Task execution timed out"

The Codex CLI enforces a 5-minute timeout. For complex tasks:
- Split the work into smaller tasks
- Increase the `maxIterations` parameter
- Inspect the execution log to understand progress

## License

MIT

## Contributing

Contributions are welcome! Open an issue or submit a pull request.

## Support

If you run into issues, open a GitHub issue and include:
- Error details
- Task description
- Execution log (if available)
- Environment information (OS, Node version)

---

**Project path**: `/mnt/c/Users/95321/codex-mcp/`  
**Documentation**: See [CLAUDE.md](./CLAUDE.md) for project architecture and development guidelines  
**Collaborative mode**: See [COLLABORATIVE_MODE.md](./COLLABORATIVE_MODE.md) for full usage details

