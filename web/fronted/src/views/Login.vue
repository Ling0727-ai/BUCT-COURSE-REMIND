<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="login-content">
      <!-- 左侧表单区域 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 品牌标识 -->
          <div class="brand-header">
            <div class="brand-logo">
              <div class="brand-text">
                <h1>作业管理系统</h1>
                <p>智能管理您的学习任务</p>
              </div>
            </div>
          </div>

          <!-- 登录表单 -->
          <div class="login-form">
            <div class="form-header">
              <h2>欢迎回来</h2>
              <p>请登录您的账号继续使用</p>
            </div>
            
            <div class="form-body">
              <div class="form-group">
                <label class="form-label">账号</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <i class="fas fa-user"></i>
                  </div>
                  <input 
                    type="text" 
                    v-model="username" 
                    placeholder="请输入您的账号"
                    @keyup.enter="handleLogin"
                    class="form-input"
                    :class="{ 'has-value': username.length > 0 }"
                  >
                  <div class="input-border"></div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <i class="fas fa-lock"></i>
                  </div>
                  <input 
                    type="password" 
                    v-model="password" 
                    placeholder="请输入您的密码"
                    @keyup.enter="handleLogin"
                    class="form-input"
                    :class="{ 'has-value': password.length > 0 }"
                  >
                  <div class="input-border"></div>
                </div>
              </div>

              <div class="form-options">
                <label class="checkbox-container">
                  <input type="checkbox" v-model="rememberMe">
                  <span class="checkmark">
                    <i class="fas fa-check"></i>
                  </span>
                  <span class="checkbox-text">记住账号</span>
                </label>
                <a href="#" class="forgot-password">忘记密码？</a>
              </div>

              <button 
                class="login-btn" 
                @click="handleLogin"
                :disabled="loading || !username.trim() || !password.trim()"
                :class="{ 
                  loading: loading,
                  disabled: !username.trim() || !password.trim()
                }"
              >
                <span v-if="!loading" class="btn-content">
                  <i class="fas fa-sign-in-alt"></i>
                  <span>立即登录</span>
                </span>
                <span v-else class="loading-spinner">
                  <i class="fas fa-spinner"></i>
                  <span>登录中...</span>
                </span>
              </button>

              <div class="divider">
                <span>或</span>
              </div>

              <div class="register-section">
                <p>还没有账号？</p>
                <router-link to="/register" class="register-link">
                  立即注册
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧插图区域 -->
      <div class="illustration-section">
        <div class="illustration-container">
          <div class="illustration-content">
            <div class="main-illustration">
              <div class="illustration-circle">
                <div class="inner-circle">
                  <i class="fas fa-tasks"></i>
                </div>
              </div>
              <div class="floating-elements">
                <div class="element element-1">
                  <i class="fas fa-book"></i>
                </div>
                <div class="element element-2">
                  <i class="fas fa-calendar-check"></i>
                </div>
                <div class="element element-3">
                  <i class="fas fa-bell"></i>
                </div>
                <div class="element element-4">
                  <i class="fas fa-chart-line"></i>
                </div>
              </div>
            </div>
            
            <div class="illustration-text">
              <h3>高效管理学习任务</h3>
              <p>一站式管理所有科目的作业和考试，让学习更有条理</p>
              
              <div class="feature-highlights">
                <div class="feature-item">
                  <div class="feature-icon">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <span>智能作业提醒</span>
                </div>
                <div class="feature-item">
                  <div class="feature-icon">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <span>多科目统一管理</span>
                </div>
                <div class="feature-item">
                  <div class="feature-icon">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <span>进度实时跟踪</span>
                </div>
              </div>
            </div>
          </div>
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
          <div class="toast-message">正在跳转到主页...</div>
        </div>
      </div>
    </transition>

    <transition name="toast-slide">
      <div v-if="errorMessage" class="toast error">
        <div class="toast-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">登录失败</div>
          <div class="toast-message">{{ errorMessage }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const rememberMe = ref(false)
    const loading = ref(false)
    const showSuccess = ref(false)
    const errorMessage = ref('')

    const handleLogin = async () => {
      if (!username.value.trim() || !password.value.trim()) {
        errorMessage.value = '请输入账号和密码'
        setTimeout(() => { errorMessage.value = '' }, 3000)
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        // 调用真实的登录API
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include', // 重要：包含cookies以支持session
          body: JSON.stringify({
            username: username.value,
            password: password.value
          })
        })

        const data = await response.json()

        if (response.ok) {
          showSuccess.value = true
          
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
          
          setTimeout(() => {
            router.push('/')
          }, 800)
        } else {
          errorMessage.value = data.error || '登录失败'
          setTimeout(() => { errorMessage.value = '' }, 3000)
        }
      } catch (error) {
        console.error('登录错误:', error)
        errorMessage.value = '网络错误，请检查网络连接后重试'
        setTimeout(() => { errorMessage.value = '' }, 3000)
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

    return {
      username,
      password,
      rememberMe,
      loading,
      showSuccess,
      errorMessage,
      handleLogin
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4facfe 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
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
  left: 20%;
  animation-delay: 2s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  right: 10%;
  animation-delay: 3s;
}

.shape-5 {
  width: 40px;
  height: 40px;
  top: 50%;
  left: 5%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 1;
  }
}

/* 主要内容 */
.login-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 表单区域 */
.form-section {
  flex: 1;
  max-width: 480px;
  margin-right: 40px;
}

.form-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 品牌标识 */
.brand-header {
  text-align: center;
  margin-bottom: 40px;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.brand-text {
  text-align: center;
}

.brand-text h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-text p {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0 0 0;
}

/* 表单头部 */
.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.form-header p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 表单主体 */
.form-body {
  width: 100%;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  color: #9ca3af;
  transition: all 0.3s ease;
}

.form-input {
  width: 100%;
  padding: 16px 16px 16px 48px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
  background: #ffffff;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.form-input:focus + .input-border {
  transform: scaleX(1);
}

.form-input.has-value + .input-border {
  transform: scaleX(1);
}

.form-input:focus ~ .input-icon,
.form-input.has-value ~ .input-icon {
  color: #667eea;
}

.input-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  border-radius: 0 0 12px 12px;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
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
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: white;
}

.checkmark i {
  font-size: 12px;
  color: white;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.checkbox-container input:checked + .checkmark {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: #667eea;
}

.checkbox-container input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: #374151;
  font-weight: 500;
}

.forgot-password {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #5a6fd8;
  text-decoration: underline;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
}

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.login-btn:hover:not(:disabled)::before {
  left: 100%;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled,
.login-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 分割线 */
.divider {
  text-align: center;
  margin: 24px 0;
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
  padding: 0 16px;
  color: #9ca3af;
  font-size: 14px;
  position: relative;
}

/* 注册区域 */
.register-section {
  text-align: center;
}

.register-section p {
  color: #6b7280;
  margin: 0 0 12px 0;
  font-size: 14px;
}

.register-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  border: 1px solid rgba(102, 126, 234, 0.2);
  min-width: 120px;
}

.register-link:hover {
  background: rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

/* 插图区域 */
.illustration-section {
  flex: 1;
  max-width: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.illustration-container {
  text-align: center;
  color: white;
}

.illustration-content {
  max-width: 400px;
}

.main-illustration {
  position: relative;
  margin-bottom: 40px;
}

.illustration-circle {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  position: relative;
}

.inner-circle {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  animation: pulse-glow 3s ease-in-out infinite;
}

.inner-circle i {
  font-size: 64px;
  color: white;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 40px rgba(255, 255, 255, 0.5);
    transform: scale(1.05);
  }
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.element {
  position: absolute;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: float-element 4s ease-in-out infinite;
}

.element i {
  font-size: 20px;
  color: white;
}

.element-1 {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.element-2 {
  top: 20%;
  right: 10%;
  animation-delay: 1s;
}

.element-3 {
  bottom: 20%;
  left: 15%;
  animation-delay: 2s;
}

.element-4 {
  bottom: 10%;
  right: 15%;
  animation-delay: 3s;
}

@keyframes float-element {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
  }
}

.illustration-text h3 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.illustration-text p {
  font-size: 18px;
  opacity: 0.9;
  line-height: 1.6;
  margin-bottom: 32px;
}

.feature-highlights {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 500;
}

.feature-icon {
  width: 24px;
  height: 24px;
  background: rgba(16, 185, 129, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon i {
  font-size: 12px;
  color: #10b981;
}

/* 提示信息 */
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
  z-index: 1000;
  border-left: 4px solid;
}

.toast.success {
  border-left-color: #10b981;
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

.toast.success .toast-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
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
@media (max-width: 1024px) {
  .login-content {
    flex-direction: column;
    gap: 40px;
  }
  
  .form-section {
    margin-right: 0;
    max-width: 480px;
  }
  
  .illustration-section {
    max-width: 400px;
  }
  
  .illustration-text h3 {
    font-size: 28px;
  }
  
  .illustration-text p {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .login-content {
    padding: 20px;
  }
  
  .form-container {
    padding: 32px 24px;
  }
  
  .brand-text h1 {
    font-size: 20px;
  }
  
  .form-header h2 {
    font-size: 24px;
  }
  
  .illustration-section {
    display: none;
  }
  
  .toast {
    left: 16px;
    right: 16px;
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .login-content {
    padding: 16px;
  }
  
  .form-container {
    padding: 24px 20px;
  }
  
  .form-header h2 {
    font-size: 22px;
  }
  
  .form-input {
    padding: 14px 14px 14px 44px;
  }
  
  .login-btn {
    padding: 14px 20px;
  }
  
  .shape {
    display: none;
  }
}
</style>