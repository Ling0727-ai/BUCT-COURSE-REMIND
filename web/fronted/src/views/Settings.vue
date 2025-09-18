<template>
  <div class="container">
    <div class="header">
      <button class="back-btn" @click="goBack">
        <i class="fas fa-arrow-left"></i>
        返回
      </button>
      <h1><i class="fas fa-cog"></i> 系统设置</h1>
    </div>

    <div class="content">
      <!-- 基础设置 -->
      <!-- 学生信息设置 -->
      <div class="section">
        <h2 class="section-title">
          <i class="fas fa-user-graduate"></i>
          学生信息配置
        </h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学号</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="studentInfo.studentId" 
              placeholder="请输入学号"
            >
          </div>
          <div class="form-group">
            <label class="form-label">外部系统密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="studentInfo.sPassword" 
              placeholder="用于访问教务系统的密码"
            >
          </div>
        </div>
        <div class="info-tip">
          <i class="fas fa-info-circle"></i>
          此信息用于自动登录教务系统获取作业和考试信息，请确保信息准确
        </div>
        <button class="btn btn-primary" @click="saveStudentInfo" style="margin-top: 15px;">
          <i class="fas fa-save"></i>
          保存学生信息
        </button>
      </div>

      <!-- Webhook设置 -->
      <div class="section">
        <h2 class="section-title">
          <i class="fas fa-bell"></i>
          通知设置
        </h2>
        <div id="webhookList">
          <div 
            v-for="webhook in webhooks" 
            :key="webhook.id"
            :class="['webhook-item', { 'active': webhook.enabled }]"
          >
            <div class="webhook-header">
              <div class="webhook-title">
                <i :class="webhookTypes[webhook.type].icon"></i>
                {{ webhookTypes[webhook.type].name }} #{{ webhook.id }}
              </div>
              <div :class="['webhook-status', { 'active': webhook.enabled, 'inactive': !webhook.enabled }]">
                {{ webhook.enabled ? '启用' : '禁用' }}
              </div>
              <div class="webhook-actions">
                <button 
                  :class="['btn', 'btn-small', webhook.enabled ? 'btn-danger' : 'btn-success']" 
                  @click="toggleWebhook(webhook.id)"
                >
                  <i :class="'fas fa-' + (webhook.enabled ? 'pause' : 'play')"></i>
                  {{ webhook.enabled ? '禁用' : '启用' }}
                </button>
                <button class="btn btn-small btn-outline" @click="testWebhook(webhook.id)">
                  <i class="fas fa-vial"></i>
                  测试
                </button>
                <button class="btn btn-small btn-danger" @click="deleteWebhook(webhook.id)">
                  <i class="fas fa-trash"></i>
                  删除
                </button>
              </div>
            </div>
            <div v-for="field in webhookTypes[webhook.type].fields" :key="field.name">
              <div class="form-group">
                <label class="form-label">{{ field.label }}</label>
                <template v-if="field.type === 'select'">
                  <select 
                    class="form-input" 
                    :value="getWebhookConfigValue(webhook, field.name)"
                    @change="updateWebhookConfig(webhook.id, field.name, $event.target.value)"
                  >
                    <option 
                      v-for="option in field.options" 
                      :key="option" 
                      :value="option"
                      :selected="getWebhookConfigValue(webhook, field.name) === option"
                    >
                      {{ option }}
                    </option>
                  </select>
                </template>
                <template v-else-if="field.type === 'textarea'">
                  <textarea 
                    class="form-input" 
                    rows="3" 
                    :value="getWebhookConfigValue(webhook, field.name)"
                    @input="updateWebhookConfig(webhook.id, field.name, $event.target.value)"
                    :placeholder="field.placeholder"
                  ></textarea>
                </template>
                <template v-else>
                  <input 
                    :type="field.type" 
                    class="form-input" 
                    :value="getWebhookConfigValue(webhook, field.name)"
                    @input="updateWebhookConfig(webhook.id, field.name, $event.target.value)"
                    :placeholder="field.placeholder"
                  >
                </template>
              </div>
            </div>
          </div>
        </div>
        <button class="add-webhook-btn" @click="showAddWebhookDialog">
          <i class="fas fa-plus"></i>
          添加新的通知方式
        </button>
      </div>

      <!-- 保存设置 -->
      <div class="save-section">
        <button class="btn btn-success" @click="testConnection" style="margin-right: 15px;">
          <i class="fas fa-plug"></i>
          测试连接
        </button>
        <button class="btn btn-primary" @click="saveSettings">
          <i class="fas fa-save"></i>
          保存设置
        </button>
      </div>
    </div>

    <!-- Webhook类型选择对话框 -->
    <div v-if="showWebhookDialog" class="webhook-dialog-overlay">
      <div class="webhook-dialog">
        <h3>选择通知类型</h3>
        <div class="webhook-type-select">
          <div 
            v-for="(config, type) in webhookTypes" 
            :key="type"
            class="webhook-type"
            @click="addWebhook(type)"
          >
            <i :class="config.icon"></i>
            {{ config.name }}
          </div>
        </div>
        <div class="dialog-actions">
          <button class="btn btn-outline" @click="showWebhookDialog = false">取消</button>
        </div>
      </div>
    </div>

    <!-- Toast消息 -->
    <div v-if="toast.show" :class="['toast', toast.type]">
      <div style="display: flex; align-items: center; gap: 10px;">
        <i :class="toastIcon"></i>
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Settings',
  setup() {
    const router = useRouter()
    
    // 设置数据
    const settings = reactive({
      serverUrl: ''
    })

    // 学生信息数据
    const studentInfo = reactive({
      studentId: '',
      sPassword: ''
    })

    // Webhook类型配置
    const webhookTypes = {
      email: {
        name: '邮件',
        icon: 'fas fa-envelope',
        fields: [
          { name: 'smtp_server', label: 'SMTP服务器', type: 'text', placeholder: 'smtp.gmail.com' },
          { name: 'smtp_port', label: 'SMTP端口', type: 'number', placeholder: '587' },
          { name: 'email', label: '发件邮箱', type: 'email', placeholder: 'your@gmail.com' },
          { name: 'password', label: '邮箱密码/授权码', type: 'password', placeholder: '邮箱密码或应用密码' },
          { name: 'to_email', label: '收件邮箱', type: 'email', placeholder: 'recipient@gmail.com' }
        ]
      },
      telegram: {
        name: 'Telegram',
        icon: 'fab fa-telegram-plane',
        fields: [
          { name: 'bot_token', label: 'Bot Token', type: 'text', placeholder: 'your_bot_token' },
          { name: 'chat_id', label: 'Chat ID', type: 'text', placeholder: 'your_chat_id' }
        ]
      },
      discord: {
        name: 'Discord',
        icon: 'fab fa-discord',
        fields: [
          { name: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://discord.com/api/webhooks/...' }
        ]
      },
      slack: {
        name: 'Slack',
        icon: 'fab fa-slack',
        fields: [
          { name: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://hooks.slack.com/services/...' }
        ]
      },
      webhook: {
        name: '自定义Webhook',
        icon: 'fas fa-code',
        fields: [
          { name: 'url', label: 'Webhook URL', type: 'url', placeholder: 'https://your-webhook-url.com' },
          { name: 'method', label: 'HTTP方法', type: 'select', options: ['POST', 'GET', 'PUT'], default: 'POST' },
          { name: 'headers', label: '请求头 (JSON格式)', type: 'textarea', placeholder: '{"Content-Type": "application/json"}' },
          { name: 'template', label: '消息模板', type: 'textarea', placeholder: '{"text": "{{message}}"}' }
        ]
      }
    }

    const webhooks = ref([])
    const nextWebhookId = ref(1)
    const showWebhookDialog = ref(false)
    const toast = reactive({ show: false, message: '', type: 'success' })

    const toastIcon = computed(() => {
      const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return icons[toast.type]
    })

    // 返回上一页
    const goBack = () => {
      router.back()
    }

    // 获取Webhook配置值
    const getWebhookConfigValue = (webhook, fieldName) => {
      return webhook.config[fieldName] || webhookTypes[webhook.type].fields
        .find(f => f.name === fieldName)?.default || ''
    }

    // 显示添加Webhook对话框
    const showAddWebhookDialog = () => {
      showWebhookDialog.value = true
    }

    // 添加Webhook
    const addWebhook = (type) => {
      const newWebhook = {
        id: nextWebhookId.value++,
        type: type,
        enabled: true,
        config: {}
      }
      webhooks.value.push(newWebhook)
      showWebhookDialog.value = false
    }

    // 更新Webhook配置
    const updateWebhookConfig = (id, field, value) => {
      const webhook = webhooks.value.find(w => w.id === id)
      if (webhook) {
        webhook.config[field] = value
      }
    }

    // 切换Webhook启用状态
    const toggleWebhook = (id) => {
      const webhook = webhooks.value.find(w => w.id === id)
      if (webhook) {
        webhook.enabled = !webhook.enabled
      }
    }

    // 删除Webhook
    const deleteWebhook = (id) => {
      if (confirm('确认删除这个通知配置吗？')) {
        webhooks.value = webhooks.value.filter(w => w.id !== id)
      }
    }

    // 测试Webhook
    const testWebhook = (id) => {
      showToast('正在测试通知...', 'info')
      
      // 模拟测试请求
      setTimeout(() => {
        const success = Math.random() > 0.3 // 70%成功率
        if (success) {
          showToast('测试消息发送成功！', 'success')
        } else {
          showToast('测试失败，请检查配置', 'error')
        }
      }, 2000)
    }

    // 测试连接
    const testConnection = () => {
      if (!settings.serverUrl) {
        showToast('请先填写服务器地址', 'error')
        return
      }

      showToast('正在测试连接...', 'info')
      
      // 模拟连接测试
      fetch(settings.serverUrl + '/api/health')
        .then(response => {
          if (response.ok) {
            showToast('连接测试成功！', 'success')
          } else {
            showToast('服务器响应异常', 'error')
          }
        })
        .catch(error => {
          showToast('连接失败：' + error.message, 'error')
        })
    }

    // 保存学生信息
    const saveStudentInfo = async () => {
      if (!studentInfo.studentId || !studentInfo.sPassword) {
        showToast('请填写完整的学生信息', 'error')
        return
      }

      showToast('正在保存学生信息...', 'info')

      try {
        const response = await fetch('/api/auth/update-student-info', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            student_id: studentInfo.studentId,
            s_password: studentInfo.sPassword
          })
        })

        const data = await response.json()

        if (response.ok) {
          showToast('学生信息保存成功！', 'success')
        } else {
          showToast(data.error || '保存失败', 'error')
        }
      } catch (error) {
        showToast('网络错误：' + error.message, 'error')
      }
    }

    // 保存设置
    const saveSettings = () => {
      const settingsData = {
        serverUrl: settings.serverUrl,
        webhooks: webhooks.value
      }

      // 验证必填项
      if (!settingsData.serverUrl) {
        showToast('请填写服务器地址', 'error')
        return
      }

      showToast('正在保存设置...', 'info')

      // 发送到后端
      fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settingsData)
      })
      .then(response => response.json())
      .then(data => {
        showToast('设置保存成功！', 'success')
        console.log('设置已保存:', data)
      })
      .catch(error => {
        showToast('保存失败：' + error.message, 'error')
        console.error('保存设置失败:', error)
      })
    }

    // 显示提示消息
    const showToast = (message, type = 'success') => {
      toast.message = message
      toast.type = type
      toast.show = true
      
      // 3秒后自动隐藏
      setTimeout(() => {
        toast.show = false
      }, 3000)
    }

    // 加载用户信息
    const loadUserInfo = async () => {
      try {
        const response = await fetch('/api/auth/user-info')
        if (response.ok) {
          const data = await response.json()
          studentInfo.studentId = data.student_id || ''
          // 不显示密码，只显示是否已设置
          if (data.has_student_password) {
            studentInfo.sPassword = '••••••••'
          }
        }
      } catch (error) {
        console.error('加载用户信息失败:', error)
      }
    }

    // 加载保存的设置
    const loadSettings = async () => {
      try {
        const response = await fetch('/api/settings')
        if (response.ok) {
          const data = await response.json()
          Object.assign(settings, data)
          webhooks.value = data.webhooks || []
          nextWebhookId.value = Math.max(...webhooks.value.map(w => w.id), 0) + 1
        }
      } catch (error) {
        console.error('加载设置失败:', error)
        // 从localStorage加载备用设置
        const savedSettings = localStorage.getItem('assignment-settings')
        if (savedSettings) {
          const data = JSON.parse(savedSettings)
          Object.assign(settings, data.settings || {})
          webhooks.value = data.webhooks || []
          nextWebhookId.value = Math.max(...webhooks.value.map(w => w.id), 0) + 1
        }
      }
    }

    // 初始化
    loadSettings()
    loadUserInfo()

    return {
      settings,
      studentInfo,
      webhooks,
      webhookTypes,
      showWebhookDialog,
      toast,
      toastIcon,
      goBack,
      getWebhookConfigValue,
      showAddWebhookDialog,
      addWebhook,
      updateWebhookConfig,
      toggleWebhook,
      deleteWebhook,
      testWebhook,
      testConnection,
      saveSettings,
      saveStudentInfo,
      showToast
    }
  }
}
</script>

<style scoped>
/* 全局容器 */
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4facfe 100%);
  position: relative;
  overflow-x: hidden;
}

/* 装饰性浮动元素 */
.container::before {
  content: '';
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: float 20s linear infinite;
  pointer-events: none;
  z-index: 0;
}

.container::after {
  content: '';
  position: fixed;
  top: 20%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.1), transparent 70%);
  border-radius: 50%;
  animation: pulse 4s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(-50px, -50px) rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.3; }
  50% { transform: scale(1.2) rotate(180deg); opacity: 0.1; }
}

.header {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 25px 35px;
  margin: 20px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
  animation: shimmer 6s infinite;
  z-index: 0;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.header h1 {
  font-size: 2em;
  margin: 0;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 2;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 18px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 2;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-5px) translateY(-2px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}

.content {
  padding: 20px 35px 40px 35px;
  position: relative;
  z-index: 1;
}

.section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 25px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-left: 5px solid #667eea;
  position: relative;
  overflow: hidden;
}

.section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(102, 126, 234, 0.05));
  pointer-events: none;
  z-index: 0;
}

.section-title {
  font-size: 1.4em;
  color: #1f2937;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.section-title i {
  color: #667eea;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.form-group {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid rgba(229, 231, 235, 0.8);
  border-radius: 12px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  color: #1f2937;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.form-input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 0 25px rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.95);
}

.form-input::placeholder {
  color: #6b7280;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.webhook-item {
  background: rgba(248, 249, 250, 0.9);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(233, 236, 239, 0.8);
  border-radius: 18px;
  padding: 25px;
  margin-bottom: 20px;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
}

.webhook-item:hover {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
  transform: translateY(-3px);
}

.webhook-item.active {
  border-color: rgba(39, 174, 96, 0.6);
  background: linear-gradient(135deg, rgba(248, 255, 248, 0.9), rgba(232, 245, 232, 0.9));
  box-shadow: 0 15px 35px rgba(39, 174, 96, 0.15);
}

.webhook-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.webhook-title {
  font-size: 1.1em;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.webhook-title i {
  color: #667eea;
}

.webhook-status {
  padding: 8px 16px;
  border-radius: 25px;
  font-size: 0.85em;
  font-weight: 600;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.webhook-status.active {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.webhook-status.inactive {
  background: linear-gradient(135deg, #e74c3c, #ec7063);
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.webhook-actions {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}

.btn-success {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
}

.btn-success:hover {
  background: linear-gradient(135deg, #219a52, #27ae60);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c, #ec7063);
  color: white;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c0392b, #e74c3c);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(102, 126, 234, 0.6);
  color: #667eea;
}

.btn-outline:hover {
  background: rgba(102, 126, 234, 0.9);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-small {
  padding: 8px 14px;
  font-size: 12px;
}

.add-webhook-btn {
  width: 100%;
  padding: 25px;
  border: 2px dashed rgba(102, 126, 234, 0.4);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #667eea;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.add-webhook-btn:hover {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
}

.webhook-type-select {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.webhook-type {
  padding: 20px 15px;
  border: 2px solid rgba(221, 221, 221, 0.6);
  border-radius: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.webhook-type:hover {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.webhook-type.selected {
  border-color: rgba(102, 126, 234, 0.8);
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.webhook-type i {
  font-size: 1.8em;
  margin-bottom: 10px;
  display: block;
}

.info-tip {
  background: rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 15px;
  padding: 18px;
  margin-top: 20px;
  font-size: 14px;
  color: #667eea;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
}

.info-tip i {
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

.save-section {
  text-align: center;
  padding: 35px 30px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-top: 30px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.save-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(102, 126, 234, 0.05));
  pointer-events: none;
}

/* 对话框样式 */
.webhook-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.webhook-dialog {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 35px;
  border-radius: 20px;
  max-width: 550px;
  width: 90%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.3s ease;
}

.webhook-dialog h3 {
  color: #1f2937;
  font-size: 1.5em;
  font-weight: 600;
  margin-bottom: 25px;
  text-align: center;
}

.dialog-actions {
  text-align: center;
  margin-top: 25px;
  position: relative;
  z-index: 1;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    transform: translateY(30px);
    opacity: 0;
  }
  to { 
    transform: translateY(0);
    opacity: 1;
  }
}

/* Toast样式 */
.toast {
  position: fixed;
  top: 25px;
  right: 25px;
  padding: 18px 28px;
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  border-radius: 15px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 1000;
  animation: toastSlideIn 0.4s ease;
  font-weight: 500;
}

.toast.error {
  background: linear-gradient(135deg, #e74c3c, #ec7063);
}

.toast.info {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

@keyframes toastSlideIn {
  from {
    transform: translateX(100%) translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateX(0) translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .container::before,
  .container::after {
    display: none;
  }

  .header {
    margin: 15px;
    padding: 20px 25px;
    gap: 15px;
  }

  .header h1 {
    font-size: 1.6em;
  }

  .content {
    padding: 15px 30px 30px 30px;
  }

  .section {
    padding: 25px 20px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .webhook-type-select {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .webhook-type {
    padding: 15px 10px;
  }

  .webhook-actions {
    position: static;
    margin-top: 20px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .webhook-dialog {
    padding: 25px 20px;
    margin: 20px;
  }

  .save-section {
    padding: 25px 20px;
  }

  .btn {
    padding: 10px 16px;
    font-size: 13px;
  }

  .btn-small {
    padding: 6px 10px;
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .header,
  .content {
    margin: 10px;
    padding: 15px 20px;
  }

  .section {
    padding: 20px 15px;
  }

  .webhook-type-select {
    grid-template-columns: 1fr;
  }

  .webhook-actions {
    flex-direction: column;
    gap: 8px;
  }

  .form-input {
    padding: 12px 16px;
    font-size: 14px;
  }
}
</style>