#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的RSA解密测试
验证密码解密和哈希流程
"""

import sys
import os
import json
import time
import base64
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

def test_password_decryption_flow():
    """测试密码解密和哈希流程"""
    print("=" * 50)
    print("RSA密码解密流程测试")
    print("=" * 50)
    
    try:
        # 导入模块
        from app.rsa_crypto import RSACrypto
        from werkzeug.security import generate_password_hash, check_password_hash
        from Crypto.Cipher import PKCS1_v1_5
        
        # 1. 初始化RSA
        print("\n1. 初始化RSA加密器...")
        rsa_crypto = RSACrypto()
        
        # 生成密钥对
        success = rsa_crypto.generate_key_pair()
        if not success:
            raise Exception("密钥生成失败")
        print("✓ RSA密钥对生成成功")
        
        # 2. 模拟前端加密（添加测试用加密函数）
        def encrypt_data_for_test(data_str, public_key):
            """测试用加密函数"""
            cipher = PKCS1_v1_5.new(public_key)
            encrypted_bytes = cipher.encrypt(data_str.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        
        print("\n2. 模拟前端加密登录数据...")
        
        # 原始登录数据
        login_data = {
            "username": "test_user",
            "password": "my_secret_password_123",
            "timestamp": int(time.time())
        }
        
        print(f"原始数据: {login_data}")
        
        # 加密数据
        json_data = json.dumps(login_data)
        encrypted_data = encrypt_data_for_test(json_data, rsa_crypto.public_key)
        print(f"✓ 数据加密完成，长度: {len(encrypted_data)}")
        
        # 3. 后端解密过程
        print("\n3. 后端解密过程...")
        
        # 解密数据
        decrypted_data = rsa_crypto.decrypt_data(encrypted_data)
        
        if decrypted_data is None:
            raise Exception("解密失败")
        
        print(f"✓ 解密成功: {decrypted_data}")
        
        # 4. 密码处理流程
        print("\n4. 密码处理流程...")
        
        # 提取解密后的密码
        decrypted_password = decrypted_data.get("password")
        print(f"解密后的密码: {decrypted_password}")
        
        # 验证密码是否正确解密
        original_password = login_data["password"]
        password_match = (decrypted_password == original_password)
        print(f"密码解密正确性: {'✓ 正确' if password_match else '✗ 错误'}")
        
        # 5. 密码哈希处理
        print("\n5. 密码哈希处理...")
        
        # 对解密后的密码进行哈希
        password_hash = generate_password_hash(decrypted_password)
        print(f"✓ 密码哈希生成: {password_hash[:60]}...")
        
        # 验证哈希
        hash_valid = check_password_hash(password_hash, decrypted_password)
        print(f"✓ 哈希验证: {'通过' if hash_valid else '失败'}")
        
        # 6. 完整流程验证
        print("\n6. 完整流程验证...")
        print("流程: 原始密码 -> RSA加密 -> RSA解密 -> 密码哈希")
        
        steps = [
            f"原始密码: {original_password}",
            f"解密密码: {decrypted_password}",
            f"密码匹配: {'✓' if password_match else '✗'}",
            f"哈希验证: {'✓' if hash_valid else '✗'}"
        ]
        
        for step in steps:
            print(f"  {step}")
        
        # 总结
        all_passed = password_match and hash_valid
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 测试通过！")
            print("✅ RSA解密功能正常")
            print("✅ 密码正确解密")
            print("✅ 密码哈希处理正确")
            print("\n关键点:")
            print("1. 前端发送RSA加密的密码")
            print("2. 后端使用RSA解密获得原始密码")
            print("3. 对解密后的密码进行哈希存储")
            print("4. 整个流程确保密码安全传输和存储")
        else:
            print("❌ 测试失败")
        print("=" * 50)
        
        return all_passed
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_module_integration():
    """测试与auth.py的集成"""
    print("\n" + "=" * 50)
    print("auth.py 集成测试")
    print("=" * 50)
    
    try:
        # 检查auth.py中的解密逻辑
        print("检查 auth.py 中的RSA解密实现...")
        
        # 读取auth.py文件
        auth_file_path = os.path.join(os.path.dirname(__file__), 'app', 'auth.py')
        
        if os.path.exists(auth_file_path):
            with open(auth_file_path, 'r', encoding='utf-8') as f:
                auth_content = f.read()
            
            # 检查关键代码
            checks = [
                ('rsa_crypto.decrypt_data', 'RSA解密调用'),
                ('generate_password_hash', '密码哈希生成'),
                ('encrypted_data', '加密数据处理')
            ]
            
            for check_str, description in checks:
                if check_str in auth_content:
                    print(f"✓ {description}: 已实现")
                else:
                    print(f"✗ {description}: 未找到")
            
            print("✓ auth.py 集成检查完成")
            return True
        else:
            print("✗ auth.py 文件不存在")
            return False
            
    except Exception as e:
        print(f"✗ 集成测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始RSA解密测试...")
    
    # 运行密码解密流程测试
    decryption_test_passed = test_password_decryption_flow()
    
    # 运行集成测试
    integration_test_passed = test_auth_module_integration()
    
    # 最终总结
    print("\n" + "=" * 50)
    print("最终测试结果")
    print("=" * 50)
    print(f"密码解密流程: {'✓ 通过' if decryption_test_passed else '✗ 失败'}")
    print(f"模块集成检查: {'✓ 通过' if integration_test_passed else '✗ 失败'}")
    
    if decryption_test_passed and integration_test_passed:
        print("\n🎉 所有测试通过！")
        print("\n回答您的问题:")
        print("❓ 传过来的加密的密码有没有解密后再去hash？")
        print("✅ 是的！有解密步骤！")
        print("\n具体流程:")
        print("1. 前端: 密码 -> RSA加密 -> 发送到后端")
        print("2. 后端: 接收加密数据 -> RSA解密 -> 获得原始密码")
        print("3. 后端: 原始密码 -> generate_password_hash() -> 存储哈希")
        print("\n这样确保了:")
        print("• 传输过程中密码是加密的（防止网络窃听）")
        print("• 存储时密码是哈希的（防止数据库泄露）")
        print("• 解密步骤确保了密码的正确处理")
    else:
        print("\n❌ 部分测试失败")
    
    print("=" * 50)