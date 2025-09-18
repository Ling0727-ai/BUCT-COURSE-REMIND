<template>
  <div class="register-container">
    <!-- 左侧表单区域 -->
    <div class="form-section">
      <div class="form-content">
        <div class="form-header">
          <div class="logo">
            <i class="fas fa-graduation-cap"></i>
            <h1>作业管理系统</h1>
          </div>
          <p class="subtitle">创建账号，开启高效学习管理</p>
        </div>

        <div class="form-body">
          <h2>用户注册</h2>
          
          <div class="form-group">
            <label>用户名</label>
            <div class="input-container">
              <i class="fas fa-user"></i>
              <input 
                type="text" 
                v-model="formData.username" 
                placeholder="请输入3-20位用户名"
                class="form-input"
              >
              <span class="input-status" v-if="formData.username.length >= 3">✓</span>
            </div>
          </div>

          <div class="form-group">
            <label>邮箱地址</label>
            <div class="input-container">
              <i class="fas fa-envelope"></i>
              <input 
                type="email" 
                v-model="formData.email" 
                placeholder="请输入邮箱"
                class="form-input"
              >
              <span class="input-status" v-if="isValidEmail">✓</span>
            </div>
          </div>

          <div class="form-group">
            <label>密码</label>
            <div class="input-container">
              <i class="fas fa-lock"></i>
              <input 
                type="password" 
                v-model="formData.password" 
                placeholder="至少6位密码"
                class="form-input"
              >
              <span class="input-status" v-if="formData.password.length >= 6">✓</span>
            </div>
            <div class="password-strength" v-if="formData.password.length > 0">
              <div class="strength-meter">
                <div class="strength-fill" :class="passwordStrength"></div>
              </div>
              <span class="strength-label">{{ strengthLabel }}</span>
            </div>
          </div>

          <div class="form-group">
            <label>确认密码</label>
            <div class="input-container">
              <i class="fas fa-lock"></i>
              <input 
                type="password" 
                v-model="formData.confirmPassword" 
                placeholder="再次输入密码"
                class="form-input"
              >
              <span class="input-status" v-if="formData.confirmPassword && formData.password === formData.confirmPassword">✓</span>
            </div>
          </div>

          <div class="form-group">
            <label>学号 (可选)</label>
            <div class="input-container">
              <i class="fas fa-id-card"></i>
              <input 
                type="text" 
                v-model="formData.studentId" 
                placeholder="请输入学号"
                class="form-input"
              >
              <span class="input-status" v-if="formData.studentId.length > 0">✓</span>
            </div>
          </div>

          <div class="form-group">
            <label>外部系统密码 (可选)</label>
            <div class="input-container">
              <i class="fas fa-key"></i>
              <input 
                type="password" 
                v-model="formData.sPassword" 
                placeholder="用于访问外部系统的密码"
                class="form-input"
              >
              <span class="input-status" v-if="formData.sPassword.length > 0">✓</span>
            </div>
            <div class="field-tip">
              <i class="fas fa-info-circle"></i>
              此密码用于自动登录教务系统等外部网站
            </div>
          </div>

          <div class="form-group">
            <label>邮箱验证码</label>
            <div class="captcha-row">
              <div class="input-container">
                <i class="fas fa-shield-alt"></i>
                <input 
                  type="text" 
                  v-model="formData.captcha" 
                  placeholder="请输入6位验证码"
                  maxlength="6"
                  class="form-input"
                >
                <span class="input-status" v-if="formData.captcha.length === 6">✓</span>
              </div>
              <button 
                class="captcha-btn" 
                @click="sendCaptcha"
                :disabled="captchaCooldown > 0 || !isValidEmail"
                :class="{ cooldown: captchaCooldown > 0 }"
              >
                {{ captchaCooldown > 0 ? `${captchaCooldown}s` : '获取验证码' }}
              </button>
            </div>
            <div class="captcha-tip" v-if="captchaSent">
              <i class="fas fa-check-circle"></i>
              验证码已发送至邮箱
            </div>
          </div>

          <div class="agree-terms">
            <label class="checkbox">
              <input type="checkbox" v-model="agreeTerms">
              <span class="checkmark"></span>
              我已阅读并同意<a href="#">服务条款</a>和<a href="#">隐私政策</a>
            </label>
          </div>

          <button 
            class="submit-btn" 
            @click="handleRegister"
            :disabled="loading || !isFormValid"
            :class="{ loading: loading }"
          >
            <span v-if="!loading">注册账号</span>
            <span v-else class="loading-text">
              <i class="fas fa-spinner"></i>
              注册中...
            </span>
          </button>

          <div class="login-link">
            已有账号？ <router-link to="/login">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧插图区域 -->
    <div class="illustration-section">
      <div class="illustration-content">
        <div class="illustration-image">
          <i class="fas fa-user-plus"></i>
        </div>
        <h3>开启学习管理之旅</h3>
        <p>注册账号，开始高效管理您的学习任务和作业进度</p>
        <div class="feature-list">
          <div class="feature-item">
            <i class="fas fa-check-circle"></i>
            <span>智能作业提醒</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-check-circle"></i>
            <span>多科目管理</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-check-circle"></i>
            <span>进度跟踪</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <transition name="fade">
      <div v-if="showSuccess" class="toast success">
        <i class="fas fa-check-circle"></i>
        <span>注册成功！</span>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="errorMessage" class="toast error">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ errorMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, reactive, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const formData = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      captcha: '',
      studentId: '',
      sPassword: ''
    })
    const agreeTerms = ref(false)
    const loading = ref(false)
    const showSuccess = ref(false)
    const errorMessage = ref('')
    const captchaCooldown = ref(0)
    const captchaSent = ref(false)
    let captchaInterval = null

    const isValidEmail = computed(() => {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
    })

    const passwordStrength = computed(() => {
      if (formData.password.length === 0) return ''
      if (formData.password.length < 6) return 'weak'
      if (formData.password.length < 10) return 'medium'
      return 'strong'
    })

    const strengthLabel = computed(() => {
      return {
        '': '',
        weak: '弱',
        medium: '中',
        strong: '强'
      }[passwordStrength.value]
    })

    const isFormValid = computed(() => {
      return formData.username.length >= 3 &&
             isValidEmail.value &&
             formData.password.length >= 6 &&
             formData.password === formData.confirmPassword &&
             formData.captcha.length === 6 &&
             agreeTerms.value
    })

    const sendCaptcha = async () => {
      if (!isValidEmail.value) {
        errorMessage.value = '请输入有效的邮箱地址'
        setTimeout(() => { errorMessage.value = '' }, 3000)
        return
      }

      // 防止重复点击
      if (captchaCooldown.value > 0) {
        return
      }

      try {
        const response = await fetch('http://localhost:5000/api/auth/send-verification-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: formData.email
          })
        })

        const data = await response.json()

        if (response.ok) {
          captchaCooldown.value = 60
          captchaSent.value = true
          
          // 检查是否为测试模式
          if (data.test_mode && data.verification_code) {
            // 测试模式：显示验证码
            const testTip = document.createElement('div')
            testTip.className = 'toast success test-mode'
            testTip.innerHTML = `
              <div>
                <i class="fas fa-info-circle"></i>
                <div>
                  <div>邮件服务暂时不可用，使用测试模式</div>
                  <div style="font-size: 18px; font-weight: bold; margin-top: 8px;">
                    验证码：${data.verification_code}
                  </div>
                </div>
              </div>
            `
            testTip.style.cssText = `
              position: fixed;
              top: 20px;
              right: 20px;
              left: 20px;
              max-width: 400px;
              margin: 0 auto;
              padding: 16px;
              background: #10b981;
              color: white;
              border-radius: 8px;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
              z-index: 1000;
              text-align: center;
            `
            document.body.appendChild(testTip)
            setTimeout(() => {
              if (document.body.contains(testTip)) {
                document.body.removeChild(testTip)
              }
            }, 10000) // 显示10秒
          } else {
            // 正常模式：显示成功提示
            const successTip = document.createElement('div')
            successTip.className = 'toast success'
            successTip.innerHTML = '<i class="fas fa-check-circle"></i><span>验证码已发送到邮箱</span>'
            document.body.appendChild(successTip)
            setTimeout(() => {
              if (document.body.contains(successTip)) {
                document.body.removeChild(successTip)
              }
            }, 3000)
          }
          
          captchaInterval = setInterval(() => {
            captchaCooldown.value--
            if (captchaCooldown.value <= 0) {
              clearInterval(captchaInterval)
              captchaSent.value = false
            }
          }, 1000)
        } else {
          errorMessage.value = data.error || '发送验证码失败'
          setTimeout(() => { errorMessage.value = '' }, 3000)
        }
        
      } catch (error) {
        console.error('发送验证码错误:', error)
        errorMessage.value = '网络错误，请检查网络连接后重试'
        setTimeout(() => { errorMessage.value = '' }, 3000)
      }
    }

    const handleRegister = async () => {
      if (!isFormValid.value) {
        errorMessage.value = '请完善所有必填信息'
        setTimeout(() => { errorMessage.value = '' }, 3000)
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        // 先验证验证码
        const verifyResponse = await fetch('http://localhost:5000/api/auth/verify-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: formData.email,
            code: formData.captcha
          })
        })

        if (!verifyResponse.ok) {
          const verifyData = await verifyResponse.json()
          errorMessage.value = verifyData.error || '验证码验证失败'
          setTimeout(() => { errorMessage.value = '' }, 3000)
          return
        }

        // 注册用户
        const response = await fetch('http://localhost:5000/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: formData.username,
            email: formData.email,
            password: formData.password,
            student_id: formData.studentId || '',
            s_password: formData.sPassword || ''
          })
        })

        const data = await response.json()

        if (response.ok) {
          showSuccess.value = true
          // 清空表单
          Object.keys(formData).forEach(key => {
            formData[key] = ''
          })
          agreeTerms.value = false
          
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else {
          errorMessage.value = data.error || '注册失败，请重试'
          setTimeout(() => { errorMessage.value = '' }, 3000)
        }
        
      } catch (error) {
        console.error('注册错误:', error)
        errorMessage.value = '网络错误，请检查网络连接后重试'
        setTimeout(() => { errorMessage.value = '' }, 3000)
      } finally {
        loading.value = false
      }
    }

    onUnmounted(() => {
      if (captchaInterval) {
        clearInterval(captchaInterval)
      }
    })

    return {
      formData,
      agreeTerms,
      loading,
      showSuccess,
      errorMessage,
      captchaCooldown,
      captchaSent,
      isValidEmail,
      passwordStrength,
      strengthLabel,
      isFormValid,
      sendCaptcha,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  background: white;
}

/* 左侧表单区域 */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: white;
  min-height: 100vh;
}

.form-content {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo i {
  font-size: 32px;
  color: #667eea;
}

.logo h1 {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.form-body h2 {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 32px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-container i {
  position: absolute;
  left: 16px;
  color: #9ca3af;
  font-size: 16px;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-status {
  position: absolute;
  right: 16px;
  color: #10b981;
  font-weight: bold;
  font-size: 14px;
}

.field-tip {
  font-size: 12px;
  color: #6b7280;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.strength-meter {
  flex: 1;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.strength-fill.weak {
  width: 33%;
  background: #ef4444;
}

.strength-fill.medium {
  width: 66%;
  background: #f59e0b;
}

.strength-fill.strong {
  width: 100%;
  background: #10b981;
}

.strength-label {
  font-size: 12px;
  font-weight: 600;
  min-width: 20px;
}

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.captcha-btn {
  padding: 0 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 100px;
}

.captcha-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.captcha-btn:disabled,
.captcha-btn.cooldown {
  background: #9ca3af;
  cursor: not-allowed;
}

.captcha-tip {
  font-size: 12px;
  color: #10b981;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.agree-terms {
  margin: 24px 0;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
}

.checkbox input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox input:checked + .checkmark {
  background: #667eea;
  border-color: #667eea;
}

.checkbox input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.checkbox a {
  color: #667eea;
  text-decoration: none;
}

.checkbox a:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-text i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}

/* 右侧插图区域 */
.illustration-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: white;
  min-height: 100vh;
}

.illustration-content {
  text-align: center;
  max-width: 400px;
}

.illustration-image {
  margin-bottom: 32px;
}

.illustration-image i {
  font-size: 64px;
  background: rgba(255, 255, 255, 0.2);
  padding: 24px;
  border-radius: 50%;
  backdrop-filter: blur(10px);
}

.illustration-content h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
}

.illustration-content p {
  font-size: 16px;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 32px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.feature-item i {
  color: #10b981;
  font-size: 16px;
}

/* 提示信息 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

.toast.success {
  background: #10b981;
}

.toast.error {
  background: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 968px) {
  .register-container {
    flex-direction: column;
  }
  
  .form-section {
    min-height: auto;
    padding: 40px 20px;
  }
  
  .illustration-section {
    min-height: auto;
    padding: 40px 20px;
  }
  
  .illustration-image i {
    font-size: 48px;
    padding: 20px;
  }
}

@media (max-width: 640px) {
  .form-content {
    max-width: 100%;
  }
  
  .captcha-row {
    flex-direction: column;
  }
  
  .captcha-btn {
    min-width: auto;
    padding: 12px;
  }
  
  .logo {
    flex-direction: column;
    gap: 8px;
  }
  
  .logo h1 {
    font-size: 24px;
  }
  
  .form-body h2 {
    font-size: 20px;
  }
  
  .toast {
    top: 16px;
    right: 16px;
    left: 16px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .form-section {
    padding: 32px 16px;
  }
  
  .illustration-section {
    padding: 32px 16px;
  }
  
  .form-input {
    padding: 12px 16px 12px 44px;
  }
  
  .submit-btn {
    padding: 14px;
  }
}
</style>