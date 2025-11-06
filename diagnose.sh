 #!/bin/bash
  echo "=== Codex MCP Diagnostics ==="
  echo ""
  echo "1. Node/npm versions:"
  node --version
  npm --version
  echo ""
  echo "2. MCP files exist:"
  ls -lh /mnt/c/Users/95321/codex-mcp/dist/index.js
  echo ""
  echo "3. Config content:"
  jq '.projects."/mnt/c/Users/95321".mcpServers.codex' /home/w/.claude/.claude.json
  echo ""
  echo "4. Server test:"
  timeout 2 node /mnt/c/Users/95321/codex-mcp/dist/index.js 2>&1 | head -5
  echo ""
  echo "5. Recent logs:"
  tail -50 /home/w/.claude/debug/*.log 2>/dev/null | grep -i "mcp\|codex" | tail -15
