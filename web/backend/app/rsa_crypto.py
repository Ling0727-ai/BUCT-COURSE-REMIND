"""
RSA加密解密模块
用于前后端数据传输加密，防止爬虫攻击
"""

import base64
import json
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Random import get_random_bytes
import hashlib
import os
from flask import current_app

class RSACrypto:
    def __init__(self):
        # 从环境变量读取RSA配置
        self.key_size = int(os.getenv('RSA_KEY_SIZE', 2048))
        self.key_expire_minutes = int(os.getenv('RSA_KEY_EXPIRE_MINUTES', 30))
        self.rsa_enabled = os.getenv('RSA_ENABLE', 'true').lower() == 'true'
        
        self.public_key = None
        self.private_key = None
        self.key_generated_at = None
        
    def is_enabled(self):
        """检查RSA加密是否启用"""
        return self.rsa_enabled
    
    def generate_key_pair(self):
        """生成RSA密钥对"""
        if not self.is_enabled():
            current_app.logger.info("RSA加密已禁用，跳过密钥生成")
            return False
            
        try:
            key = RSA.generate(self.key_size)
            self.private_key = key
            self.public_key = key.publickey()
            self.key_generated_at = datetime.now()
            
            current_app.logger.info("RSA密钥对生成成功")
            return True
        except Exception as e:
            current_app.logger.error(f"RSA密钥对生成失败: {str(e)}")
            return False
    
    def is_key_expired(self):
        """检查密钥是否过期"""
        if not self.key_generated_at:
            return True
        
        expire_time = self.key_generated_at + timedelta(minutes=self.key_expire_minutes)
        return datetime.now() > expire_time
    
    def get_public_key_pem(self):
        """获取PEM格式的公钥"""
        if not self.is_enabled():
            return None
            
        if not self.public_key or self.is_key_expired():
            if not self.generate_key_pair():
                return None
        
        if self.public_key:
            return self.public_key.export_key().decode('utf-8')
        return None
    
    def get_public_key_info(self):
        """获取公钥信息，包含时间戳用于前端验证"""
        if not self.is_enabled():
            return None
            
        if not self.public_key or self.is_key_expired():
            if not self.generate_key_pair():
                return None
        
        public_key_pem = self.get_public_key_pem()
        if not public_key_pem or not self.key_generated_at:
            return None
            
        return {
            'public_key': public_key_pem,
            'timestamp': int(self.key_generated_at.timestamp()),
            'expire_minutes': self.key_expire_minutes
        }
    
    def decrypt_data(self, encrypted_data):
        """解密数据"""
        try:
            if not self.private_key:
                raise Exception("私钥未初始化")
            
            # Base64解码
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # RSA解密
            cipher = PKCS1_v1_5.new(self.private_key)
            decrypted_bytes = cipher.decrypt(encrypted_bytes, None)
            
            if decrypted_bytes is None:
                raise Exception("解密失败")
            
            # 解析JSON数据
            decrypted_text = decrypted_bytes.decode('utf-8')
            data = json.loads(decrypted_text)
            
            # 验证时间戳（防重放攻击）
            if 'timestamp' in data:
                request_time = datetime.fromtimestamp(data['timestamp'])
                time_diff = datetime.now() - request_time
                
                # 请求时间不能超过5分钟
                if time_diff.total_seconds() > 300:
                    raise Exception("请求已过期")
            
            current_app.logger.info("数据解密成功")
            return data
            
        except Exception as e:
            current_app.logger.error(f"数据解密失败: {str(e)}")
            return None
    
    def create_challenge(self):
        """创建挑战码，用于验证客户端加密能力"""
        challenge = base64.b64encode(get_random_bytes(16)).decode('utf-8')
        challenge_hash = hashlib.sha256(challenge.encode()).hexdigest()
        
        return {
            'challenge': challenge,
            'hash': challenge_hash,
            'timestamp': int(datetime.now().timestamp())
        }
    
    def verify_challenge_response(self, encrypted_response, expected_hash):
        """验证挑战响应"""
        try:
            decrypted_data = self.decrypt_data(encrypted_response)
            if not decrypted_data:
                return False
            
            response_hash = decrypted_data.get('challenge_hash')
            return response_hash == expected_hash
            
        except Exception as e:
            current_app.logger.error(f"挑战验证失败: {str(e)}")
            return False

# 全局RSA实例
rsa_crypto = RSACrypto()

def get_rsa_crypto():
    """获取RSA加密实例"""
    return rsa_crypto