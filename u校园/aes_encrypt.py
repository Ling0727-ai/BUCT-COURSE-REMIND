from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii

def encrypt(text):
    """
    对应前端的AES加密函数
    
    Args:
        text: 要加密的文本
        
    Returns:
        16进制大写字符串的加密结果
    """
    # 固定密钥和IV（从前端代码获取）
    key_hex = "***REMOVED***"
    iv_hex = "***REMOVED***"
    
    # 将16进制字符串转换为字节
    key = binascii.unhexlify(key_hex)
    iv = binascii.unhexlify(iv_hex)
    
    # 创建AES cipher对象
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # PKCS7填充并加密
    padded_data = pad(text.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # 返回16进制大写字符串
    return ciphertext.hex().upper()

def decrypt(encrypted_hex):
    """
    AES解密函数
    
    Args:
        encrypted_hex: 16进制加密字符串
        
    Returns:
        解密后的原文
    """
    key_hex = "***REMOVED***"
    iv_hex = "***REMOVED***"
    
    key = binascii.unhexlify(key_hex)
    iv = binascii.unhexlify(iv_hex)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 将16进制字符串转换为字节并解密
    ciphertext = binascii.unhexlify(encrypted_hex)
    decrypted_data = cipher.decrypt(ciphertext)
    
    # 去除PKCS7填充
    plaintext = unpad(decrypted_data, AES.block_size)
    return plaintext.decode('utf-8')

# 使用示例
if __name__ == "__main__":
    # 测试加密
    username = ""  # 替换为实际用户名
    password = ""  # 替换为实际密码

    encrypted_username = encrypt(username)
    encrypted_password = encrypt(password)
    print(f"用户名: {encrypted_username}")
    print(f"密码: {encrypted_password}")
