#!/usr/bin/env python3
"""
环境验证脚本

检查项目结构和依赖是否完整
"""

import sys
import importlib
from pathlib import Path


def check_file(path, desc):
    """Check if file exists"""
    exists = Path(path).exists()
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {desc}: {path}")
    return exists


def check_module(name, desc):
    """Check if module can be imported"""
    try:
        importlib.import_module(name)
        print(f"  [OK] {desc}")
        return True
    except Exception as e:
        print(f"  [FAIL] {desc}: {e}")
        return False


def main():
    # Windows 编码设置
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("Weizheng Agent Setup Verification")
    print("=" * 60)
    
    all_ok = True
    
    # 1. Check core files
    print("\n[1/5] Core Files:")
    files = [
        ("src/cli/__init__.py", "CLI 模块"),
        ("src/cli/__main__.py", "CLI 入口"),
        ("src/cli/weizheng_cli.py", "CLI Implementation"),
        ("src/server/__init__.py", "服务端模块"),
        ("src/server/__main__.py", "服务端入口"),
        ("src/server/pixel_server.py", "Server Implementation"),
        ("src/core/agent.py", "Agent Core"),
        ("src/core/critic.py", "Critic Engine"),
        ("src/ui/pixel_weizheng_v4.py", "Pixel Animation V4"),
        ("skills/openclaw/weizheng_skill/hook.py", "OpenClaw Skill Hook"),
        ("skills/openclaw/weizheng_skill/SKILL.md", "Skill Config"),
    ]
    for path, desc in files:
        if not check_file(path, desc):
            all_ok = False
    
    # 2. Check assets
    print("\n[2/5] Asset Files:")
    sprites = [
        ("assets/sprites/v4/idle_00.png", "Idle Frame 0"),
        ("assets/sprites/v4/talk_00.png", "Talk Frame 0"),
    ]
    for path, desc in sprites:
        if not check_file(path, desc):
            all_ok = False
    
    # 3. Check dependencies
    print("\n[3/5] Python Dependencies:")
    deps = [
        ("PIL", "Pillow (pip install Pillow)"),
        ("tkinter", "Tkinter GUI (built-in)"),
    ]
    for name, desc in deps:
        if not check_module(name, desc):
            all_ok = False
    
    # 4. Check module imports
    print("\n[4/5] Module Imports:")
    sys.path.insert(0, str(Path(__file__).parent))
    modules = [
        ("src.cli.weizheng_cli", "CLI Tool"),
        ("src.server.pixel_server", "Pixel Server"),
        ("src.core.agent", "Agent Core"),
        ("src.ui.pixel_weizheng_v4", "Pixel Animation V4"),
        ("skills.openclaw.weizheng_skill.hook", "Skill Hook"),
    ]
    for name, desc in modules:
        if not check_module(name, desc):
            all_ok = False
    
    # 5. Check batch scripts
    print("\n[5/5] Batch Scripts:")
    scripts = [
        ("start_server.bat", "Start Server Script"),
        ("test.bat", "Test Script"),
    ]
    for path, desc in scripts:
        if not check_file(path, desc):
            all_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("All checks passed! Ready to use.")
        print()
        print("Usage:")
        print("  1. Start pixel server: python -m src.server")
        print("     Or double-click: start_server.bat")
        print()
        print("  2. Run tests: python test_complete_flow.py")
        print("     Or double-click: test.bat")
        print()
        print("  3. Use in OpenClaw: '魏征，你怎么看？'")
    else:
        print("Verification failed! Check errors above.")
        print()
        print("Common issues:")
        print("  - Missing files: re-clone the repo")
        print("  - Missing deps: pip install Pillow")
    print("=" * 60)
    
    return all_ok


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
