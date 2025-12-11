/**
 * RSA加密工具模块
 * 用于前端数据加密，防止爬虫攻击
 */

import JSEncrypt from 'jsencrypt'

class RSACrypto {
  constructor() {
    this.jsencrypt = new JSEncrypt()
    this.publicKey = null
    this.keyTimestamp = null
    this.keyExpireMinutes = 30
    this.rsaDisabled = false  // RSA是否被服务端禁用
  }

  /**
   * 获取RSA公钥
   */
  async getPublicKey() {
    try {
      const response = await fetch('/api/crypto/public-key', {
        method: 'GET',
        credentials: 'include'
      })

      const result = await response.json()
      
      // 检查RSA是否被禁用
      if (result.disabled) {
        console.warn('RSA加密已在服务端禁用')
        this.rsaDisabled = true
        return false
      }

      if (result.success && result.data) {
        this.publicKey = result.data.public_key
        this.keyTimestamp = result.data.timestamp
        this.keyExpireMinutes = result.data.expire_minutes
        this.rsaDisabled = false

        // 设置公钥到JSEncrypt
        this.jsencrypt.setPublicKey(this.publicKey)
        
        console.log('RSA公钥获取成功')
        return true
      } else {
        console.error('获取RSA公钥失败:', result.error || '未知错误')
        return false
      }
    } catch (error) {
      console.error('获取RSA公钥异常:', error)
      return false
    }
  }

  /**
   * 检查密钥是否过期
   * 提前2分钟判断为过期，给刷新留出缓冲时间
   */
  isKeyExpired() {
    if (!this.keyTimestamp) {
      return true
    }

    const now = Math.floor(Date.now() / 1000)
    // 提前2分钟刷新，避免临界点问题
    const bufferSeconds = 120
    const expireTime = this.keyTimestamp + (this.keyExpireMinutes * 60) - bufferSeconds

    return now > expireTime
  }

  /**
   * 确保有有效的公钥
   */
  async ensureValidKey() {
    // 如果RSA被禁用，直接返回false
    if (this.rsaDisabled) {
      return false
    }

    if (!this.publicKey || this.isKeyExpired()) {
      return await this.getPublicKey()
    }
    return true
  }

  /**
   * 加密数据
   * @param {Object} data - 要加密的数据对象
   * @param {boolean} isRetry - 是否是重试请求
   * @returns {string|null} - 加密后的Base64字符串，失败返回null
   */
  async encryptData(data, isRetry = false) {
    try {
      // 确保有有效的公钥
      const hasValidKey = await this.ensureValidKey()
      if (!hasValidKey) {
        throw new Error('无法获取有效的RSA公钥')
      }

      // 添加时间戳防重放攻击
      const dataWithTimestamp = {
        ...data,
        timestamp: Math.floor(Date.now() / 1000)
      }

      // 转换为JSON字符串
      const jsonString = JSON.stringify(dataWithTimestamp)
      
      // RSA加密
      const encrypted = this.jsencrypt.encrypt(jsonString)
      
      if (!encrypted) {
        // 加密失败时，强制刷新密钥并重试一次
        if (!isRetry) {
          console.warn('RSA加密失败，尝试刷新密钥后重试')
          this.publicKey = null  // 强制清除缓存的公钥
          this.keyTimestamp = null
          return await this.encryptData(data, true)
        }
        throw new Error('RSA加密失败')
      }

      console.log('数据加密成功')
      return encrypted
      
    } catch (error) {
      console.error('数据加密失败:', error)
      return null
    }
  }

  /**
   * 加密登录数据
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {string|null} - 加密后的数据
   */
  async encryptLoginData(username, password) {
    return await this.encryptData({
      username: username,
      password: password
    })
  }

  /**
   * 加密注册数据
   * @param {Object} registerData - 注册数据
   * @returns {string|null} - 加密后的数据
   */
  async encryptRegisterData(registerData) {
    return await this.encryptData(registerData)
  }

  /**
   * 创建加密请求体
   * @param {Object} data - 原始数据
   * @returns {Object} - 包含加密数据的请求体
   */
  async createEncryptedRequest(data) {
    // 如果RSA被禁用，直接返回原始数据
    if (this.rsaDisabled) {
      console.info('RSA加密已禁用，使用原始数据')
      return data
    }

    const encryptedData = await this.encryptData(data)
    
    if (!encryptedData) {
      // 如果加密失败，返回原始数据（兼容模式）
      console.warn('加密失败，使用原始数据')
      return data
    }

    return {
      encrypted_data: encryptedData
    }
  }

  /**
   * 测试加密功能
   * @returns {boolean|string} - true表示加密可用，'disabled'表示RSA已禁用，false表示失败
   */
  async testEncryption() {
    try {
      // 先尝试获取公钥
      const keyResult = await this.getPublicKey()

      // 如果RSA被禁用，返回特殊标识
      if (this.rsaDisabled) {
        console.info('RSA加密已在服务端禁用，将使用非加密模式')
        return 'disabled'
      }

      if (!keyResult) {
        console.error('RSA公钥获取失败')
        return false
      }

      const testData = {
        test: 'hello world',
        timestamp: Math.floor(Date.now() / 1000)
      }

      const encrypted = await this.encryptData(testData)
      
      if (encrypted) {
        console.log('RSA加密测试成功')
        console.log('原始数据:', testData)
        console.log('加密数据长度:', encrypted.length)
        return true
      } else {
        console.error('RSA加密测试失败')
        return false
      }
    } catch (error) {
      console.error('RSA加密测试异常:', error)
      return false
    }
  }
}

// 创建全局实例
const rsaCrypto = new RSACrypto()

export default rsaCrypto