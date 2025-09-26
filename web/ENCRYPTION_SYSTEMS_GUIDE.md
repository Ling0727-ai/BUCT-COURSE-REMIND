# 加密系统架构说明

## 概述

本系统采用双重加密架构，RSA和ECC两套加密系统各司其职，确保数据安全的同时防止爬虫攻击。

## 🔐 加密系统分离架构

### ECC加密系统（原有系统）
**用途**: 用户数据存储加密
**位置**: `web/backend/app/model.py`
**配置**: 
```env
ECC_PRIVATE_KEY=REDACTED_ECC_PRIVATE_KEY
ECC_PUBLIC_KEY=10000000667
```

**功能**:
- 用户密码加密存储
- 敏感用户信息保护
- 数据库数据加密

### RSA加密系统（新增防爬虫系统）
**用途**: 前后端传输数据加密
**位置**: `web/backend/app/rsa_crypto.py`
**配置**:
```env
RSA_KEY_SIZE=2048
RSA_KEY_EXPIRE_MINUTES=30
RSA_ENABLE=true
```

**功能**:
- 登录数据传输加密
- 注册数据传输加密
- 防止爬虫攻击
- 动态密钥管理

## 🛡️ 安全特性对比

| 特性 | ECC加密 | RSA加密 |
|------|---------|---------|
| **用途** | 数据存储 | 数据传输 |
| **密钥类型** | 固定密钥 | 动态密钥 |
| **更新频率** | 不更新 | 30分钟更新 |
| **加密对象** | 用户密码等 | 登录注册数据 |
| **防护目标** | 数据泄露 | 爬虫攻击 |

## 📋 系统集成

### 后端集成
1. **环境变量分离**: ECC和RSA使用不同的环境变量前缀
2. **模块独立**: 两套加密系统在不同的模块中实现
3. **API分离**: RSA有独立的API端点获取公钥

### 前端集成
1. **RSA加密**: 登录注册页面使用RSA加密
2. **安全指示器**: 显示加密状态
3. **降级机制**: RSA不可用时自动降级

## 🔧 配置说明

### 启用/禁用RSA加密
```env
RSA_ENABLE=true   # 启用RSA加密
RSA_ENABLE=false  # 禁用RSA加密（开发模式）
```

### RSA密钥配置
```env
RSA_KEY_SIZE=2048              # RSA密钥长度
RSA_KEY_EXPIRE_MINUTES=30      # 密钥过期时间（分钟）
```

### ECC密钥配置
```env
ECC_PRIVATE_KEY=REDACTED_ECC_PRIVATE_KEY  # ECC私钥
ECC_PUBLIC_KEY=10000000667                   # ECC公钥
```

## 🚀 API端点

### RSA加密相关
- `GET /api/crypto/public-key` - 获取RSA公钥
- `GET /api/crypto/challenge` - 获取加密挑战

### 认证相关（支持RSA加密）
- `POST /api/auth/login` - 登录（支持RSA加密数据）
- `POST /api/auth/register` - 注册（支持RSA加密数据）

## 🧪 测试验证

运行测试脚本验证系统分离：
```bash
cd web/backend
python test_encryption_separation.py
```

测试内容：
- ✅ 环境变量配置检查
- ✅ RSA加密模块功能测试
- ✅ ECC加密模块功能测试
- ✅ API端点功能测试

## 📝 使用示例

### 前端RSA加密使用
```javascript
import rsaCrypto from '@/utils/rsa-crypto'

// 登录时加密数据
const loginData = {
  username: 'user123',
  password: 'password123',
  timestamp: Date.now()
}

const encryptedData = await rsaCrypto.encryptData(loginData)
// 发送加密数据到后端
```

### 后端RSA解密处理
```python
from app.rsa_crypto import get_rsa_crypto

# 解密前端发送的数据
rsa_crypto = get_rsa_crypto()
decrypted_data = rsa_crypto.decrypt_data(encrypted_data)

if decrypted_data:
    username = decrypted_data.get('username')
    password = decrypted_data.get('password')
```

## ⚠️ 注意事项

1. **密钥分离**: RSA和ECC密钥完全独立，不可混用
2. **环境变量**: 确保使用正确的环境变量前缀
3. **兼容性**: 系统支持加密和非加密请求的兼容处理
4. **性能**: RSA加密会增加一定的计算开销
5. **调试**: 开发环境可以禁用RSA加密便于调试

## 🔍 故障排除

### RSA加密不工作
1. 检查 `RSA_ENABLE=true` 是否设置
2. 验证前端是否正确导入RSA工具
3. 检查网络请求是否包含加密数据

### ECC加密问题
1. 确认 `ECC_PRIVATE_KEY` 和 `ECC_PUBLIC_KEY` 已设置
2. 检查User模型是否正确初始化
3. 验证数据库连接是否正常

### 环境变量问题
1. 确保.env文件在正确位置
2. 检查环境变量是否被正确加载
3. 验证变量名是否正确（注意前缀）