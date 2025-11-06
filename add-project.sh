#!/bin/bash
#
# Codex MCP 项目配置工具 - Bash 包装脚本
#
# 用法:
#   ./add-project.sh add <项目路径>     # 添加项目
#   ./add-project.sh list                # 列出已配置项目
#   ./add-project.sh remove <项目路径>   # 移除项目配置
#

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/add-project.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 python3${NC}"
    echo "   请先安装 Python 3"
    exit 1
fi

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ 找不到 Python 脚本: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 执行 Python 脚本
python3 "$PYTHON_SCRIPT" "$@"
