<template>
  <div class="security-indicator" :class="{ 'secure': isSecure, 'loading': isLoading }">
    <div class="security-content">
      <div class="security-icon">
        <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
        <i v-else-if="isSecure" class="fas fa-shield-alt"></i>
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
    const errorMessage = ref('')

    const securityTitle = computed(() => {
      if (isLoading.value) return '正在初始化安全连接...'
      if (isSecure.value) return '密码加密已启用'
      return '安全连接失败'
    })

    const securitySubtitle = computed(() => {
      if (isLoading.value) return '请稍候'
      if (isSecure.value) return '您的数据已受到加密保护'
      return errorMessage.value || '请刷新页面重试'
    })

    const initSecurity = async () => {
      try {
        isLoading.value = true
        
        // 测试RSA加密功能
        const testResult = await rsaCrypto.testEncryption()
        
        if (testResult) {
          isSecure.value = true
          console.log('安全连接初始化成功')
        } else {
          isSecure.value = false
          errorMessage.value = '加密功能初始化失败'
          console.warn('安全连接初始化失败')
        }
      } catch (error) {
        isSecure.value = false
        errorMessage.value = '网络连接异常'
        console.error('安全连接初始化异常:', error)
      } finally {
        isLoading.value = false
      }
    }

    onMounted(() => {
      initSecurity()
    })

    return {
      isSecure,
      isLoading,
      securityTitle,
      securitySubtitle
    }
  }
}
</script>

<style scoped>
.security-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  border: 1px solid;
}

.security-indicator.loading {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

.security-indicator.secure {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.security-indicator:not(.secure):not(.loading) {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.security-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.security-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.security-icon i {
  font-size: 16px;
}

.security-text {
  flex: 1;
}

.security-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
}

.security-subtitle {
  font-size: 12px;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .security-indicator {
    padding: 10px 14px;
    margin-bottom: 16px;
  }
  
  .security-content {
    gap: 10px;
  }
  
  .security-icon {
    width: 20px;
    height: 20px;
  }
  
  .security-icon i {
    font-size: 14px;
  }
  
  .security-title {
    font-size: 13px;
  }
  
  .security-subtitle {
    font-size: 11px;
  }
}
</style>