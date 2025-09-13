#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
u校园登录测试脚本

运行程序后输入用户名和密码进行登录测试。
用法: python u校园_test_main.py
"""

import sys
import getpass
from u校园 import UClient, encrypt
from u校园.exceptions import ULoginError, UNetworkError


def main():
    """主函数"""
    print("🎯 u校园登录测试工具")
    print("=" * 50)
    
    # 提示用户输入登录信息
    try:
        print("请输入登录信息:")
        username = input("📝 用户名: ").strip()
        
        # 使用getpass隐藏密码输入
        password = getpass.getpass("🔒 密码: ").strip()
        
        # 检查输入是否为空
        if not username:
            print("❌ 用户名不能为空")
            sys.exit(1)
        if not password:
            print("❌ 密码不能为空")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 输入错误: {e}")
        sys.exit(1)
    
    school_id = ""  # 学校ID留空
    
    # 显示输入信息
    print(f"📝 用户名: {username}")
    print(f"🔒 密码: {'*' * len(password)}")
    print(f"🏫 学校ID: {school_id or '留空'}")
    
    # 显示加密信息
    try:
        encrypted_username = encrypt(username)
        encrypted_password = encrypt(password)
    except Exception as e:
        print(f"❌ 加密失败: {e}")
        sys.exit(1)
    
    # 创建客户端
    client = UClient()
    
    print("\n" + "=" * 50)
    print("🔄 正在登录...")
    print("=" * 50)
    
    try:
        # 执行登录（学校ID留空）
        success = client.login(username, password, school_id)
        
        if success:
            print("✅ 登录成功!")
            print(f"✅ 登录状态: {client.is_logged_in()}")
            
            # 显示请求信息
            print("\n" + "-" * 30)
            print("📋 请求详情:")
            print("-" * 30)
            print(f"🌐 登录URL: {client.LOGIN_URL}")
            print(f"⏱️  超时时间: {client.timeout}秒")
            print(f"📤 学校ID: {'留空'}")
            
        else:
            print("❌ 登录失败")
            
    except ULoginError as e:
        print(f"❌ 登录错误: {e}")
        if hasattr(e, 'status_code'):
            print(f"   📊 状态码: {e.status_code}")
        
    except UNetworkError as e:
        print(f"❌ 网络错误: {e}")
        print("   🔌 请检查网络连接")
        
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        
    print("\n" + "=" * 50)
    print("🏁 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()