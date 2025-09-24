<template>
  <div class="container">
    <!-- 头部组件 -->
    <Header 
      :current-time="currentTime"
      :user="user"
      @show-recycle-bin="showRecycleBin"
      @logout="handleLogout"
    />

    <!-- 控制面板组件 -->
    <Controls
      v-model:search-term="searchTerm"
      v-model:subject-filter="subjectFilter"
      v-model:status-filter="statusFilter"
      :subjects="subjects"
      :urgent-count="urgentCount"
      :soon-count="soonCount"
      :total-count="totalCount"
      :completed-count="completedCount"
      :todo-count="todoCount"
      @show-stat-modal="showStatModal"
    />

    <!-- 作业网格组件 -->
    <AssignmentGrid
      :assignments="filteredAssignments"
      :loading="loading"
      :error="error"
      @refresh="fetchAssignments"
      @open-url="openAssignmentUrl"
      @show-preview="showPreview"
      @set-reminder="setReminder"
      @delete-assignment="deleteAssignment"
      @mark-completed="markCompleted"
      @undo-completed="undoCompleted"
    />

    <!-- 浮动添加按钮 -->
    <FloatingAddButton @show-add-todo="showAddTodoModal = true" />

    <!-- 添加待办弹窗 -->
    <AddTodoModal
      :show="showAddTodoModal"
      v-model:todo="newTodo"
      :adding="addingTodo"
      @close="closeAddTodoModal"
      @add="addTodo"
    />

    <!-- 预览详情弹窗 -->
    <PreviewModal
      :show="showPreviewModal"
      :item="previewItem"
      @close="closePreviewModal"
      @open-url="openAssignmentUrl"
    />

    <!-- 自定义确认对话框 -->
    <ConfirmModal
      :show="showConfirmModal"
      :message="confirmMessage"
      @confirm="confirmAction"
      @cancel="cancelConfirm"
    />

    <!-- 统计详情弹窗 -->
    <StatisticsModal
      :show="showStatisticsModal"
      :type="currentStatType"
      :items="filteredStatItems"
      @close="closeStatModal"
      @open-url="openAssignmentUrl"
      @show-preview="showPreview"
      @set-reminder="setReminder"
      @delete-assignment="deleteAssignment"
      @mark-completed="markCompleted"
      @undo-completed="undoCompleted"
    />

    <!-- 回收站弹窗 -->
    <RecycleBinModal
      :show="showRecycleBinModal"
      :items="deletedItems"
      @close="closeRecycleBin"
      @restore-item="restoreItem"
      @permanent-delete="permanentDelete"
      @clear-recycle-bin="clearRecycleBin"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from './home/composables/useToast'

// 导入组件
import Header from './home/Header.vue'
import Controls from './home/Controls.vue'
import AssignmentGrid from './home/AssignmentGrid.vue'
import FloatingAddButton from './home/FloatingAddButton.vue'

// 导入弹窗组件
import AddTodoModal from './home/modals/AddTodoModal.vue'
import PreviewModal from './home/modals/PreviewModal.vue'
import ConfirmModal from './home/modals/ConfirmModal.vue'
import StatisticsModal from './home/modals/StatisticsModal.vue'
import RecycleBinModal from './home/modals/RecycleBinModal.vue'

export default {
  name: 'Home',
  components: {
    Header,
    Controls,
    AssignmentGrid,
    FloatingAddButton,
    AddTodoModal,
    PreviewModal,
    ConfirmModal,
    StatisticsModal,
    RecycleBinModal
  },
  setup() {
    const router = useRouter()
    const { showToast } = useToast()
    
    // 用户状态
    const user = ref(null)
    // 实时时间
    const currentTime = ref('')
    let timeInterval
    
    const updateTime = () => {
      const now = new Date()
      // 只显示时间部分，精确到秒
      currentTime.value = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: 'Asia/Shanghai'
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

    // 预览相关状态
    const showPreviewModal = ref(false)
    const previewItem = ref(null)

    // 确认对话框相关状态
    const showConfirmModal = ref(false)
    const confirmMessage = ref('')
    const confirmCallback = ref(null)

    // 统计弹窗相关状态
    const showStatisticsModal = ref(false)
    const currentStatType = ref('')
    const filteredStatItems = ref([])

    // 回收站相关状态
    const showRecycleBinModal = ref(false)
    const deletedItems = ref([])

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

    // 监听筛选条件变化
    const watchFilters = () => {
      filterAssignments()
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
      
      const performDelete = async () => {
        try {
          const response = await fetch(`/api/todos/${assignment._todoId}/delete`, {
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
            
            // 重新获取待办列表（已删除的项目会被过滤掉）
            await fetchTodos()
            filterAssignments()
            
            showToast('success', '移至回收站', `待办事项"${assignment.title}"已移至回收站`)
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
      
      showCustomConfirm(
        `确定要删除待办事项"${assignment.title}"吗？\n\n项目将移至回收站，可以恢复。`, 
        performDelete
      )
    }

    // 删除作业或待办的统一方法
    const deleteAssignment = async (assignment) => {
      if (assignment.type === '待办') {
        // 调用原有的删除待办方法
        await deleteTodo(assignment)
        return
      }
      
      // 处理作业删除
      const itemType = assignment.type === '作业' ? '作业' : '测试'
      const performDelete = async () => {
        try {
          const response = await fetch(`/api/assignments/${assignment.id}/delete`, {
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
            
            // 从本地列表中移除（已删除的项目不再显示在主列表中）
            const assignmentIndex = assignments.value.findIndex(a => a.id === assignment.id)
            if (assignmentIndex !== -1) {
              assignments.value.splice(assignmentIndex, 1)
              filterAssignments()
              showToast('success', '移至回收站', `${itemType}"${assignment.title}"已移至回收站`)
            }
            
            console.log('删除作业成功:', result)
          } else {
            const errorData = await response.json()
            console.error('删除作业失败:', errorData)
            showToast('error', '删除失败', errorData.error || '删除作业失败，请重试')
          }
        } catch (error) {
          console.error('删除作业错误:', error)
          showToast('error', '网络错误', '请检查网络连接后重试')
        }
      }
      
      showCustomConfirm(
        `确定要删除${itemType}"${assignment.title}"吗？\n\n项目将移至回收站，可以恢复。`, 
        performDelete
      )
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
          
          // 适配新的后端数据结构
          let dataArray = []
          if (result.success && result.tasks && Array.isArray(result.tasks)) {
            dataArray = result.tasks
          } else if (result.tasks && Array.isArray(result.tasks)) {
            dataArray = result.tasks
          }
          
          if (dataArray.length > 0) {
            // 获取数据库中的已完成状态和已删除状态
            let completedIds = new Set()
            let deletedIds = new Set()
            
            try {
              // 并行获取已完成和已删除列表
              const [completedResponse, deletedResponse] = await Promise.all([
                fetch('/api/assignments/completed', {
                  method: 'GET',
                  credentials: 'include'
                }),
                fetch('/api/assignments/deleted', {
                  method: 'GET',
                  credentials: 'include'
                })
              ])
              
              if (completedResponse.ok) {
                const completedData = await completedResponse.json()
                completedIds = new Set(completedData.completed_assignments || [])
                console.log('获取已完成作业列表成功:', completedData.completed_assignments)
              } else {
                console.warn('获取已完成作业列表失败，使用空列表')
              }
              
              if (deletedResponse.ok) {
                const deletedData = await deletedResponse.json()
                deletedIds = new Set((deletedData.deleted_assignments || []).map(item => item.assignment_id))
                console.log('获取已删除作业列表成功:', deletedIds)
              } else {
                console.warn('获取已删除作业列表失败，使用空列表')
              }
            } catch (error) {
              console.error('获取作业状态列表错误:', error)
            }
            
            assignments.value = dataArray.map((item, index) => {
              console.log(`处理第${index}项数据:`, item)
              
              // 直接使用后端返回的数据结构
              const assignmentId = item.id
              const taskTitle = item.details?.task || item.title || '未知任务'
              const detailsContent = item.details?.details_content || ''
              
              return {
                id: assignmentId,
                subject: item.subject || '未知科目',
                title: taskTitle,
                content: detailsContent || `${item.subject} - ${taskTitle}`,
                dueDate: item.details?.deadline || null,
                type: item.type === 'homework' ? '作业' : '测试',
                completed: item.completed || completedIds.has(assignmentId),
                completedAt: item.completed ? new Date().toISOString() : null,
                url: item.details?.url || '',
                completing: false,
                undoing: false,
                details: detailsContent // 添加详情内容字段
              }
            }).filter(assignment => 
              // !assignment.subject.includes('') &&    //过滤掉特殊字段
              !deletedIds.has(assignment.id) // 过滤掉已删除的作业
            ).sort((a, b) => {
              // 已完成的任务置底
              if (a.completed && !b.completed) return 1
              if (!a.completed && b.completed) return -1
              // 如果都是已完成或都是未完成，按截止时间排序
              if (a.dueDate && b.dueDate) {
                return new Date(a.dueDate) - new Date(b.dueDate)
              }
              if (a.dueDate && !b.dueDate) return -1
              if (!a.dueDate && b.dueDate) return 1
              return 0
            })
            
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

    // 预览功能相关方法
    const showPreview = (assignment) => {
      previewItem.value = assignment
      showPreviewModal.value = true
    }

    const closePreviewModal = () => {
      showPreviewModal.value = false
      previewItem.value = null
    }

    // 自定义确认对话框方法
    const showCustomConfirm = (message, callback) => {
      confirmMessage.value = message
      confirmCallback.value = callback
      showConfirmModal.value = true
    }

    const confirmAction = () => {
      if (confirmCallback.value) {
        confirmCallback.value()
      }
      showConfirmModal.value = false
      confirmCallback.value = null
    }

    const cancelConfirm = () => {
      showConfirmModal.value = false
      confirmCallback.value = null
    }

    // 统计弹窗相关方法
    const showStatModal = (type) => {
      currentStatType.value = type
      filteredStatItems.value = getStatItems(type)
      showStatisticsModal.value = true
    }

    const closeStatModal = () => {
      showStatisticsModal.value = false
      currentStatType.value = ''
      filteredStatItems.value = []
    }

    const getStatItems = (type) => {
      const items = allItems.value
      
      switch (type) {
        case 'urgent':
          return items.filter(item => assignmentStatus(item) === 'urgent')
        case 'warning':
          return items.filter(item => assignmentStatus(item) === 'warning')
        case 'completed':
          return items.filter(item => item.completed)
        case 'todos':
          return items.filter(item => item.type === '待办' && !item.completed)
        case 'all':
        default:
          return items
      }
    }

    // 回收站相关方法
    const showRecycleBin = async () => {
      // 获取已删除的项目
      await fetchDeletedItems()
      showRecycleBinModal.value = true
    }

    const closeRecycleBin = () => {
      showRecycleBinModal.value = false
    }

    // 获取已删除的项目
    const fetchDeletedItems = async () => {
      try {
        // 并行获取已删除的作业和待办
        const [assignmentsResponse, todosResponse] = await Promise.all([
          fetch('/api/assignments/deleted', {
            method: 'GET',
            credentials: 'include'
          }),
          fetch('/api/todos/deleted', {
            method: 'GET',
            credentials: 'include'
          })
        ])
        
        const deletedAssignments = []
        const deletedTodos = []
        
        // 处理已删除的作业
        if (assignmentsResponse.ok) {
          const result = await assignmentsResponse.json()
          if (result.success && result.deleted_assignments) {
            deletedAssignments.push(...result.deleted_assignments.map(item => ({
              id: item.assignment_id,
              subject: item.assignment_subject || '未知科目',
              title: item.assignment_title || '未知作业',
              content: item.assignment_title || '未知作业',
              type: '作业',
              deletedAt: item.delete_time,
              dueDate: null,
              url: ''
            })))
          }
        }
        
        // 处理已删除的待办
        if (todosResponse.ok) {
          const result = await todosResponse.json()
          if (result.success && result.deleted_todos) {
            deletedTodos.push(...result.deleted_todos.map(item => ({
              id: `todo_${item.todo_id}`,
              _todoId: item.todo_id,
              subject: '待办事项',
              title: item.title,
              content: item.title,
              type: '待办',
              deletedAt: item.delete_time,
              dueDate: null,
              url: ''
            })))
          }
        }
        
        // 合并并按删除时间排序
        deletedItems.value = [...deletedAssignments, ...deletedTodos].sort((a, b) => 
          new Date(b.deletedAt) - new Date(a.deletedAt)
        )
        
        console.log('获取已删除项目成功:', deletedItems.value)
      } catch (error) {
        console.error('获取已删除项目失败:', error)
        showToast('error', '获取失败', '无法获取回收站内容')
        deletedItems.value = []
      }
    }

    const restoreItem = async (item) => {
      try {
        let response
        
        if (item.type === '待办') {
          // 恢复待办事项
          response = await fetch(`/api/todos/${item._todoId}/restore`, {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              title: item.title
            })
          })
        } else {
          // 恢复作业/测试
          response = await fetch(`/api/assignments/${item.id}/restore`, {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              title: item.title,
              subject: item.subject
            })
          })
        }
        
        if (response.ok) {
          const result = await response.json()
          
          // 从回收站列表中移除
          const index = deletedItems.value.findIndex(d => d.id === item.id)
          if (index !== -1) {
            deletedItems.value.splice(index, 1)
          }
          
          // 重新获取数据
          if (item.type === '待办') {
            await fetchTodos()
          } else {
            await fetchAssignments()
          }
          filterAssignments()
          
          showToast('success', '恢复成功', `${item.type}"${item.title}"已恢复`)
          console.log('恢复成功:', result)
        } else {
          const errorData = await response.json()
          console.error('恢复失败:', errorData)
          showToast('error', '恢复失败', errorData.error || '恢复失败，请重试')
        }
      } catch (error) {
        console.error('恢复错误:', error)
        showToast('error', '网络错误', '请检查网络连接后重试')
      }
    }

    const permanentDelete = (item) => {
      const performDelete = async () => {
        try {
          let response
          
          if (item.type === '待办') {
            // 永久删除待办事项
            response = await fetch(`/api/todos/${item._todoId}/permanent-delete`, {
              method: 'DELETE',
              credentials: 'include'
            })
          } else {
            // 永久删除作业/测试
            response = await fetch(`/api/assignments/${item.id}/permanent-delete`, {
              method: 'DELETE',
              credentials: 'include'
            })
          }
          
          if (response.ok) {
            const result = await response.json()
            
            // 从回收站列表中移除
            const index = deletedItems.value.findIndex(d => d.id === item.id)
            if (index !== -1) {
              deletedItems.value.splice(index, 1)
            }
            
            showToast('success', '永久删除', `"${item.title}"已永久删除`)
            console.log('永久删除成功:', result)
          } else {
            const errorData = await response.json()
            console.error('永久删除失败:', errorData)
            showToast('error', '删除失败', errorData.error || '永久删除失败，请重试')
          }
        } catch (error) {
          console.error('永久删除错误:', error)
          showToast('error', '网络错误', '请检查网络连接后重试')
        }
      }
      
      showCustomConfirm(
        `确定要永久删除"${item.title}"吗？\n\n此操作无法撤销！`, 
        performDelete
      )
    }

    const clearRecycleBin = () => {
      const performClear = async () => {
        try {
          // 并行清空作业和待办的回收站
          const [assignmentsResponse, todosResponse] = await Promise.all([
            fetch('/api/assignments/clear-deleted', {
              method: 'DELETE',
              credentials: 'include'
            }),
            fetch('/api/todos/clear-deleted', {
              method: 'DELETE',
              credentials: 'include'
            })
          ])
          
          let success = true
          const errors = []
          
          if (!assignmentsResponse.ok) {
            const errorData = await assignmentsResponse.json()
            errors.push(`作业清空失败: ${errorData.error || '未知错误'}`)
            success = false
          }
          
          if (!todosResponse.ok) {
            const errorData = await todosResponse.json()
            errors.push(`待办清空失败: ${errorData.error || '未知错误'}`)
            success = false
          }
          
          if (success) {
            deletedItems.value = []
            showToast('success', '清空完成', '回收站已清空')
            console.log('清空回收站成功')
          } else {
            console.error('清空回收站部分失败:', errors)
            showToast('error', '清空失败', errors.join('\n'))
          }
        } catch (error) {
          console.error('清空回收站错误:', error)
          showToast('error', '网络错误', '请检查网络连接后重试')
        }
      }
      
      showCustomConfirm(
        '确定要清空回收站吗？\n\n此操作将永久删除所有项目，无法撤销！', 
        performClear
      )
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
      
      // 初始化时间显示
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
      filterAssignments,
      watchFilters,
      openAssignmentUrl,
      setReminder,
      markCompleted,
      undoCompleted,
      handleLogout,
      fetchAssignments,
      showAddTodoModal,
      addingTodo,
      newTodo,
      closeAddTodoModal,
      addTodo,
      fetchTodos,
      deleteTodo,
      deleteAssignment,
      showPreviewModal,
      previewItem,
      showPreview,
      closePreviewModal,
      showConfirmModal,
      confirmMessage,
      showCustomConfirm,
      confirmAction,
      cancelConfirm,
      showStatisticsModal,
      currentStatType,
      filteredStatItems,
      showStatModal,
      closeStatModal,
      getStatItems,
      showRecycleBinModal,
      deletedItems,
      showRecycleBin,
      closeRecycleBin,
      fetchDeletedItems,
      restoreItem,
      permanentDelete,
      clearRecycleBin
    }
  }
}
</script>

<style>
@import './home/styles/toast.css';

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
</style>