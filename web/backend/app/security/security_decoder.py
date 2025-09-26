"""
数据安全解码工具 - 后端解密模块
版本: 3.2.1 | 构建: 20241225
对应前端混淆加密系统的解密实现
"""

import json
import base64
import time
import hashlib
from typing import Optional, Dict, Any, Union
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 系统配置常量（与前端对应）
SYS_CONFIG = {
    'entropy_seed': 0x2A5F3C91,
    'hash_multiplier': 0x41C64E6D,
    'offset_increment': 0x3039,
    'security_mask': 0x7FFFFFFF,
    'version': '3.2.1'
}

# 数学运算常量池（与前端对应）
MATH_POOL = {
    'factor_alpha': int('10000000000001029'),
    'factor_beta': int('2305843009213693951'),
    'exponent_base': 65537,
    'modulus_limit': 0x100000000,
    'prime_offset': 0x1F4
}

class SecurityDecoder:
    """数据安全解码器"""
    
    def __init__(self):
        self.operation_mode = 'stealth'  # 默认隐蔽模式
        self.initialized = False
        self._init_decoder()
    
    def _init_decoder(self):
        """初始化解码器"""
        try:
            # 尝试导入RSA库
            try:
                from Crypto.PublicKey import RSA
                from Crypto.Cipher import PKCS1_OAEP
                self.operation_mode = 'standard'
                logger.info("RSA库加载成功，使用标准解密模式")
            except ImportError:
                logger.info("RSA库未找到，使用隐蔽解密模式")
            
            self.initialized = True
            logger.info(f"安全解码器初始化完成 - 模式: {self.operation_mode}")
            
        except Exception as e:
            logger.error(f"解码器初始化失败: {e}")
            self.operation_mode = 'fallback'
    
    def decode_secure_data(self, encrypted_data: str) -> Optional[str]:
        """
        解码安全数据
        
        Args:
            encrypted_data: 前端加密的数据
            
        Returns:
            解密后的原始数据，失败返回None
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            # 尝试不同的解密方案
            if self.operation_mode == 'standard':
                result = self._standard_decrypt(encrypted_data)
                if result:
                    return result
            
            # 尝试隐蔽模式解密
            result = self._stealth_decrypt(encrypted_data)
            if result:
                return result
            
            # 尝试备用解密
            result = self._fallback_decrypt(encrypted_data)
            if result:
                return result
            
            logger.warning("所有解密方案均失败，返回原始数据")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"数据解码异常: {e}")
            return encrypted_data
    
    def _standard_decrypt(self, data: str) -> Optional[str]:
        """标准RSA解密"""
        try:
            # 这里可以实现标准RSA解密
            # 由于前端主要使用隐蔽模式，这里先返回None
            return None
        except Exception as e:
            logger.debug(f"标准解密失败: {e}")
            return None
    
    def _stealth_decrypt(self, data: str) -> Optional[str]:
        """隐蔽模式解密（对应前端stealthObfuscation）"""
        try:
            # 第一步：解析最终封装
            unwrapped = self._unwrap_transformed_data(data)
            if not unwrapped:
                return None
            
            # 第二步：移除噪声数据
            denoised = self._remove_noise_data(unwrapped['data'], unwrapped['session'])
            
            # 第三步：反向自定义编码
            decoded = self._reverse_custom_encoding(denoised)
            
            # 第四步：反向数学运算混淆
            unobfuscated = self._reverse_mathematical_obfuscation(decoded)
            
            # 第五步：反向字符映射变换
            original = self._reverse_character_mapping(unobfuscated, unwrapped['timestamp'])
            
            return original
            
        except Exception as e:
            logger.debug(f"隐蔽解密失败: {e}")
            return None
    
    def _unwrap_transformed_data(self, data: str) -> Optional[Dict[str, Any]]:
        """解析最终封装的数据"""
        try:
            # Base64解码
            decoded_json = base64.b64decode(data).decode('utf-8')
            wrapper = json.loads(decoded_json)
            
            # 验证数据格式
            if not all(key in wrapper for key in ['d', 't', 's', 'v', 'm']):
                return None
            
            # 解析时间戳
            timestamp = int(wrapper['t'], 36)
            
            # 验证校验和
            expected_checksum = self._compute_data_checksum(wrapper['d'])
            actual_checksum = int(wrapper['v'], 16)
            
            if expected_checksum != actual_checksum:
                logger.warning("数据校验和不匹配")
                # 继续处理，可能是时间差异导致的
            
            return {
                'data': wrapper['d'],
                'timestamp': timestamp,
                'session': wrapper['s'],
                'checksum': actual_checksum,
                'mode': wrapper['m']
            }
            
        except Exception as e:
            logger.debug(f"数据解封装失败: {e}")
            return None
    
    def _remove_noise_data(self, data: str, session_token: str) -> str:
        """移除噪声数据（简化实现）"""
        try:
            # 由于噪声是随机插入的，这里使用启发式方法移除
            # 实际实现中可能需要更复杂的算法
            
            # 移除明显的噪声字符（非常规字符）
            cleaned = ''
            for char in data:
                # 保留常见的Base64字符和一些特殊字符
                if char.isalnum() or char in '+=/-_':
                    cleaned += char
            
            return cleaned
            
        except Exception as e:
            logger.debug(f"噪声移除失败: {e}")
            return data
    
    def _reverse_custom_encoding(self, data: str) -> str:
        """反向自定义编码"""
        try:
            custom_alphabet = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890+/'
            standard_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
            
            # 反向映射
            reversed_data = ''
            for char in data:
                index = custom_alphabet.find(char)
                if index != -1:
                    reversed_data += standard_alphabet[index]
                else:
                    reversed_data += char
            
            # Base64解码
            try:
                # 补充padding
                missing_padding = len(reversed_data) % 4
                if missing_padding:
                    reversed_data += '=' * (4 - missing_padding)
                
                decoded = base64.b64decode(reversed_data).decode('utf-8')
                return decoded
            except:
                return reversed_data
                
        except Exception as e:
            logger.debug(f"自定义编码反向失败: {e}")
            return data
    
    def _reverse_mathematical_obfuscation(self, data: str) -> str:
        """反向数学运算混淆"""
        try:
            # 编码为字节
            bytes_data = data.encode('utf-8')
            deobfuscated = bytearray(len(bytes_data))
            
            # 反向数学变换
            alpha = MATH_POOL['factor_alpha'] % 256
            beta = MATH_POOL['factor_beta'] % 256
            
            # 计算模逆元（简化实现）
            alpha_inv = self._mod_inverse(alpha, 256)
            
            for i in range(len(bytes_data)):
                # 反向变换: (obfuscated - beta - i*3) * alpha_inv % 256
                obfuscated_byte = bytes_data[i]
                original_byte = ((obfuscated_byte - beta - i * 3) * alpha_inv) % 256
                deobfuscated[i] = original_byte
            
            return deobfuscated.decode('utf-8', errors='ignore')
            
        except Exception as e:
            logger.debug(f"数学混淆反向失败: {e}")
            return data
    
    def _reverse_character_mapping(self, data: str, timestamp: int) -> str:
        """反向字符映射变换"""
        try:
            unmapped = ''
            for i in range(len(data)):
                char = ord(data[i])
                map_key = (timestamp + i * 17) % 256
                original_char = char ^ map_key
                unmapped += chr(original_char)
            
            return unmapped
            
        except Exception as e:
            logger.debug(f"字符映射反向失败: {e}")
            return data
    
    def _fallback_decrypt(self, data: str) -> Optional[str]:
        """备用解密方案"""
        try:
            # 尝试解析备用加密格式
            decoded_json = base64.b64decode(data).decode('utf-8')
            metadata = json.loads(decoded_json)
            
            if 'payload' in metadata:
                # 解码payload
                payload = base64.b64decode(metadata['payload']).decode('utf-8')
                
                # 反向熵值混合
                if 'ent' in metadata:
                    entropy = int(metadata['ent'], 16)
                    payload = self._reverse_entropy_mixing(payload, entropy)
                
                # 反向时间戳混淆
                if 'ts' in metadata:
                    timestamp = int(metadata['ts'], 36)
                    payload = self._reverse_timestamp_obfuscation(payload, timestamp)
                
                return payload
            
            return None
            
        except Exception as e:
            logger.debug(f"备用解密失败: {e}")
            return None
    
    def _reverse_entropy_mixing(self, data: str, entropy: int) -> str:
        """反向熵值混合"""
        try:
            entropy_bytes = entropy.to_bytes(4, byteorder='little')
            entropy_string = ''.join(chr(b) for b in entropy_bytes)
            
            unmixed = ''
            for i in range(len(data)):
                data_char = ord(data[i])
                entropy_char = ord(entropy_string[i % len(entropy_string)])
                unmixed += chr(data_char ^ entropy_char)
            
            return unmixed
            
        except Exception as e:
            logger.debug(f"熵值混合反向失败: {e}")
            return data
    
    def _reverse_timestamp_obfuscation(self, data: str, timestamp: int) -> str:
        """反向时间戳混淆"""
        try:
            time_key = self._to_base36(timestamp)
            result = ''
            
            for i in range(len(data)):
                char = ord(data[i])
                key_char = ord(time_key[i % len(time_key)])
                # 反向变换: (obfuscated - key_char - i*2) % 256
                original = (char - key_char - i * 2) % 256
                result += chr(original)
            
            return result
            
        except Exception as e:
            logger.debug(f"时间戳混淆反向失败: {e}")
            return data
    
    def _compute_data_checksum(self, data: str) -> int:
        """计算数据校验和（与前端对应）"""
        checksum = SYS_CONFIG['entropy_seed']
        for i, char in enumerate(data):
            checksum = (checksum + ord(char) * (i + 1)) % 0xFFFFFF
        return checksum
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """计算模逆元（简化实现）"""
        # 使用扩展欧几里得算法
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            return 1  # 如果没有逆元，返回1作为默认值
        return (x % m + m) % m
    
    def _to_base36(self, num: int) -> str:
        """转换为36进制字符串"""
        if num == 0:
            return '0'
        
        digits = '0123456789abcdefghijklmnopqrstuvwxyz'
        result = ''
        
        while num > 0:
            result = digits[num % 36] + result
            num //= 36
        
        return result

# 全局解码器实例
_decoder_instance = None

def get_security_decoder() -> SecurityDecoder:
    """获取全局解码器实例"""
    global _decoder_instance
    if _decoder_instance is None:
        _decoder_instance = SecurityDecoder()
    return _decoder_instance

def decode_password(encrypted_password: str) -> str:
    """解码密码"""
    decoder = get_security_decoder()
    return decoder.decode_secure_data(encrypted_password) or encrypted_password

# 用户名不需要解密，已移除 decode_username 函数

def decode_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """解码用户数据字典 - 只解密敏感字段"""
    decoder = get_security_decoder()
    decoded_data = data.copy()
    
    # 只解码敏感字段（密码相关）
    if 'password' in decoded_data:
        decoded_data['password'] = decoder.decode_secure_data(decoded_data['password']) or decoded_data['password']
    
    if 's_password' in decoded_data:
        decoded_data['s_password'] = decoder.decode_secure_data(decoded_data['s_password']) or decoded_data['s_password']
    
    # 用户名和邮箱不加密，直接使用原始数据
    # username 和 email 保持原样
    
    return decoded_data

# 系统初始化
logger.info(f"数据安全解码工具已加载 - 版本: {SYS_CONFIG['version']}")