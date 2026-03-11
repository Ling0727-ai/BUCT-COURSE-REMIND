<template>
  <div class="login-page">
    <div class="login-container">
      <div class="form-section">
        <div class="brand">
          <div class="brand-icon">
            <i class="fas fa-graduation-cap"></i>
          </div>
          <h1>作业管理系统</h1>
          <p>智能管理您的学习任务</p>
        </div>

        <div class="form-card">
          <SecurityIndicator />

          <div class="form-body">
            <div class="field">
              <label class="label">用户名 / 邮箱</label>
              <input v-model="username" type="text" placeholder="请输入用户名或邮箱"
                     @keyup.enter="handleLogin" class="input">
            </div>

            <div class="field">
              <label class="label">密码</label>
              <div class="input-wrap">
                <input v-model="password" :type="showPassword ? 'text' : 'password'"
                       placeholder="请输入您的密码" @keyup.enter="handleLogin"
                       class="input" autocomplete="current-password">
                <button class="eye" @click="showPassword = !showPassword" type="button"
                        :aria-label="showPassword ? '隐藏密码' : '显示密码'">
                  <i :class="['fas', showPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
            </div>

            <div class="form-options">
              <label class="checkbox">
                <input type="checkbox" v-model="rememberMe">
                <span class="check-box"><i class="fas fa-check"></i></span>
                <span>记住账号</span>
              </label>
              <a href="#" class="forgot" @click.prevent="showForgotPassword">忘记密码？</a>
            </div>

            <button class="login-btn" @click="handleLogin"
                    :disabled="loading || !username.trim() || !password.trim()">
              <span v-if="!loading">登 录</span>
              <span v-else><i class="fas fa-spinner fa-spin"></i> 登录中...</span>
            </button>

            <div class="divider"><span>或</span></div>

            <div class="register-row">
              <span>还没有账号？</span>
              <router-link to="/register" class="register-link">
                立即注册 <i class="fas fa-arrow-right"></i>
              </router-link>
            </div>
            <div class="legal">
              登录即表示您已阅读并同意
              <router-link to="/terms">服务条款</router-link>
              和
              <router-link to="/privacy">隐私政策</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toasts -->
    <transition name="slide">
      <div v-if="showSuccess" class="toast success">
        <div class="toast-title">登录成功！</div>
        <div class="toast-msg">{{ dataRefreshMessage || '正在跳转到主页...' }}</div>
      </div>
    </transition>
    <transition name="slide">
      <div v-if="showDataRefresh" class="toast info">
        <div class="toast-title">数据更新</div>
        <div class="toast-msg">{{ dataRefreshMessage }}</div>
      </div>
    </transition>
    <transition name="slide">
      <div v-if="showError" class="toast error">
        <div class="toast-title">登录失败</div>
        <div class="toast-msg">{{ errorMessage }}</div>
      </div>
    </transition>

    <ForgotPasswordModal
      :visible="showForgotPasswordModal"
      @close="closeForgotPassword"
      @success="handleForgotPasswordSuccess"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SecurityIndicator from './components/SecurityIndicator.vue';
import ForgotPasswordModal from './components/ForgotPasswordModal.vue';
import { useLoginService } from './login';

export default defineComponent({
  name: 'Login',
  components: { SecurityIndicator, ForgotPasswordModal },
  setup() { return useLoginService(); }
});
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

.login-container {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
}

/* Brand */
.brand {
  text-align: center;
  margin-bottom: var(--space-8);
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: var(--primary-subtle);
  color: var(--primary);
  border-radius: var(--radius-lg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-bottom: var(--space-4);
}

.brand h1 {
  font-size: var(--font-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.brand p {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
}

/* Form Card */
.form-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--space-8) var(--space-6);
  box-shadow: var(--shadow-sm);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* Fields */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  color: var(--text-primary);
  background: var(--bg);
  transition: all var(--transition);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.input-wrap {
  position: relative;
}

.input-wrap .input {
  padding-right: 44px;
}

.eye {
  position: absolute;
  right: 4px; top: 50%;
  transform: translateY(-50%);
  width: 36px; height: 36px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.eye:hover { background: var(--gray-100); color: var(--text-primary); }

/* Options */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: var(--font-sm);
  color: var(--text-tertiary);
  user-select: none;
}

.checkbox input { display: none; }

.check-box {
  width: 18px; height: 18px;
  border: 2px solid var(--gray-300);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: transparent;
  transition: all var(--transition);
  flex-shrink: 0;
}

.checkbox input:checked + .check-box {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.forgot {
  font-size: var(--font-sm);
  color: var(--primary);
  font-weight: var(--font-medium);
}

.forgot:hover { text-decoration: underline; }

/* Button */
.login-btn {
  width: 100%;
  padding: 11px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all var(--transition);
}

.login-btn:hover:not(:disabled) {
  background: var(--primary-dark);
}

.login-btn:disabled {
  background: var(--gray-100);
  color: var(--gray-400);
  cursor: not-allowed;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  color: var(--text-tertiary);
  font-size: var(--font-sm);
}

.divider::before, .divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.divider span { padding: 0 var(--space-4); }

/* Register & Legal */
.register-row {
  text-align: center;
  font-size: var(--font-sm);
  color: var(--text-tertiary);
}

.register-link {
  color: var(--primary);
  font-weight: var(--font-medium);
  margin-left: 4px;
}

.register-link i { font-size: 12px; }

.legal {
  text-align: center;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
  line-height: 1.6;
}

.legal a { color: var(--text-tertiary); font-weight: var(--font-medium); }
.legal a:hover { color: var(--primary); }

/* Toast */
.toast {
  position: fixed;
  top: var(--space-6); left: 50%;
  transform: translateX(-50%);
  background: var(--bg);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  border-left: 4px solid var(--gray-300);
  z-index: 1000;
  min-width: 280px;
}

.toast.success { border-left-color: var(--green); }
.toast.error { border-left-color: var(--red); }
.toast.info { border-left-color: var(--primary); }

.toast-title { font-weight: var(--font-semibold); font-size: var(--font-sm); color: var(--text-primary); margin-bottom: 2px; }
.toast-msg { font-size: var(--font-xs); color: var(--text-tertiary); }

.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translate(-50%, -12px); }

/* Responsive */
@media (max-width: 480px) {
  .login-page { padding: var(--space-4); }
  .brand { margin-bottom: var(--space-6); }
  .form-card { padding: var(--space-6) var(--space-5); }
}
</style>
