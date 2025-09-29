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
      
      if (result.success) {
        this.publicKey = result.data.public_key
        this.keyTimestamp = result.data.timestamp
        this.keyExpireMinutes = result.data.expire_minutes
        
        // 设置公钥到JSEncrypt
        this.jsencrypt.setPublicKey(this.publicKey)
        
        console.log('RSA公钥获取成功')
        return true
      } else {
        console.error('获取RSA公钥失败:', result.error)
        return false
      }
    } catch (error) {
      console.error('获取RSA公钥异常:', error)
      return false
    }
  }

  /**
   * 检查密钥是否过期
   */
  isKeyExpired() {
    if (!this.keyTimestamp) {
      return true
    }

    const now = Math.floor(Date.now() / 1000)
    const expireTime = this.keyTimestamp + (this.keyExpireMinutes * 60)
    
    return now > expireTime
  }

  /**
   * 确保有有效的公钥
   */
  async ensureValidKey() {
    if (!this.publicKey || this.isKeyExpired()) {
      return await this.getPublicKey()
    }
    return true
  }

  /**
   * 加密数据
   * @param {Object} data - 要加密的数据对象
   * @returns {string|null} - 加密后的Base64字符串，失败返回null
   */
  async encryptData(data) {
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
   */
  async testEncryption() {
    try {
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