<template>
  <div class="register-container">
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
              <label class="form-label">用户名</label>
              <div class="input-wrapper">
                <input
                  type="text" 
                  v-model="formData.username" 
                  placeholder="请输入3-20位用户名"
                  class="form-input"
                >
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">邮箱地址</label>
              <div class="input-wrapper">
                <input
                  type="email" 
                  v-model="formData.email" 
                  placeholder="请输入邮箱地址"
                  class="form-input"
                >
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">密码</label>
              <div class="input-wrapper has-eye">
                <input
                    v-model="formData.password"
                    :type="showPassword ? 'text' : 'password'"
                  placeholder="至少6位密码"
                  class="form-input"
                    autocomplete="new-password"
                >
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
                <span class="strength-text">密码强度：{{ strengthLabel }}</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">确认密码</label>
              <div class="input-wrapper has-eye">
                <input
                    v-model="formData.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="再次输入密码"
                  class="form-input"
                    autocomplete="new-password"
                >
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
              <label class="form-label">学号 <span class="optional">(选填)</span></label>
              <div class="input-wrapper">
                <input
                  type="text" 
                  v-model="formData.studentId" 
                  placeholder="请输入学号"
                  class="form-input"
                >
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">外部系统密码 <span class="optional">(选填)</span></label>
              <div class="input-wrapper has-eye">
                <input
                    v-model="formData.sPassword"
                    :type="showSPassword ? 'text' : 'password'"
                  placeholder="教务系统密码"
                  class="form-input"
                    autocomplete="new-password"
                >
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
                <i class="fas fa-info-circle"></i>
                用于自动登录教务系统等外部网站
              </div>
            </div>
          </div>

          <div class="form-group captcha-group">
            <label class="form-label">邮箱验证码</label>
            <div class="captcha-container">
              <div class="input-wrapper captcha-input">
                <input
                  type="text" 
                  v-model="formData.captcha"
                  placeholder="6位验证码"
                  maxlength="6"
                  class="form-input"
                >
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
            <span v-if="!loading">创建账号</span>
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

    <!-- 右侧说明区域 -->
    <div class="illustration-section">
      <div class="illustration-content">
        <h3>开启智能学习之旅</h3>
        <p>注册即可享受全方位的课程与作业管理服务</p>
        <ul class="feature-list">
          <li>多平台数据自动同步</li>
          <li>智能提醒，科学规划时间</li>
          <li>数据加密，安全可靠</li>
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
  background: linear-gradient(160deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdfa 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 20px;
  gap: 60px;
  overflow-y: auto;
}

/* ── 表单区域 ── */
.form-section {
  flex: 0 0 auto;
  width: 100%;
  max-width: 480px;
  z-index: 2;
}

.form-card {
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(14, 165, 233, 0.1);
}

/* 品牌 */
.form-content {
  width: 100%;
}

.brand-logo {
  text-align: center;
  margin-bottom: 20px;
}

.brand-title {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
  letter-spacing: -0.3px;
}

.brand-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* 头部 */
.form-header {
  margin-bottom: 20px;
}

.form-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px;
}

.form-header p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* 表单布局 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

.form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
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
  padding: 11px 13px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 13.5px;
  background: #fff;
  color: #1e293b;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}

.input-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  font-size: 13px;
  pointer-events: none;
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
  transition: color 0.2s;
}

.toggle-visibility:hover {
  color: #475569;
}

/* 密码强度 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 5px;
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
  transition: all 0.3s;
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
  color: #64748b;
  font-weight: 600;
  white-space: nowrap;
}

/* 字段提示 */
.field-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 验证码 */
.captcha-group {
  margin-top: 4px;
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
  padding: 0 14px;
  background: #f8fafc;
  color: #475569;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  height: 40px;
}

.captcha-btn:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.captcha-btn.btn-disabled, .captcha-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.captcha-success {
  font-size: 12px;
  color: #22c55e;
  margin-top: 5px;
  font-weight: 500;
}

/* 协议勾选 */
.terms-agreement {
  margin: 16px 0;
}

.custom-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
}

.custom-checkbox input {
  display: none;
}
.checkmark {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  border: 1.5px solid #cbd5e1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  transition: all 0.2s;
}

.checkmark i {
  font-size: 9px;
  color: white;
  opacity: 0;
  transition: opacity 0.15s;
}

.custom-checkbox input:checked + .checkmark {
  background: #0ea5e9;
  border-color: #0ea5e9;
}

.custom-checkbox input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: #64748b;
  line-height: 1.5;
}

.terms-link {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 500;
}

.terms-link:hover {
  text-decoration: underline;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  padding: 13px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14.5px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  margin-bottom: 14px;
}

.register-btn:hover:not(:disabled) {
  background: #0284c7;
  transform: translateY(-1px);
  box-shadow: 0 5px 16px rgba(14, 165, 233, 0.28);
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
}

.login-link {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 600;
}

.login-link:hover {
  text-decoration: underline;
}

/* 右侧说明区域 */
.illustration-section {
  display: none;
  flex: 1;
  max-width: 360px;
  align-self: center;
}

.illustration-content h3 {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 12px;
  letter-spacing: -0.5px;
  line-height: 1.3;
}

.illustration-content > p {
  color: #64748b;
  font-size: 15px;
  line-height: 1.65;
  margin: 0 0 24px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-list li {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.68);
  border-radius: 12px;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  border-left: 3px solid #0ea5e9;
}

/* Toast */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
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
  transition: all 0.3s ease;
}

.toast-slide-enter-from, .toast-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
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
    padding: 24px 18px;
    border-radius: 16px;
  }

  .register-container {
    padding: 20px 14px;
  }
}
</style>