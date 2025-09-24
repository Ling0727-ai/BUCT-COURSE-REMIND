<template>
  <div v-if="show" class="modal-overlay preview-modal-overlay" @click="$emit('close')">
    <div class="modal-content preview-modal" @click.stop>
      <div class="modal-header">
        <h3><i class="fas fa-eye"></i> 详情预览</h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body" v-if="item">
        <div class="preview-field">
          <label>类型</label>
          <div class="preview-value">
            <span :class="['type-badge', item.type]">{{ item.type }}</span>
          </div>
        </div>
        <div class="preview-field">
          <label>科目</label>
          <div class="preview-value">{{ item.subject }}</div>
        </div>
        <div class="preview-field">
          <label>标题</label>
          <div class="preview-value preview-title">{{ item.title }}</div>
        </div>
        <div class="preview-field">
          <label>内容</label>
          <div class="preview-value preview-content">
            <div v-if="item.details && item.details.trim()">
              {{ item.details }}
            </div>
            <div v-else>
              {{ item.content }}
            </div>
          </div>
        </div>
        <div v-if="item.dueDate" class="preview-field">
          <label>截止时间</label>
          <div class="preview-value preview-date">
            <i :class="statusIcon"></i>
            <span v-html="formattedDate"></span>
          </div>
        </div>
        <div v-if="item.priority && item.type === '待办'" class="preview-field">
          <label>优先级</label>
          <div class="preview-value">
            <span :class="['priority-badge', item.priority]">
              <i class="fas fa-flag"></i>
              {{ getPriorityText(item.priority) }}
            </span>
          </div>
        </div>
        <div v-if="item.url" class="preview-field">
          <label>链接</label>
          <div class="preview-value">
            <a :href="item.url" target="_blank" class="preview-link">
              <i class="fas fa-external-link-alt"></i>
              打开链接
            </a>
          </div>
        </div>
        <div class="preview-field">
          <label>状态</label>
          <div class="preview-value">
            <span :class="['status-badge', assignmentStatus]">
              <i :class="statusIcon"></i>
              {{ getStatusText(assignmentStatus) }}
            </span>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
        <button 
          v-if="item && item.url" 
          class="btn btn-primary" 
          @click="$emit('open-url', item)"
        >
          <i class="fas fa-external-link-alt"></i> 打开链接
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PreviewModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    item: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'open-url'],
  computed: {
    assignmentStatus() {
      if (!this.item) return 'normal'
      if (this.item.completed) return 'completed'
      
      const days = this.getDaysUntilDue(this.item.dueDate)
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
      if (!this.item || !this.item.dueDate) return ''
      return this.formatDate(this.item.dueDate, this.item.type, this.item.estimatedHours)
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
    getPriorityText(priority) {
      const priorityMap = {
        'high': '高',
        'medium': '中',
        'low': '低'
      }
      return priorityMap[priority] || priority
    },
    getStatusText(status) {
      const statusMap = {
        'urgent': '紧急',
        'warning': '即将到期',
        'normal': '正常',
        'completed': '已完成'
      }
      return statusMap[status] || status
    }
  }
}
</script>

<style scoped>
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

.preview-modal-overlay {
  z-index: 1100 !important;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.preview-modal {
  max-width: 600px;
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

.preview-field {
  margin-bottom: 20px;
}

.preview-field label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-value {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 15px;
  line-height: 1.6;
  color: #1f2937;
  min-height: 20px;
}

.preview-title {
  font-weight: 600;
  font-size: 16px;
  color: #111827;
}

.preview-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.preview-date {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-link {
  color: #667eea;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.preview-link:hover {
  color: #5a6fd8;
  text-decoration: underline;
}

/* 类型标签 */
.type-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-badge.作业 {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.type-badge.测试 {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
}

.type-badge.待办 {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
}

/* 优先级标签 */
.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.priority-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.priority-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.priority-badge.low {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

/* 状态标签 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.urgent {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.status-badge.normal {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.modal-footer {
  padding: 20px 30px 25px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 12px 24px;
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
  font-weight: 500;
  min-width: 100px;
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #5a6268, #3d4043);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
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
</style>