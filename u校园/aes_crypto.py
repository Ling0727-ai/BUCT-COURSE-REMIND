"""
AES加密模块 - 对应U校园前端加密算法

提供与U校园前端一致的AES-CBC加密解密功能。
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii

# 处理导入问题 - 支持直接运行和作为包导入
try:
    # 作为包导入
    from .exceptions import UEncryptionError
except ImportError:
    # 直接运行时导入
    from exceptions import UEncryptionError

# U校园固定的加密参数
U_KEY = "***REMOVED***"
U_IV = "***REMOVED***"

def encrypt(text: str) -> str:
    """
    U校园AES加密
    
    Args:
        text: 要加密的文本
        
    Returns:
        16进制大写字符串的加密结果
        
    Raises:
        ValueError: 输入不是字符串时抛出
    """
    if not isinstance(text, str):
        raise ValueError("输入必须是字符串")
    
    # 将16进制字符串转换为字节
    key = binascii.unhexlify(U_KEY)
    iv = binascii.unhexlify(U_IV)
    
    # 创建AES cipher对象
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # PKCS7填充并加密
    padded_data = pad(text.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # 返回16进制大写字符串
    return ciphertext.hex().upper()

def decrypt(encrypted_hex: str) -> str:
    """
    U校园AES解密
    
    Args:
        encrypted_hex: 16进制加密字符串
        
    Returns:
        解密后的原文
        
    Raises:
        ValueError: 输入格式错误时抛出
    """
    if not isinstance(encrypted_hex, str):
        raise ValueError("输入必须是字符串")
    
    # 验证16进制格式
    if not all(c in '0123456789ABCDEF' for c in encrypted_hex):
        raise ValueError("输入必须是有效的16进制字符串")
    
    key = binascii.unhexlify(U_KEY)
    iv = binascii.unhexlify(U_IV)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    try:
        # 将16进制字符串转换为字节并解密
        ciphertext = binascii.unhexlify(encrypted_hex)
        decrypted_data = cipher.decrypt(ciphertext)
        
        # 去除PKCS7填充
        plaintext = unpad(decrypted_data, AES.block_size)
        return plaintext.decode('utf-8')
    except (ValueError, TypeError) as e:
        raise UEncryptionError(f"解密失败: {str(e)}")

def get_encryption_params() -> dict:
    """
    获取加密参数信息
    
    Returns:
        包含加密参数的字典
    """
    return {
        'algorithm': 'AES-CBC',
        'key': U_KEY,
        'iv': U_IV,
        'padding': 'PKCS7',
        'output_format': 'HEX_UPPERCASE'
    }