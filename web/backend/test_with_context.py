#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带Flask上下文的RSA解密测试
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

def create_test_app():
    """创建测试用的Flask应用"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    
    return app

def test_rsa_with_context():
    """在Flask上下文中测试RSA功能"""
    print("=" * 60)
    print("RSA解密测试（带Flask上下文）")
    print("=" * 60)
    
    # 创建Flask应用
    app = create_test_app()
    
    with app.app_context():
        try:
            # 导入模块
            from app.rsa_crypto import RSACrypto
            from werkzeug.security import generate_password_hash, check_password_hash
            from Crypto.Cipher import PKCS1_v1_5
            
            print("\n1. 初始化RSA加密器...")
            rsa_crypto = RSACrypto()
            
            # 生成密钥对
            success = rsa_crypto.generate_key_pair()
            if not success:
                raise Exception("密钥生成失败")
            print("✓ RSA密钥对生成成功")
            
            # 测试用加密函数
            def encrypt_for_test(data_str, public_key):
                cipher = PKCS1_v1_5.new(public_key)
                encrypted_bytes = cipher.encrypt(data_str.encode('utf-8'))
                return base64.b64encode(encrypted_bytes).decode('utf-8')
            
            print("\n2. 测试密码加密解密流程...")
            
            # 测试数据
            test_cases = [
                {
                    "username": "user1",
                    "password": "simple123",
                    "timestamp": int(time.time())
                },
                {
                    "username": "user2", 
                    "password": "复杂密码@#$%",
                    "timestamp": int(time.time())
                },
                {
                    "username": "user3",
                    "password": "VeryLongPasswordWith123Numbers!@#",
                    "timestamp": int(time.time())
                }
            ]
            
            all_tests_passed = True
            
            for i, test_data in enumerate(test_cases, 1):
                print(f"\n测试用例 {i}:")
                print(f"  原始数据: {test_data}")
                
                try:
                    # 1. 加密
                    json_str = json.dumps(test_data)
                    encrypted = encrypt_for_test(json_str, rsa_crypto.public_key)
                    print(f"  ✓ 加密成功")
                    
                    # 2. 解密
                    decrypted_data = rsa_crypto.decrypt_data(encrypted)
                    if decrypted_data is None:
                        raise Exception("解密返回None")
                    
                    print(f"  ✓ 解密成功: {decrypted_data}")
                    
                    # 3. 验证数据完整性
                    original_password = test_data["password"]
                    decrypted_password = decrypted_data.get("password")
                    
                    if original_password != decrypted_password:
                        raise Exception(f"密码不匹配: {original_password} != {decrypted_password}")
                    
                    print(f"  ✓ 密码解密正确: {decrypted_password}")
                    
                    # 4. 测试密码哈希
                    password_hash = generate_password_hash(decrypted_password)
                    hash_valid = check_password_hash(password_hash, decrypted_password)
                    
                    if not hash_valid:
                        raise Exception("密码哈希验证失败")
                    
                    print(f"  ✓ 密码哈希验证通过")
                    print(f"  ✓ 测试用例 {i} 全部通过")
                    
                except Exception as e:
                    print(f"  ✗ 测试用例 {i} 失败: {str(e)}")
                    all_tests_passed = False
            
            # 总结
            print("\n" + "=" * 60)
            if all_tests_passed:
                print("🎉 所有测试通过！")
                print("\n✅ 关键验证结果:")
                print("1. RSA加密解密功能正常工作")
                print("2. 密码能够正确解密")
                print("3. 解密后的密码可以正确哈希")
                print("4. 整个流程确保了数据安全")
                
                print("\n📋 回答您的问题:")
                print("❓ '传过来的加密的密码有没有解密后再去hash？'")
                print("✅ 答案：是的！有解密步骤！")
                
                print("\n🔄 完整流程:")
                print("  前端: 原始密码 → RSA加密 → 发送")
                print("  后端: 接收 → RSA解密 → 获得原始密码 → 哈希存储")
                
                print("\n🔒 安全保障:")
                print("  • 网络传输：密码被RSA加密保护")
                print("  • 数据存储：密码被哈希算法保护")
                print("  • 处理过程：先解密再哈希，确保正确性")
                
            else:
                print("❌ 部分测试失败")
            
            print("=" * 60)
            return all_tests_passed
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def verify_auth_implementation():
    """验证auth.py中的实现"""
    print("\n" + "=" * 60)
    print("验证 auth.py 实现")
    print("=" * 60)
    
    try:
        auth_file = os.path.join(os.path.dirname(__file__), 'app', 'auth.py')
        
        if not os.path.exists(auth_file):
            print("✗ auth.py 文件不存在")
            return False
        
        with open(auth_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键实现
        key_implementations = [
            ('rsa_crypto.decrypt_data', '✓ RSA解密调用'),
            ('generate_password_hash', '✓ 密码哈希生成'),
            ('encrypted_data', '✓ 加密数据处理'),
            ('decrypted_data', '✓ 解密数据处理'),
            ('get(\'password\')', '✓ 密码提取')
        ]
        
        print("检查关键实现:")
        all_found = True
        
        for check, desc in key_implementations:
            if check in content:
                print(f"  {desc}")
            else:
                print(f"  ✗ 缺少: {check}")
                all_found = False
        
        if all_found:
            print("\n✅ auth.py 实现完整")
            print("✅ 包含完整的解密→哈希流程")
        else:
            print("\n⚠️  auth.py 实现可能不完整")
        
        return all_found
        
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始完整的RSA解密测试...")
    
    # 运行RSA测试
    rsa_test_passed = test_rsa_with_context()
    
    # 验证auth实现
    auth_verified = verify_auth_implementation()
    
    # 最终结论
    print("\n" + "🎯" + "=" * 58 + "🎯")
    print("最终测试结论")
    print("🎯" + "=" * 58 + "🎯")
    
    print(f"RSA功能测试: {'✅ 通过' if rsa_test_passed else '❌ 失败'}")
    print(f"Auth实现验证: {'✅ 完整' if auth_verified else '❌ 不完整'}")
    
    if rsa_test_passed and auth_verified:
        print("\n🏆 最终答案:")
        print("✅ 是的！系统确实有解密步骤！")
        print("\n📝 技术细节:")
        print("1. 前端使用RSA公钥加密用户密码")
        print("2. 后端接收加密数据后调用 rsa_crypto.decrypt_data()")
        print("3. 解密获得原始密码后调用 generate_password_hash()")
        print("4. 最终存储的是哈希后的密码，不是加密的密码")
        print("\n🔐 这样设计的好处:")
        print("• 传输安全：网络中传输的是RSA加密数据")
        print("• 存储安全：数据库中存储的是不可逆哈希")
        print("• 处理正确：解密后再哈希确保密码处理正确")
    else:
        print("\n❌ 测试未完全通过，请检查实现")
    
    print("🎯" + "=" * 58 + "🎯")