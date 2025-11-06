[English](COLLABORATIVE_MODE.md) | [简体中文](COLLABORATIVE_MODE.zh-CN.md)

# Collaborative Mode: Claude Code + Codex

## Overview

Collaborative mode lets Claude Code and Codex split responsibilities when fixing bugs or delivering features:
- **Claude Code**: analysis, search, reasoning
- **Codex**: execution, edits, implementation

This avoids duplicate analysis work and lets each agent play to its strengths.

## Workflow

```
User request
   ↓
Claude Code analyzes
   ↓ (passes structured context)
Codex applies the fix
   ↓
Tests run automatically
   ↓
Results go back to Claude Code
   ↓
Delivered to the user
```

## Usage

### Standard Mode (simple tasks)

```typescript
// Claude Code invokes Codex directly
invoke_codex({
  task: "Create a user login API",
  projectPath: "/path/to/project"
})
```

### Collaborative Mode (complex bug fixes)

```typescript
// Claude Code analyzes first, then calls Codex
invoke_codex({
  task: "Fix the token expiration bug",
  projectPath: "/path/to/project",
  context: {
    analysis: "The issue lives in auth.ts:45 where the token refresh logic is missing. The current implementation only fetches a token at startup and never handles expiration.",
    relatedFiles: [
      "src/auth/auth.ts",
      "src/middleware/auth-middleware.ts",
      "src/utils/token.ts"
    ],
    suggestedFix: "Add an automatic refresh mechanism in auth.ts that renews the token before it expires. Update the middleware to detect expiration and retry.",
    errorDetails: "Error: jwt expired\\n  at verify (/node_modules/jsonwebtoken/verify.js:224:19)",
    testCommand: "npm test -- auth"  // Optional: run after the fix
  }
})
```

## Collaborative Context Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `analysis` | string | ✅ | Claude Code's analysis output |
| `relatedFiles` | string[] | ❌ | List of related files |
| `suggestedFix` | string | ❌ | Suggested fix plan |
| `errorDetails` | string | ❌ | Error messages or logs |
| `testCommand` | string | ❌ | Test command to run after the fix |

## Result Payload

```typescript
{
  result: "Description of the completed fix",
  executionLog: [
    { tool: "write_file", args: {...}, timestamp: "..." }
  ],
  iterations: 1,
  testResult: {  // If testCommand was provided
    success: true,
    output: "All tests passed",
    exitCode: 0
  }
}
```

## Practical Examples

### Example 1: Fixing an API bug

```typescript
// 1. User report: "POST /api/users returns a 500 error"

// 2. Claude Code actions
//    - Search the codebase and find routes/users.ts
//    - Read the file and notice missing error handling
//    - Inspect controllers/user-controller.ts for related logic

// 3. Claude Code calls Codex
invoke_codex({
  task: "Fix the 500 error for POST /api/users",
  context: {
    analysis: "routes/users.ts:23 calls createUser without catching exceptions. When the database connection fails the unhandled error bubbles up and returns 500.",
    relatedFiles: [
      "routes/users.ts",
      "controllers/user-controller.ts"
    ],
    suggestedFix: "Wrap the call in routes/users.ts in try/catch and return an appropriate status code and message.",
    testCommand: "npm test -- routes/users"
  }
})

// 4. Codex applies the fix

// 5. Tests run for verification

// 6. Return the result to the user
```

### Example 2: Performance optimization

```typescript
invoke_codex({
  task: "Optimize the user list query performance",
  context: {
    analysis: "users.service.ts:45 implements getAllUsers with an N+1 query. Each user triggers a separate profile lookup, so 1000 users produce 1000 database queries.",
    relatedFiles: [
      "services/users.service.ts",
      "models/user.model.ts",
      "models/profile.model.ts"
    ],
    suggestedFix: "Use a JOIN or eager loading to fetch everything in a single query",
    testCommand: "npm run test:performance"
  }
})
```

## Benefits

✅ **Avoid duplicate analysis** - Codex executes directly on Claude's insights  
✅ **Leverage complementary strengths** - Claude analyzes while Codex implements  
✅ **Automated verification** - Optional test commands ensure the fix works  
✅ **Lower token usage** - Skip re-analyzing the same code  
✅ **Higher success rate** - Structured context keeps Codex focused

## When to Use Collaborative Mode

**Great for:**
- Complex bugs spanning multiple files
- Performance issues that require deep analysis
- Refactors that touch multiple modules
- Bugs with ambiguous error messages

**Avoid when:**
- Simple one-file edits
- Clearly scoped new features
- Mechanical tasks like formatting

## Timeout Configuration

Collaborative mode lets you set a custom timeout (30 minutes by default):

```typescript
invoke_codex({
  task: "Fix an auth bug",
  context: {
    analysis: "...",
    relatedFiles: ["auth.ts"],
    suggestedFix: "...",
    testCommand: "npm test -- auth"
  },
  timeout: 1200  // 20 minutes
})
```

**Suggested timeouts:**
- Simple bug fixes: 10–15 minutes
- Complex refactors: 20–30 minutes
- Large-scale changes: 30–60 minutes

If tasks time out often, consider:
1. Splitting into smaller subtasks
2. Simplifying `suggestedFix` so the direction is clearer
3. Trimming `relatedFiles` to only the essential files

## Tips

1. **Keep Claude's analysis accurate** - Codex assumes the guidance is correct
2. **Provide enough context** - Related files and error details matter
3. **Keep test commands fast** - Avoid full suites that exceed the two-minute limit
4. **This is collaboration, not review** - Claude is not auditing Codex's code
5. **Tune the timeout** - Match duration to task complexity

## Standard Mode vs Collaborative Mode

| Dimension | Standard Mode | Collaborative Mode |
|-----------|---------------|--------------------|
| Analysis | Codex analyzes on its own | Claude supplies the analysis |
| Best for | Simple tasks | Complex bugs |
| Token usage | Codex needs more tokens | Combined usage is optimized |
| Accuracy | Depends on Codex alone | Combines both strengths |
| Verification | Manual | Can run automated tests |

