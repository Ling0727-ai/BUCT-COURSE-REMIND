<template>
  <div class="register-page">
    <div class="register-container">
      <div class="brand">
        <div class="brand-icon">
          <i class="fas fa-graduation-cap"></i>
        </div>
        <h1>作业管理系统</h1>
        <p>创建账号，开启高效学习管理</p>
      </div>

      <div class="form-card">
        <div class="form-header">
          <h2>用户注册</h2>
          <p>填写信息，创建您的专属账号</p>
        </div>

        <div class="form-body">
          <div class="form-row">
            <div class="field">
              <label class="label">用户名</label>
              <input v-model="formData.username" type="text" placeholder="请输入3-20位用户名" class="input">
            </div>
            <div class="field">
              <label class="label">邮箱地址</label>
              <input v-model="formData.email" type="email" placeholder="请输入邮箱地址" class="input">
            </div>
          </div>

          <div class="form-row">
            <div class="field">
              <label class="label">密码</label>
              <div class="input-wrap">
                <input v-model="formData.password" :type="showPassword ? 'text' : 'password'"
                       placeholder="至少6位密码" class="input" autocomplete="new-password">
                <button class="eye" @click="showPassword = !showPassword" type="button"
                        :aria-label="showPassword ? '隐藏密码' : '显示密码'">
                  <i :class="['fas', showPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
              <div v-if="formData.password.length > 0" class="strength">
                <div class="strength-bar">
                  <div :class="['strength-fill', passwordStrength]"></div>
                </div>
                <span class="strength-label">{{ strengthLabel }}</span>
              </div>
            </div>
            <div class="field">
              <label class="label">确认密码</label>
              <div class="input-wrap">
                <input v-model="formData.confirmPassword" :type="showConfirmPassword ? 'text' : 'password'"
                       placeholder="再次输入密码" class="input" autocomplete="new-password">
                <button class="eye" @click="showConfirmPassword = !showConfirmPassword" type="button"
                        :aria-label="showConfirmPassword ? '隐藏密码' : '显示密码'">
                  <i :class="['fas', showConfirmPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="field">
              <label class="label">学号 <span class="opt">(选填)</span></label>
              <input v-model="formData.studentId" type="text" placeholder="请输入学号" class="input">
            </div>
            <div class="field">
              <label class="label">教务密码 <span class="opt">(选填)</span></label>
              <div class="input-wrap">
                <input v-model="formData.sPassword" :type="showSPassword ? 'text' : 'password'"
                       placeholder="教务系统密码" class="input" autocomplete="new-password">
                <button class="eye" @click="showSPassword = !showSPassword" type="button"
                        :aria-label="showSPassword ? '隐藏密码' : '显示密码'">
                  <i :class="['fas', showSPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
                </button>
              </div>
              <span class="hint">用于自动登录教务系统等外部网站</span>
            </div>
          </div>

          <div class="field captcha-field">
            <label class="label">邮箱验证码</label>
            <div class="captcha-row">
              <input v-model="formData.captcha" type="text" placeholder="6位验证码" maxlength="6" class="input">
              <button class="captcha-btn" @click="handleSendCaptcha"
                      :disabled="captchaCooldown > 0 || !isValidEmail">
                {{ captchaCooldown > 0 ? `${captchaCooldown}s` : '获取验证码' }}
              </button>
            </div>
            <span v-if="captchaSent" class="captcha-ok">验证码已发送</span>
          </div>

          <label class="terms-checkbox">
            <input type="checkbox" v-model="formData.agreeTerms">
            <span class="check-box"><i class="fas fa-check"></i></span>
            <span class="check-text">
              我已阅读并同意
              <router-link to="/terms">服务条款</router-link>
              和
              <router-link to="/privacy">隐私政策</router-link>
            </span>
          </label>

          <button class="register-btn" @click="handleRegister"
                  :disabled="loading || !isFormValid">
            <span v-if="!loading">创建账号</span>
            <span v-else><i class="fas fa-spinner fa-spin"></i> 注册中...</span>
          </button>

          <div class="form-footer">
            <span>已有账号？</span>
            <router-link to="/login" class="login-link">
              立即登录 <i class="fas fa-arrow-right"></i>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 由全局 ToastHost 统一渲染（见 register.ts 中的 useToast 调用） -->
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRegisterService } from './register';

export default defineComponent({
  name: 'Register',
  setup() { return useRegisterService(); }
});
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

.register-container {
  width: 100%;
  max-width: 560px;
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

.form-header {
  margin-bottom: var(--space-6);
}

.form-header h2 {
  font-size: var(--font-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: 4px;
}

.form-header p {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-row {
  display: flex;
  gap: var(--space-4);
}

.field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.opt { font-weight: var(--font-normal); color: var(--text-tertiary); }

.input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  color: var(--text-primary);
  background: var(--bg);
  transition: all var(--transition);
  box-sizing: border-box;
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.input-wrap { position: relative; }
.input-wrap .input { padding-right: 44px; }

.eye {
  position: absolute;
  right: 4px; top: 50%;
  transform: translateY(-50%);
  width: 36px; height: 36px;
  border: none; background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
}
.eye:hover { background: var(--gray-100); color: var(--text-primary); }

/* Strength */
.strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 2px;
}
.strength-bar {
  flex: 1; height: 4px;
  background: var(--gray-100);
  border-radius: 2px;
  overflow: hidden;
}
.strength-fill { height: 100%; transition: all 0.3s ease; }
.strength-fill.weak { width: 33%; background: var(--red); }
.strength-fill.medium { width: 66%; background: var(--orange); }
.strength-fill.strong { width: 100%; background: var(--green); }
.strength-label { font-size: var(--font-xs); color: var(--text-tertiary); min-width: 24px; text-align: right; }

/* Hint */
.hint { font-size: var(--font-xs); color: var(--text-tertiary); margin-top: 2px; }

/* Captcha */
.captcha-field {  }
.captcha-row { display: flex; gap: 10px; }
.captcha-row .input { flex: 1; }
.captcha-btn {
  padding: 0 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
  font-size: var(--font-sm);
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition);
}
.captcha-btn:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); }
.captcha-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.captcha-ok { font-size: var(--font-xs); color: var(--green); }

/* Terms */
.terms-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
}
.terms-checkbox input { display: none; }
.check-box {
  width: 18px; height: 18px;
  border: 2px solid var(--gray-300);
  border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px;
  color: transparent;
  flex-shrink: 0;
  margin-top: 2px;
  transition: all var(--transition);
}
.terms-checkbox input:checked + .check-box { background: var(--primary); border-color: var(--primary); color: white; }
.check-text { font-size: var(--font-sm); color: var(--text-tertiary); line-height: 1.5; }
.check-text a { color: var(--primary); font-weight: var(--font-medium); }

/* Button */
.register-btn {
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
.register-btn:hover:not(:disabled) { background: var(--primary-dark); }
.register-btn:disabled { background: var(--gray-100); color: var(--gray-400); cursor: not-allowed; }

.form-footer { text-align: center; margin-top: var(--space-4); font-size: var(--font-sm); color: var(--text-tertiary); }
.login-link { color: var(--primary); font-weight: var(--font-medium); margin-left: 4px; }
.login-link i { font-size: 12px; }

/* Responsive */
@media (max-width: 768px) {
  .register-page { padding: var(--space-4); align-items: flex-start; padding-top: var(--space-8); }
  .form-row { flex-direction: column; gap: var(--space-4); }
  .form-card { padding: var(--space-6) var(--space-5); }
  .captcha-row { flex-direction: column; }
  .captcha-btn { padding: 10px; }
}

@media (max-width: 480px) {
  .brand { margin-bottom: var(--space-6); }
  .form-card { padding: var(--space-5) var(--space-4); }
}
</style>
