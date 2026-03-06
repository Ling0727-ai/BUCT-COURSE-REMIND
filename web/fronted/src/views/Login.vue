<template>
  <div class="login-container">
    <!-- 主要内容 -->
    <div class="login-content">
      <!-- 左侧表单区域 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 品牌标识 -->
          <div class="brand-header">
            <div class="brand-text">
              <h1>作业管理系统</h1>
              <p>智能管理您的学习任务</p>
            </div>
          </div>

          <!-- 登录表单 -->
          <div class="login-form">
            <div class="form-header">
              <h2>欢迎回来</h2>
              <p>请登录您的账号继续使用</p>
            </div>
            
            <!-- 安全指示器 -->
            <SecurityIndicator />
            
            <div class="form-body">
              <div class="form-group">
                <label class="form-label">用户名 / 邮箱</label>
                <div class="input-wrapper">
                  <input
                    type="text" 
                    v-model="username" 
                    placeholder="请输入用户名或邮箱"
                    @keyup.enter="handleLogin"
                    class="form-input"
                    :class="{ 'has-value': username.length > 0 }"
                  >
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">密码</label>
                <div class="input-wrapper has-eye">
                  <input
                      v-model="password"
                      :type="showPassword ? 'text' : 'password'"
                    placeholder="请输入您的密码"
                    @keyup.enter="handleLogin"
                    class="form-input"
                    :class="{ 'has-value': password.length > 0 }"
                      autocomplete="current-password"
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
              </div>

              <div class="form-options">
                <label class="checkbox-container">
                  <input type="checkbox" v-model="rememberMe">
                  <span class="checkmark"><i class="fas fa-check"></i></span>
                  <span class="checkbox-text">记住账号</span>
                </label>
                <a href="#" class="forgot-password" @click.prevent="showForgotPassword">忘记密码？</a>
              </div>

              <button 
                class="login-btn" 
                @click="handleLogin"
                :disabled="loading || !username.trim() || !password.trim()"
                :class="{ loading: loading, disabled: !username.trim() || !password.trim() }"
              >
                <span v-if="!loading">登录</span>
                <span v-else class="loading-spinner">
                  <i class="fas fa-spinner"></i>
                  <span>登录中...</span>
                </span>
              </button>

              <div class="divider"><span>或</span></div>

              <div class="register-section">
                <p>还没有账号？</p>
                <router-link class="register-link" to="/register">立即注册</router-link>
              </div>
              <div class="legal-links">
                登录即表示您已阅读并同意
                <router-link class="terms-link" to="/terms">服务条款</router-link>
                和
                <router-link class="terms-link" to="/privacy">隐私政策</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧说明区域 -->
      <div class="illustration-section">
        <div class="illustration-content">
          <h3>高效管理学习任务</h3>
          <p>一站式汇总所有科目作业与考试，让学习更有条理</p>
          <ul class="feature-list">
            <li>智能作业提醒，不错过任何截止日期</li>
            <li>多科目统一管理，清晰一览</li>
            <li>待办事项与进度实时跟踪</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <transition name="toast-slide">
      <div v-if="showSuccess" class="toast success">
        <div class="toast-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">登录成功！</div>
          <div class="toast-message">
            {{ dataRefreshMessage || '正在跳转到主页...' }}
          </div>
        </div>
      </div>
    </transition>

    <transition name="toast-slide">
      <div v-if="showDataRefresh" class="toast info">
        <div class="toast-icon">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': dataRefreshLoading }"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">数据更新</div>
          <div class="toast-message">{{ dataRefreshMessage }}</div>
        </div>
      </div>
    </transition>

    <transition name="toast-slide">
      <div v-if="showError" class="toast error">
        <div class="toast-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">登录失败</div>
          <div class="toast-message">{{ errorMessage }}</div>
        </div>
      </div>
    </transition>

    <!-- 忘记密码弹窗 -->
    <ForgotPasswordModal 
      :visible="showForgotPasswordModal"
      @close="closeForgotPassword"
      @success="handleForgotPasswordSuccess"
    />
  </div>
</template>

<script>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import rsaCrypto from '@/utils/rsa-crypto'
import SecurityIndicator from '@/components/SecurityIndicator.vue'
import ForgotPasswordModal from '@/components/ForgotPasswordModal.vue'
import {useToast} from './home/composables/useToast' // 新增：全局悬浮 Toast

export default {
  name: 'Login',
  components: {
    SecurityIndicator,
    ForgotPasswordModal
  },
  setup() {
    const router = useRouter()
    const {showToast: showTopToast} = useToast() // 新增：顶部浮层提醒
    const username = ref('')
    const password = ref('')
    const showPassword = ref(false)
    const rememberMe = ref(false)
    const loading = ref(false)
    const showSuccess = ref(false)
    const showDataRefresh = ref(false)
    const dataRefreshLoading = ref(false)
    const dataRefreshMessage = ref('')
    const errorMessage = ref('')
    const showError = ref(false)
    const showForgotPasswordModal = ref(false)

    const showErrorToast = (msg) => {
      errorMessage.value = msg
      showError.value = true
      setTimeout(() => {
        showError.value = false
      }, 3000)
      // 同步触发全局悬浮提示
      showTopToast('error', '登录失败', msg)
    }

    const handleLogin = async () => {
      if (!username.value.trim() || !password.value.trim()) {
        showErrorToast('请输入用户名/邮箱和密码')
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        // 创建加密的请求数据
        const requestData = await rsaCrypto.createEncryptedRequest({
          username: username.value,
          password: password.value
        })

        // 调用真实的登录API - 使用相对路径，通过Nginx代理
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include', // 重要：包含cookies以支持session
          body: JSON.stringify(requestData)
        })

        let data = {}
        try {
          data = await response.json()
        } catch (e) {
          // 非JSON响应
          data = {error: '服务器返回异常'}
        }

        if (response.ok) {
          showSuccess.value = true
          // 顶部提示登录成功
          showTopToast('success', '登录成功', '欢迎回来')

          // 处理数据刷新状态（顶部 info 也提示一下）
          if (data.data_refresh) {
            const msg = data.data_refresh.message || '作业数据正在后台更新...'
            showTopToast(data.data_refresh.success ? 'info' : 'warning', '数据更新', msg)
            if (data.data_refresh.success) {
              dataRefreshMessage.value = data.data_refresh.message
              showDataRefresh.value = true
              dataRefreshLoading.value = false
              
              // 3秒后隐藏数据刷新提示
              setTimeout(() => {
                showDataRefresh.value = false
              }, 3000)
            } else {
              // 数据刷新失败，显示警告但不影响登录
              dataRefreshMessage.value = data.data_refresh.message
              showDataRefresh.value = true
              dataRefreshLoading.value = false
              
              setTimeout(() => {
                showDataRefresh.value = false
              }, 4000)
            }
          }
          
          // 保存登录状态到localStorage
          const userInfo = {
            id: data.user.id,
            username: data.user.username,
            is_admin: data.user.is_admin,
            remember: rememberMe.value
          }
          
          if (rememberMe.value) {
            localStorage.setItem('user', JSON.stringify(userInfo))
          } else {
            // 即使不记住密码，也要保存当前会话的用户信息
            sessionStorage.setItem('user', JSON.stringify(userInfo))
          }

          // 清除关闭计时器，避免重新登录后误触发退出
          try {
            localStorage.removeItem('app_last_closed_at')
            // 设置一个标记表示刚刚登录成功
            localStorage.setItem('app_just_logged_in', String(Date.now()))
          } catch (e) {
            console.warn('清除关闭计时器失败:', e)
          }

          setTimeout(() => {
            router.push('/')
          }, 800)
        } else {
          showErrorToast(data.error || '登录失败')
        }
      } catch (error) {
        console.error('登录错误:', error)
        showErrorToast('网络错误，请检查网络连接后重试')
      } finally {
        loading.value = false
        setTimeout(() => {
          showSuccess.value = false
        }, 3000)
      }
    }

    // 检查记住的登录状态
    const checkRememberedLogin = () => {
      const savedUser = localStorage.getItem('user')
      if (savedUser) {
        const user = JSON.parse(savedUser)
        if (user.remember) {
          username.value = user.username
          rememberMe.value = true
        }
      }
    }

    // 初始化检查
    checkRememberedLogin()

    const showForgotPassword = () => {
      showForgotPasswordModal.value = true
    }

    const closeForgotPassword = () => {
      showForgotPasswordModal.value = false
    }

    const handleForgotPasswordSuccess = () => {
      showForgotPasswordModal.value = false
      // 可以显示成功提示
      showSuccess.value = true
      dataRefreshMessage.value = '密码重置成功，请使用新密码登录'
      setTimeout(() => {
        showSuccess.value = false
      }, 3000)
    }

    // 自动登出提示（关闭超过6h）
    const autoLogoutMessage = sessionStorage.getItem('logout_reason')
    if (autoLogoutMessage) {
      errorMessage.value = autoLogoutMessage
      showError.value = true
      setTimeout(() => {
        showError.value = false
      }, 4000)
      showTopToast('info', '自动退出', autoLogoutMessage)
      sessionStorage.removeItem('logout_reason')
    }

    return {
      username,
      password,
      showPassword,
      rememberMe,
      loading,
      showSuccess,
      showDataRefresh,
      dataRefreshLoading,
      dataRefreshMessage,
      errorMessage,
      showError,
      showForgotPasswordModal,
      handleLogin,
      showForgotPassword,
      closeForgotPassword,
      handleForgotPasswordSuccess
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(160deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdfa 100%);
}

/* 主要内容 */
.login-content {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 60px;
}

/* 表单区域 */
.form-section {
  flex: 0 0 auto;
  width: 100%;
  max-width: 420px;
}

.form-container {
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px 36px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(14, 165, 233, 0.1);
}

/* 品牌标识 */
.brand-header {
  margin-bottom: 32px;
}

.brand-text h1 {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 4px;
  color: #0f172a;
  letter-spacing: -0.3px;
}

.brand-text p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* 表单头部 */
.form-header {
  margin-bottom: 28px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
  letter-spacing: -0.2px;
}

.form-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 表单 */
.form-body {
  width: 100%;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 7px;
}

.input-wrapper {
  position: relative;
}

.input-wrapper.has-eye .form-input {
  padding-right: 48px;
}

.toggle-visibility {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 0.2s;
}

.toggle-visibility:hover {
  color: #475569;
}

.form-input {
  width: 100%;
  padding: 13px 16px;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  background: #fff;
  color: #1e293b;
  font-weight: 500;
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

/* 选项行 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 14px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.checkbox-container input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 1.5px solid #d1d5db;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  transition: all 0.2s;
}

.checkmark i {
  font-size: 10px;
  color: white;
  opacity: 0;
  transition: opacity 0.15s;
}

.checkbox-container input:checked + .checkmark {
  background: #0ea5e9;
  border-color: #0ea5e9;
}

.checkbox-container input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: #374151;
  font-weight: 500;
}

.forgot-password {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 500;
  font-size: 13px;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: #0284c7;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  padding: 14px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  margin-bottom: 20px;
  letter-spacing: 0.3px;
}
.login-btn:hover:not(:disabled) {
  background: #0284c7;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.3);
}

.login-btn:active:not(:disabled) {
  transform: none;
}

.login-btn:disabled, .login-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 分割线 */
.divider {
  text-align: center;
  margin: 20px 0;
  position: relative;
}
.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e5e7eb;
}
.divider span {
  background: white;
  padding: 0 14px;
  color: #9ca3af;
  font-size: 13px;
  position: relative;
}

/* 注册区域 */
.register-section {
  text-align: center;
}

.register-section p {
  color: #64748b;
  margin: 0 0 10px;
  font-size: 13px;
}

.register-link {
  display: inline-block;
  padding: 10px 28px;
  background: transparent;
  color: #0ea5e9;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  border: 1.5px solid #0ea5e9;
  transition: all 0.2s;
}

.register-link:hover {
  background: #0ea5e9;
  color: white;
}

/* 法律链接 */
.legal-links {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 16px;
  line-height: 1.6;
}

.terms-link {
  color: #0ea5e9;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

/* 右侧区域 */
.illustration-section {
  flex: 1;
  max-width: 400px;
  display: flex;
  align-items: center;
}

.illustration-content {
  padding: 16px 0;
}

.illustration-content h3 {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 12px;
  line-height: 1.3;
  letter-spacing: -0.4px;
}

.illustration-content > p {
  font-size: 15px;
  color: #64748b;
  line-height: 1.7;
  margin: 0 0 28px;
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
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  border-left: 3px solid #0ea5e9;
  backdrop-filter: blur(8px);
}

/* Toast */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  min-width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  z-index: 1000;
  border-left: 3px solid;
}

.toast.success {
  border-left-color: #22c55e;
}

.toast.info {
  border-left-color: #0ea5e9;
}

.toast.error {
  border-left-color: #ef4444;
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 1px;
}

.toast.success .toast-icon {
  color: #22c55e;
}

.toast.info .toast-icon {
  color: #0ea5e9;
}

.toast.error .toast-icon {
  color: #ef4444;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  color: #0f172a;
  font-size: 14px;
  margin-bottom: 2px;
}

.toast-message {
  font-size: 13px;
  color: #64748b;
}

/* Toast 动画 */
.toast-slide-enter-active, .toast-slide-leave-active {
  transition: all 0.3s ease;
}

.toast-slide-enter-from, .toast-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 响应式 */
@media (max-width: 900px) {
  .illustration-section {
    display: none;
  }

  .login-content {
    padding: 24px 16px;
  }

  .form-section {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .form-container {
    padding: 28px 22px;
  }

  .form-header h2 {
    font-size: 20px;
  }
}
</style>
