<template>
  <div class="modal-overlay" v-if="visible" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <!-- 步骤1: 输入邮箱验证 -->
      <div v-if="currentStep === 1" class="modal-content">
        <div class="modal-header">
          <h3>忘记密码</h3>
          <button class="close-btn" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p class="step-description">请输入您的注册邮箱，我们将发送验证码到您的邮箱</p>
          
          <div class="form-group">
            <label>邮箱地址</label>
            <div class="input-wrapper">
              <i class="fas fa-envelope input-icon"></i>
              <input 
                type="email" 
                v-model="formData.email" 
                placeholder="请输入注册邮箱"
                class="form-input"
                :class="{ 'has-value': formData.email.length > 0 }"
              >
              <span class="input-status success" v-if="isValidEmail">
                <i class="fas fa-check"></i>
              </span>
            </div>
          </div>

          <!-- 显示用户名提示 -->
          <div v-if="formData.username" class="username-hint">
            <i class="fas fa-user-circle"></i>
            <span>该邮箱对应的用户名：<strong>{{ formData.username }}</strong></span>
          </div>

          <div class="form-group">
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
        </div>

        <div class="modal-footer">
          <button 
            class="btn btn-primary" 
            @click="verifyEmail"
            :disabled="loading || !isValidEmail || formData.captcha.length !== 6"
            :class="{ 'btn-loading': loading }"
          >
            <span v-if="!loading">下一步</span>
            <span v-else>
              <i class="fas fa-spinner fa-spin"></i>
              验证中...
            </span>
          </button>
        </div>
      </div>

      <!-- 步骤2: 重置密码 -->
      <div v-if="currentStep === 2" class="modal-content">
        <div class="modal-header">
          <h3>重置密码</h3>
          <button class="close-btn" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p class="step-description">请设置您的新密码</p>
          
          <div class="form-group">
            <label>新密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input 
                type="password" 
                v-model="formData.newPassword" 
                placeholder="至少6位密码"
                class="form-input"
              >
              <span class="input-status success" v-if="formData.newPassword.length >= 6">
                <i class="fas fa-check"></i>
              </span>
            </div>
            <div class="password-strength" v-if="formData.newPassword.length > 0">
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
                placeholder="再次输入新密码"
                class="form-input"
              >
              <span class="input-status success" v-if="formData.confirmPassword && formData.newPassword === formData.confirmPassword">
                <i class="fas fa-check"></i>
              </span>
              <span class="input-status error" v-if="formData.confirmPassword && formData.newPassword !== formData.confirmPassword">
                <i class="fas fa-times"></i>
              </span>
            </div>
            <div class="password-match-hint" v-if="formData.confirmPassword && formData.newPassword !== formData.confirmPassword">
              <i class="fas fa-exclamation-triangle"></i>
              两次输入的密码不一致
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="goBack">
            <i class="fas fa-arrow-left"></i>
            返回
          </button>
          <button 
            class="btn btn-primary" 
            @click="resetPassword"
            :disabled="loading || !isPasswordValid"
            :class="{ 'btn-loading': loading }"
          >
            <span v-if="!loading">重置密码</span>
            <span v-else>
              <i class="fas fa-spinner fa-spin"></i>
              重置中...
            </span>
          </button>
        </div>
      </div>

      <!-- 步骤3: 成功提示 -->
      <div v-if="currentStep === 3" class="modal-content success-content">
        <div class="modal-header">
          <h3>密码重置成功</h3>
          <button class="close-btn" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body text-center">
          <div class="success-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <p class="success-message">您的密码已成功重置！</p>
          <p class="success-description">请使用新密码登录您的账号</p>
        </div>

        <div class="modal-footer">
          <button class="btn btn-primary" @click="goToLogin">
            <i class="fas fa-sign-in-alt"></i>
            立即登录
          </button>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <transition name="toast-slide">
      <div v-if="errorMessage" class="toast error">
        <div class="toast-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">操作失败</div>
          <div class="toast-message">{{ errorMessage }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import {computed, onUnmounted, reactive, ref} from 'vue'
import rsaCrypto from '@/utils/rsa-crypto'

export default {
  name: 'ForgotPasswordModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'success'],
  setup(props, { emit }) {
    const currentStep = ref(1)
    const loading = ref(false)
    const errorMessage = ref('')
    const captchaCooldown = ref(0)
    const captchaSent = ref(false)
    let captchaInterval = null

    const formData = reactive({
      email: '',
      captcha: '',
      newPassword: '',
      confirmPassword: '',
      username: ''  // 存储用户名
    })

    const isValidEmail = computed(() => {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
    })

    const passwordStrength = computed(() => {
      if (formData.newPassword.length === 0) return ''
      if (formData.newPassword.length < 6) return 'weak'
      if (formData.newPassword.length < 10) return 'medium'
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

    const isPasswordValid = computed(() => {
      return formData.newPassword.length >= 6 && 
             formData.newPassword === formData.confirmPassword
    })

    const showError = (message) => {
      errorMessage.value = message
      setTimeout(() => { errorMessage.value = '' }, 3000)
    }

    const sendCaptcha = async () => {
      if (!isValidEmail.value) {
        showError('请输入有效的邮箱地址')
        return
      }

      if (captchaCooldown.value > 0) {
        return
      }

      try {
        // 创建加密的请求数据
        const requestData = await rsaCrypto.createEncryptedRequest({
          email: formData.email
        })

        const response = await fetch('/api/auth/send-verification-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        const data = await response.json()

        if (response.ok) {
          captchaCooldown.value = 60
          captchaSent.value = true
          
          if (data.test_mode && data.verification_code) {
            // 保存用户名（如果有）
            if (data.username) {
              formData.username = data.username
            }

            const testTip = document.createElement('div')
            testTip.className = 'toast success test-mode'
            testTip.innerHTML = `
              <div>
                <i class="fas fa-info-circle"></i>
                <div>
                  <div>邮件服务暂时不可用，使用测试模式</div>
                  ${data.username ? `<div style="margin-top: 8px;">用户名：<strong>${data.username}</strong></div>` : ''}
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
          }
          
          captchaInterval = setInterval(() => {
            captchaCooldown.value--
            if (captchaCooldown.value <= 0) {
              clearInterval(captchaInterval)
              captchaSent.value = false
            }
          }, 1000)
        } else {
          showError(data.error || '发送验证码失败')
        }
        
      } catch (error) {
        console.error('发送验证码错误:', error)
        showError('网络错误，请检查网络连接后重试')
      }
    }

    const verifyEmail = async () => {
      if (!isValidEmail.value || formData.captcha.length !== 6) {
        showError('请输入有效的邮箱和验证码')
        return
      }

      loading.value = true

      try {
        // 验证邮箱和验证码
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

        if (verifyResponse.ok) {
          // 检查邮箱是否已注册
          const checkResponse = await fetch('/api/auth/check-email', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              email: formData.email
            })
          })

          const checkData = await checkResponse.json()
          
          if (checkResponse.ok && checkData.exists) {
            currentStep.value = 2
          } else {
            showError('该邮箱未注册，请检查邮箱地址')
          }
        } else {
          const verifyData = await verifyResponse.json()
          showError(verifyData.error || '验证码验证失败')
        }
      } catch (error) {
        console.error('验证邮箱错误:', error)
        showError('网络错误，请重试')
      } finally {
        loading.value = false
      }
    }

    const resetPassword = async () => {
      if (!isPasswordValid.value) {
        showError('请输入有效的密码')
        return
      }

      loading.value = true

      try {
        // 创建加密的请求数据
        const requestData = await rsaCrypto.createEncryptedRequest({
          email: formData.email,
          new_password: formData.newPassword
        })

        const response = await fetch('/api/auth/reset-password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        const data = await response.json()

        if (response.ok) {
          currentStep.value = 3
        } else {
          showError(data.error || '密码重置失败')
        }
      } catch (error) {
        console.error('重置密码错误:', error)
        showError('网络错误，请重试')
      } finally {
        loading.value = false
      }
    }

    const goBack = () => {
      currentStep.value = 1
      formData.newPassword = ''
      formData.confirmPassword = ''
    }

    const goToLogin = () => {
      emit('success')
      closeModal()
    }

    const closeModal = () => {
      emit('close')
      // 重置表单
      currentStep.value = 1
      Object.keys(formData).forEach(key => {
        formData[key] = ''
      })
      captchaCooldown.value = 0
      captchaSent.value = false
      if (captchaInterval) {
        clearInterval(captchaInterval)
      }
    }

    const handleOverlayClick = (event) => {
      if (event.target === event.currentTarget) {
        closeModal()
      }
    }

    onUnmounted(() => {
      if (captchaInterval) {
        clearInterval(captchaInterval)
      }
    })

    return {
      currentStep,
      loading,
      errorMessage,
      captchaCooldown,
      captchaSent,
      formData,
      isValidEmail,
      passwordStrength,
      strengthLabel,
      isPasswordValid,
      sendCaptcha,
      verifyEmail,
      resetPassword,
      goBack,
      goToLogin,
      closeModal,
      handleOverlayClick
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content {
  padding: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 0 24px 24px 24px;
}

.step-description {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 24px;
  line-height: 1.5;
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
  font-size: 14px;
}

.input-status.success {
  color: #10b981;
}

.input-status.error {
  color: #ef4444;
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
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
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

.username-hint {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  border-radius: 10px;
  margin-top: 16px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.username-hint i {
  font-size: 18px;
}

.username-hint strong {
  font-weight: 600;
  text-decoration: underline;
}

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

.password-match-hint {
  font-size: 12px;
  color: #ef4444;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.modal-footer {
  padding: 0 24px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn:disabled,
.btn.btn-loading {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.success-content .modal-body {
  text-align: center;
  padding: 24px;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px auto;
}

.success-icon i {
  font-size: 36px;
  color: white;
}

.success-message {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.success-description {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 0;
}

.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  min-width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  z-index: 1100;
  border-left: 4px solid;
}

.toast.error {
  border-left-color: #ef4444;
}

.toast-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.toast.error .toast-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
  margin-bottom: 2px;
}

.toast-message {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
@media (max-width: 768px) {
  .modal-overlay {
    padding: 16px;
  }
  
  .modal-container {
    max-width: 100%;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 20px;
    padding-right: 20px;
  }
  
  .captcha-container {
    flex-direction: column;
    gap: 8px;
  }
  
  .captcha-btn {
    min-width: auto;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .toast {
    left: 16px;
    right: 16px;
    min-width: auto;
  }
}
</style>