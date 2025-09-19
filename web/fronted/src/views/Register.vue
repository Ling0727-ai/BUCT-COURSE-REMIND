<template>
  <div class="register-container">
    <!-- 浮动装饰元素 -->
    <div class="floating-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
      <div class="shape shape-5"></div>
    </div>

    <!-- 左侧表单区域 -->
    <div class="form-section">
      <div class="form-content">
        <!-- 品牌标识 -->
        <div class="brand-logo">
          <h1 class="brand-title">作业管理系统</h1>
          <p class="brand-subtitle">创建账号，开启高效学习管理</p>
        </div>

        <div class="form-card">
          <div class="form-header">
            <h2>用户注册</h2>
            <p>填写信息，创建您的专属账号</p>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>用户名</label>
              <div class="input-wrapper">
                <i class="fas fa-user input-icon"></i>
                <input 
                  type="text" 
                  v-model="formData.username" 
                  placeholder="请输入3-20位用户名"
                  class="form-input"
                >
                <span class="input-status success" v-if="formData.username.length >= 3">
                  <i class="fas fa-check"></i>
                </span>
              </div>
            </div>

            <div class="form-group">
              <label>邮箱地址</label>
              <div class="input-wrapper">
                <i class="fas fa-envelope input-icon"></i>
                <input 
                  type="email" 
                  v-model="formData.email" 
                  placeholder="请输入邮箱地址"
                  class="form-input"
                >
                <span class="input-status success" v-if="isValidEmail">
                  <i class="fas fa-check"></i>
                </span>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>密码</label>
              <div class="input-wrapper">
                <i class="fas fa-lock input-icon"></i>
                <input 
                  type="password" 
                  v-model="formData.password" 
                  placeholder="至少6位密码"
                  class="form-input"
                >
                <span class="input-status success" v-if="formData.password.length >= 6">
                  <i class="fas fa-check"></i>
                </span>
              </div>
              <div class="password-strength" v-if="formData.password.length > 0">
                <div class="strength-bar">
                  <div class="strength-fill" :class="passwordStrength"></div>
                </div>
                <span class="strength-text">密码强度：{{ strengthLabel }}</span>
              </div>
            </div>

            <div class="form-group">
              <label>确认密码</label>
              <div class="input-wrapper">
                <i class="fas fa-lock input-icon"></i>
                <input 
                  type="password" 
                  v-model="formData.confirmPassword" 
                  placeholder="再次输入密码"
                  class="form-input"
                >
                <span class="input-status success" v-if="formData.confirmPassword && formData.password === formData.confirmPassword">
                  <i class="fas fa-check"></i>
                </span>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>学号 <span class="optional">(可选)</span></label>
              <div class="input-wrapper">
                <i class="fas fa-id-card input-icon"></i>
                <input 
                  type="text" 
                  v-model="formData.studentId" 
                  placeholder="请输入学号"
                  class="form-input"
                >
                <span class="input-status success" v-if="formData.studentId.length > 0">
                  <i class="fas fa-check"></i>
                </span>
              </div>
            </div>

            <div class="form-group">
              <label>外部系统密码 <span class="optional">(可选)</span></label>
              <div class="input-wrapper">
                <i class="fas fa-key input-icon"></i>
                <input 
                  type="password" 
                  v-model="formData.sPassword" 
                  placeholder="教务系统密码"
                  class="form-input"
                >
                <span class="input-status success" v-if="formData.sPassword.length > 0">
                  <i class="fas fa-check"></i>
                </span>
              </div>
              <div class="field-hint">
                <i class="fas fa-info-circle"></i>
                用于自动登录教务系统等外部网站
              </div>
            </div>
          </div>

          <div class="form-group captcha-group">
            <label>邮箱验证码</label>
            <div class="captcha-container">
              <div class="input-wrapper captcha-input">
                <i class="fas fa-shield-alt input-icon"></i>
                <input 
                  type="text" 
                  v-model="formData.captcha" 
                  placeholder="请输入6位验证码"
                  maxlength="6"
                  class="form-input"
                >
                <span class="input-status success" v-if="formData.captcha.length === 6">
                  <i class="fas fa-check"></i>
                </span>
              </div>
              <button 
                class="captcha-btn" 
                @click="sendCaptcha"
                :disabled="captchaCooldown > 0 || !isValidEmail"
                :class="{ 'btn-disabled': captchaCooldown > 0 || !isValidEmail }"
              >
                <span v-if="captchaCooldown > 0">{{ captchaCooldown }}s</span>
                <span v-else>获取验证码</span>
              </button>
            </div>
            <div class="captcha-success" v-if="captchaSent">
              <i class="fas fa-check-circle"></i>
              验证码已发送至邮箱，请查收
            </div>
          </div>

          <div class="terms-agreement">
            <label class="custom-checkbox">
              <input type="checkbox" v-model="agreeTerms">
              <span class="checkmark">
                <i class="fas fa-check"></i>
              </span>
              <span class="checkbox-text">
                我已阅读并同意 <a href="#" class="terms-link">服务条款</a> 和 <a href="#" class="terms-link">隐私政策</a>
              </span>
            </label>
          </div>

          <button 
            class="register-btn" 
            @click="handleRegister"
            :disabled="loading || !isFormValid"
            :class="{ 'btn-loading': loading, 'btn-disabled': !isFormValid }"
          >
            <span v-if="!loading" class="btn-content">
              <i class="fas fa-user-plus"></i>
              创建账号
            </span>
            <span v-else class="btn-loading-content">
              <i class="fas fa-spinner fa-spin"></i>
              注册中...
            </span>
          </button>

          <div class="form-footer">
            <p>已有账号？ 
              <router-link to="/login" class="login-link">立即登录</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧插图区域 -->
    <div class="illustration-section">
      <div class="illustration-content">
        <!-- 主要图标 -->
        <div class="main-illustration">
          <div class="central-icon">
            <i class="fas fa-user-plus"></i>
            <div class="pulse-ring"></div>
            <div class="pulse-ring pulse-ring-2"></div>
          </div>
          
          <!-- 浮动功能图标 -->
          <div class="floating-icons">
            <div class="floating-icon icon-1">
              <i class="fas fa-tasks"></i>
            </div>
            <div class="floating-icon icon-2">
              <i class="fas fa-bell"></i>
            </div>
            <div class="floating-icon icon-3">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="floating-icon icon-4">
              <i class="fas fa-graduation-cap"></i>
            </div>
          </div>
        </div>

        <!-- 文字内容 -->
        <div class="illustration-text">
          <h3>开启学习管理之旅</h3>
          <p>注册账号，开始高效管理您的学习任务和作业进度</p>
          
          <div class="feature-highlights">
            <div class="feature-item">
              <div class="feature-icon">
                <i class="fas fa-bell"></i>
              </div>
              <span>智能作业提醒</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <i class="fas fa-tasks"></i>
              </div>
              <span>多科目管理</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <span>进度跟踪分析</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <transition name="toast-slide">
      <div v-if="showSuccess" class="toast-notification success">
        <div class="toast-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">注册成功！</div>
          <div class="toast-message">正在跳转到登录页面...</div>
        </div>
      </div>
    </transition>

    <transition name="toast-slide">
      <div v-if="errorMessage" class="toast-notification error">
        <div class="toast-icon">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">注册失败</div>
          <div class="toast-message">{{ errorMessage }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
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

    // 移动端viewport高度修复
    const setVH = () => {
      const vh = window.innerHeight * 0.01
      document.documentElement.style.setProperty('--vh', `${vh}px`)
    }

    onMounted(() => {
      // 设置初始viewport高度
      setVH()
      
      // 监听窗口大小变化
      window.addEventListener('resize', setVH)
      window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100) // 延迟执行，等待方向改变完成
      })
    })

    onUnmounted(() => {
      if (captchaInterval) {
        clearInterval(captchaInterval)
      }
      
      // 清理事件监听器
      window.removeEventListener('resize', setVH)
      window.removeEventListener('orientationchange', setVH)
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
/* 容器和背景 */
.register-container {
  height: 100vh;
  max-width: 100vw;
  display: flex;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4facfe 100%);
  overflow: hidden;
}

/* 浮动装饰元素 */
.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 30%;
  left: 5%;
  animation-delay: 2s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 10%;
  right: 10%;
  animation-delay: 3s;
}

.shape-5 {
  width: 140px;
  height: 140px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 左侧表单区域 */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  z-index: 2;
  overflow-y: auto;
}

.form-content {
  width: 100%;
  max-width: 480px;
}

/* 品牌标识 */
.brand-logo {
  text-align: center;
  margin-bottom: 24px;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 6px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.brand-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin: 0;
}

/* 表单卡片 */
.form-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-header {
  text-align: center;
  margin-bottom: 24px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.form-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

/* 表单行和组 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 6px;
}

.optional {
  color: #9ca3af;
  font-weight: 400;
  font-size: 12px;
}

/* 输入框样式 */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #6b7280;
  font-size: 14px;
  z-index: 1;
  transition: color 0.3s ease;
}

.form-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  background: #ffffff;
  color: #1f2937;
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.form-input:focus + .input-icon {
  color: #667eea;
}

.input-status {
  position: absolute;
  right: 16px;
  color: #10b981;
  font-size: 14px;
}

/* 密码强度指示器 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
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

.strength-text {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

/* 字段提示 */
.field-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 验证码组 */
.captcha-group {
  grid-column: 1 / -1;
  margin-bottom: 16px;
}

.captcha-container {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.captcha-input {
  flex: 1;
}

.captcha-btn {
  padding: 0 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 120px;
}

.captcha-btn:hover:not(.btn-disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.captcha-btn.btn-disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.captcha-success {
  font-size: 12px;
  color: #10b981;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 条款同意 */
.terms-agreement {
  margin: 20px 0;
}

.custom-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  font-size: 14px;
  line-height: 1.5;
}

.custom-checkbox input {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-top: 2px;
}

.custom-checkbox input:checked + .checkmark {
  background: #667eea;
  border-color: #667eea;
}

.checkmark i {
  color: white;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.custom-checkbox input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: #6b7280;
}

.terms-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.terms-link:hover {
  text-decoration: underline;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
}

.register-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.register-btn:hover:not(.btn-disabled):not(.btn-loading)::before {
  left: 100%;
}

.register-btn:hover:not(.btn-disabled):not(.btn-loading) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.register-btn.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-content,
.btn-loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 表单底部 */
.form-footer {
  text-align: center;
}

.form-footer p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.login-link:hover {
  text-decoration: underline;
}

/* 右侧插图区域 */
.illustration-section {
  flex: 0 0 40%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  position: relative;
  z-index: 2;
}

.illustration-content {
  text-align: center;
  color: white;
  max-width: 300px;
  width: 100%;
  position: relative;
  z-index: 10;
}

/* 主要插图 */
.main-illustration {
  position: relative;
  margin-bottom: 24px;
}

.central-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  z-index: 10;
}

.central-icon i {
  font-size: 32px;
  color: white;
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
  z-index: 1;
}

.pulse-ring-2 {
  width: 100px;
  height: 100px;
  animation-delay: 1.5s;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0;
  }
}

/* 浮动功能图标 */
.floating-icons {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 180px;
  height: 180px;
  z-index: 1;
}

.floating-icon {
  position: absolute;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: floatAround 8s ease-in-out infinite;
}

.floating-icon i {
  font-size: 16px;
  color: white;
}

.icon-1 {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 0s;
}

.icon-2 {
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  animation-delay: 2s;
}

.icon-3 {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 4s;
}

.icon-4 {
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  animation-delay: 6s;
}

@keyframes floatAround {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  25% { transform: translateX(-50%) translateY(-5px); }
  50% { transform: translateX(-50%) translateY(0); }
  75% { transform: translateX(-50%) translateY(5px); }
}

/* 插图文字 */
.illustration-text {
  position: relative;
  z-index: 10;
}

.illustration-text h3 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.illustration-text p {
  font-size: 14px;
  line-height: 1.5;
  opacity: 0.9;
  margin: 0 0 24px 0;
}

/* 功能亮点 */
.feature-highlights {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature-icon {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon i {
  font-size: 14px;
  color: white;
}

/* 消息提示 */
.toast-notification {
  position: fixed;
  top: 24px;
  right: 24px;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  z-index: 1000;
}

.toast-notification.success {
  border-left: 4px solid #10b981;
}

.toast-notification.error {
  border-left: 4px solid #ef4444;
}

.toast-notification {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.toast-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-notification.success .toast-icon {
  color: #10b981;
}

.toast-notification.error .toast-icon {
  color: #ef4444;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 14px;
  color: #6b7280;
}

/* 动画 */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s ease;
}

.toast-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .register-container {
    flex-direction: column;
  }
  
  .illustration-section {
    order: -1;
    flex: 0 0 auto;
    min-height: 280px;
    padding: 20px;
  }
  
  .form-section {
    flex: 1;
    min-height: auto;
  }
  
  .main-illustration {
    margin-bottom: 20px;
  }
  
  .central-icon {
    width: 70px;
    height: 70px;
  }
  
  .central-icon i {
    font-size: 28px;
  }
  
  .floating-icons {
    width: 180px;
    height: 180px;
  }
  
  .floating-icon {
    width: 36px;
    height: 36px;
  }
  
  .floating-icon i {
    font-size: 14px;
  }
  
  .illustration-text h3 {
    font-size: 20px;
  }
  
  .illustration-text p {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .register-container {
    height: auto;
    min-height: 100vh;
  }
  
  .illustration-section {
    min-height: 200px;
    padding: 16px;
  }
  
  .form-section {
    padding: 16px;
  }
  
  .form-content {
    max-width: 100%;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 14px;
    margin-bottom: 16px;
  }
  
  .form-card {
    padding: 24px 20px;
    border-radius: 16px;
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .brand-subtitle {
    font-size: 13px;
  }
  
  .form-header h2 {
    font-size: 20px;
  }
  
  .form-header p {
    font-size: 13px;
  }
  
  .form-input {
    padding: 12px 14px 12px 38px;
    font-size: 14px;
  }
  
  .input-icon {
    left: 12px;
    font-size: 13px;
  }
  
  .captcha-container {
    flex-direction: column;
    gap: 10px;
  }
  
  .captcha-btn {
    min-width: auto;
    padding: 12px 20px;
    font-size: 13px;
  }
  
  .register-btn {
    padding: 14px;
    font-size: 14px;
  }
  
  .toast-notification {
    top: 16px;
    right: 16px;
    left: 16px;
    max-width: none;
  }
  
  .central-icon {
    width: 60px;
    height: 60px;
  }
  
  .central-icon i {
    font-size: 24px;
  }
  
  .floating-icons {
    width: 140px;
    height: 140px;
  }
  
  .floating-icon {
    width: 30px;
    height: 30px;
  }
  
  .floating-icon i {
    font-size: 12px;
  }
  
  .illustration-text h3 {
    font-size: 18px;
  }
  
  .illustration-text p {
    font-size: 12px;
  }
  
  .feature-item {
    padding: 10px 12px;
    font-size: 12px;
  }
  
  .feature-icon {
    width: 28px;
    height: 28px;
  }
  
  .feature-icon i {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .register-container {
    overflow-x: hidden;
  }
  
  .form-section,
  .illustration-section {
    padding: 12px;
  }
  
  .form-card {
    padding: 20px 16px;
    margin: 0;
    border-radius: 12px;
  }
  
  .brand-logo {
    margin-bottom: 20px;
  }
  
  .brand-title {
    font-size: 22px;
  }
  
  .form-header {
    margin-bottom: 20px;
  }
  
  .form-header h2 {
    font-size: 18px;
  }
  
  .form-row {
    gap: 12px;
    margin-bottom: 14px;
  }
  
  .form-group label {
    font-size: 12px;
    margin-bottom: 5px;
  }
  
  .form-input {
    padding: 11px 12px 11px 36px;
    font-size: 14px;
    border-radius: 8px;
  }
  
  .input-icon {
    left: 11px;
    font-size: 12px;
  }
  
  .input-status {
    right: 12px;
    font-size: 12px;
  }
  
  .password-strength {
    gap: 8px;
    margin-top: 6px;
  }
  
  .strength-text {
    font-size: 11px;
  }
  
  .field-hint {
    font-size: 11px;
    margin-top: 4px;
  }
  
  .captcha-container {
    gap: 8px;
  }
  
  .captcha-btn {
    padding: 11px 16px;
    font-size: 12px;
    border-radius: 8px;
  }
  
  .captcha-success {
    font-size: 11px;
    margin-top: 6px;
  }
  
  .terms-agreement {
    margin: 16px 0;
  }
  
  .custom-checkbox {
    font-size: 12px;
    gap: 8px;
  }
  
  .checkmark {
    width: 18px;
    height: 18px;
  }
  
  .checkmark i {
    font-size: 10px;
  }
  
  .register-btn {
    padding: 12px;
    font-size: 13px;
    border-radius: 8px;
    margin-bottom: 14px;
  }
  
  .form-footer p {
    font-size: 12px;
  }
  
  .shape {
    display: none;
  }
  
  .illustration-section {
    min-height: 160px;
  }
  
  .central-icon {
    width: 50px;
    height: 50px;
  }
  
  .central-icon i {
    font-size: 20px;
  }
  
  .floating-icons {
    width: 120px;
    height: 120px;
  }
  
  .floating-icon {
    width: 24px;
    height: 24px;
  }
  
  .floating-icon i {
    font-size: 10px;
  }
  
  .illustration-text h3 {
    font-size: 16px;
    margin-bottom: 8px;
  }
  
  .illustration-text p {
    font-size: 11px;
    margin-bottom: 16px;
  }
  
  .feature-highlights {
    gap: 8px;
  }
  
  .feature-item {
    padding: 8px 10px;
    font-size: 11px;
    border-radius: 8px;
  }
  
  .feature-icon {
    width: 24px;
    height: 24px;
  }
  
  .feature-icon i {
    font-size: 10px;
  }
  
  .toast-notification {
    top: 12px;
    right: 12px;
    left: 12px;
    padding: 12px;
  }
  
  .toast-icon {
    width: 20px;
    height: 20px;
  }
  
  .toast-title {
    font-size: 13px;
  }
  
  .toast-message {
    font-size: 12px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 360px) {
  .form-card {
    padding: 16px 12px;
  }
  
  .brand-title {
    font-size: 20px;
  }
  
  .form-header h2 {
    font-size: 16px;
  }
  
  .form-input {
    padding: 10px 11px 10px 34px;
    font-size: 13px;
  }
  
  .input-icon {
    left: 10px;
  }
  
  .captcha-btn {
    padding: 10px 14px;
    font-size: 11px;
  }
  
  .register-btn {
    padding: 11px;
    font-size: 12px;
  }
  
  .illustration-section {
    min-height: 140px;
  }
  
  .central-icon {
    width: 40px;
    height: 40px;
  }
  
  .central-icon i {
    font-size: 16px;
  }
  
  .floating-icons {
    width: 100px;
    height: 100px;
  }
  
  .floating-icon {
    width: 20px;
    height: 20px;
  }
  
  .floating-icon i {
    font-size: 8px;
  }
}

/* 横屏模式优化 */
@media (max-width: 768px) and (orientation: landscape) {
  .register-container {
    flex-direction: row;
  }
  
  .illustration-section {
    order: 0;
    flex: 0 0 35%;
    min-height: 100vh;
  }
  
  .form-section {
    flex: 1;
    overflow-y: auto;
  }
  
  .form-card {
    margin: 20px 0;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .form-input {
    padding: 14px 16px 14px 40px;
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  .captcha-btn,
  .register-btn {
    min-height: 44px; /* iOS推荐的最小触摸目标 */
  }
  
  .custom-checkbox {
    padding: 8px;
  }
  
  .checkmark {
    width: 22px;
    height: 22px;
  }
}

/* 高分辨率屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .form-input,
  .captcha-btn,
  .register-btn {
    border-width: 0.5px;
  }
}
</style>