<template>
  <div class="container">
    <div class="header">
      <div class="header-content">
        <h1><i class="fas fa-graduation-cap"></i> 作业管理系统</h1>
        <p>智能汇总所有科目作业，永不错过截止日期</p>
      </div>
      <div class="header-actions">
        <div class="current-time">
          <i class="fas fa-clock"></i>
          {{ currentTime }}
        </div>
        <div class="user-info" v-if="user">
          <span class="username">{{ user.username }}</span>
          <button class="logout-btn" @click="handleLogout">
            <i class="fas fa-sign-out-alt"></i>
            登出
          </button>
        </div>
        <router-link to="/settings" class="settings-btn">
          <i class="fas fa-cog"></i>
          <span>设置</span>
        </router-link>
      </div>
    </div>

    <div class="controls">
      <div class="controls-row">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchTerm" 
            @input="filterAssignments"
            placeholder="搜索作业标题或科目..."
          >
        </div>
        <select class="filter-select" v-model="subjectFilter" @change="filterAssignments">
          <option value="">全部科目</option>
          <option v-for="subject in subjects" :key="subject" :value="subject">{{ subject }}</option>
        </select>
        <select class="filter-select" v-model="statusFilter" @change="filterAssignments">
          <option value="">全部状态</option>
          <option value="urgent">紧急</option>
          <option value="warning">即将到期</option>
          <option value="normal">正常</option>
          <option value="completed">已完成</option>
        </select>
      </div>
      
      <div class="stats">
        <div class="stat-card urgent">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>{{ urgentCount }}</h3>
          <p>紧急作业</p>
        </div>
        <div class="stat-card soon">
          <i class="fas fa-clock"></i>
          <h3>{{ soonCount }}</h3>
          <p>即将到期</p>
        </div>
        <div class="stat-card total">
          <i class="fas fa-tasks"></i>
          <h3>{{ totalCount }}</h3>
          <p>总作业数</p>
        </div>
        <div class="stat-card completed">
          <i class="fas fa-check-circle"></i>
          <h3>{{ completedCount }}</h3>
          <p>已完成</p>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <h3>加载中...</h3>
        <p>正在获取最新的作业数据</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="fetchAssignments">重新加载</button>
      </div>
      
      <div v-else class="assignments-grid">
        <div v-if="filteredAssignments.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <h3>暂无作业</h3>
          <p>没有找到符合条件的作业</p>
        </div>
        <div 
          v-for="assignment in filteredAssignments" 
          :key="assignment.id"
          :class="['assignment-card', assignmentStatus(assignment)]"
          @click="openAssignmentUrl(assignment)"
          style="cursor: pointer;"
        >
          <div class="card-header">
            <span class="subject-tag">{{ assignment.subject }}</span>
            <small>{{ assignment.type }}</small>
          </div>
          <h3 class="card-title">{{ assignment.title }}</h3>
          <p class="card-content">{{ assignment.content }}</p>
          <div class="card-footer">
            <div v-if="assignment.dueDate && assignment.type !== '作业'" :class="['due-date', assignmentStatus(assignment)]">
              <i :class="statusIcon(assignment)"></i>
              <span>{{ formatDate(assignment.dueDate) }}</span>
            </div>
            <div v-else class="due-date-placeholder">
              <!-- 作业类型不显示时间或无截止日期 -->
            </div>
            <div class="actions" @click.stop>
              <button 
                v-if="!assignment.completed"
                class="btn btn-primary"
                @click="setReminder(assignment)"
              >
                <i class="fas fa-bell"></i> 提醒
              </button>
              <button 
                v-if="!assignment.completed"
                class="btn btn-success complete-btn"
                @click="markCompleted(assignment)"
                :disabled="assignment.completing"
              >
                <span v-if="!assignment.completing" class="btn-content">
                  <i class="fas fa-check"></i> 完成
                </span>
                <span v-else class="btn-loading">
                  <i class="fas fa-spinner fa-spin"></i> 处理中...
                </span>
              </button>
              <div v-else class="completed-actions">
                <button class="btn btn-completed">
                  <i class="fas fa-check-circle"></i> 已完成
                </button>
                <button 
                  class="btn btn-secondary undo-btn"
                  @click="undoCompleted(assignment)"
                  :disabled="assignment.undoing"
                  title="撤销完成"
                >
                  <span v-if="!assignment.undoing">
                    <i class="fas fa-undo"></i>
                  </span>
                  <span v-else>
                    <i class="fas fa-spinner fa-spin"></i>
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    
    // 用户状态
    const user = ref(null)
    // 实时时间
    const currentTime = ref('')
    let timeInterval
    
    const updateTime = () => {
      const now = new Date()
      currentTime.value = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
    }
    
    // 添加一些动画效果的状态
    const isPageLoaded = ref(false)
    
    // 动态数据
    const assignments = ref([])
    const loading = ref(false)
    const error = ref('')

    const searchTerm = ref('')
    const subjectFilter = ref('')
    const statusFilter = ref('')
    const filteredAssignments = ref([])

    // 计算统计信息
    const urgentCount = computed(() => 
      assignments.value.filter(a => assignmentStatus(a) === 'urgent').length
    )

    const soonCount = computed(() => 
      assignments.value.filter(a => assignmentStatus(a) === 'warning').length
    )

    const totalCount = computed(() => assignments.value.length)

    const completedCount = computed(() => 
      assignments.value.filter(a => a.completed).length
    )

    const subjects = computed(() => {
      const uniqueSubjects = new Set(assignments.value.map(a => a.subject))
      return Array.from(uniqueSubjects)
    })

    // 计算剩余天数
    const getDaysUntilDue = (dueDate) => {
      try {
        if (!dueDate) {
          return Infinity
        }
        
        const now = new Date()
        const due = new Date(dueDate)
        
        // 检查日期是否有效
        if (isNaN(due.getTime())) {
          console.warn('无效的截止日期:', dueDate)
          return 7 // 默认7天
        }
        
        const diffTime = due - now
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      } catch (error) {
        console.error('计算剩余天数时出错:', error, '日期:', dueDate)
        return 7 // 默认7天
      }
    }

    // 获取作业状态
    const assignmentStatus = (assignment) => {
      if (assignment.completed) return 'completed'
      
      const days = getDaysUntilDue(assignment.dueDate)
      if (days < 0) return 'urgent'
      if (days <= 2) return 'urgent'
      if (days <= 7) return 'warning'
      return 'normal'
    }

    // 状态图标
    const statusIcon = (assignment) => {
      const status = assignmentStatus(assignment)
      const icons = {
        urgent: 'fas fa-exclamation-triangle',
        warning: 'fas fa-clock',
        normal: 'fas fa-calendar-alt',
        completed: 'fas fa-check-circle'
      }
      return icons[status]
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const days = getDaysUntilDue(dateString)
      
      const options = { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      }
      
      let formatted = date.toLocaleDateString('zh-CN', options)
      
      if (days < 0) {
        formatted += ` (已过期${Math.abs(days)}天)`
      } else if (days === 0) {
        formatted += ' (今天截止)'
      } else if (days === 1) {
        formatted += ' (明天截止)'
      } else if (days <= 7) {
        formatted += ` (还有${days}天)`
      }
      
      return formatted
    }

    // 筛选作业
    const filterAssignments = () => {
      console.log('开始筛选作业，原始数据:', assignments.value)
      
      if (!assignments.value || !Array.isArray(assignments.value)) {
        console.warn('assignments.value 不是有效数组:', assignments.value)
        filteredAssignments.value = []
        return
      }
      
      filteredAssignments.value = assignments.value.filter(assignment => {
        // 安全检查
        if (!assignment) {
          console.warn('发现空的 assignment 项')
          return false
        }
        
        const title = assignment.title || ''
        const subject = assignment.subject || ''
        const searchTerm_lower = (searchTerm.value || '').toLowerCase()
        
        const matchesSearch = title.toLowerCase().includes(searchTerm_lower) ||
                            subject.toLowerCase().includes(searchTerm_lower)
        const matchesSubject = !subjectFilter.value || subject === subjectFilter.value
        const matchesStatus = !statusFilter.value || assignmentStatus(assignment) === statusFilter.value
        
        return matchesSearch && matchesSubject && matchesStatus
      })
      
      console.log('筛选后的数据:', filteredAssignments.value)
    }

    // 打开作业链接
    const openAssignmentUrl = (assignment) => {
      if (assignment.url && assignment.url.trim() !== '') {
        window.open(assignment.url, '_blank')
      } else {
        console.log('该作业没有可用的链接')
      }
    }

    // 设置提醒
    const setReminder = (assignment) => {
      if (assignment.type === '作业') {
        alert(`已设置提醒：${assignment.title}`)
        console.log('发送提醒webhook:', {
          type: 'reminder',
          assignment: assignment,
          message: `提醒：${assignment.subject} - ${assignment.title}`
        })
      } else {
        alert(`已设置提醒：${assignment.title}\n截止时间：${formatDate(assignment.dueDate)}`)
        console.log('发送提醒webhook:', {
          type: 'reminder',
          assignment: assignment,
          message: `提醒：${assignment.subject} - ${assignment.title} 将于 ${formatDate(assignment.dueDate)} 截止`
        })
      }
    }

    // 标记完成
    const markCompleted = async (assignment) => {
      if (assignment.completing) return
      
      assignment.completing = true
      
      try {
        const response = await fetch(`/api/assignments/${assignment.id}/complete`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: assignment.title,
            subject: assignment.subject
          })
        })
        
        if (response.ok) {
          const result = await response.json()
          
          // 更新本地状态
          assignment.completed = true
          assignment.completedAt = new Date().toISOString()
          
          filterAssignments()
          
          // 显示成功提示
          showToast('success', '任务完成', `${assignment.title} 已标记为完成，12小时后自动清除`)
          console.log('作业标记完成成功:', result)
        } else {
          const errorData = await response.json()
          console.error('标记完成失败:', errorData)
          showToast('error', '操作失败', errorData.error || '标记完成失败，请重试')
        }
      } catch (error) {
        console.error('标记完成错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      } finally {
        assignment.completing = false
      }
    }

    // 撤销完成
    const undoCompleted = async (assignment) => {
      if (assignment.undoing) return
      
      assignment.undoing = true
      
      try {
        const response = await fetch(`/api/assignments/${assignment.id}/uncomplete`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const result = await response.json()
          
          // 更新本地状态
          assignment.completed = false
          assignment.completedAt = null
          
          filterAssignments()
          
          showToast('info', '已撤销', `${assignment.title} 已撤销完成状态`)
          console.log('撤销完成成功:', result)
        } else {
          const errorData = await response.json()
          console.error('撤销完成失败:', errorData)
          showToast('error', '操作失败', errorData.error || '撤销失败，请重试')
        }
      } catch (error) {
        console.error('撤销完成错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      } finally {
        assignment.undoing = false
      }
    }

    // 显示提示消息
    const showToast = (type, title, message) => {
      const toast = document.createElement('div')
      toast.className = `toast toast-${type}`
      toast.innerHTML = `
        <div class="toast-icon">
          <i class="fas ${getToastIcon(type)}"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">${title}</div>
          <div class="toast-message">${message}</div>
        </div>
      `
      
      document.body.appendChild(toast)
      
      // 显示动画
      setTimeout(() => toast.classList.add('show'), 100)
      
      // 自动移除
      setTimeout(() => {
        toast.classList.remove('show')
        setTimeout(() => {
          if (document.body.contains(toast)) {
            document.body.removeChild(toast)
          }
        }, 300)
      }, 3000)
    }

    const getToastIcon = (type) => {
      const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
      }
      return icons[type] || 'fa-info-circle'
    }

    // 获取作业数据
    const fetchAssignments = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await fetch('/api/assignments/standard', {
          method: 'GET',
          credentials: 'include'
        })
        
        if (response.ok) {
          const result = await response.json()
          console.log('后端返回的原始数据:', result)
          
          // 适配后端实际返回的数据结构
          let dataArray = []
          if (result.tasks && Array.isArray(result.tasks)) {
            dataArray = result.tasks
          } else if (result.data && Array.isArray(result.data)) {
            dataArray = result.data
          } else if (result.success && result.data && Array.isArray(result.data)) {
            dataArray = result.data
          }
          
          if (dataArray.length > 0) {
            // 转换后端统一格式为前端期望格式
            // 获取数据库中的已完成状态
            let completedIds = new Set()
            try {
              const completedResponse = await fetch('/api/assignments/completed', {
                method: 'GET',
                credentials: 'include'
              })
              
              if (completedResponse.ok) {
                const completedData = await completedResponse.json()
                completedIds = new Set(completedData.completed_assignments || [])
                console.log('获取已完成作业列表成功:', completedData.completed_assignments)
              } else {
                console.warn('获取已完成作业列表失败，使用空列表')
              }
            } catch (error) {
              console.error('获取已完成作业列表错误:', error)
            }
            
            assignments.value = dataArray.map((item, index) => {
              // 数据验证和默认值处理
              const safeItem = {
                type: item?.type || 'homework',
                subject: item?.subject || '未知科目',
                details: {
                  task: item?.details?.task || '未知任务',
                  deadline: item?.details?.deadline || null,
                  url: item?.details?.url || ''
                }
              }
              
              console.log(`处理第${index}项数据:`, safeItem)
              
              const assignmentId = `${safeItem.type}_${safeItem.subject}_${safeItem.details.task}`.replace(/\s+/g, '_')
              
              return {
                id: assignmentId,
                subject: safeItem.subject,
                title: safeItem.details.task,
                content: `${safeItem.subject} - ${safeItem.details.task}`,
                dueDate: safeItem.details.deadline,
                type: safeItem.type === 'homework' ? '作业' : '测试',
                completed: completedIds.has(assignmentId),
                completedAt: completedIds.has(assignmentId) ? new Date().toISOString() : null,
                url: safeItem.details.url,
                completing: false,
                undoing: false
              }
            }).filter(assignment => !assignment.subject.includes('英语'))
            
            console.log('转换后的前端数据:', assignments.value)
            filterAssignments()
          } else {
            console.error('数据格式错误:', result)
            error.value = result?.error || '获取作业数据失败 - 数据格式错误'
          }
        } else if (response.status === 401) {
          router.push('/login')
        } else {
          error.value = '获取作业数据失败'
        }
      } catch (err) {
        console.error('获取作业数据错误:', err)
        error.value = '网络连接错误'
      } finally {
        loading.value = false
      }
    }

    // 刷新作业数据
    const refreshAssignments = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/assignments/refresh', {
          method: 'POST',
          credentials: 'include'
        })
        
        if (response.ok) {
          await fetchAssignments()
          alert('作业数据刷新成功')
        } else {
          alert('刷新失败，请重试')
        }
      } catch (error) {
        console.error('刷新作业数据错误:', error)
        alert('网络错误，请检查连接')
      } finally {
        loading.value = false
      }
    }

    // 检查用户登录状态
    const checkUserStatus = async () => {
      try {
        const response = await fetch('/api/auth/status', {
          method: 'GET',
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.authenticated) {
            user.value = data.user
          } else {
            router.push('/login')
          }
        } else {
          router.push('/login')
        }
      } catch (error) {
        console.error('检查用户状态失败:', error)
        router.push('/login')
      }
    }

    // 登出功能
    const handleLogout = async () => {
      try {
        const response = await fetch('/api/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })
        
        if (response.ok) {
          // 清除本地存储
          localStorage.removeItem('user')
          sessionStorage.removeItem('user')
          
          // 跳转到登录页
          router.push('/login')
        } else {
          console.error('登出失败')
        }
      } catch (error) {
        console.error('登出错误:', error)
        // 即使API调用失败，也清除本地状态并跳转
        localStorage.removeItem('user')
        sessionStorage.removeItem('user')
        router.push('/login')
      }
    }

    // 初始化
    onMounted(async () => {
      // 检查用户登录状态
      await checkUserStatus()
      
      // 获取作业数据
      await fetchAssignments()
      
      updateTime()
      timeInterval = setInterval(updateTime, 1000)
      
      // 页面加载动画
      setTimeout(() => {
        isPageLoaded.value = true
      }, 100)
      
      // 定期更新状态和数据
      setInterval(() => {
        filterAssignments()
      }, 60000)
      
      // 每5分钟自动刷新一次数据
      setInterval(() => {
        fetchAssignments()
      }, 300000)
    })
    
    onUnmounted(() => {
      if (timeInterval) {
        clearInterval(timeInterval)
      }
    })

    return {
      currentTime,
      isPageLoaded,
      user,
      assignments,
      loading,
      error,
      searchTerm,
      subjectFilter,
      statusFilter,
      filteredAssignments,
      urgentCount,
      soonCount,
      totalCount,
      completedCount,
      subjects,
      assignmentStatus,
      statusIcon,
      formatDate,
      filterAssignments,
      openAssignmentUrl,
      setReminder,
      markCompleted,
      undoCompleted,
      handleLogout,
      fetchAssignments,
      refreshAssignments
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
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.header-content {
  text-align: left;
  flex: 1;
  z-index: 2;
  position: relative;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 2;
  position: relative;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 10px 18px;
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.current-time:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
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
  font-size: 2.2em;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header p {
  opacity: 0.95;
  font-size: 1em;
  position: relative;
  z-index: 2;
  text-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.settings-btn {
  color: white;
  text-decoration: none;
  font-size: 0.9em;
  padding: 12px 18px;
  border-radius: 25px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
}

.settings-btn i {
  font-size: 1em;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.settings-btn span {
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(255, 255, 255, 0.2);
}

.settings-btn:hover i {
  transform: rotate(90deg);
  color: #ffffff;
  text-shadow: 0 2px 15px rgba(255, 255, 255, 0.5);
}

.settings-btn:hover span {
  color: #ffffff;
  text-shadow: 0 2px 15px rgba(255, 255, 255, 0.5);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
}

.username {
  font-weight: 600;
  font-size: 0.95em;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-align: center;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.controls {
  padding: 30px 40px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.controls-row {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  min-width: 300px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 15px 20px 15px 50px;
  border: 2px solid #ddd;
  border-radius: 25px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.search-box i {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.filter-select {
  padding: 15px 20px;
  border: 2px solid #ddd;
  border-radius: 25px;
  font-size: 16px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 25px 20px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(102, 126, 234, 0.05));
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.stat-card i {
  font-size: 2.2em;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.stat-card.urgent i { 
  color: #e74c3c;
  text-shadow: 0 2px 10px rgba(231, 76, 60, 0.3);
}
.stat-card.soon i { 
  color: #f39c12;
  text-shadow: 0 2px 10px rgba(243, 156, 18, 0.3);
}
.stat-card.total i { 
  color: #667eea;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}
.stat-card.completed i { 
  color: #27ae60;
  text-shadow: 0 2px 10px rgba(39, 174, 96, 0.3);
}

.stat-card h3 {
  font-size: 2.2em;
  margin-bottom: 8px;
  color: #1f2937;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.stat-card p {
  color: #6b7280;
  font-weight: 500;
  font-size: 0.95em;
  position: relative;
  z-index: 1;
  margin: 0;
}

.main-content {
  padding: 40px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading-state i {
  font-size: 3em;
  margin-bottom: 20px;
  color: #667eea;
}

.error-state i {
  font-size: 3em;
  margin-bottom: 20px;
  color: #e74c3c;
}

.loading-state h3, .error-state h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.assignment-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  border-left: 5px solid #667eea;
  position: relative;
  overflow: hidden;
}

.assignment-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(102, 126, 234, 0.05));
  pointer-events: none;
}

.assignment-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.assignment-card.urgent {
  border-left-color: #e74c3c;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
  50% { box-shadow: 0 10px 30px rgba(231, 76, 60, 0.3); }
  100% { box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
}

.assignment-card.warning {
  border-left-color: #f39c12;
}

.assignment-card.completed {
  border-left-color: #27ae60;
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.subject-tag {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
}

.card-title {
  font-size: 1.3em;
  color: #2c3e50;
  margin-bottom: 10px;
  line-height: 1.4;
  position: relative;
  z-index: 1;
}

.card-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.due-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.due-date.urgent {
  color: #e74c3c;
}

.due-date.warning {
  color: #f39c12;
}

.due-date.normal {
  color: #27ae60;
}

.due-date-placeholder {
  /* 作业类型不显示时间时的占位样式 */
  height: 20px;
  display: flex;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}

.btn-success {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-success:hover {
  background: linear-gradient(135deg, #219a52, #27ae60);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4);
}

/* 完成按钮特殊样式 */
.complete-btn {
  position: relative;
  overflow: hidden;
}

.complete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 已完成状态样式 */
.completed-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-completed {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
  cursor: default;
  position: relative;
  overflow: hidden;
}

.btn-completed::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 8px 12px;
  min-width: auto;
}

.btn-secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6268, #3d4043);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.undo-btn {
  transition: all 0.3s ease;
}

.undo-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

/* 已完成卡片的特殊样式 */
.assignment-card.completed {
  position: relative;
  background: linear-gradient(135deg, rgba(39, 174, 96, 0.05), rgba(46, 204, 113, 0.05));
  border-left-color: #27ae60;
  opacity: 0.9;
}

.assignment-card.completed::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(39, 174, 96, 0.1));
  pointer-events: none;
}

.assignment-card.completed .card-title {
  color: #27ae60;
  text-decoration: line-through;
  text-decoration-color: rgba(39, 174, 96, 0.5);
}

.assignment-card.completed .card-content {
  color: #6c757d;
}

/* Toast 通知样式 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  z-index: 1000;
  transform: translateX(100%);
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.toast.show {
  transform: translateX(0);
  opacity: 1;
}

.toast-success {
  border-left: 4px solid #10b981;
}

.toast-error {
  border-left: 4px solid #ef4444;
}

.toast-warning {
  border-left: 4px solid #f59e0b;
}

.toast-info {
  border-left: 4px solid #3b82f6;
}

.toast-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-success .toast-icon {
  color: #10b981;
}

.toast-error .toast-icon {
  color: #ef4444;
}

.toast-warning .toast-icon {
  color: #f59e0b;
}

.toast-info .toast-icon {
  color: #3b82f6;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
  font-size: 14px;
}

.toast-message {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}



.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  color: white;
  grid-column: 1 / -1;
}

.empty-state i {
  font-size: 4.5em;
  margin-bottom: 25px;
  opacity: 0.6;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
}

.empty-state h3 {
  font-size: 1.6em;
  margin-bottom: 12px;
  font-weight: 600;
  text-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  opacity: 0.9;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .container::before,
  .container::after {
    display: none;
  }

  .header {
    margin: 15px;
    padding: 20px 25px;
    flex-direction: column;
    gap: 20px;
  }

  .header h1 {
    font-size: 1.8em;
  }

  .header p {
    font-size: 0.9em;
  }

  .header-actions {
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
  }

  .controls {
    margin: 0 15px 15px 15px;
    padding: 20px 25px;
  }

  .controls-row {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .search-box {
    min-width: auto;
  }

  .search-box input,
  .filter-select {
    padding: 12px 16px 12px 45px;
    font-size: 14px;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }

  .stat-card {
    padding: 20px 15px;
  }

  .stat-card h3 {
    font-size: 1.8em;
  }

  .main-content {
    padding: 15px 30px 30px 30px;
  }

  .assignments-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .assignment-card {
    padding: 22px;
  }

  .floating-add {
    bottom: 20px;
    right: 20px;
    width: 55px;
    height: 55px;
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .header,
  .controls {
    margin: 10px;
    padding: 15px 20px;
  }

  .main-content {
    padding: 10px 25px 25px 25px;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .assignment-card {
    padding: 18px;
  }

  .card-footer {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .actions {
    justify-content: center;
  }
}
</style>