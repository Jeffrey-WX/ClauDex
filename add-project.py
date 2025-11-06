#!/usr/bin/env python3
"""
Codex MCP 项目配置工具

自动为新项目添加 Codex MCP Server 配置到 Claude CLI 或 Claude Code GUI。
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


class CodexProjectConfigurator:
    def __init__(self, target='auto'):
        """
        初始化配置器

        Args:
            target: 配置目标 ('cli', 'gui', 'auto')
                - 'cli': Claude CLI (命令行工具)
                - 'gui': Claude Code GUI (图形界面)
                - 'auto': 自动检测并配置两者
        """
        self.target = target
        self.cli_config = Path.home() / '.claude.json'
        self.gui_config = Path.home() / '.claude' / '.claude.json'
        self.codex_mcp_path = Path(__file__).parent / 'dist' / 'index.js'

    def get_config_files(self):
        """根据目标返回需要操作的配置文件"""
        if self.target == 'cli':
            return [('CLI', self.cli_config)]
        elif self.target == 'gui':
            return [('GUI', self.gui_config)]
        else:  # auto
            configs = []
            if self.cli_config.exists():
                configs.append(('CLI', self.cli_config))
            if self.gui_config.exists():
                configs.append(('GUI', self.gui_config))

            if not configs:
                print("❌ 未找到任何 Claude 配置文件")
                print(f"   CLI 配置: {self.cli_config}")
                print(f"   GUI 配置: {self.gui_config}")
                print("\n   请先运行 Claude CLI 或 Claude Code 并打开一个项目")
                sys.exit(1)

            return configs

    def load_config(self, config_file):
        """加载现有配置"""
        if not config_file.exists():
            return None

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  配置文件格式错误: {config_file}")
            print(f"   错误: {e}")
            return None

    def save_config(self, config_file, config, label):
        """保存配置（带备份）"""
        # 备份原配置
        backup_file = config_file.with_suffix(
            f'.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        shutil.copy2(config_file, backup_file)
        print(f"✓ 已备份 {label} 配置: {backup_file.name}")

        # 保存新配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def add_project(self, project_path):
        """为项目添加 Codex MCP 配置"""
        # 验证项目路径
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            print(f"❌ 项目路径不存在: {project_path}")
            sys.exit(1)

        if not project_path.is_dir():
            print(f"❌ 路径不是目录: {project_path}")
            sys.exit(1)

        project_path_str = str(project_path)

        # 验证 Codex MCP Server
        if not self.codex_mcp_path.exists():
            print(f"❌ Codex MCP Server 未构建: {self.codex_mcp_path}")
            print("   请先运行: npm run build")
            sys.exit(1)

        # 获取要操作的配置文件
        configs = self.get_config_files()

        modified_count = 0
        skipped_count = 0

        for label, config_file in configs:
            print(f"\n🔧 处理 {label} 配置...")

            # 加载配置
            config = self.load_config(config_file)
            if config is None:
                print(f"⚠️  跳过 {label} 配置（文件不存在或无效）")
                skipped_count += 1
                continue

            # 确保 projects 键存在
            if 'projects' not in config:
                config['projects'] = {}

            # 检查项目是否已配置
            if project_path_str in config['projects']:
                if 'mcpServers' in config['projects'][project_path_str]:
                    if 'codex' in config['projects'][project_path_str]['mcpServers']:
                        print(f"ℹ️  {label}: 项目已配置 Codex MCP")
                        skipped_count += 1
                        continue

            # 添加项目配置
            if project_path_str not in config['projects']:
                config['projects'][project_path_str] = {
                    "allowedTools": [],
                    "mcpContextUris": [],
                    "mcpServers": {},
                    "enabledMcpjsonServers": [],
                    "disabledMcpjsonServers": [],
                    "hasTrustDialogAccepted": True,
                    "ignorePatterns": [],
                    "projectOnboardingSeenCount": 1
                }

            # 添加 Codex MCP Server
            if 'mcpServers' not in config['projects'][project_path_str]:
                config['projects'][project_path_str]['mcpServers'] = {}

            config['projects'][project_path_str]['mcpServers']['codex'] = {
                "command": "node",
                "args": [str(self.codex_mcp_path)]
            }

            # 保存配置
            self.save_config(config_file, config, label)
            print(f"✅ {label}: 成功添加 Codex MCP 配置")
            modified_count += 1

        # 总结
        print(f"\n📊 配置结果:")
        print(f"   成功: {modified_count}")
        print(f"   跳过: {skipped_count}")

        if modified_count > 0:
            print(f"\n✅ 项目: {project_path_str}")
            print(f"   MCP Server: {self.codex_mcp_path}")
            print(f"\n📝 下一步:")
            if any(label == 'CLI' for label, _ in configs if _ in [c[1] for c in configs]):
                print(f"   CLI: 在项目目录运行 'claude' 命令")
            if any(label == 'GUI' for label, _ in configs if _ in [c[1] for c in configs]):
                print(f"   GUI: 重启 Claude Code 应用")
            print(f"   然后在项目中使用: '使用 Codex 创建...'")

    def list_projects(self):
        """列出所有已配置 Codex MCP 的项目"""
        configs = self.get_config_files()

        all_projects = {}

        for label, config_file in configs:
            config = self.load_config(config_file)
            if config is None:
                continue

            if 'projects' not in config:
                continue

            for project_path, project_config in config['projects'].items():
                if 'mcpServers' in project_config:
                    if 'codex' in project_config['mcpServers']:
                        if project_path not in all_projects:
                            all_projects[project_path] = []
                        all_projects[project_path].append(label)

        if not all_projects:
            print("没有项目配置了 Codex MCP")
        else:
            print(f"\n已配置 Codex MCP 的项目 ({len(all_projects)}):\n")
            for i, (project, labels) in enumerate(sorted(all_projects.items()), 1):
                labels_str = ', '.join(labels)
                print(f"  {i}. {project}")
                print(f"     └─ 配置在: {labels_str}")

    def remove_project(self, project_path):
        """移除项目的 Codex MCP 配置"""
        project_path = str(Path(project_path).resolve())
        configs = self.get_config_files()

        removed_count = 0

        for label, config_file in configs:
            config = self.load_config(config_file)
            if config is None:
                continue

            if 'projects' not in config or project_path not in config['projects']:
                continue

            if 'mcpServers' in config['projects'][project_path]:
                if 'codex' in config['projects'][project_path]['mcpServers']:
                    del config['projects'][project_path]['mcpServers']['codex']
                    self.save_config(config_file, config, label)
                    print(f"✅ {label}: 已移除 Codex MCP 配置")
                    removed_count += 1

        if removed_count == 0:
            print(f"ℹ️  项目未配置 Codex MCP: {project_path}")
        else:
            print(f"\n📊 从 {removed_count} 个配置中移除")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Codex MCP 项目配置工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s add /home/user/my-project          # 自动配置（CLI + GUI）
  %(prog)s add --target cli /path/to/project  # 只配置 CLI
  %(prog)s add --target gui /path/to/project  # 只配置 GUI
  %(prog)s list                                # 列出已配置项目
  %(prog)s remove /path/to/project            # 移除项目配置
        """
    )

    parser.add_argument('command', choices=['add', 'list', 'remove'],
                        help='操作命令')
    parser.add_argument('path', nargs='?',
                        help='项目路径 (add/remove 命令需要)')
    parser.add_argument('--target', choices=['cli', 'gui', 'auto'], default='auto',
                        help='配置目标: cli (命令行), gui (图形界面), auto (自动检测，默认)')

    args = parser.parse_args()

    configurator = CodexProjectConfigurator(target=args.target)

    if args.command == 'add':
        if not args.path:
            print("❌ 请指定项目路径")
            print("   用法: add-project.py add <项目路径>")
            sys.exit(1)
        configurator.add_project(args.path)

    elif args.command == 'list':
        configurator.list_projects()

    elif args.command == 'remove':
        if not args.path:
            print("❌ 请指定项目路径")
            print("   用法: add-project.py remove <项目路径>")
            sys.exit(1)
        configurator.remove_project(args.path)


if __name__ == '__main__':
    main()
