<template>
  <div class="register-container">
    <!-- 动态背景 -->
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <!-- 左侧表单区域 -->
    <div class="form-section">
      <div class="form-content">
        <!-- 品牌标识 -->
        <div class="brand-logo">
          <div class="brand-accent"></div>
          <div class="brand-text">
            <h1 class="brand-title">作业管理系统</h1>
            <p class="brand-subtitle">创建账号，开启高效学习管理</p>
          </div>
        </div>

        <div class="form-card">
          <div class="form-header">
            <h2>用户注册</h2>
            <p>填写信息，创建您的专属账号</p>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label :class="{ active: formData.username.length > 0, focused: usernameFocused }"
                     class="form-label">用户名</label>
              <div class="input-wrapper">
                <input
                    v-model="formData.username"
                    type="text"
                  placeholder="请输入3-20位用户名"
                  class="form-input"
                    @blur="usernameFocused = false"
                    @focus="usernameFocused = true"
                >
                <span class="input-underline"></span>
              </div>
            </div>

            <div class="form-group">
              <label :class="{ active: formData.email.length > 0, focused: emailFocused }"
                     class="form-label">邮箱地址</label>
              <div class="input-wrapper">
                <input
                    v-model="formData.email"
                    type="email"
                  placeholder="请输入邮箱地址"
                  class="form-input"
                    @blur="emailFocused = false"
                    @focus="emailFocused = true"
                >
                <span class="input-underline"></span>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label :class="{ active: formData.password.length > 0, focused: passwordFocused }"
                     class="form-label">密码</label>
              <div class="input-wrapper has-eye">
                <input
                    v-model="formData.password"
                    :type="showPassword ? 'text' : 'password'"
                  placeholder="至少6位密码"
                  class="form-input"
                    autocomplete="new-password"
                    @blur="passwordFocused = false"
                    @focus="passwordFocused = true"
                >
                <span class="input-underline"></span>
                <button
                    :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                    class="toggle-visibility"
                    type="button"
                    @click="showPassword = !showPassword"
                >
                  <i :class="['fas', showPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
              <div class="password-strength" v-if="formData.password.length > 0">
                <div class="strength-bar">
                  <div class="strength-fill" :class="passwordStrength"></div>
                </div>
                <span class="strength-text">{{ strengthLabel }}</span>
              </div>
            </div>

            <div class="form-group">
              <label :class="{ active: formData.confirmPassword.length > 0, focused: confirmPasswordFocused }"
                     class="form-label">确认密码</label>
              <div class="input-wrapper has-eye">
                <input
                    v-model="formData.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="再次输入密码"
                  class="form-input"
                    autocomplete="new-password"
                    @blur="confirmPasswordFocused = false"
                    @focus="confirmPasswordFocused = true"
                >
                <span class="input-underline"></span>
                <button
                    :aria-label="showConfirmPassword ? '隐藏密码' : '显示密码'"
                    class="toggle-visibility"
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                >
                  <i :class="['fas', showConfirmPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label optional-label">学号 <span class="optional">(选填)</span></label>
              <div class="input-wrapper">
                <input
                    v-model="formData.studentId"
                    type="text"
                  placeholder="请输入学号"
                  class="form-input"
                >
                <span class="input-underline"></span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label optional-label">外部系统密码 <span class="optional">(选填)</span></label>
              <div class="input-wrapper has-eye">
                <input
                    v-model="formData.sPassword"
                    :type="showSPassword ? 'text' : 'password'"
                  placeholder="教务系统密码"
                  class="form-input"
                    autocomplete="new-password"
                >
                <span class="input-underline"></span>
                <button
                    :aria-label="showSPassword ? '隐藏密码' : '显示密码'"
                    class="toggle-visibility"
                    type="button"
                    @click="showSPassword = !showSPassword"
                >
                  <i :class="['fas', showSPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
              <div class="field-hint">
                <span class="hint-dot"></span>
                用于自动登录教务系统等外部网站
              </div>
            </div>
          </div>

          <div class="form-group captcha-group">
            <label :class="{ active: formData.captcha.length > 0, focused: captchaFocused }"
                   class="form-label">邮箱验证码</label>
            <div class="captcha-container">
              <div class="input-wrapper captcha-input">
                <input
                    type="text"
                  v-model="formData.captcha"
                  placeholder="6位验证码"
                  maxlength="6"
                  class="form-input"
                    @blur="captchaFocused = false"
                    @focus="captchaFocused = true"
                >
                <span class="input-underline"></span>
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
              <span class="success-dot"></span>
              验证码已发送
            </div>
          </div>

          <div class="terms-agreement">
            <label class="custom-checkbox">
              <input type="checkbox" v-model="agreeTerms">
              <span class="checkmark"><i class="fas fa-check"></i></span>
              <span class="checkbox-text">
                我已阅读并同意
                <router-link class="terms-link" to="/terms">服务条款</router-link>
                和
                <router-link class="terms-link" to="/privacy">隐私政策</router-link>
              </span>
            </label>
          </div>

          <button
              class="register-btn"
            @click="handleRegister"
            :disabled="loading || !isFormValid"
            :class="{ 'btn-loading': loading, 'btn-disabled': !isFormValid }"
          >
            <span v-if="!loading" class="btn-text">创建账号</span>
            <span v-else class="btn-loading-content">
              <i class="fas fa-spinner fa-spin"></i>
              注册中...
            </span>
            <span class="btn-shine"></span>
          </button>

          <div class="form-footer">
            <p>已有账号？
              <router-link class="login-link" to="/login">
                <span>立即登录</span>
                <i class="fas fa-arrow-right"></i>
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧说明区域 -->
    <div class="illustration-section">
      <div class="illustration-content">
        <h3>开启智能学习之旅</h3>
        <p>注册即可享受全方位的课程与作业管理服务</p>
        <ul class="feature-list">
          <li>
            <span class="feature-dot"></span>
            多平台数据自动同步
          </li>
          <li>
            <span class="feature-dot"></span>
            智能提醒，科学规划时间
          </li>
          <li>
            <span class="feature-dot"></span>
            数据加密，安全可靠
          </li>
        </ul>
      </div>
    </div>

    <!-- 消息提示 -->
    <transition name="toast-slide">
      <div v-if="showSuccess" class="toast">
        <div class="toast-title">注册成功！</div>
        <div class="toast-message">正在跳转到登录页面...</div>
      </div>
    </transition>
  </div>
</template>

<script>
import {computed, onMounted, onUnmounted, reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import rsaCrypto from '@/utils/rsa-crypto'

export default {
  name: 'RegisterOptimized',
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
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const showSPassword = ref(false)
    const usernameFocused = ref(false)
    const emailFocused = ref(false)
    const passwordFocused = ref(false)
    const confirmPasswordFocused = ref(false)
    const captchaFocused = ref(false)
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

      if (captchaCooldown.value > 0) {
        return
      }

      try {
        const response = await fetch('/api/auth/send-verification-code', {
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
          
          if (data.test_mode && data.verification_code) {
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
            }, 10000)
          } else {
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
        const verifyResponse = await fetch('/api/auth/verify-code', {
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

        // 创建加密的请求数据
        const requestData = await rsaCrypto.createEncryptedRequest({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          student_id: formData.studentId || '',
          s_password: formData.sPassword || ''
        })

        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        const data = await response.json()

        if (response.ok) {
          showSuccess.value = true
          Object.keys(formData).forEach(key => {
            formData[key] = ''
          })
          agreeTerms.value = false
          
          // 显示注册后的数据刷新提示（若后端返回）
          try {
            if (data && data.data_refresh) {
              const tip = document.createElement('div')
              const success = !!data.data_refresh.success
              const count = data.data_refresh.count || 0
              const message = data.data_refresh.message || (success ? `已刷新 ${count} 条记录` : '数据刷新失败')
              tip.className = `toast ${success ? 'success' : 'error'}`
              tip.innerHTML = `
                <i class="fas ${success ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
              `
              tip.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                left: 20px;
                max-width: 420px;
                margin: 0 auto;
                padding: 14px 16px;
                background: ${success ? '#10b981' : '#ef4444'};
                color: white;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                text-align: center;
                display: flex;
                gap: 8px;
                align-items: center;
                justify-content: center;
              `
              document.body.appendChild(tip)
              setTimeout(() => {
                if (document.body.contains(tip)) document.body.removeChild(tip)
              }, 3000)
            }
          } catch (e) {
            console.warn('显示注册后数据刷新提示失败:', e)
          }

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

    const setVH = () => {
      const vh = window.innerHeight * 0.01
      document.documentElement.style.setProperty('--vh', `${vh}px`)
    }

    onMounted(() => {
      setVH()
      window.addEventListener('resize', setVH)
      window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100)
      })
    })

    onUnmounted(() => {
      if (captchaInterval) {
        clearInterval(captchaInterval)
      }
      window.removeEventListener('resize', setVH)
      window.removeEventListener('orientationchange', setVH)
    })

    return {
      formData,
      showPassword,
      showConfirmPassword,
      showSPassword,
      usernameFocused,
      emailFocused,
      passwordFocused,
      confirmPasswordFocused,
      captchaFocused,
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
/* ─── 页面容器 ─── */
.register-container {
  min-height: 100vh;
  background: linear-gradient(160deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdfa 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 20px;
  gap: 60px;
  overflow-y: auto;
  position: relative;
}

/* ─── 动态背景 ─── */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(14, 165, 233, 0.03) 1px, transparent 1px),
  linear-gradient(90deg, rgba(14, 165, 233, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 20%, transparent 100%);
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.blob-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #dbeafe, #eff6ff);
  top: -150px;
  left: -100px;
  animation: drift1 20s ease-in-out infinite alternate;
}

.blob-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #d1fae5, #ecfdf5);
  bottom: -100px;
  right: -50px;
  animation: drift2 18s ease-in-out infinite alternate;
}

.blob-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #ede9fe, #f5f3ff);
  top: 50%;
  right: 20%;
  animation: drift3 22s ease-in-out infinite alternate;
}

@keyframes drift1 {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(50px, -40px) scale(1.05);
  }
}

@keyframes drift2 {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(-40px, 50px) scale(1.08);
  }
}

@keyframes drift3 {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(30px, -30px) scale(0.95);
  }
}

/* ─── 表单区域 ─── */
.form-section {
  flex: 0 0 auto;
  width: 100%;
  max-width: 480px;
  z-index: 2;
  animation: formSlideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}

@keyframes formSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.form-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 36px 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(14, 165, 233, 0.1);
  position: relative;
  overflow: hidden;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8, #0ea5e9);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 品牌 */
.form-content {
  width: 100%;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease 0.1s both;
}

.brand-accent {
  width: 4px;
  height: 32px;
  background: linear-gradient(180deg, #0ea5e9, #38bdf8);
  border-radius: 4px;
  flex-shrink: 0;
  animation: accentGrow 0.5s ease 0.2s both;
}

@keyframes accentGrow {
  from {
    transform: scaleY(0);
    opacity: 0;
  }
  to {
    transform: scaleY(1);
    opacity: 1;
  }
}

.brand-title {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 2px;
  letter-spacing: -0.3px;
}

.brand-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* 头部 */
.form-header {
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease 0.15s both;
}

.form-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
}

.form-header p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 表单布局 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-row:nth-child(1) .form-group {
  animation: fadeInUp 0.5s ease 0.2s both;
}

.form-row:nth-child(2) .form-group {
  animation: fadeInUp 0.5s ease 0.25s both;
}

.form-row:nth-child(3) .form-group {
  animation: fadeInUp 0.5s ease 0.3s both;
}

.form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  transition: color 0.25s ease;
  position: relative;
}

.form-label.active,
.form-label.focused {
  color: #0ea5e9;
}

.form-label::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
  transition: width 0.3s ease;
  border-radius: 1px;
}

.form-label.focused::after {
  width: 100%;
}

.optional-label {
  color: #64748b;
}

.optional {
  color: #94a3b8;
  font-weight: 400;
  font-size: 11px;
  margin-left: 2px;
}

/* 输入框 */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper.has-eye .form-input {
  padding-right: 40px;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  background: #fff;
  color: #1e293b;
  transition: all 0.25s ease;
  box-sizing: border-box;
  outline: none;
}

.form-input::placeholder {
  color: #c4cdd6;
  font-weight: 400;
}

.form-input:focus {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
  transform: translateY(-1px);
}

.form-input:hover:not(:focus) {
  border-color: #cbd5e1;
}

.input-underline {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
  transition: all 0.3s ease;
  border-radius: 1px;
  transform: translateX(-50%);
}

.form-input:focus ~ .input-underline {
  width: 100%;
}

.toggle-visibility {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  transition: all 0.2s ease;
}

.toggle-visibility:hover {
  color: #475569;
  transform: translateY(-50%) scale(1.1);
}

/* 密码强度 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.strength-bar {
  flex: 1;
  height: 3px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  width: 33%;
  background: #ef4444;
}

.strength-fill.medium {
  width: 66%;
  background: #f97316;
}

.strength-fill.strong {
  width: 100%;
  background: #22c55e;
}

.strength-text {
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  transition: color 0.3s;
}

.strength-fill.weak + .strength-text {
  color: #ef4444;
}

.strength-fill.medium + .strength-text {
  color: #f97316;
}

.strength-fill.strong + .strength-text {
  color: #22c55e;
}

/* 字段提示 */
.field-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.hint-dot {
  width: 4px;
  height: 4px;
  background: #94a3b8;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 验证码 */
.captcha-group {
  margin-top: 6px;
  animation: fadeInUp 0.5s ease 0.35s both;
}

.captcha-container {
  display: flex;
  gap: 10px;
}

.captcha-input {
  flex: 1;
}

.captcha-btn {
  flex-shrink: 0;
  padding: 0 16px;
  background: #f8fafc;
  color: #475569;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
  height: 44px;
  position: relative;
  overflow: hidden;
}

.captcha-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.2s;
}

.captcha-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.captcha-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.captcha-btn.btn-disabled, .captcha-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.captcha-success {
  font-size: 12px;
  color: #22c55e;
  margin-top: 6px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.success-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.5;
  }
}

/* 协议勾选 */
.terms-agreement {
  margin: 20px 0;
  animation: fadeInUp 0.5s ease 0.4s both;
}

.custom-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  font-size: 13px;
}

.custom-checkbox input {
  display: none;
}

.checkmark {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  border: 1.5px solid #cbd5e1;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
  transition: all 0.25s ease;
}

.checkmark i {
  font-size: 10px;
  color: white;
  opacity: 0;
  transition: opacity 0.15s;
}

.custom-checkbox input:checked + .checkmark {
  background: #0ea5e9;
  border-color: #0ea5e9;
  transform: scale(1.1);
}

.custom-checkbox input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: #64748b;
  line-height: 1.6;
}

.terms-link {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.terms-link:hover {
  color: #0284c7;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  margin-bottom: 16px;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease 0.45s both;
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.2),
      transparent
  );
  transition: left 0.5s ease;
}

.register-btn:hover:not(:disabled) .btn-shine {
  left: 100%;
}

.register-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), transparent);
  opacity: 0;
  transition: opacity 0.2s;
}

.register-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.35);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn.btn-disabled, .register-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-loading-content {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-loading-content i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 底部 */
.form-footer {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  animation: fadeInUp 0.5s ease 0.5s both;
}

.login-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.25s ease;
}

.login-link i {
  font-size: 12px;
  transition: transform 0.25s ease;
}

.login-link:hover {
  color: #0284c7;
}

.login-link:hover i {
  transform: translateX(3px);
}

/* 右侧说明区域 */
.illustration-section {
  display: none;
  flex: 1;
  max-width: 360px;
  align-self: center;
  animation: slideInRight 0.7s 0.2s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.illustration-content h3 {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 14px;
  letter-spacing: -0.5px;
  line-height: 1.3;
  animation: fadeInUp 0.6s ease 0.3s both;
}

.illustration-content > p {
  color: #64748b;
  font-size: 15px;
  line-height: 1.7;
  margin: 0 0 28px;
  animation: fadeInUp 0.6s ease 0.35s both;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-list li {
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.75);
  border-radius: 14px;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  border-left: 3px solid #0ea5e9;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  animation: fadeInUp 0.5s ease both;
}

.feature-list li:nth-child(1) {
  animation-delay: 0.4s;
}

.feature-list li:nth-child(2) {
  animation-delay: 0.45s;
}

.feature-list li:nth-child(3) {
  animation-delay: 0.5s;
}

.feature-list li:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.12);
}

.feature-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #0ea5e9;
  border-radius: 50%;
  margin-right: 10px;
  animation: pulse 2s ease-in-out infinite;
}

/* Toast */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  background: white;
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  z-index: 1000;
  border-left: 4px solid #22c55e;
  min-width: 240px;
}

.toast-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 14px;
}

.toast-message {
  font-size: 13px;
  color: #64748b;
  margin-top: 3px;
}

.toast-slide-enter-active, .toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-enter-from, .toast-slide-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.96);
}

/* 响应式 */
@media (min-width: 1024px) {
  .illustration-section {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .register-container {
    align-items: center;
  }
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .form-card {
    padding: 28px 20px;
    border-radius: 20px;
  }

  .register-container {
    padding: 20px 14px;
  }

  .brand-logo {
    flex-direction: column;
    gap: 8px;
  }

  .brand-accent {
    display: none;
  }
}
</style>