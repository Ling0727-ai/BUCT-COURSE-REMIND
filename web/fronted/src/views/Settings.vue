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

      <!-- 邮箱提醒设置 -->
      <div class="section">
        <h2 class="section-title">
          <i class="fas fa-envelope"></i>
          邮箱提醒设置
        </h2>
        <div class="form-group">
          <label class="form-label">收件邮箱</label>
          <input 
            type="email" 
            class="form-input" 
            v-model="emailSettings.toEmail" 
            placeholder="请输入接收提醒的邮箱地址"
          >
        </div>
        <div class="info-tip">
          <i class="fas fa-info-circle"></i>
          系统将使用发送验证码的邮箱配置来发送作业提醒邮件
        </div>
        <button class="btn btn-primary" @click="saveEmailSettings" style="margin-top: 15px;">
          <i class="fas fa-save"></i>
          保存邮箱设置
        </button>
      </div>

      <!-- 数据管理设置 -->
      <div class="section">
        <h2 class="section-title">
          <i class="fas fa-database"></i>
          数据管理
        </h2>
        <div class="data-status-card">
          <div class="status-info">
            <div class="status-item">
              <span class="status-label">数据状态:</span>
              <span :class="['status-value', dataStatus.hasData ? 'status-active' : 'status-inactive']">
                {{ dataStatus.hasData ? '已同步' : '未同步' }}
              </span>
            </div>
            <div class="status-item" v-if="dataStatus.lastUpdate">
              <span class="status-label">最后更新:</span>
              <span class="status-value">{{ formatDateTime(dataStatus.lastUpdate) }}</span>
            </div>
            <div class="status-item" v-if="dataStatus.hoursUntilRefresh !== null">
              <span class="status-label">下次自动刷新:</span>
              <span class="status-value">{{ formatNextRefresh(dataStatus.hoursUntilRefresh) }}</span>
            </div>
          </div>
          <div class="refresh-actions">
            <button 
              class="btn btn-refresh" 
              @click="refreshCourseData" 
              :disabled="refreshing"
              :class="{ 'refreshing': refreshing }"
            >
              <i :class="['fas', refreshing ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
              {{ refreshing ? '刷新中...' : '手动刷新数据' }}
            </button>
            <div class="refresh-tip">
              <i class="fas fa-info-circle"></i>
              数据每12小时自动刷新一次，也可手动刷新
            </div>
          </div>
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

    // 邮箱设置
    const emailSettings = reactive({
      toEmail: ''
    })
    const toast = reactive({ show: false, message: '', type: 'success' })
    
    // 数据状态相关
    const dataStatus = reactive({
      hasData: false,
      lastUpdate: null,
      nextAutoRefresh: null,
      hoursUntilRefresh: null
    })
    const refreshing = ref(false)

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

    // 保存邮箱设置
    const saveEmailSettings = async () => {
      if (!emailSettings.toEmail) {
        showToast('请填写收件邮箱', 'error')
        return
      }

      showToast('正在保存邮箱设置...', 'info')

      try {
        const response = await fetch('/api/settings/email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            to_email: emailSettings.toEmail
          })
        })

        const data = await response.json()

        if (response.ok) {
          showToast('邮箱设置保存成功！', 'success')
        } else {
          showToast(data.error || '保存失败', 'error')
        }
      } catch (error) {
        showToast('网络错误：' + error.message, 'error')
      }
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

    // 格式化日期时间
    const formatDateTime = (dateString) => {
      if (!dateString) return '未知'
      try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZone: 'Asia/Shanghai'
        })
      } catch (error) {
        return '格式错误'
      }
    }

    // 格式化下次刷新时间
    const formatNextRefresh = (hours) => {
      if (hours === null || hours === undefined) return '未知'
      if (hours <= 0) return '即将刷新'
      if (hours < 1) {
        const minutes = Math.round(hours * 60)
        return `${minutes}分钟后`
      }
      return `${Math.round(hours * 10) / 10}小时后`
    }

    // 获取数据状态
    const loadDataStatus = async () => {
      try {
        const response = await fetch('/api/course-data/status', {
          method: 'GET',
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            dataStatus.hasData = data.has_data
            dataStatus.lastUpdate = data.last_update
            dataStatus.nextAutoRefresh = data.next_auto_refresh
            dataStatus.hoursUntilRefresh = data.hours_until_refresh
          }
        } else {
          console.warn('获取数据状态失败')
        }
      } catch (error) {
        console.error('获取数据状态错误:', error)
      }
    }

    // 手动刷新课程数据
    const refreshCourseData = async () => {
      if (refreshing.value) return
      
      refreshing.value = true
      showToast('正在刷新课程数据...', 'info')
      
      try {
        const response = await fetch('/api/course-data/refresh', {
          method: 'POST',
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            showToast(`数据刷新成功！共更新 ${data.count} 条记录`, 'success')
            // 重新加载数据状态
            await loadDataStatus()
          } else {
            showToast(data.error || '刷新失败', 'error')
          }
        } else {
          const errorData = await response.json()
          showToast(errorData.error || '刷新失败，请重试', 'error')
        }
      } catch (error) {
        console.error('刷新数据错误:', error)
        showToast('网络错误，请检查连接后重试', 'error')
      } finally {
        refreshing.value = false
      }
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

    // 加载邮箱设置
    const loadEmailSettings = async () => {
      try {
        const response = await fetch('/api/settings/email')
        if (response.ok) {
          const data = await response.json()
          emailSettings.toEmail = data.to_email || ''
        }
      } catch (error) {
        console.error('加载邮箱设置失败:', error)
      }
    }

    // 初始化
    loadEmailSettings()
    loadUserInfo()
    loadDataStatus()

    return {
      settings,
      studentInfo,
      emailSettings,
      toast,
      toastIcon,
      goBack,
      saveEmailSettings,
      saveStudentInfo,
      showToast,
      dataStatus,
      refreshing,
      formatDateTime,
      formatNextRefresh,
      loadDataStatus,
      refreshCourseData
    }
  }
}
</script>

<style scoped>
/* 全局容器 */
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdfa 100%);
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
  background: radial-gradient(circle, rgba(14, 165, 233, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  animation: float 30s linear infinite;
  pointer-events: none;
  z-index: 0;
}

.container::after {
  content: '';
  position: fixed;
  top: 10%;
  right: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.05), transparent 70%);
  border-radius: 50%;
  animation: pulse 6s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes float {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-30px, -30px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.1); opacity: 0.2; }
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.1);
  color: #0f172a;
  padding: 25px 35px;
  margin: 20px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
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
  background: linear-gradient(45deg, transparent, rgba(14, 165, 233, 0.05), transparent);
  animation: shimmer 8s infinite;
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
  color: #0f172a;
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header h1 i {
  color: #0ea5e9;
}

.back-btn {
  background: rgba(14, 165, 233, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  color: #0ea5e9;
  padding: 12px 18px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 2;
}

.back-btn:hover {
  background: rgba(14, 165, 233, 0.15);
  transform: translateX(-3px) translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(14, 165, 233, 0.1);
  border-left: 4px solid #0ea5e9;
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
  background: linear-gradient(135deg, transparent, rgba(14, 165, 233, 0.02));
  pointer-events: none;
  z-index: 0;
}

.section-title {
  font-size: 1.4em;
  color: #0f172a;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.section-title i {
  color: #0ea5e9;
  text-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
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
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
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
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
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
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 5px;
  border: 1px solid rgba(255, 255, 255, 0.2);
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

.webhook-status i {
  font-size: 0.9em;
}

.webhook-actions {
  display: flex;
  gap: 8px;
  margin-top: 15px;
  justify-content: flex-end;
  flex-wrap: wrap;
  align-items: center;
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
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
  background: linear-gradient(135deg, #0284c7, #0891b2);
}

.btn-success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}

.btn-success:hover {
  background: linear-gradient(135deg, #16a34a, #15803d);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(14, 165, 233, 0.3);
  color: #0ea5e9;
}

.btn-outline:hover {
  background: #0ea5e9;
  color: white;
  border-color: #0ea5e9;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.3);
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
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.9));
  backdrop-filter: blur(10px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.1);
  color: #1e293b;
  font-weight: 600;
}

.webhook-type:hover {
  border-color: rgba(102, 126, 234, 0.7);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.1));
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25);
  color: #667eea;
}

.webhook-type.selected {
  border-color: rgba(102, 126, 234, 0.9);
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.webhook-type i {
  font-size: 2.2em;
  margin-bottom: 12px;
  display: block;
  opacity: 0.8;
}

.webhook-type:hover i,
.webhook-type.selected i {
  opacity: 1;
}

.info-tip {
  background: rgba(14, 165, 233, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 15px;
  padding: 18px;
  margin-top: 20px;
  font-size: 14px;
  color: #0284c7;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
}

.info-tip i {
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
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
  z-index: 1100;
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
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border-radius: 15px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 1000;
  animation: toastSlideIn 0.4s ease;
  font-weight: 500;
}

.toast.error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.toast.info {
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
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

/* 数据状态卡片样式 */
.data-status-card {
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(226, 232, 240, 0.8);
  border-radius: 18px;
  padding: 25px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 30px;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.data-status-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(14, 165, 233, 0.02));
  pointer-events: none;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  font-weight: 600;
  color: #475569;
  min-width: 100px;
}

.status-value {
  font-weight: 500;
  color: #1e293b;
}

.status-active {
  color: #22c55e !important;
  font-weight: 600;
}

.status-inactive {
  color: #ef4444 !important;
  font-weight: 600;
}

.refresh-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.btn-refresh {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  padding: 14px 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 160px;
  justify-content: center;
}

.btn-refresh:hover:not(:disabled) {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
}

.btn-refresh:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-refresh.refreshing {
  background: linear-gradient(135deg, #6b7280, #9ca3af);
}

.refresh-tip {
  font-size: 12px;
  color: #64748b;
  text-align: center;
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 200px;
}

.refresh-tip i {
  color: #0ea5e9;
  font-size: 11px;
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

  .data-status-card {
    grid-template-columns: 1fr;
    gap: 20px;
    text-align: center;
  }

  .status-info {
    align-items: center;
  }

  .status-item {
    justify-content: center;
  }

  .refresh-actions {
    align-items: center;
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