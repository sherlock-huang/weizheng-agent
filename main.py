#!/usr/bin/env python3
"""
魏征 Agent - 入口文件

使用方式:
    python main.py [选项]

示例:
    python main.py --intensity high
    python main.py --interactive
    python main.py --content "要审查的代码或文案"

触发词：
    "魏征，你怎么看？" - 激活Agent开始提意见
"""

import os
import sys
import argparse
import json
from pathlib import Path

# 确保可以导入src模块
sys.path.insert(0, str(Path(__file__).parent))

from src.core.agent import WeizhengAgent, CriticIntensity
from src.config.settings import get_settings, create_default_config
from src.utils.helpers import parse_intensity


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     魏征 Agent - 专门提反对意见、挑毛病的独立Agent            ║
║     Weizheng Agent - The Critical Voice                     ║
║                                                              ║
║     触发词："魏征，你怎么看？"                                ║
║     Trigger: "Weizheng, what do you think?"                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_stats(agent: WeizhengAgent):
    """打印Agent统计信息"""
    stats = agent.get_stats()
    print("\n[Agent 统计信息]:")
    print(f"   对话次数: {stats['conversation_count']}")
    print(f"   累计批判: {stats['total_critics_made']}")
    print(f"   当前强度: {stats['current_intensity']}")
    print(f"   洞察积累: {stats['insights_count']}")


def interactive_mode(agent: WeizhengAgent):
    """交互模式"""
    print("\n[进入交互模式]")
    print("提示：")
    print("  - 输入 '魏征，你怎么看？' 触发Agent")
    print("  - 输入 '/intensity <强度>' 调整反对强度 (low/medium/high/extreme)")
    print("  - 输入 '/stats' 查看统计")
    print("  - 输入 '/quit' 或 '/exit' 退出")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n[你]: ").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.startswith('/'):
                cmd = user_input[1:].lower()
                
                if cmd in ['quit', 'exit', 'q']:
                    print("\n[魏征告退...]")
                    break
                
                elif cmd == 'stats':
                    print_stats(agent)
                    continue
                
                elif cmd.startswith('intensity '):
                    intensity_str = cmd[10:].strip()
                    try:
                        intensity = CriticIntensity(parse_intensity(intensity_str))
                        agent.set_intensity(intensity)
                        print(f"[OK] 反对强度已设置为: {intensity.value}")
                    except ValueError:
                        print("[Error] 无效的强度值，请使用: low/medium/high/extreme")
                    continue
                
                elif cmd == 'help':
                    print("""
可用命令：
  /intensity <level>  - 设置反对强度 (low/medium/high/extreme)
  /stats             - 查看统计信息
  /help              - 显示帮助
  /quit 或 /exit     - 退出
                    """)
                    continue
                
                else:
                    print(f"[?] 未知命令: {cmd}")
                    continue
            
            # 处理内容
            print("\n[魏征思考中...]")
            result = agent.process(user_input)
            
            # 输出结果
            print(f"\n魏征 [{result['intensity']}]: {result['agent_personality']}")
            print(f"\n[总结] {result['summary']}")
            
            if result['critics']:
                print("\n详细意见：")
                for i, critic in enumerate(result['critics'][:5], 1):  # 最多显示5条
                    severity_icon = {"critical": "[C]", "major": "[M]", "minor": "[m]", "suggestion": "[S]"}.get(
                        critic.get('severity', 'minor'), "⚪"
                    )
                    print(f"\n{severity_icon} {i}. {critic['title']}")
                    print(f"   {critic['critique']}")
                    if critic.get('suggestion'):
                        print(f"   [建议] {critic['suggestion']}")
            
            if result['suggestions']:
                print("\n[核心建议]:")
                for suggestion in result['suggestions'][:3]:
                    print(f"   - {suggestion}")
        
        except KeyboardInterrupt:
            print("\n\n👋 魏征告退...")
            break
        except Exception as e:
            print(f"\n[Error] 错误: {e}")


def single_review(agent: WeizhengAgent, content: str, content_type: str = "general"):
    """单次审查"""
    print("\n[魏征正在审查...]")
    result = agent.process(content, content_type)
    
    print(f"\n{'='*60}")
    print(f"魏征 [{result['intensity'].upper()}]: {result['agent_personality']}")
    print(f"{'='*60}")
    
    print(f"\n[统计] {result['summary']}")
    
    if result['critics']:
        print(f"\n[发现] {len(result['critics'])} 个问题：")
        print("-" * 60)
        
        severity_order = {"critical": 0, "major": 1, "minor": 2, "suggestion": 3}
        sorted_critics = sorted(result['critics'], 
                               key=lambda x: severity_order.get(x.get('severity', 'minor'), 4))
        
        for i, critic in enumerate(sorted_critics, 1):
            severity = critic.get('severity', 'minor')
            icons = {"critical": "[C]", "major": "[M]", "minor": "[m]", "suggestion": "[S]"}
            icon = icons.get(severity, "⚪")
            
            print(f"\n{icon} 问题 {i} [{severity.upper()}]: {critic['title']}")
            print(f"   类型: {critic.get('type', '未知')}")
            print(f"   描述: {critic['critique']}")
            if critic.get('suggestion'):
                print(f"   [建议] {critic['suggestion']}")
    else:
        print("\n[OK] 未发现明显问题（但这不代表真的没问题，魏征可能手下留情了）")
    
    if result['suggestions']:
        print(f"\n{'='*60}")
        print("[改进建议汇总]:")
        for suggestion in result['suggestions']:
            print(f"   - {suggestion}")
    
    print(f"\n{'='*60}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="魏征 Agent - 专门提反对意见、挑毛病的独立Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                           # 交互模式
  python main.py -i high                   # 交互模式，高强度
  python main.py -c "代码内容" -t code     # 审查代码
  python main.py -f plan.md -t plan        # 审查计划文件
  python main.py --init-config             # 创建默认配置文件
        """
    )
    
    parser.add_argument(
        '-i', '--intensity',
        choices=['low', 'medium', 'high', 'extreme'],
        default='medium',
        help='设置反对强度 (默认: medium)'
    )
    
    parser.add_argument(
        '-c', '--content',
        type=str,
        help='要审查的内容'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='要审查的文件路径'
    )
    
    parser.add_argument(
        '-t', '--type',
        choices=['code', 'text', 'plan', 'design', 'general'],
        default='general',
        help='内容类型 (默认: general)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='进入交互模式'
    )
    
    parser.add_argument(
        '--init-config',
        action='store_true',
        help='创建默认配置文件'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示统计信息'
    )
    
    parser.add_argument(
        '--memory-path',
        type=str,
        help='指定记忆存储路径'
    )
    
    args = parser.parse_args()
    
    # 初始化配置
    if args.init_config:
        config_path = Path.home() / ".weizheng" / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        create_default_config(str(config_path))
        print(f"✅ 默认配置已创建: {config_path}")
        return
    
    # 打印横幅
    print_banner()
    
    # 初始化Agent
    intensity = CriticIntensity(args.intensity)
    memory_path = args.memory_path
    
    agent = WeizhengAgent(intensity=intensity, memory_path=memory_path)
    
    # 显示统计
    if args.stats:
        print_stats(agent)
        return
    
    # 文件审查
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            sys.exit(1)
        
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 根据文件扩展名推断类型
        ext = Path(args.file).suffix.lower()
        type_mapping = {
            '.py': 'code', '.js': 'code', '.ts': 'code', '.java': 'code',
            '.cpp': 'code', '.c': 'code', '.go': 'code', '.rs': 'code',
            '.md': 'text', '.txt': 'text', '.rst': 'text',
            '.json': 'code', '.yaml': 'code', '.yml': 'code',
        }
        content_type = type_mapping.get(ext, args.type)
        
        single_review(agent, content, content_type)
        return
    
    # 内容审查
    if args.content:
        single_review(agent, args.content, args.type)
        return
    
    # 默认进入交互模式
    interactive_mode(agent)


if __name__ == "__main__":
    main()
