#!/usr/bin/env python3
"""
调试scraper导入问题的脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Python路径:")
for path in sys.path:
    print(f"  {path}")

print("\n当前工作目录:", os.getcwd())
print("脚本所在目录:", current_dir)

try:
    print("\n1. 尝试直接导入scraper...")
    from scraper import get_scraper
    scraper = get_scraper()
    print(f"✓ 成功: {scraper}")
    print(f"  类型: {type(scraper)}")
    print(f"  有client属性: {hasattr(scraper, 'client')}")
    print(f"  有get_pending_tasks方法: {hasattr(scraper, 'get_pending_tasks')}")
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. 尝试通过app.assignments导入...")
    from app.assignments import get_scraper_instance
    scraper = get_scraper_instance()
    print(f"✓ 成功: {scraper}")
    if scraper:
        print(f"  类型: {type(scraper)}")
        print(f"  有client属性: {hasattr(scraper, 'client')}")
        print(f"  有get_pending_tasks方法: {hasattr(scraper, 'get_pending_tasks')}")
    else:
        print("  scraper为None")
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. 测试Flask应用上下文中的导入...")
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.assignments import get_scraper_instance
        scraper = get_scraper_instance()
        print(f"✓ Flask上下文中成功: {scraper}")
        if scraper:
            print(f"  类型: {type(scraper)}")
            print(f"  有client属性: {hasattr(scraper, 'client')}")
            print(f"  有get_pending_tasks方法: {hasattr(scraper, 'get_pending_tasks')}")
        else:
            print("  scraper为None")
except Exception as e:
    print(f"✗ Flask上下文中失败: {e}")
    import traceback
    traceback.print_exc()