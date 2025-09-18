<template>
  <div class="login-container">
    <div class="login-header">
      <h1><i class="fas fa-graduation-cap"></i> 作业管理系统</h1>
      <p>智能管理您的学习任务</p>
    </div>

    <div class="login-card">
      <div class="login-form">
        <h2>用户登录</h2>
        
        <div class="form-group">
          <label class="form-label">账号</label>
          <div class="input-wrapper">
            <i class="fas fa-user input-icon"></i>
            <input 
              type="text" 
              v-model="username" 
              placeholder="请输入账号"
              @keyup.enter="handleLogin"
              class="form-input"
            >
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="input-wrapper">
            <i class="fas fa-lock input-icon"></i>
            <input 
              type="password" 
              v-model="password" 
              placeholder="请输入密码"
              @keyup.enter="handleLogin"
              class="form-input"
            >
          </div>
        </div>

        <div class="form-options">
          <label class="checkbox-container">
            <input type="checkbox" v-model="rememberMe">
            <span class="checkmark"></span>
            记住账号
          </label>
        </div>

        <button 
          class="login-btn" 
          @click="handleLogin"
          :disabled="loading"
          :class="{ loading: loading }"
        >
          <span v-if="!loading">登录</span>
          <span v-else class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            登录中...
          </span>
        </button>

        <div class="register-link">
          还没有账号？ <router-link to="/register">立即注册</router-link>
        </div>
      </div>

      <div class="login-illustration">
        <div class="illustration-content">
          <i class="fas fa-tasks"></i>
          <h3>高效管理学习任务</h3>
          <p>一站式管理所有科目的作业和考试</p>
        </div>
      </div>
    </div>

    <!-- 登录成功提示 -->
    <div v-if="showSuccess" class="toast success">
      <i class="fas fa-check-circle"></i>
      <span>登录成功！</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="toast error">
      <i class="fas fa-exclamation-triangle"></i>
      <span>{{ errorMessage }}</span>
    </div>
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
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  color: white;
}

.login-header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  font-weight: 700;
}

.login-header p {
  font-size: 1.1em;
  opacity: 0.9;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  max-width: 900px;
  width: 100%;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.login-form {
  flex: 1;
  padding: 40px;
  min-width: 300px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
  font-size: 1.8em;
  font-weight: 600;
}

.form-group {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
  font-size: 0.95em;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 15px 15px 15px 45px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.form-options {
  margin-bottom: 25px;
  font-size: 0.9em;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #666;
}

.checkbox-container input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-container input:checked + .checkmark {
  background: #667eea;
  border-color: #667eea;
}

.checkbox-container input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.login-btn {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.test-account {
  text-align: center;
  color: #666;
  font-size: 0.9em;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 15px;
}

.test-account p {
  margin: 0;
}

.login-illustration {
  flex: 1;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.login-illustration::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  animation: shimmer 3s infinite;
}

.illustration-content {
  text-align: center;
  color: #2c3e50;
  position: relative;
  z-index: 1;
}

.illustration-content i {
  font-size: 4em;
  color: #667eea;
  margin-bottom: 20px;
  display: block;
}

.illustration-content h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
  font-weight: 600;
}

.illustration-content p {
  color: #666;
  line-height: 1.6;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

/* Toast 样式 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1001;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: toastSlideIn 0.3s ease;
}

.toast.success {
  background: #27ae60;
}

.toast.error {
  background: #e74c3c;
}

@keyframes toastSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    flex-direction: column;
    max-width: 400px;
  }
  
  .login-illustration {
    display: none;
  }
  
  .login-form {
    padding: 30px 25px;
  }
  
  .login-header h1 {
    font-size: 2em;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 15px;
  }
  
  .login-form {
    padding: 25px 20px;
  }
  
  .login-form h2 {
    font-size: 1.5em;
  }
}
</style>