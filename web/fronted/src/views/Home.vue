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
        <div class="stat-card todos">
          <i class="fas fa-list-check"></i>
          <h3>{{ todoCount }}</h3>
          <p>待办事项</p>
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
          :data-type="assignment.type"
          @click="openAssignmentUrl(assignment)"
          style="cursor: pointer;"
        >
          <!-- 优先级指示器 (仅待办显示) -->
          <div 
            v-if="assignment.type === '待办' && assignment.priority" 
            :class="['priority-indicator', assignment.priority]"
          ></div>
          <div class="card-header">
            <span class="subject-tag">{{ assignment.subject }}</span>
            <small>{{ assignment.type }}</small>
          </div>
          <h3 class="card-title">{{ assignment.title }}</h3>
          <p class="card-content">{{ assignment.content }}</p>
          <div class="card-footer">
            <div v-if="assignment.dueDate && assignment.type !== '作业'" :class="['due-date', assignmentStatus(assignment)]">
              <i :class="statusIcon(assignment)"></i>
              <span v-html="formatDate(assignment.dueDate, assignment.type, assignment.estimatedHours)"></span>
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
              <!-- 待办事项的删除按钮 - 无论是否完成都显示 -->
              <button 
                v-if="assignment.type === '待办' && !assignment.completed"
                class="btn btn-danger delete-btn"
                @click="deleteTodo(assignment)"
                title="删除待办"
              >
                <i class="fas fa-trash"></i>
              </button>
              <div v-else-if="assignment.completed" class="completed-actions">
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
                <button 
                  v-if="assignment.type === '待办'"
                  class="btn btn-danger delete-btn"
                  @click="deleteTodo(assignment)"
                  title="删除待办"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加待办按钮 -->
    <button class="floating-add" @click="showAddTodoModal = true" title="添加待办">
      <i class="fas fa-plus"></i>
    </button>

    <!-- 添加待办弹窗 -->
    <div v-if="showAddTodoModal" class="modal-overlay" @click="closeAddTodoModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-plus-circle"></i> 添加待办事项</h3>
          <button class="close-btn" @click="closeAddTodoModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="todoTitle">名称 *</label>
            <input 
              id="todoTitle"
              type="text" 
              v-model="newTodo.title" 
              placeholder="请输入待办事项名称"
              maxlength="100"
              @keyup.enter="addTodo"
            >
          </div>
          <div class="form-group">
            <label for="todoHours">预计时间</label>
            <div class="hours-input-group">
              <input 
                id="todoHours"
                type="number" 
                v-model="newTodo.hours"
                placeholder="1"
                min="0.5"
                max="168"
                step="0.5"
              >
              <span class="hours-suffix">小时后</span>
            </div>
          </div>
          <div class="form-group">
            <label for="todoDescription">备注</label>
            <textarea 
              id="todoDescription"
              v-model="newTodo.description" 
              placeholder="请输入备注信息（可选）"
              rows="3"
              maxlength="500"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="todoPriority">优先级</label>
            <select id="todoPriority" v-model="newTodo.priority">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeAddTodoModal">取消</button>
          <button 
            class="btn btn-primary" 
            @click="addTodo"
            :disabled="!newTodo.title.trim() || addingTodo"
          >
            <span v-if="!addingTodo">
              <i class="fas fa-plus"></i> 添加
            </span>
            <span v-else>
              <i class="fas fa-spinner fa-spin"></i> 添加中...
            </span>
          </button>
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
      // 确保使用中国时区 (UTC+8)
      currentTime.value = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: 'Asia/Beijing'
      })
    }
    
    // 添加一些动画效果的状态
    const isPageLoaded = ref(false)
    
    // 动态数据
    const assignments = ref([])
    const todos = ref([])
    const loading = ref(false)
    const error = ref('')

    const searchTerm = ref('')
    const subjectFilter = ref('')
    const statusFilter = ref('')
    const filteredAssignments = ref([])

    // 待办相关状态
    const showAddTodoModal = ref(false)
    const addingTodo = ref(false)
    const newTodo = ref({
      title: '',
      description: '',
      hours: 1,
      priority: 'medium'
    })

    // 计算统计信息 - 包含作业和待办
    const allItems = computed(() => {
      const items = []
      
      // 添加作业数据
      if (assignments.value && Array.isArray(assignments.value)) {
        items.push(...assignments.value)
      }
      
      // 添加待办数据，转换为统一格式
      if (todos.value && Array.isArray(todos.value)) {
        const todoItems = todos.value.map(todo => ({
          id: `todo_${todo._id}`,
          subject: '待办事项',
          title: todo.title,
          content: todo.description || '无备注',
          dueDate: todo.due_date,
          type: '待办',
          completed: todo.completed,
          priority: todo.priority,
          estimatedHours: todo.estimated_hours, // 添加预计小时数
          _todoId: todo._id
        }))
        items.push(...todoItems)
      }
      
      return items
    })

    const urgentCount = computed(() => 
      allItems.value.filter(a => assignmentStatus(a) === 'urgent').length
    )

    const soonCount = computed(() => 
      allItems.value.filter(a => assignmentStatus(a) === 'warning').length
    )

    const totalCount = computed(() => allItems.value.length)

    const completedCount = computed(() => 
      allItems.value.filter(a => a.completed).length
    )

    const todoCount = computed(() => 
      todos.value.filter(t => !t.completed).length
    )

    const subjects = computed(() => {
      const uniqueSubjects = new Set(allItems.value.map(a => a.subject))
      return Array.from(uniqueSubjects)
    })

    // 计算剩余天数
    // 获取当前时间（用于比较）
    const getCurrentTime = () => {
      return new Date()
    }

    const getDaysUntilDue = (dueDate) => {
      try {
        if (!dueDate) {
          return Infinity
        }
        
        const now = getCurrentTime()
        
        // 如果时间字符串没有时区信息，假设是北京时间
        let due
        if (dueDate.includes('T') && !dueDate.includes('+') && !dueDate.includes('Z')) {
          // 没有时区信息的ISO字符串，假设是北京时间
          due = new Date(dueDate + '+08:00')
        } else {
          due = new Date(dueDate)
        }
        
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

    // 格式化日期 - 待办显示预计时间和剩余时间
    const formatDate = (dateString, itemType, estimatedHours) => {
      if (!dateString) return ''
      
      // 如果时间字符串没有时区信息，假设是北京时间
      let date
      if (dateString.includes('T') && !dateString.includes('+') && !dateString.includes('Z')) {
        // 没有时区信息的ISO字符串，假设是北京时间
        date = new Date(dateString + '+08:00')
      } else {
        date = new Date(dateString)
      }
      
      // 使用当前时间进行计算
      const now = getCurrentTime()
      const diffMs = date.getTime() - now.getTime()
      
      // 如果是待办事项，显示预计时间和剩余时间
      if (itemType === '待办') {
        let timeInfo = ''
        
        // 显示预计时间
        if (estimatedHours) {
          if (estimatedHours >= 24) {
            const days = Math.floor(estimatedHours / 24)
            const hours = estimatedHours % 24
            timeInfo = `预计 ${days}天${hours > 0 ? hours + '小时' : ''}<br>`
          } else {
            timeInfo = `预计 ${estimatedHours}小时<br>`
          }
        }
        
        // 显示剩余时间
        if (diffMs < 0) {
          // 已超时
          const overdueDays = Math.floor(Math.abs(diffMs) / (1000 * 60 * 60 * 24))
          const overdueHours = Math.floor(Math.abs(diffMs) / (1000 * 60 * 60)) % 24
          
          if (overdueDays > 0) {
            timeInfo += `已超时 ${overdueDays}天${overdueHours > 0 ? overdueHours + '小时' : ''}`
          } else {
            timeInfo += `已超时 ${overdueHours}小时`
          }
        } else {
          // 剩余时间
          const remainingDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
          const remainingHours = Math.floor(diffMs / (1000 * 60 * 60)) % 24
          const remainingMinutes = Math.floor(diffMs / (1000 * 60)) % 60
          
          if (remainingDays > 0) {
            timeInfo += `剩余 ${remainingDays}天${remainingHours > 0 ? remainingHours + '小时' : ''}`
          } else if (remainingHours > 0) {
            timeInfo += `剩余 ${remainingHours}小时${remainingMinutes > 0 ? remainingMinutes + '分钟' : ''}`
          } else {
            timeInfo += `剩余 ${remainingMinutes}分钟`
          }
        }
        
        return timeInfo
      }
      
      // 作业显示原有格式
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

    // 筛选作业和待办
    const filterAssignments = () => {
      console.log('开始筛选作业和待办，原始数据:', assignments.value, todos.value)
      
      // 使用计算属性中的合并数据
      const items = allItems.value.map(item => ({
        ...item,
        publisher: item.publisher || (item.type === '待办' ? '用户' : '系统'),
        url: item.url || '',
        completing: item.completing || false,
        undoing: item.undoing || false
      }))
      
      if (!items || !Array.isArray(items)) {
        console.warn('合并后的数据不是有效数组:', items)
        filteredAssignments.value = []
        return
      }
      
      filteredAssignments.value = items.filter(item => {
        // 安全检查
        if (!item) {
          console.warn('发现空的 item 项')
          return false
        }
        
        const title = item.title || ''
        const subject = item.subject || ''
        const searchTerm_lower = (searchTerm.value || '').toLowerCase()
        
        const matchesSearch = title.toLowerCase().includes(searchTerm_lower) ||
                            subject.toLowerCase().includes(searchTerm_lower)
        const matchesSubject = !subjectFilter.value || subject === subjectFilter.value
        const matchesStatus = !statusFilter.value || assignmentStatus(item) === statusFilter.value
        
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
    const setReminder = async (assignment) => {
      try {
        console.log('设置提醒 - assignment:', assignment)
        let response
        
        if (assignment.type === '待办') {
          // 待办提醒API
          const url = `/api/todos/${assignment._todoId}/remind`
          console.log('调用待办提醒API:', url)
          response = await fetch(url, {
            method: 'POST',
            credentials: 'include'
          })
        } else {
          // 作业/测试提醒API
          const url = `/api/assignments/${assignment.id}/remind`
          console.log('调用作业提醒API:', url, '类型:', assignment.type)
          response = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              title: assignment.title,
              subject: assignment.subject,
              deadline: assignment.dueDate
            })
          })
        }
        
        console.log('提醒API响应状态:', response.status)
        
        if (response.ok) {
          const result = await response.json()
          console.log('提醒成功:', result)
          showToast('success', '提醒设置', result.message || '提醒设置成功')
        } else {
          const errorText = await response.text()
          console.error('提醒失败 - 状态码:', response.status, '响应:', errorText)
          let errorData
          try {
            errorData = JSON.parse(errorText)
          } catch (e) {
            errorData = { error: errorText }
          }
          showToast('error', '提醒失败', errorData.error || `HTTP ${response.status}: 设置提醒失败`)
        }
      } catch (error) {
        console.error('提醒错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      }
    }

    // 删除待办
    const deleteTodo = async (assignment) => {
      if (assignment.type !== '待办') return
      
      if (!confirm(`确定要删除待办事项"${assignment.title}"吗？`)) {
        return
      }
      
      try {
        const response = await fetch(`/api/todos/${assignment._todoId}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        
        if (response.ok) {
          const result = await response.json()
          
          // 从待办列表中移除
          await fetchTodos()
          filterAssignments()
          
          showToast('success', '删除成功', `待办事项"${assignment.title}"已删除`)
          console.log('删除待办成功:', result)
        } else {
          const errorData = await response.json()
          console.error('删除待办失败:', errorData)
          showToast('error', '删除失败', errorData.error || '删除待办失败，请重试')
        }
      } catch (error) {
        console.error('删除待办错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      }
    }

    // 标记完成
    const markCompleted = async (assignment) => {
      if (assignment.completing) return
      
      console.log('标记完成 - assignment:', assignment)
      assignment.completing = true
      
      try {
        let response
        
        // 判断是作业还是待办
        if (assignment.type === '待办') {
          const url = `/api/todos/${assignment._todoId}/complete`
          console.log('调用待办完成API:', url)
          response = await fetch(url, {
            method: 'POST',
            credentials: 'include'
          })
        } else {
          const url = `/api/assignments/${assignment.id}/complete`
          console.log('调用作业完成API:', url, '类型:', assignment.type, 'ID:', assignment.id)
          response = await fetch(url, {
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
        }
        
        console.log('完成API响应状态:', response.status)
        
        if (response.ok) {
          const result = await response.json()
          console.log('标记完成成功:', result)
          
          // 更新本地状态
          if (assignment.type === '待办') {
            // 如果是待办，重新获取待办列表
            await fetchTodos()
          } else {
            // 如果是作业，更新作业数组中对应的项目
            const assignmentIndex = assignments.value.findIndex(a => a.id === assignment.id)
            if (assignmentIndex !== -1) {
              assignments.value[assignmentIndex].completed = true
              assignments.value[assignmentIndex].completedAt = new Date().toISOString()
            }
            // 同时更新传入的assignment对象以立即反映UI变化
            assignment.completed = true
            assignment.completedAt = new Date().toISOString()
          }
          
          filterAssignments()
          
          // 显示成功提示
          const message = assignment.type === '待办' ? 
            `${assignment.title} 已完成` : 
            `${assignment.title} 已标记为完成，12小时后自动清除`
          showToast('success', '任务完成', message)
        } else {
          const errorText = await response.text()
          console.error('标记完成失败 - 状态码:', response.status, '响应:', errorText)
          let errorData
          try {
            errorData = JSON.parse(errorText)
          } catch (e) {
            errorData = { error: errorText }
          }
          showToast('error', '操作失败', errorData.error || `HTTP ${response.status}: 标记完成失败`)
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
        let response
        
        // 判断是作业还是待办
        if (assignment.type === '待办') {
          response = await fetch(`/api/todos/${assignment._todoId}/uncomplete`, {
            method: 'POST',
            credentials: 'include'
          })
        } else {
          response = await fetch(`/api/assignments/${assignment.id}/uncomplete`, {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json'
            }
          })
        }
        
        if (response.ok) {
          const result = await response.json()
          
          // 更新本地状态
          if (assignment.type === '待办') {
            // 如果是待办，重新获取待办列表
            await fetchTodos()
          } else {
            // 如果是作业，更新作业数组中对应的项目
            const assignmentIndex = assignments.value.findIndex(a => a.id === assignment.id)
            if (assignmentIndex !== -1) {
              assignments.value[assignmentIndex].completed = false
              assignments.value[assignmentIndex].completedAt = null
            }
            // 同时更新传入的assignment对象以立即反映UI变化
            assignment.completed = false
            assignment.completedAt = null
          }
          
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
        // 并行获取作业和待办数据
        const [assignmentsResponse, todosResponse] = await Promise.all([
          fetch('/api/assignments/standard', {
            method: 'GET',
            credentials: 'include'
          }),
          fetch('/api/todos/', {
            method: 'GET',
            credentials: 'include'
          })
        ])
        
        // 处理作业数据
        if (assignmentsResponse.ok) {
          const result = await assignmentsResponse.json()
          console.log('后端返回的作业数据:', result)
          
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
              
              // 使用与后端相同的ID生成逻辑 - 简单哈希函数
              const hashInput = safeItem.subject + safeItem.details.task
              let hash = 0
              for (let i = 0; i < hashInput.length; i++) {
                const char = hashInput.charCodeAt(i)
                hash = ((hash << 5) - hash) + char
                hash = hash & hash // 转换为32位整数
              }
              const assignmentId = `${safeItem.type}_${Math.abs(hash)}`
              
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
            
            console.log('转换后的作业数据:', assignments.value)
          } else {
            console.error('作业数据格式错误:', result)
          }
        } else if (assignmentsResponse.status === 401) {
          router.push('/login')
          return
        }

        // 处理待办数据
        if (todosResponse.ok) {
          const todosResult = await todosResponse.json()
          console.log('后端返回的待办数据:', todosResult)
          
          if (todosResult.success && todosResult.todos) {
            todos.value = todosResult.todos
            console.log('获取待办数据成功:', todos.value)
          } else {
            console.warn('待办数据格式错误:', todosResult)
            todos.value = []
          }
        } else {
          console.warn('获取待办数据失败')
          todos.value = []
        }

        filterAssignments()
        
      } catch (err) {
        console.error('获取数据错误:', err)
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

    // 待办相关方法
    const closeAddTodoModal = () => {
      showAddTodoModal.value = false
      newTodo.value = {
        title: '',
        description: '',
        hours: 1,
        priority: 'medium'
      }
    }

    const addTodo = async () => {
      if (!newTodo.value.title.trim()) {
        showToast('warning', '提示', '请输入待办事项名称')
        return
      }

      addingTodo.value = true

      try {
        // 发送小时数给后端，让后端计算截止时间
        const todoData = {
          title: newTodo.value.title.trim(),
          description: newTodo.value.description && newTodo.value.description.trim() ? newTodo.value.description.trim() : null,
          priority: newTodo.value.priority,
          hours: newTodo.value.hours && newTodo.value.hours > 0 ? newTodo.value.hours : null
        }

        const response = await fetch('/api/todos/', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(todoData)
        })

        if (response.ok) {
          const result = await response.json()
          console.log('添加待办成功:', result)
          
          showToast('success', '成功', '待办事项添加成功')
          closeAddTodoModal()
          
          // 重新获取待办列表
          await fetchTodos()
          filterAssignments()
        } else {
          const errorData = await response.json()
          console.error('添加待办失败:', errorData)
          showToast('error', '添加失败', errorData.error || '请重试')
        }
      } catch (error) {
        console.error('添加待办错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      } finally {
        addingTodo.value = false
      }
    }

    const fetchTodos = async () => {
      try {
        const response = await fetch('/api/todos/?include_completed=true', {
          method: 'GET',
          credentials: 'include'
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success && result.todos) {
            todos.value = result.todos
            console.log('获取待办列表成功:', todos.value)
          }
        } else {
          console.warn('获取待办列表失败')
        }
      } catch (error) {
        console.error('获取待办列表错误:', error)
      }
    }

    const completeTodo = async (todoId) => {
      try {
        const response = await fetch(`/api/todos/${todoId}/complete`, {
          method: 'POST',
          credentials: 'include'
        })

        if (response.ok) {
          showToast('success', '完成', '待办事项已完成')
          await fetchTodos()
          filterAssignments()
        } else {
          const errorData = await response.json()
          showToast('error', '操作失败', errorData.error || '请重试')
        }
      } catch (error) {
        console.error('完成待办错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      }
    }

    const uncompleteTodo = async (todoId) => {
      try {
        const response = await fetch(`/api/todos/${todoId}/uncomplete`, {
          method: 'POST',
          credentials: 'include'
        })

        if (response.ok) {
          showToast('info', '已撤销', '待办事项已撤销完成状态')
          await fetchTodos()
          filterAssignments()
        } else {
          const errorData = await response.json()
          showToast('error', '操作失败', errorData.error || '请重试')
        }
      } catch (error) {
        console.error('撤销待办错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
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
      todos,
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
      todoCount,
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
      refreshAssignments,
      showAddTodoModal,
      addingTodo,
      newTodo,
      closeAddTodoModal,
      addTodo,
      fetchTodos,
      completeTodo,
      uncompleteTodo,
      deleteTodo
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
.stat-card.todos i { 
  color: #9b59b6;
  text-shadow: 0 2px 10px rgba(155, 89, 182, 0.3);
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

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9em;
  transition: all 0.3s ease;
  min-width: auto;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c82333, #a71e2a);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
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
  background: linear-gradient(135deg, rgba(39, 174, 96, 0.1), rgba(46, 204, 113, 0.1));
  border-left-color: #27ae60 !important;
  border-left-width: 6px !important;
  opacity: 0.85;
  transform: scale(0.98);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.2) !important;
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
  color: #27ae60 !important;
  text-decoration: line-through;
  text-decoration-color: #27ae60;
  text-decoration-thickness: 2px;
  opacity: 0.8;
  font-weight: 500;
}

.assignment-card.completed .card-content {
  color: #6c757d;
}

/* 浮动添加按钮 */
.floating-add {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-add:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}

.floating-add:active {
  transform: translateY(-1px) scale(0.98);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 25px 30px 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h3 i {
  color: #667eea;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2em;
  color: #6c757d;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #495057;
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.95em;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: #f8f9fa;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.hours-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hours-input-group input {
  flex: 1;
  min-width: 0;
}

.hours-suffix {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  padding: 0 4px;
}

.modal-footer {
  padding: 20px 30px 25px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-footer .btn {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  min-width: 100px;
}

/* 待办卡片特殊样式 */
.assignment-card[data-type="待办"] {
  border-left-color: #9b59b6;
  background: white;
}

.assignment-card[data-type="待办"] .card-title {
  color: #2c3e50;
  font-weight: 600;
}

.assignment-card[data-type="待办"] .card-content {
  color: #4a5568;
}

.assignment-card[data-type="待办"] .subject-tag {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
  font-weight: 500;
}

.assignment-card[data-type="待办"] .subject-tag {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
}

.assignment-card[data-type="待办"]:hover {
  box-shadow: 0 20px 40px rgba(155, 89, 182, 0.15);
}

/* 待办事项完成时的样式 - 覆盖默认完成样式 */
.assignment-card[data-type="待办"].completed {
  background: linear-gradient(135deg, rgba(39, 174, 96, 0.05), rgba(46, 204, 113, 0.05));
  border-left-color: #27ae60;
  opacity: 0.9;
}

.assignment-card[data-type="待办"].completed .card-title {
  color: #27ae60;
  text-decoration: line-through;
  text-decoration-color: rgba(39, 174, 96, 0.5);
}

.assignment-card[data-type="待办"].completed .card-content {
  color: #6c757d;
}

/* 优先级指示器 */
.priority-indicator {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  z-index: 1;
}

.priority-indicator.high {
  background: #e74c3c;
  box-shadow: 0 0 10px rgba(231, 76, 60, 0.5);
}

.priority-indicator.medium {
  background: #f39c12;
  box-shadow: 0 0 10px rgba(243, 156, 18, 0.5);
}

.priority-indicator.low {
  background: #27ae60;
  box-shadow: 0 0 10px rgba(39, 174, 96, 0.5);
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