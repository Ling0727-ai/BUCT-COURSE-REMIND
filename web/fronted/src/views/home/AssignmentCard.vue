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
    
    <!-- 日期信息区域 (仅移动端使用) -->
    <div v-if="assignment.dueDate" class="date-info mobile-only">
      <div :class="['due-date-line', assignmentStatus]">
        <i :class="statusIcon"></i>
        <span class="date-text">{{ formattedDateOnly }}</span>
      </div>
      <div v-if="remainingTimeText" class="remaining-time">
        {{ remainingTimeText }}
      </div>
    </div>
    
    <!-- 操作按钮区域 -->
    <div class="card-footer">
      <!-- 桌面端日期信息 -->
      <div v-if="assignment.dueDate" class="date-section desktop-only">
        <div :class="['due-date-line', assignmentStatus]">
          <i :class="statusIcon"></i>
          <span class="date-text">{{ formattedDateOnly }}</span>
        </div>
        <div v-if="remainingTimeText" class="remaining-time">
          {{ remainingTimeText }}
        </div>
      </div>
      
      <div class="actions" @click.stop>
        <!-- 拉黑按钮（仅作业/测试卡片，不含待办） -->
        <button
            v-if="assignment.type !== '待办'"
            class="btn btn-blacklist"
            title="拉黑此科目"
            @click="$emit('blacklist-subject', assignment)"
        >
          <i class="fas fa-ban"></i>
          <span class="btn-text">拉黑</span>
        </button>
        <button
          v-if="!assignment.completed"
          class="btn btn-warning"
          @click="$emit('set-reminder', assignment)"
          title="设置提醒"
        >
          <i class="fas fa-bell"></i>
          <span class="btn-text">提醒</span>
        </button>
        <!-- 删除按钮 - 在提醒和完成之间 -->
        <button 
          v-if="!assignment.completed"
          class="btn btn-danger delete-btn"
          @click="$emit('delete-assignment', assignment)"
          :title="assignment.type === '待办' ? '删除待办' : '删除作业'"
        >
          <i class="fas fa-trash"></i>
          <span class="btn-text">删除</span>
        </button>
        <button 
          v-if="!assignment.completed"
          class="btn btn-success complete-btn"
          @click="$emit('mark-completed', assignment)"
          :disabled="assignment.completing"
          title="标记为完成"
        >
          <span v-if="!assignment.completing" class="btn-content">
            <i class="fas fa-check"></i>
            <span class="btn-text">完成</span>
          </span>
          <span v-else class="btn-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <span class="btn-text">处理中...</span>
          </span>
        </button>
        <div v-else-if="assignment.completed" class="completed-actions">
          <button class="btn btn-completed" title="已完成">
            <i class="fas fa-check-circle"></i>
            <span class="btn-text">已完成</span>
          </button>
          <button 
            class="btn btn-secondary undo-btn"
            @click="$emit('undo-completed', assignment)"
            :disabled="assignment.undoing"
            title="撤销完成"
          >
            <i v-if="!assignment.undoing" class="fas fa-undo"></i>
            <i v-else class="fas fa-spinner fa-spin"></i>
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
  emits: ['open-url', 'show-preview', 'set-reminder', 'delete-assignment', 'mark-completed', 'undo-completed', 'blacklist-subject'],
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
    },
    formattedDateOnly() {
      if (!this.assignment.dueDate) return ''
      const date = this.parseDate(this.assignment.dueDate)
      if (!date || isNaN(date.getTime())) return ''
      const options = {
        year: 'numeric',
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit' 
      }
      return date.toLocaleString('zh-CN', options).replace(/\//g, '-')
    },
    remainingTimeText() {
      if (!this.assignment.dueDate) return ''
      const now = this.getCurrentTime()
      const date = this.parseDate(this.assignment.dueDate)
      if (!date || isNaN(date.getTime())) return ''
      const diffMs = date.getTime() - now.getTime()
      
      if (diffMs < 0) {
        // 已过期
        const overdueDays = Math.floor(Math.abs(diffMs) / (1000 * 60 * 60 * 24))
        const overdueHours = Math.floor(Math.abs(diffMs) / (1000 * 60 * 60)) % 24
        
        if (overdueDays > 0) {
          return `已超时 ${overdueDays}天${overdueHours > 0 ? overdueHours + '小时' : ''}`
        } else {
          return `已超时 ${overdueHours}小时`
        }
      } else {
        // 剩余时间
        const remainingDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
        const remainingHours = Math.floor(diffMs / (1000 * 60 * 60)) % 24
        const remainingMinutes = Math.floor(diffMs / (1000 * 60)) % 60
        
        if (remainingDays > 0) {
          return `剩余 ${remainingDays}天${remainingHours > 0 ? remainingHours + '小时' : ''}`
        } else if (remainingHours > 0) {
          return `剩余 ${remainingHours}小时${remainingMinutes > 0 ? remainingMinutes + '分钟' : ''}`
        } else {
          return `剩余 ${remainingMinutes}分钟`
        }
      }
    }
  },
  methods: {
    getCurrentTime() {
      return new Date()
    },
    // 统一日期解析：兼容 ISO（T分隔）、"YYYY-MM-DD HH:mm:ss"（空格分隔）和中文格式
    parseDate(s) {
      if (!s) return null
      // 已有时区信息，直接解析
      if (s.includes('+') || s.endsWith('Z')) return new Date(s)
      // "YYYY-MM-DD HH:mm:ss" 空格分隔 → 转成 ISO + 北京时区
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(s)) return new Date(s.replace(' ', 'T') + '+08:00')
      // ISO 无时区
      if (s.includes('T')) return new Date(s + '+08:00')
      // 中文格式兜底：2025年9月23日 23:59:00 → 2025-09-23T23:59:00+08:00
      const cn = s.match(/^(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{2}:\d{2}:\d{2})$/)
      if (cn) {
        const [, y, mo, d, t] = cn
        return new Date(`${y}-${mo.padStart(2, '0')}-${d.padStart(2, '0')}T${t}+08:00`)
      }
      return new Date(s)
    },
    getDaysUntilDue(dueDate) {
      try {
        if (!dueDate) return Infinity
        const now = this.getCurrentTime()
        const due = this.parseDate(dueDate)
        if (!due || isNaN(due.getTime())) {
          console.warn('无效的截止日期:', dueDate)
          return 7
        }
        return Math.ceil((due - now) / (1000 * 60 * 60 * 24))
      } catch (error) {
        console.error('计算剩余天数时出错:', error, '日期:', dueDate)
        return 7
      }
    },
    formatDate(dateString, itemType, estimatedHours) {
      if (!dateString) return ''

      const date = this.parseDate(dateString)
      if (!date || isNaN(date.getTime())) return ''
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
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  border-radius: 18px;
  padding: 22px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.28s cubic-bezier(0.34, 1.2, 0.64, 1);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-left: 3px solid #0ea5e9;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 280px;
}

.assignment-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.6) 0%, rgba(240, 249, 255, 0.2) 100%);
  pointer-events: none;
}

.assignment-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1), 0 4px 12px rgba(14, 165, 233, 0.08);
  border-color: rgba(14, 165, 233, 0.25);
  background: rgba(255, 255, 255, 0.97);
}

.assignment-card.urgent {
  border-left-color: #ef4444;
  background: rgba(255, 255, 255, 0.94);
  animation: pulse 2.2s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  }
  50% {
    box-shadow: 0 6px 24px rgba(239, 68, 68, 0.18);
  }
  100% {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  }
}

.assignment-card.warning {
  border-left-color: #f97316;
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
  background: rgba(14, 165, 233, 0.07);
  color: #0284c7;
  padding: 4px 11px;
  border-radius: 10px;
  font-size: 0.73em;
  font-weight: 600;
  border: 1px solid rgba(14, 165, 233, 0.15);
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.subject-tag {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  padding: 5px 13px;
  border-radius: 20px;
  font-size: 0.78em;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(14, 165, 233, 0.28);
  letter-spacing: 0.2px;
}

.card-title {
  font-size: 1.15em;
  color: #0f172a;
  margin-bottom: 10px;
  font-weight: 700;
  line-height: 1.45;
  position: relative;
  z-index: 1;
  letter-spacing: -0.1px;
}

.card-content {
  color: #64748b;
  font-size: 0.9em;
  line-height: 1.65;
  margin-bottom: 14px;
  position: relative;
  z-index: 1;
  flex: 1;
}

/* 响应式显示控制 */
.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

/* 日期信息区域 */
.date-info {
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.date-section {
  flex: 1 1 auto;
  min-width: 0; /* 允许收缩 */
}

.due-date-line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.due-date-line i {
  font-size: 14px;
}

.date-text {
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remaining-time {
  font-size: 13px;
  color: #64748b;
  padding-left: 22px;
  font-weight: 500;
}

.due-date-line.urgent {
  color: #ef4444;
}

.due-date-line.urgent .date-text {
  color: #ef4444;
}

.due-date-line.warning {
  color: #f97316;
}

.due-date-line.warning .date-text {
  color: #f97316;
}

.due-date-line.normal {
  color: #22c55e;
}

.due-date-line.normal .date-text {
  color: #22c55e;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
  padding-top: 14px;
  margin-top: auto;
  border-top: 1px solid rgba(14, 165, 233, 0.08);
  gap: 20px;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap; /* 禁止换行，三按钮同排 */
  align-items: center;
  flex-shrink: 0;
}

.btn {
  padding: 9px 16px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-align: center;
  white-space: nowrap;
  line-height: 1;
}

/* 新增：黄色提醒按钮样式 */
.btn-warning {
  background: linear-gradient(135deg, #f59e0b, #f97316);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-warning:hover {
  background: linear-gradient(135deg, #d97706, #ea580c);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

/* 拉黑按钮 */
.btn-blacklist {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.25);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.btn-blacklist:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* 新增：绿色完成按钮样式 */
.btn-success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #16a34a, #15803d);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
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
  flex-wrap: nowrap;
}

.btn-completed {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.2);
  cursor: default;
  position: relative;
  overflow: hidden;
  padding: 9px 14px;
  font-size: 13px;
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
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 8px 12px;
  min-width: auto;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
  color: #4b5563;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9em;
  transition: all 0.3s ease;
  min-width: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.undo-btn {
  transition: all 0.3s ease;
}

.undo-btn:hover:not(:disabled) {
  background: #e5e7eb;
  color: #4b5563;
}

/* 已完成卡片 */
.assignment-card.completed {
  background: linear-gradient(145deg, rgba(240, 253, 244, 0.95), rgba(220, 252, 231, 0.85));
  border-left-color: #22c55e;
  border-left-width: 3px;
  opacity: 0.88;
  box-shadow: 0 2px 12px rgba(34, 197, 94, 0.1) !important;
}

.assignment-card.completed::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(34, 197, 94, 0.04));
  pointer-events: none;
}

.assignment-card.completed .card-title {
  color: #15803d !important;
  text-decoration: line-through;
  text-decoration-color: rgba(21, 128, 61, 0.5);
  text-decoration-thickness: 1.5px;
  opacity: 0.85;
}

.assignment-card.completed .card-content {
  color: #86a890;
}

/* 待办卡片 */
.assignment-card[data-type="待办"] {
  border-left-color: #8b5cf6;
  background: rgba(255, 255, 255, 0.92);
}

.assignment-card[data-type="待办"] .subject-tag {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  box-shadow: 0 3px 10px rgba(139, 92, 246, 0.28);
}

.assignment-card[data-type="待办"]:hover {
  box-shadow: 0 16px 40px rgba(139, 92, 246, 0.12), 0 4px 12px rgba(139, 92, 246, 0.08);
  border-color: rgba(139, 92, 246, 0.25);
}

.assignment-card[data-type="待办"].completed {
  background: linear-gradient(145deg, rgba(240, 253, 244, 0.95), rgba(220, 252, 231, 0.85));
  border-left-color: #22c55e;
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
  background: #ef4444;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.priority-indicator.medium {
  background: #f97316;
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}

.priority-indicator.low {
  background: #22c55e;
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}

/* 预览按钮 */
.preview-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 32px;
  height: 32px;
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 50%;
  color: #0ea5e9;
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
  background: rgba(14, 165, 233, 0.15);
  border-color: rgba(14, 165, 233, 0.3);
  color: #0284c7;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

.preview-btn:active {
  transform: scale(0.95);
}

/* 中屏优化（≤768px）：缩小按钮与文字，尽量同排 */
@media (max-width: 768px) {
  .card-footer {
    gap: 12px;
  }

  .due-date-line {
    font-size: 13px;
    gap: 6px;
  }

  .actions {
    gap: 6px;
  }

  .btn-text {
    display: none; /* 中小屏隐藏按钮文字，仅留图标节省空间 */
  }

  .btn {
    width: 36px;
    height: 36px;
    padding: 0;
    min-width: 36px;
  }

  .btn i {
    font-size: 14px;
  }
}

/* 小屏优化（≤480px）：进一步压缩，确保三按钮同一行 */
@media (max-width: 480px) {
  .card-footer {
    gap: 10px;
  }

  .date-section {
    flex: 1 1 auto;
    min-width: 0;
  }

  .due-date-line {
    font-size: 12px;
    gap: 6px;
  }

  .date-text {
    max-width: 65vw; /* 防止日期挤占按钮空间 */
  }

  .actions {
    gap: 6px;
  }

  .btn {
    width: 32px;
    height: 32px;
    min-width: 32px;
    padding: 0;
    border-radius: 8px;
  }

  .btn i {
    font-size: 13px;
  }
}

/* 超小屏（≤340px）：最小化占用 */
@media (max-width: 340px) {
  .due-date-line {
    font-size: 11px;
  }

  .date-text {
    max-width: 58vw;
  }

  .btn {
    width: 30px;
    height: 30px;
    min-width: 30px;
  }

  .btn i {
    font-size: 12px;
  }
}

/* 桌面端样式优化 (>768px) */
@media (min-width: 769px) {
  .mobile-only {
    display: none !important;
  }

  .desktop-only {
    display: block !important;
  }

  .assignment-card {
    padding: 22px 26px;
    min-height: 280px;
  }

  .card-footer {
    padding-top: 18px;
    gap: 24px;
  }

  .date-section {
    min-width: 200px;
  }

  .due-date-line {
    font-size: 14px;
    margin-bottom: 4px;
  }

  .remaining-time {
    font-size: 13px;
  }

  .actions {
    gap: 8px;
    flex-shrink: 0;
  }

  /* 桌面端按钮 - 只显示图标 */
  .btn-text {
    display: none !important;
  }

  .btn {
    min-width: 36px !important;
    width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    font-weight: 500 !important;
  }

  .btn i {
    font-size: 14px !important;
    margin: 0 !important;
  }

  /* 特定按钮优化 */
  .btn-primary {
    min-width: 36px !important;
    width: 36px !important;
  }

  .btn-warning {
    min-width: 36px !important;
    width: 36px !important;
  }

  .btn-danger {
    min-width: 36px !important;
    width: 36px !important;
  }

  .btn-blacklist {
    min-width: 36px !important;
    width: 36px !important;
  }

  .btn-success {
    min-width: 36px !important;
    width: 36px !important;
  }

  .btn-completed {
    min-width: auto !important;
    width: auto !important;
    padding: 0 12px !important;
    height: 36px !important;
    font-size: 12px !important;
  }

  .btn-completed .btn-text {
    display: inline !important;
  }

  .undo-btn {
    min-width: 36px !important;
    width: 36px !important;
  }

  .completed-actions {
    gap: 8px;
  }
}

/* 大屏幕进一步优化 (>1200px) */
@media (min-width: 1201px) {
  .assignment-card {
    padding: 24px 28px;
    min-height: 300px;
  }

  .card-footer {
    padding-top: 20px;
    gap: 28px;
  }

  .date-section {
    min-width: 220px;
  }

  .due-date-line {
    font-size: 15px;
    margin-bottom: 5px;
  }

  .remaining-time {
    font-size: 14px;
  }

  .actions {
    gap: 10px;
  }

  .btn {
    min-width: 38px !important;
    width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
  }

  .btn i {
    font-size: 15px !important;
    margin: 0 !important;
  }

  .btn-primary {
    min-width: 38px !important;
    width: 38px !important;
  }

  .btn-warning {
    min-width: 38px !important;
    width: 38px !important;
  }

  .btn-danger {
    min-width: 38px !important;
    width: 38px !important;
  }

  .btn-blacklist {
    min-width: 38px !important;
    width: 38px !important;
  }

  .btn-success {
    min-width: 38px !important;
    width: 38px !important;
  }

  .btn-completed {
    min-width: auto !important;
    width: auto !important;
    padding: 0 14px !important;
    height: 38px !important;
  }

  .undo-btn {
    min-width: 38px !important;
    width: 38px !important;
  }
}

/* 中等屏幕优化 (481px-768px) - 日期和按钮在同一行 */
@media (min-width: 481px) and (max-width: 768px) {
  .mobile-only {
    display: none !important;
  }

  .desktop-only {
    display: block !important;
  }

  .assignment-card {
    padding: 18px;
    min-height: 260px;
  }

  .card-content {
    margin-bottom: 14px;
  }

  .date-info {
    display: none !important;
  }

  /* 日期时间和按钮在同一行 */
  .card-footer {
    padding-top: 14px;
    justify-content: space-between !important;
    gap: 12px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
  }

  .date-section {
    display: block !important;
    flex: 0 0 auto;
    min-width: 0;
    flex-shrink: 1;
  }

  .due-date-line {
    font-size: 12px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .remaining-time {
    font-size: 11px;
    padding-left: 18px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .actions {
    gap: 5px;
    justify-content: flex-end;
    flex-wrap: nowrap !important;
    display: flex !important;
    flex-shrink: 0 !important;
  }

  /* 中等屏幕按钮 - 所有按钮只显示图标 */
  .btn-text {
    display: none !important;
  }

  .btn {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    flex-shrink: 0;
    border-radius: 8px !important;
  }

  .btn i {
    font-size: 12px !important;
    margin: 0 !important;
  }

  .btn-primary {
    min-width: 32px !important;
    width: 32px !important;
  }

  .btn-warning {
    min-width: 32px !important;
    width: 32px !important;
  }

  .btn-success {
    min-width: 32px !important;
    width: 32px !important;
  }

  .btn-danger {
    min-width: 32px !important;
    width: 32px !important;
  }

  .btn-blacklist {
    min-width: 32px !important;
    width: 32px !important;
  }

  .btn-completed {
    min-width: auto !important;
    width: auto !important;
    padding: 0 8px !important;
    height: 32px !important;
    font-size: 10px !important;
  }

  .btn-completed .btn-text {
    display: inline !important;
  }

  .undo-btn {
    min-width: 32px !important;
    width: 32px !important;
  }

  .completed-actions {
    gap: 5px;
    flex-wrap: nowrap !important;
    display: flex !important;
  }

  .completed-actions .btn-danger {
    min-width: 32px !important;
    width: 32px !important;
  }
}



/* 小屏幕移动端样式 (340px-480px) - 日期和按钮在同一行 */
@media (min-width: 340px) and (max-width: 480px) {
  .mobile-only {
    display: none !important;
  }

  .desktop-only {
    display: block !important;
  }

  .assignment-card {
    padding: 16px;
    min-height: 240px;
  }

  .card-content {
    margin-bottom: 12px;
  }

  .date-info {
    display: none !important;
  }

  /* 日期时间和按钮在同一行，紧凑布局 */
  .card-footer {
    padding-top: 12px;
    justify-content: space-between !important;
    gap: 10px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
  }

  .date-section {
    display: block !important;
    flex: 0 0 auto;
    min-width: 0;
    flex-shrink: 1;
    overflow: hidden;
  }

  .due-date-line {
    font-size: 11px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .due-date-line i {
    font-size: 11px;
  }

  .remaining-time {
    font-size: 10px;
    padding-left: 16px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .actions {
    gap: 5px !important;
    justify-content: flex-end;
    flex-wrap: nowrap !important;
    display: flex !important;
    flex-shrink: 0 !important;
  }

  /* 隐藏所有按钮文字，只显示图标 */
  .btn-text {
    display: none !important;
  }

  /* 统一按钮尺寸 - 紧凑图标按钮 */
  .btn {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    border-radius: 10px !important;
    flex-shrink: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  .btn i {
    margin: 0 !important;
    font-size: 12px !important;
  }

  .btn-content,
  .btn-loading {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
  }

  .btn-content i,
  .btn-loading i {
    font-size: 12px !important;
    margin: 0 !important;
  }

  /* 提醒按钮 */
  .btn-warning {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
  }

  /* 删除按钮 */
  .btn-danger,
  .delete-btn {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
  }

  /* 拉黑按钮 */
  .btn-blacklist {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
  }

  /* 完成按钮 */
  .btn-success,
  .complete-btn {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
  }

  /* 已完成按钮 - 保持文字显示但压缩 */
  .btn-completed {
    min-width: auto !important;
    width: auto !important;
    white-space: nowrap !important;
    padding: 0 8px !important;
    height: 32px !important;
    font-size: 10px !important;
    flex-shrink: 0 !important;
  }

  .btn-completed .btn-text {
    display: inline !important;
  }

  /* 撤销按钮 */
  .undo-btn {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
  }

  /* 已完成状态的按钮组 */
  .completed-actions {
    gap: 5px !important;
    flex-shrink: 0 !important;
    flex-wrap: nowrap !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
  }

  .completed-actions .btn-danger {
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
  }

  .card-title {
    font-size: 1.05em;
  }

  .card-content {
    font-size: 0.9em;
  }
}

/* 超小屏幕 (≤340px) - 极致紧凑布局 */
@media (max-width: 340px) {
  .mobile-only {
    display: block !important;
  }

  .desktop-only {
    display: none !important;
  }

  .assignment-card {
    padding: 12px;
    min-height: 220px;
  }

  .card-content {
    margin-bottom: 10px;
    font-size: 0.88em;
  }

  .date-info {
    margin-bottom: 8px;
  }

  .due-date-line {
    font-size: 12px;
  }

  .remaining-time {
    font-size: 11px;
    padding-left: 18px;
  }

  .card-footer {
    padding-top: 10px;
    justify-content: flex-end !important;
    gap: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
  }

  .actions {
    gap: 4px !important;
    width: 100%;
    justify-content: flex-end;
    flex-wrap: nowrap !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
  }

  /* 隐藏所有按钮文字 */
  .btn-text {
    display: none !important;
  }

  /* 更小的按钮尺寸 */
  .btn {
    min-width: 30px !important;
    width: 30px !important;
    height: 30px !important;
    padding: 0 !important;
    border-radius: 8px !important;
    flex-shrink: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  .btn i {
    margin: 0 !important;
    font-size: 11px !important;
  }

  .btn-content,
  .btn-loading {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
  }

  .btn-content i,
  .btn-loading i {
    font-size: 11px !important;
    margin: 0 !important;
  }

  /* 所有按钮统一尺寸 */
  .btn-primary,
  .btn-warning,
  .btn-danger,
  .delete-btn,
  .btn-success,
  .complete-btn,
  .undo-btn {
    min-width: 30px !important;
    width: 30px !important;
    height: 30px !important;
  }

  /* 已完成按钮 */
  .btn-completed {
    min-width: auto !important;
    width: auto !important;
    height: 30px !important;
    padding: 0 8px !important;
    font-size: 10px !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
  }

  .btn-completed .btn-text {
    display: inline !important;
  }

  /* 已完成按钮组 */
  .completed-actions {
    gap: 4px !important;
    flex-shrink: 0 !important;
    flex-wrap: nowrap !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
  }

  .completed-actions .btn-danger {
    min-width: 30px !important;
    width: 30px !important;
    height: 30px !important;
  }

  .card-title {
    font-size: 1em;
  }
}
</style>