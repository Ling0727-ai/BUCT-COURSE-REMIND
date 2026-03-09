<template>
  <div class="login-container">
    <!-- 动态背景装饰 -->
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <!-- 主要内容 -->
    <div class="login-content">
      <!-- 左侧表单区域 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 品牌标识 -->
          <div class="brand-header">
            <div class="brand-accent"></div>
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
                <label :class="{ active: username.length > 0, focused: usernameFocused }" class="form-label">用户名 /
                  邮箱</label>
                <div class="input-wrapper">
                  <input
                      v-model="username"
                      type="text"
                    placeholder="请输入用户名或邮箱"
                    @keyup.enter="handleLogin"
                    class="form-input"
                    :class="{ 'has-value': username.length > 0 }"
                      @blur="usernameFocused = false"
                      @focus="usernameFocused = true"
                  >
                  <span class="input-underline"></span>
                </div>
              </div>

              <div class="form-group">
                <label :class="{ active: password.length > 0, focused: passwordFocused }"
                       class="form-label">密码</label>
                <div class="input-wrapper has-eye">
                  <input
                      v-model="password"
                      :type="showPassword ? 'text' : 'password'"
                    placeholder="请输入您的密码"
                    @keyup.enter="handleLogin"
                    class="form-input"
                    :class="{ 'has-value': password.length > 0 }"
                      autocomplete="current-password"
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
                <span v-if="!loading" class="btn-text">登 录</span>
                <span v-else class="loading-spinner">
                  <i class="fas fa-spinner"></i>
                  <span>登录中...</span>
                </span>
                <span class="btn-shine"></span>
              </button>

              <div class="divider"><span>或</span></div>

              <div class="register-section">
                <p>还没有账号？</p>
                <router-link class="register-link" to="/register">
                  <span>立即注册</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
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
          <h3>高效管理<br>学习任务</h3>
          <p>一站式汇总所有科目作业与考试，让学习更有条理</p>
          <ul class="feature-list">
            <li>
              <span class="feature-dot"></span>
              智能作业提醒，不错过任何截止日期
            </li>
            <li>
              <span class="feature-dot"></span>
              多科目统一管理，清晰一览
            </li>
            <li>
              <span class="feature-dot"></span>
              待办事项与进度实时跟踪
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <transition name="toast-slide">
      <div v-if="showSuccess" class="toast success">
        <div class="toast-content">
          <div class="toast-title">登录成功！</div>
          <div class="toast-message">{{ dataRefreshMessage || '正在跳转到主页...' }}</div>
        </div>
      </div>
    </transition>

    <transition name="toast-slide">
      <div v-if="showDataRefresh" class="toast info">
        <div class="toast-content">
          <div class="toast-title">数据更新</div>
          <div class="toast-message">{{ dataRefreshMessage }}</div>
        </div>
      </div>
    </transition>

    <transition name="toast-slide">
      <div v-if="showError" class="toast error">
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
    const usernameFocused = ref(false)
    const passwordFocused = ref(false)
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
      usernameFocused,
      passwordFocused,
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
/* ─── 页面容器 ─── */
.login-container {
  min-height: 100vh;
  background: #f8faff;
  position: relative;
  overflow: hidden;
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
  opacity: 0.45;
}

.blob-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #bae6fd, #e0f2fe);
  top: -200px;
  right: -100px;
  animation: drift1 18s ease-in-out infinite alternate;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #d1fae5, #ecfdf5);
  bottom: -150px;
  left: -80px;
  animation: drift2 22s ease-in-out infinite alternate;
}

.blob-3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, #e0e7ff, #ede9fe);
  top: 40%;
  left: 30%;
  animation: drift3 15s ease-in-out infinite alternate;
}

@keyframes drift1 {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(-60px, 40px) scale(1.08);
  }
}

@keyframes drift2 {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(40px, -50px) scale(1.05);
  }
}

@keyframes drift3 {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(-30px, 30px) scale(0.95);
  }
}

/* ─── 主布局 ─── */
.login-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 72px;
}

/* ─── 表单区域 ─── */
.form-section {
  flex: 0 0 auto;
  width: 100%;
  max-width: 400px;
}

.form-section {
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

.form-container {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px;
  padding: 44px 40px;
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.08),
  0 4px 6px rgba(0, 0, 0, 0.04),
  0 20px 48px rgba(14, 165, 233, 0.08);
  position: relative;
  overflow: hidden;
}

.form-container::before {
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

/* ─── 品牌标识 ─── */
.brand-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 36px;
}

.brand-accent {
  width: 4px;
  height: 36px;
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

.brand-text h1 {
  font-size: 18px;
  font-weight: 800;
  margin: 0 0 2px;
  color: #0f172a;
  letter-spacing: -0.2px;
  animation: fadeInUp 0.4s ease 0.1s both;
}

.brand-text p {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
  animation: fadeInUp 0.4s ease 0.15s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ─── 表单头部 ─── */
.form-header {
  margin-bottom: 28px;
}

.form-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
  line-height: 1.2;
  animation: fadeInUp 0.5s ease 0.25s both;
}

.form-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  animation: fadeInUp 0.5s ease 0.3s both;
}

/* ─── 表单正文 ─── */
.form-body {
  width: 100%;
}

.form-group {
  margin-bottom: 22px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  letter-spacing: 0.1px;
  transition: all 0.25s ease;
  position: relative;
}

.form-label.active,
.form-label.focused {
  color: #0ea5e9;
}

.form-label::after {
  content: '';
  position: absolute;
  bottom: -2px;
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

/* ─── 输入框 ─── */
.input-wrapper {
  position: relative;
}

.input-wrapper.has-eye .form-input {
  padding-right: 48px;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.8);
  color: #1e293b;
  font-weight: 500;
  transition: border-color 0.25s, box-shadow 0.25s, background 0.25s, transform 0.2s;
  box-sizing: border-box;
  outline: none;
}

.form-input::placeholder {
  color: #c4cdd6;
  font-weight: 400;
}

.form-input:focus {
  border-color: #0ea5e9;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
  transform: translateY(-1px);
}

.form-input:hover:not(:focus) {
  border-color: #cbd5e1;
}

.toggle-visibility {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: #b0bec5;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 0.2s, transform 0.2s;
  line-height: 1;
}

.toggle-visibility:hover {
  color: #475569;
  transform: translateY(-50%) scale(1.1);
}

/* ─── 选项行 ─── */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 13px;
  animation: fadeInUp 0.5s ease 0.4s both;
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
  width: 17px;
  height: 17px;
  border: 1.5px solid #d1d5db;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  transition: all 0.2s;
}

.checkmark i {
  font-size: 9px;
  color: white;
  opacity: 0;
  transition: opacity 0.15s;
}

.checkbox-container input:checked + .checkmark {
  background: #0ea5e9;
  border-color: #0ea5e9;
  transform: scale(1.1);
}

.checkbox-container input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: #4b5563;
  font-weight: 500;
}

.forgot-password {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  position: relative;
}

.forgot-password::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #0ea5e9;
  transition: width 0.2s ease;
}

.forgot-password:hover::after {
  width: 100%;
}

.forgot-password:hover {
  color: #0284c7;
}

/* ─── 登录按钮 ─── */
.login-btn {
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
  margin-bottom: 20px;
  letter-spacing: 2px;
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

.login-btn:hover:not(:disabled) .btn-shine {
  left: 100%;
}

.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), transparent);
  opacity: 0;
  transition: opacity 0.2s;
}

.login-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.35);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.login-btn:disabled,
.login-btn.disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  display: inline-flex;
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

/* ─── 分割线 ─── */
.divider {
  text-align: center;
  margin: 20px 0;
  position: relative;
  animation: fadeInUp 0.5s ease 0.5s both;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
}

.divider span {
  background: rgba(255, 255, 255, 0.88);
  padding: 0 14px;
  color: #94a3b8;
  font-size: 12px;
  position: relative;
}

/* ─── 注册区域 ─── */
.register-section {
  text-align: center;
  animation: fadeInUp 0.5s ease 0.55s both;
}

.register-section p {
  color: #64748b;
  margin: 0 0 10px;
  font-size: 13px;
}

.register-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: transparent;
  color: #0ea5e9;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  border: 1.5px solid rgba(14, 165, 233, 0.5);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.register-link i {
  font-size: 12px;
  transition: transform 0.25s ease;
}

.register-link:hover {
  background: #0ea5e9;
  border-color: #0ea5e9;
  color: white;
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25);
  gap: 12px;
}

.register-link:hover i {
  transform: translateX(3px);
}

/* ─── 法律链接 ─── */
.legal-links {
  text-align: center;
  font-size: 11.5px;
  color: #adb5bd;
  margin-top: 16px;
  line-height: 1.7;
  animation: fadeInUp 0.5s ease 0.6s both;
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

/* ─── 右侧说明区域 ─── */
.illustration-section {
  flex: 1;
  max-width: 380px;
  display: flex;
  align-items: center;
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

.illustration-content {
  padding: 8px 0;
}

.illustration-content h3 {
  font-size: 42px;
  font-weight: 900;
  color: #0f172a;
  margin: 0 0 16px;
  line-height: 1.15;
  letter-spacing: -1.5px;
  animation: fadeInUp 0.6s ease 0.3s both;
}

.illustration-content > p {
  font-size: 15px;
  color: #64748b;
  line-height: 1.75;
  margin: 0 0 32px;
  animation: fadeInUp 0.6s ease 0.35s both;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-list li {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  padding: 13px 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  border-left: 3px solid #0ea5e9;
  backdrop-filter: blur(8px);
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
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.1);
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

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

/* ─── Toast ─── */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  min-width: 260px;
  max-width: 340px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04), 0 12px 28px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: flex-start;
  padding: 16px 18px;
  z-index: 1000;
  border-top: 3px solid;
}

.toast.success {
  border-top-color: #22c55e;
}

.toast.info {
  border-top-color: #0ea5e9;
}

.toast.error {
  border-top-color: #ef4444;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 13.5px;
  margin-bottom: 2px;
}

.toast-message {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

/* ─── Toast 动画 ─── */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.96);
}

/* ─── 响应式 ─── */
@media (max-width: 900px) {
  .illustration-section {
    display: none;
  }

  .login-content {
    padding: 32px 16px;
  }

  .form-section {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .form-container {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .form-header h2 {
    font-size: 22px;
  }

  .login-btn {
    letter-spacing: 1px;
  }
}
</style>
