<template>
  <div 
    :class="['assignment-card', assignmentStatus]"
    :data-type="assignment.type"
    @click="$emit('open-url', assignment)"
    style="cursor: pointer;"
  >
    <!-- 优先级指示器 (仅待办显示) -->
    <div 
      v-if="assignment.type === '待办' && assignment.priority" 
      :class="['priority-indicator', assignment.priority]"
    ></div>
    <!-- 预览按钮 -->
    <button 
      class="preview-btn" 
      @click.stop="$emit('show-preview', assignment)"
      title="预览详情"
    >
      <i class="fas fa-eye"></i>
    </button>
    <div class="card-header">
      <span class="subject-tag">{{ assignment.subject }}</span>
      <small class="type-tag">{{ assignment.type }}</small>
    </div>
    <h3 class="card-title">{{ truncateText(assignment.title, 50) }}</h3>
    <p class="card-content">{{ truncateText(assignment.content, 80) }}</p>
    <div class="card-footer">
      <div v-if="assignment.dueDate" :class="['due-date', assignmentStatus]">
        <i :class="statusIcon"></i>
        <span v-html="formattedDate"></span>
      </div>
      <div v-else class="due-date-placeholder">
        <!-- 无截止日期 -->
      </div>
      <div class="actions" @click.stop>
        <button 
          v-if="!assignment.completed"
          class="btn btn-primary"
          @click="$emit('set-reminder', assignment)"
        >
          <i class="fas fa-bell"></i> 提醒
        </button>
        <!-- 删除按钮 - 在提醒和完成之间 -->
        <button 
          v-if="!assignment.completed"
          class="btn btn-danger delete-btn"
          @click="$emit('delete-assignment', assignment)"
          :title="assignment.type === '待办' ? '删除待办' : '删除作业'"
        >
          <i class="fas fa-trash"></i>
        </button>
        <button 
          v-if="!assignment.completed"
          class="btn btn-success complete-btn"
          @click="$emit('mark-completed', assignment)"
          :disabled="assignment.completing"
        >
          <span v-if="!assignment.completing" class="btn-content">
            <i class="fas fa-check"></i> 完成
          </span>
          <span v-else class="btn-loading">
            <i class="fas fa-spinner fa-spin"></i> 处理中...
          </span>
        </button>
        <div v-else-if="assignment.completed" class="completed-actions">
          <button class="btn btn-completed">
            <i class="fas fa-check-circle"></i> 已完成
          </button>
          <button 
            class="btn btn-secondary undo-btn"
            @click="$emit('undo-completed', assignment)"
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
            class="btn btn-danger delete-btn"
            @click="$emit('delete-assignment', assignment)"
            :title="assignment.type === '待办' ? '删除待办' : '删除作业'"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssignmentCard',
  props: {
    assignment: {
      type: Object,
      required: true
    }
  },
  emits: ['open-url', 'show-preview', 'set-reminder', 'delete-assignment', 'mark-completed', 'undo-completed'],
  computed: {
    assignmentStatus() {
      if (this.assignment.completed) return 'completed'
      
      const days = this.getDaysUntilDue(this.assignment.dueDate)
      if (days < 0) return 'urgent'
      if (days <= 2) return 'urgent'
      if (days <= 7) return 'warning'
      return 'normal'
    },
    statusIcon() {
      const status = this.assignmentStatus
      const icons = {
        urgent: 'fas fa-exclamation-triangle',
        warning: 'fas fa-clock',
        normal: 'fas fa-calendar-alt',
        completed: 'fas fa-check-circle'
      }
      return icons[status]
    },
    formattedDate() {
      return this.formatDate(this.assignment.dueDate, this.assignment.type, this.assignment.estimatedHours)
    }
  },
  methods: {
    getCurrentTime() {
      return new Date()
    },
    getDaysUntilDue(dueDate) {
      try {
        if (!dueDate) {
          return Infinity
        }
        
        const now = this.getCurrentTime()
        
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
    },
    formatDate(dateString, itemType, estimatedHours) {
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
      const now = this.getCurrentTime()
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
      const days = this.getDaysUntilDue(dateString)
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
    },
    truncateText(text, maxLength) {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
  }
}
</script>

<style scoped>
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

/* 测试类型卡片特殊布局 */
.assignment-card[data-type="测试"] {
  display: flex;
  flex-direction: column;
  min-height: 280px;
}

.assignment-card[data-type="测试"] .card-header {
  flex-shrink: 0;
}

.assignment-card[data-type="测试"] .card-title {
  flex-shrink: 0;
}

.assignment-card[data-type="测试"] .card-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin: 20px 0;
}

.assignment-card[data-type="测试"] .card-footer {
  flex-shrink: 0;
  margin-top: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  padding-right: 50px; /* 为右上角的眼睛图标留出空间 */
}

.type-tag {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75em;
  font-weight: 500;
  border: 1px solid rgba(102, 126, 234, 0.2);
  white-space: nowrap; /* 防止文字换行 */
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
  right: 50px;
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

/* 预览按钮 */
.preview-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 32px;
  height: 32px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 50%;
  color: #667eea;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.3s ease;
  z-index: 2;
  backdrop-filter: blur(10px);
}

.preview-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
  color: #5a6fd8;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.preview-btn:active {
  transform: scale(0.95);
}

@media (max-width: 768px) {
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