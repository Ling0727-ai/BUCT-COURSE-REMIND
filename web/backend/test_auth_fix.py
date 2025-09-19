#!/usr/bin/env python3
"""
测试认证修复的脚本
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_auth_flow():
    """测试完整的认证流程"""
    session = requests.Session()
    
    print("🧪 开始测试认证流程...")
    
    # 1. 测试认证状态检查（未登录）
    print("\n1. 测试未登录状态...")
    response = session.get(f'{BASE_URL}/api/auth/status')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 测试登录
    print("\n2. 测试登录...")
    login_data = {
        'username': 'admin',  # 使用默认管理员账号
        'password': 'admin123'
    }
    
    response = session.post(f'{BASE_URL}/api/auth/login', 
                           json=login_data,
                           headers={'Content-Type': 'application/json'})
    print(f"登录状态码: {response.status_code}")
    print(f"登录响应: {response.json()}")
    
    if response.status_code == 200:
        print("✅ 登录成功")
        
        # 3. 测试登录后的认证状态
        print("\n3. 测试登录后状态...")
        response = session.get(f'{BASE_URL}/api/auth/status')
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.json().get('authenticated'):
            print("✅ 认证状态正确")
        else:
            print("❌ 认证状态错误")
            
        # 4. 测试受保护的资源
        print("\n4. 测试受保护资源...")
        response = session.get(f'{BASE_URL}/api/assignments/standard')
        print(f"作业数据状态码: {response.status_code}")
        
        # 5. 测试登出
        print("\n5. 测试登出...")
        response = session.post(f'{BASE_URL}/api/auth/logout')
        print(f"登出状态码: {response.status_code}")
        print(f"登出响应: {response.json()}")
        
        # 6. 测试登出后的认证状态
        print("\n6. 测试登出后状态...")
        response = session.get(f'{BASE_URL}/api/auth/status')
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if not response.json().get('authenticated'):
            print("✅ 登出后认证状态正确")
        else:
            print("❌ 登出后认证状态错误")
            
    else:
        print("❌ 登录失败")
        print("请确保后端服务正在运行，并且存在默认管理员账号")

def test_cors():
    """测试CORS配置"""
    print("\n🌐 测试CORS配置...")
    
    headers = {
        'Origin': 'http://localhost:3033',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    response = requests.options(f'{BASE_URL}/api/auth/status', headers=headers)
    print(f"OPTIONS请求状态码: {response.status_code}")
    print(f"CORS头部: {dict(response.headers)}")

if __name__ == '__main__':
    try:
        test_auth_flow()
        test_cors()
        print("\n🎉 测试完成")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行在 http://localhost:5000")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")