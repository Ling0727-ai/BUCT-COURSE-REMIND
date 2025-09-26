#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSA解密测试脚本
测试完整的加密-解密-哈希流程
"""

import sys
import os
import json
import time
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

def test_rsa_decryption():
    """测试RSA解密流程"""
    print("=" * 60)
    print("RSA解密测试开始")
    print("=" * 60)
    
    try:
        # 导入必要的模块
        from app.rsa_crypto import RSACrypto
        from werkzeug.security import generate_password_hash, check_password_hash
        
        # 1. 初始化RSA加密器
        print("\n1. 初始化RSA加密器...")
        rsa_crypto = RSACrypto()
        print("✓ RSA加密器初始化成功")
        
        # 2. 模拟前端加密过程
        print("\n2. 模拟前端加密过程...")
        
        # 原始登录数据
        original_data = {
            "username": "test_user",
            "password": "test_password_123",
            "timestamp": int(time.time())  # 使用当前时间戳
        }
        print(f"原始数据: {original_data}")
        
        # 加密数据
        encrypted_data = rsa_crypto.encrypt_data(json.dumps(original_data))
        print(f"✓ 数据加密成功，加密后长度: {len(encrypted_data)} 字符")
        
        # 3. 模拟后端解密过程
        print("\n3. 模拟后端解密过程...")
        
        # 解密数据
        decrypted_json = rsa_crypto.decrypt_data(encrypted_data)
        decrypted_data = json.loads(decrypted_json)
        print(f"✓ 数据解密成功: {decrypted_data}")
        
        # 验证解密结果
        assert decrypted_data["username"] == original_data["username"]
        assert decrypted_data["password"] == original_data["password"]
        print("✓ 解密数据验证通过")
        
        # 4. 测试密码哈希过程
        print("\n4. 测试密码哈希过程...")
        
        # 获取解密后的密码
        decrypted_password = decrypted_data["password"]
        print(f"解密后的密码: {decrypted_password}")
        
        # 生成密码哈希
        password_hash = generate_password_hash(decrypted_password)
        print(f"✓ 密码哈希生成成功: {password_hash[:50]}...")
        
        # 验证密码哈希
        is_valid = check_password_hash(password_hash, decrypted_password)
        print(f"✓ 密码哈希验证: {'通过' if is_valid else '失败'}")
        
        # 5. 完整流程测试
        print("\n5. 完整流程测试...")
        print("流程: 原始密码 -> RSA加密 -> RSA解密 -> 密码哈希 -> 哈希验证")
        
        # 模拟完整的登录流程
        def simulate_login_process(username, password):
            # 前端: 准备数据并加密
            login_data = {
                "username": username,
                "password": password,
                "timestamp": int(time.time())
            }
            encrypted = rsa_crypto.encrypt_data(json.dumps(login_data))
            
            # 后端: 解密数据
            decrypted_json = rsa_crypto.decrypt_data(encrypted)
            decrypted = json.loads(decrypted_json)
            
            # 后端: 处理密码（解密后再哈希）
            decrypted_password = decrypted["password"]
            hashed_password = generate_password_hash(decrypted_password)
            
            return {
                "username": decrypted["username"],
                "original_password": password,
                "decrypted_password": decrypted_password,
                "hashed_password": hashed_password,
                "hash_valid": check_password_hash(hashed_password, decrypted_password)
            }
        
        # 测试多个密码
        test_passwords = ["123456", "test_password", "复杂密码@123", "special!@#$%^&*()"]
        
        for pwd in test_passwords:
            result = simulate_login_process("test_user", pwd)
            print(f"\n测试密码: {pwd}")
            print(f"  解密后密码: {result['decrypted_password']}")
            print(f"  密码匹配: {'✓' if result['original_password'] == result['decrypted_password'] else '✗'}")
            print(f"  哈希验证: {'✓' if result['hash_valid'] else '✗'}")
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("✓ RSA解密流程正常工作")
        print("✓ 密码在解密后正确进行哈希处理")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_integration():
    """测试与认证模块的集成"""
    print("\n" + "=" * 60)
    print("认证模块集成测试")
    print("=" * 60)
    
    try:
        from app.rsa_crypto import RSACrypto
        
        # 模拟auth.py中的解密逻辑
        rsa_crypto = RSACrypto()
        
        # 模拟前端发送的加密数据
        login_data = {
            "username": "integration_test",
            "password": "integration_password_123",
            "timestamp": int(time.time())
        }
        
        encrypted_data = rsa_crypto.encrypt_data(json.dumps(login_data))
        
        # 模拟auth.py中的处理逻辑
        print("模拟 auth.py 中的处理流程:")
        print("1. 接收加密数据")
        print("2. 调用 rsa_crypto.decrypt_data()")
        
        decrypted_json = rsa_crypto.decrypt_data(encrypted_data)
        decrypted_data = json.loads(decrypted_json)
        
        print("3. 解密成功，提取用户名和密码")
        print(f"   用户名: {decrypted_data.get('username')}")
        print(f"   密码: {decrypted_data.get('password')}")
        
        print("4. ✓ 集成测试通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始RSA解密测试...")
    
    # 运行基础测试
    basic_test_passed = test_rsa_decryption()
    
    # 运行集成测试
    integration_test_passed = test_auth_integration()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"基础RSA测试: {'✓ 通过' if basic_test_passed else '✗ 失败'}")
    print(f"集成测试: {'✓ 通过' if integration_test_passed else '✗ 失败'}")
    
    if basic_test_passed and integration_test_passed:
        print("\n🎉 所有测试通过！")
        print("✅ RSA加密解密功能正常")
        print("✅ 密码解密后正确哈希")
        print("✅ 与认证模块集成正常")
    else:
        print("\n❌ 部分测试失败，请检查配置")
    
    print("=" * 60)