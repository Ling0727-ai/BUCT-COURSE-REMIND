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
                class="btn btn-success"
                @click="markCompleted(assignment)"
              >
                <i class="fas fa-check"></i> 完成
              </button>
              <button 
                v-else
                class="btn btn-success"
              >
                <i class="fas fa-check"></i> 已完成
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button class="floating-add" @click="refreshAssignments" title="刷新作业数据">
      <i class="fas fa-sync-alt"></i>
    </button>
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
      try {
        const response = await fetch(`http://localhost:5000/api/assignments/${assignment.id}/complete`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          assignment.completed = true
          filterAssignments()
          console.log('作业标记完成成功')
        } else {
          console.error('标记完成失败')
          alert('标记完成失败，请重试')
        }
      } catch (error) {
        console.error('标记完成错误:', error)
        alert('网络错误，请检查连接')
      }
    }

    // 获取作业数据
    const fetchAssignments = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await fetch('http://localhost:5000/api/assignments/standard', {
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
              
              return {
                id: `${safeItem.type}_${index}_${Date.now()}`, // 生成更唯一的ID
                subject: safeItem.subject,
                title: safeItem.details.task,
                content: `${safeItem.subject} - ${safeItem.details.task}`,
                dueDate: safeItem.details.deadline,
                type: safeItem.type === 'homework' ? '作业' : '测试',
                completed: false,
                url: safeItem.details.url
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
        const response = await fetch('http://localhost:5000/api/assignments/refresh', {
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
        const response = await fetch('http://localhost:5000/api/auth/status', {
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
        const response = await fetch('http://localhost:5000/api/auth/logout', {
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
      handleLogout,
      fetchAssignments,
      refreshAssignments
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 30px 40px;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-content {
  text-align: left;
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  opacity: 0.9;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 15px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.current-time:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  position: relative;
  z-index: 1;
}

.header p {
  opacity: 0.9;
  font-size: 1.1em;
  position: relative;
  z-index: 1;
}

.settings-btn {
  color: white;
  text-decoration: none;
  font-size: 1.5em;
  padding: 0px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  position: relative;
  z-index: 1;
}

.settings-btn::before {
  content: '';
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  z-index: -1;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(45deg);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
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
  gap: 6px;
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
  background: white;
  padding: 20px;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card i {
  font-size: 2em;
  margin-bottom: 10px;
}

.stat-card.urgent i { color: #e74c3c; }
.stat-card.soon i { color: #f39c12; }
.stat-card.total i { color: #3498db; }
.stat-card.completed i { color: #27ae60; }

.stat-card h3 {
  font-size: 2em;
  margin-bottom: 5px;
  color: #2c3e50;
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
  gap: 5px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover {
  background: #219a52;
  transform: translateY(-2px);
}

.floating-add {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.floating-add:hover {
  transform: scale(1.1) rotate(180deg);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  grid-column: 1 / -1;
}

.empty-state i {
  font-size: 4em;
  margin-bottom: 20px;
  opacity: 0.3;
}

.empty-state h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .header {
    padding: 20px;
    flex-direction: column;
    gap: 20px;
  }

  .header h1 {
    font-size: 2em;
  }

  .controls {
    padding: 20px;
  }

  .controls-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    min-width: auto;
  }

  .main-content {
    padding: 20px;
  }

  .assignments-grid {
    grid-template-columns: 1fr;
  }

  .floating-add {
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    font-size: 18px;
  }
}
</style>