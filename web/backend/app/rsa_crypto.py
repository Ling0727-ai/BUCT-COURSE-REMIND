"""
RSA加密解密模块
用于前后端数据传输加密，防止爬虫攻击
"""

import base64
import hashlib
import json
import os
import threading
from datetime import datetime, timedelta

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
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

        # 保留旧密钥用于过渡期解密（防止密钥刷新时前端还在用旧公钥）
        self.old_private_key = None
        self.old_key_expired_at = None
        self.old_key_grace_period_minutes = 5  # 旧密钥额外保留5分钟

        # 线程锁，防止并发密钥生成冲突
        self._lock = threading.RLock()

    def is_enabled(self):
        """检查RSA加密是否启用"""
        return self.rsa_enabled

    def generate_key_pair(self):
        """生成RSA密钥对"""
        if not self.is_enabled():
            try:
                current_app.logger.info("RSA加密已禁用，跳过密钥生成")
            except RuntimeError:
                print("RSA加密已禁用，跳过密钥生成")
            return False

        with self._lock:
            # 双重检查，避免在等待锁期间其他线程已经生成了密钥
            if self.public_key and not self.is_key_expired():
                return True

            try:
                # 保存旧密钥用于过渡期解密
                if self.private_key:
                    self.old_private_key = self.private_key
                    self.old_key_expired_at = datetime.now() + timedelta(minutes=self.old_key_grace_period_minutes)
                    try:
                        current_app.logger.info("保留旧密钥用于过渡期解密")
                    except RuntimeError:
                        pass

                key = RSA.generate(self.key_size)
                self.private_key = key
                self.public_key = key.publickey()
                self.key_generated_at = datetime.now()

                try:
                    current_app.logger.info("RSA密钥对生成成功")
                except RuntimeError:
                    print("RSA密钥对生成成功")
                return True
            except Exception as e:
                try:
                    current_app.logger.error(f"RSA密钥对生成失败: {str(e)}")
                except RuntimeError:
                    print(f"RSA密钥对生成失败: {str(e)}")
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

        with self._lock:
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

        with self._lock:
            if not self.public_key or self.is_key_expired():
                if not self.generate_key_pair():
                    return None

            public_key_pem = self.public_key.export_key().decode('utf-8') if self.public_key else None
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

            # 首先尝试用当前私钥解密
            cipher = PKCS1_v1_5.new(self.private_key)
            decrypted_bytes = cipher.decrypt(encrypted_bytes, None)

            # 如果当前私钥解密失败，尝试用旧私钥解密（过渡期）
            if decrypted_bytes is None and self.old_private_key:
                # 检查旧密钥是否还在有效期内
                if self.old_key_expired_at and datetime.now() < self.old_key_expired_at:
                    try:
                        current_app.logger.info("尝试使用旧密钥解密（过渡期）")
                    except RuntimeError:
                        pass
                    old_cipher = PKCS1_v1_5.new(self.old_private_key)
                    decrypted_bytes = old_cipher.decrypt(encrypted_bytes, None)
                else:
                    # 旧密钥已过期，清理
                    self.old_private_key = None
                    self.old_key_expired_at = None

            if decrypted_bytes is None:
                raise Exception("解密失败")

            # 解析JSON数据
            decrypted_text = decrypted_bytes.decode('utf-8')
            data = json.loads(decrypted_text)

            # 验证时间戳（防重放攻击）- 放宽到10分钟
            if 'timestamp' in data:
                request_time = datetime.fromtimestamp(data['timestamp'])
                time_diff = datetime.now() - request_time

                # 请求时间不能超过10分钟（从5分钟放宽）
                if time_diff.total_seconds() > 600:
                    raise Exception("请求已过期")

            try:
                current_app.logger.info("数据解密成功")
            except RuntimeError:
                pass
            return data

        except Exception as e:
            try:
                current_app.logger.error(f"数据解密失败: {str(e)}")
            except RuntimeError:
                print(f"数据解密失败: {str(e)}")
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
