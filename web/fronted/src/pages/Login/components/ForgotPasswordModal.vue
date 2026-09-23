<template>
  <BaseModal
    :model-value="visible"
    :title="stepTitle"
    width="480px"
    panel-class="forgot-password-modal"
    @update:model-value="onUpdate"
  >
    <!-- 步骤1: 输入邮箱验证 -->
    <template v-if="currentStep === 1">
      <p class="step-description">请输入您的注册邮箱，我们将发送验证码到您的邮箱</p>

      <div class="form-group">
        <label for="forgotEmail">邮箱地址</label>
        <div class="input-wrapper">
          <i class="fas fa-envelope input-icon" aria-hidden="true"></i>
          <input
            id="forgotEmail"
            type="email"
            v-model="formData.email"
            placeholder="请输入注册邮箱"
            class="form-input"
            :class="{ 'has-value': formData.email.length > 0 }"
            data-autofocus
          >
          <span class="input-status success" v-if="isValidEmail">
            <i class="fas fa-check" aria-hidden="true"></i>
          </span>
        </div>
      </div>

      <!-- 显示用户名提示 -->
      <div v-if="formData.username" class="username-hint">
        <i class="fas fa-user-circle" aria-hidden="true"></i>
        <span>该邮箱对应的用户名：<strong>{{ formData.username }}</strong></span>
      </div>

      <div class="form-group">
        <label for="forgotCaptcha">邮箱验证码</label>
        <div class="captcha-container">
          <div class="input-wrapper captcha-input">
            <i class="fas fa-shield-alt input-icon" aria-hidden="true"></i>
            <input
              id="forgotCaptcha"
              type="text"
              v-model="formData.captcha"
              placeholder="请输入6位验证码"
              maxlength="6"
              class="form-input"
            >
            <span class="input-status success" v-if="formData.captcha.length === 6">
              <i class="fas fa-check" aria-hidden="true"></i>
            </span>
          </div>
          <button
            type="button"
            class="captcha-btn"
            @click="sendCaptcha"
            :disabled="captchaCooldown > 0 || !isValidEmail"
          >
            <span v-if="captchaCooldown > 0">{{ captchaCooldown }}s</span>
            <span v-else>获取验证码</span>
          </button>
        </div>
        <div class="captcha-success" v-if="captchaSent">
          <i class="fas fa-check-circle" aria-hidden="true"></i>
          验证码已发送至邮箱，请查收
        </div>
        <div class="captcha-success" v-if="testModeCode">
          <i class="fas fa-info-circle" aria-hidden="true"></i>
          邮件服务不可用，测试模式验证码：<strong>{{ testModeCode }}</strong>
        </div>
      </div>
    </template>

    <!-- 步骤2: 重置密码 -->
    <template v-else-if="currentStep === 2">
      <p class="step-description">请设置您的新密码</p>

      <div class="form-group">
        <label for="forgotNewPassword">新密码</label>
        <div class="input-wrapper">
          <i class="fas fa-lock input-icon" aria-hidden="true"></i>
          <input
            id="forgotNewPassword"
            type="password"
            v-model="formData.newPassword"
            placeholder="至少6位密码"
            class="form-input"
            data-autofocus
          >
          <span class="input-status success" v-if="formData.newPassword.length >= 6">
            <i class="fas fa-check" aria-hidden="true"></i>
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
        <label for="forgotConfirmPassword">确认密码</label>
        <div class="input-wrapper">
          <i class="fas fa-lock input-icon" aria-hidden="true"></i>
          <input
            id="forgotConfirmPassword"
            type="password"
            v-model="formData.confirmPassword"
            placeholder="再次输入新密码"
            class="form-input"
          >
          <span class="input-status success" v-if="formData.confirmPassword && formData.newPassword === formData.confirmPassword">
            <i class="fas fa-check" aria-hidden="true"></i>
          </span>
          <span class="input-status error" v-if="formData.confirmPassword && formData.newPassword !== formData.confirmPassword">
            <i class="fas fa-times" aria-hidden="true"></i>
          </span>
        </div>
        <div class="password-match-hint" v-if="formData.confirmPassword && formData.newPassword !== formData.confirmPassword">
          <i class="fas fa-exclamation-triangle" aria-hidden="true"></i>
          两次输入的密码不一致
        </div>
      </div>
    </template>

    <!-- 步骤3: 成功提示 -->
    <template v-else>
      <div class="text-center">
        <div class="success-icon">
          <i class="fas fa-check-circle" aria-hidden="true"></i>
        </div>
        <p class="success-message">您的密码已成功重置！</p>
        <p class="success-description">请使用新密码登录您的账号</p>
      </div>
    </template>

    <template #footer>
      <template v-if="currentStep === 1">
        <button
          type="button"
          class="btn btn-primary"
          @click="verifyEmail"
          :disabled="loading || !isValidEmail || formData.captcha.length !== 6"
        >
          <span v-if="!loading">下一步</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
            验证中...
          </span>
        </button>
      </template>

      <template v-else-if="currentStep === 2">
        <button type="button" class="btn btn-secondary" @click="goBack">
          <i class="fas fa-arrow-left" aria-hidden="true"></i>
          返回
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="resetPassword"
          :disabled="loading || !isPasswordValid"
        >
          <span v-if="!loading">重置密码</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
            重置中...
          </span>
        </button>
      </template>

      <template v-else>
        <button type="button" class="btn btn-primary" @click="goToLogin">
          <i class="fas fa-sign-in-alt" aria-hidden="true"></i>
          立即登录
        </button>
      </template>
    </template>
  </BaseModal>
</template>

<script lang="ts">
import {computed, defineComponent, onUnmounted, reactive, ref} from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import {useToast} from '@/composables/useToast'
import rsaCrypto from '@/utils/rsa-crypto'

interface ForgotForm {
  email: string
  captcha: string
  newPassword: string
  confirmPassword: string
  username: string
}

const STEP_TITLES: Record<number, string> = {
  1: '忘记密码',
  2: '重置密码',
  3: '密码重置成功'
}

export default defineComponent({
  name: 'ForgotPasswordModal',
  components: { BaseModal },
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'success'],
  setup(props, { emit }) {
    const { error: showErrorToast } = useToast()

    const currentStep = ref(1)
    const loading = ref(false)
    const captchaCooldown = ref(0)
    const captchaSent = ref(false)
    /** 邮件服务不可用时的测试验证码，替代原先的 innerHTML 提示。 */
    const testModeCode = ref('')
    let captchaInterval: number | null = null

    const formData = reactive<ForgotForm>({
      email: '',
      captcha: '',
      newPassword: '',
      confirmPassword: '',
      username: ''
    })

    const stepTitle = computed(() => STEP_TITLES[currentStep.value] ?? '忘记密码')

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
      const labels: Record<string, string> = {
        '': '',
        weak: '弱',
        medium: '中',
        strong: '强'
      }
      return labels[passwordStrength.value]
    })

    const isPasswordValid = computed(() => {
      return formData.newPassword.length >= 6 &&
             formData.newPassword === formData.confirmPassword
    })

    const showError = (message: string) => {
      showErrorToast('操作失败', message)
    }

    const onUpdate = (value: boolean) => {
      if (!value) {
        closeModal()
      }
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
        const requestData = await rsaCrypto.createEncryptedRequest({
          email: formData.email
        })

        const response = await fetch('/api/auth/send-verification-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        })

        const data = await response.json()

        if (response.ok) {
          captchaCooldown.value = 60
          captchaSent.value = true

          if (data.test_mode && data.verification_code) {
            if (data.username) {
              formData.username = data.username
            }
            testModeCode.value = String(data.verification_code)
          }

          captchaInterval = window.setInterval(() => {
            captchaCooldown.value--
            if (captchaCooldown.value <= 0) {
              if (captchaInterval !== null) {
                window.clearInterval(captchaInterval)
                captchaInterval = null
              }
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
        const verifyRequest = await rsaCrypto.createEncryptedRequest({
          email: formData.email,
          code: formData.captcha
        })

        const verifyResponse = await fetch('/api/auth/verify-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(verifyRequest)
        })

        if (verifyResponse.ok) {
          const checkResponse = await fetch('/api/auth/check-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: formData.email })
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
        const requestData = await rsaCrypto.createEncryptedRequest({
          email: formData.email,
          new_password: formData.newPassword
        })

        const response = await fetch('/api/auth/reset-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
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
      currentStep.value = 1
      Object.keys(formData).forEach((key) => {
        formData[key as keyof ForgotForm] = ''
      })
      captchaCooldown.value = 0
      captchaSent.value = false
      testModeCode.value = ''
      if (captchaInterval !== null) {
        window.clearInterval(captchaInterval)
        captchaInterval = null
      }
    }

    onUnmounted(() => {
      if (captchaInterval !== null) {
        window.clearInterval(captchaInterval)
      }
    })

    return {
      currentStep, loading, captchaCooldown, captchaSent, testModeCode,
      formData, isValidEmail, passwordStrength, strengthLabel, isPasswordValid,
      stepTitle, sendCaptcha, verifyEmail, resetPassword, goBack, goToLogin, closeModal, onUpdate
    }
  }
})
</script>

<style scoped>
/* 弹窗外壳（.modal-overlay / .modal-content / .modal-header / .modal-body /
   .modal-footer / .modal-close）由 assets/modal.css 统一提供。 */

.step-description {
  color: var(--text-tertiary);
  font-size: var(--font-sm);
  margin-bottom: var(--space-5);
  line-height: 1.5;
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group label {
  display: block;
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: 6px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-tertiary);
  font-size: 14px;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 11px 14px 11px 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  background: var(--bg);
  color: var(--text-primary);
  transition: all var(--transition);
}

.form-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.input-status {
  position: absolute;
  right: 14px;
  font-size: 14px;
}

.input-status.success { color: var(--green); }
.input-status.error { color: var(--red); }

.captcha-container {
  display: flex;
  gap: 10px;
  align-items: stretch;
}

.captcha-input { flex: 1; }

.captcha-btn {
  padding: 0 20px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
  min-width: 100px;
}

.captcha-btn:hover:not(:disabled) { background: var(--primary-dark); }

.captcha-btn:disabled {
  background: var(--gray-200);
  color: var(--gray-400);
  cursor: not-allowed;
}

.captcha-success {
  font-size: var(--font-xs);
  color: var(--green);
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.username-hint {
  background: var(--primary-subtle);
  color: var(--primary);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--font-sm);
  border: 1px solid var(--primary);
  opacity: 0.85;
}

.username-hint i { font-size: 18px; }
.username-hint strong { font-weight: var(--font-semibold); }

.password-strength {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: var(--gray-100);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-fill.weak { width: 33%; background: var(--red); }
.strength-fill.medium { width: 66%; background: var(--orange); }
.strength-fill.strong { width: 100%; background: var(--green); }

.strength-text {
  font-size: var(--font-xs);
  font-weight: var(--font-semibold);
  color: var(--text-tertiary);
}

.password-match-hint {
  font-size: var(--font-xs);
  color: var(--red);
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary { background: var(--primary); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--primary-dark); }

.btn-secondary { background: var(--gray-100); color: var(--text-secondary); }
.btn-secondary:hover:not(:disabled) { background: var(--gray-200); }

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.text-center { text-align: center; }

.success-icon {
  width: 64px;
  height: 64px;
  background: var(--green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-5) auto;
}

.success-icon i { font-size: 28px; color: #fff; }

.success-message {
  font-size: var(--font-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.success-description {
  color: var(--text-tertiary);
  font-size: var(--font-sm);
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .captcha-container {
    flex-direction: column;
    gap: 8px;
  }

  .captcha-btn {
    min-width: auto;
    padding: 11px;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

