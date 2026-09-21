<template>
  <div class="security-indicator" :class="{ 'secure': isSecure, 'loading': isLoading, 'disabled': isDisabled }">
    <div class="security-content">
      <div class="security-icon">
        <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
        <i v-else-if="isSecure" class="fas fa-shield-alt"></i>
        <i v-else-if="isDisabled" class="fas fa-info-circle"></i>
        <i v-else class="fas fa-exclamation-triangle"></i>
      </div>
      <div class="security-text">
        <div class="security-title">
          {{ securityTitle }}
        </div>
        <div class="security-subtitle">
          {{ securitySubtitle }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import rsaCrypto from '@/utils/rsa-crypto'

export default {
  name: 'SecurityIndicator',
  setup() {
    const isSecure = ref(false)
    const isLoading = ref(true)
    const isDisabled = ref(false)
    const errorMessage = ref('')

    const securityTitle = computed(() => {
      if (isLoading.value) return '正在初始化安全连接...'
      if (isSecure.value) return '密码加密已启用'
      if (isDisabled.value) return '标准安全模式'
      return '安全连接失败'
    })

    const securitySubtitle = computed(() => {
      if (isLoading.value) return '请稍候'
      if (isSecure.value) return '您的数据已受到加密保护'
      if (isDisabled.value) return '使用HTTPS传输保护'
      return errorMessage.value || '请刷新页面重试'
    })

    const initSecurity = async () => {
      try {
        isLoading.value = true
        const testResult = await rsaCrypto.testEncryption()

        if (testResult === true) {
          isSecure.value = true
          isDisabled.value = false
        } else if (testResult === 'disabled') {
          isSecure.value = false
          isDisabled.value = true
        } else {
          isSecure.value = false
          isDisabled.value = false
          errorMessage.value = '加密功能初始化失败'
        }
      } catch (error) {
        isSecure.value = false
        isDisabled.value = false
        errorMessage.value = '网络连接异常'
      } finally {
        isLoading.value = false
      }
    }

    onMounted(() => { initSecurity() })

    return { isSecure, isLoading, isDisabled, securityTitle, securitySubtitle }
  }
}
</script>

<style scoped>
.security-indicator {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-5);
  transition: all var(--transition);
  border: 1px solid;
}

.security-indicator.loading,
.security-indicator.disabled {
  background: var(--primary-subtle);
  border-color: transparent;
  color: var(--primary);
}

.security-indicator.secure {
  background: var(--green-subtle);
  border-color: transparent;
  color: var(--green);
}

.security-indicator:not(.secure):not(.loading):not(.disabled) {
  background: var(--red-subtle);
  border-color: transparent;
  color: var(--red);
}

.security-content {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.security-icon {
  width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.security-icon i { font-size: 15px; }

.security-text { flex: 1; }

.security-title {
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  margin-bottom: 1px;
}

.security-subtitle {
  font-size: var(--font-xs);
  opacity: 0.8;
}

@media (max-width: 768px) {
  .security-indicator { padding: 8px 12px; }
  .security-content { gap: 8px; }
  .security-icon { width: 20px; height: 20px; }
  .security-icon i { font-size: 13px; }
  .security-title { font-size: var(--font-xs); }
  .security-subtitle { font-size: 11px; }
}
</style>
