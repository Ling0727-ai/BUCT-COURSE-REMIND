<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-container">
      <div class="modal-header">
        <h3>
          <i class="fas fa-bell"></i>
          设置提醒时间
        </h3>
        <button class="close-btn" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <div class="assignment-info">
          <div class="info-row">
            <span class="label">科目：</span>
            <span class="value">{{ assignment?.subject || '未知' }}</span>
          </div>
          <div class="info-row">
            <span class="label">标题：</span>
            <span class="value">{{ assignment?.title || '未知' }}</span>
          </div>
          <div class="info-row" v-if="assignment?.dueDate">
            <span class="label">截止时间：</span>
            <span class="value">{{ formatDueDate(assignment.dueDate) }}</span>
          </div>
        </div>

        <div class="reminder-options">
          <h4>选择提醒方式</h4>

          <!-- 快捷选项 -->
          <div class="quick-options">
            <button
              v-for="option in quickOptions"
              :key="option.value"
              :class="['option-btn', { active: selectedOption === option.value }]"
              @click="selectQuickOption(option.value)"
            >
              <i :class="option.icon"></i>
              <span>{{ option.label }}</span>
            </button>
          </div>

          <!-- 自定义小时数 -->
          <div class="custom-hours" v-if="selectedOption === 'custom-hours'">
            <label>
              <i class="fas fa-clock"></i>
              提前几小时提醒
            </label>
            <input
              type="number"
              v-model.number="customHours"
              min="0.5"
              step="0.5"
              placeholder="例如：2"
            />
            <span class="unit">小时</span>
          </div>

          <!-- 自定义时间 -->
          <div class="custom-datetime" v-if="selectedOption === 'custom-datetime'">
            <label>
              <i class="fas fa-calendar-alt"></i>
              选择具体提醒时间
            </label>
            <input
              type="datetime-local"
              v-model="customDatetime"
              :max="maxDatetime"
            />
          </div>

          <!-- 立即提醒 -->
          <div class="instant-reminder" v-if="selectedOption === 'instant'">
            <p class="tip">
              <i class="fas fa-info-circle"></i>
              将立即发送提醒到您的注册邮箱
            </p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-cancel" @click="close">
          <i class="fas fa-times"></i>
          取消
        </button>
        <button
          class="btn btn-confirm"
          @click="confirm"
          :disabled="!isValid"
        >
          <i class="fas fa-check"></i>
          确认设置
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'ReminderModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    assignment: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const selectedOption = ref('instant')
    const customHours = ref(2)
    const customDatetime = ref('')

    const quickOptions = [
      { value: 'instant', label: '立即提醒', icon: 'fas fa-bolt' },
      { value: '1h', label: '1小时前', icon: 'fas fa-clock' },
      { value: '3h', label: '3小时前', icon: 'fas fa-clock' },
      { value: '6h', label: '6小时前', icon: 'fas fa-clock' },
      { value: '12h', label: '12小时前', icon: 'fas fa-clock' },
      { value: '1d', label: '1天前', icon: 'fas fa-calendar-day' },
      { value: 'custom-hours', label: '自定义小时', icon: 'fas fa-edit' },
      { value: 'custom-datetime', label: '具体时间', icon: 'fas fa-calendar-alt' }
    ]

    // 计算最大可选时间（截止时间）
    const maxDatetime = computed(() => {
      if (!props.assignment?.dueDate) return ''

      let date
      if (props.assignment.dueDate.includes('T') && !props.assignment.dueDate.includes('+') && !props.assignment.dueDate.includes('Z')) {
        date = new Date(props.assignment.dueDate + '+08:00')
      } else {
        date = new Date(props.assignment.dueDate)
      }

      // 转换为本地时间字符串格式 (YYYY-MM-DDTHH:mm)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')

      return `${year}-${month}-${day}T${hours}:${minutes}`
    })

    // 验证输入是否有效
    const isValid = computed(() => {
      if (selectedOption.value === 'instant') return true
      if (selectedOption.value === 'custom-hours') {
        return customHours.value > 0 && customHours.value <= 720 // 最多30天
      }
      if (selectedOption.value === 'custom-datetime') {
        if (!customDatetime.value) return false
        const selectedTime = new Date(customDatetime.value)
        const now = new Date()
        const dueDate = new Date(maxDatetime.value)
        return selectedTime > now && selectedTime < dueDate
      }
      return true
    })

    const selectQuickOption = (value) => {
      selectedOption.value = value
    }

    const formatDueDate = (dateString) => {
      if (!dateString) return ''

      let date
      if (dateString.includes('T') && !dateString.includes('+') && !dateString.includes('Z')) {
        date = new Date(dateString + '+08:00')
      } else {
        date = new Date(dateString)
      }

      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(/\//g, '-')
    }

    const close = () => {
      emit('close')
    }

    const confirm = () => {
      if (!isValid.value) return

      let reminderConfig = {
        type: selectedOption.value
      }

      // 根据不同选项构建配置
      if (selectedOption.value === 'instant') {
        reminderConfig.when = 'now'
      } else if (selectedOption.value === 'custom-hours') {
        reminderConfig.hours = customHours.value
      } else if (selectedOption.value === 'custom-datetime') {
        reminderConfig.datetime = customDatetime.value
      } else {
        // 快捷选项（1h, 3h, 6h, 12h, 1d）
        const hoursMap = {
          '1h': 1,
          '3h': 3,
          '6h': 6,
          '12h': 12,
          '1d': 24
        }
        reminderConfig.hours = hoursMap[selectedOption.value]
      }

      emit('confirm', reminderConfig)
      close()
    }

    // 重置状态
    watch(() => props.show, (newVal) => {
      if (newVal) {
        selectedOption.value = 'instant'
        customHours.value = 2
        customDatetime.value = ''
      }
    })

    return {
      selectedOption,
      customHours,
      customDatetime,
      quickOptions,
      maxDatetime,
      isValid,
      selectQuickOption,
      formatDueDate,
      close,
      confirm
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
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h3 i {
  color: #3b82f6;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  padding: 24px 28px;
}

.assignment-info {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 600;
  color: #6b7280;
  min-width: 80px;
}

.info-row .value {
  color: #1f2937;
}

.reminder-options h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.quick-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.option-btn {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #4b5563;
}

.option-btn i {
  font-size: 20px;
  color: #3b82f6;
}

.option-btn:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.option-btn.active {
  border-color: #3b82f6;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 600;
}

.custom-hours,
.custom-datetime {
  background: #f9fafb;
  padding: 20px;
  border-radius: 12px;
  margin-top: 16px;
}

.custom-hours label,
.custom-datetime label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.custom-hours input,
.custom-datetime input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s;
}

.custom-hours input {
  width: calc(100% - 60px);
  display: inline-block;
}

.custom-hours .unit {
  margin-left: 10px;
  color: #6b7280;
  font-weight: 500;
}

.custom-hours input:focus,
.custom-datetime input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.instant-reminder {
  background: #eff6ff;
  padding: 16px;
  border-radius: 12px;
  margin-top: 16px;
}

.instant-reminder .tip {
  margin: 0;
  color: #1e40af;
  display: flex;
  align-items: center;
  gap: 10px;
}

.instant-reminder .tip i {
  font-size: 18px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-confirm {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-confirm:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-confirm:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    max-height: 85vh;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }

  .quick-options {
    grid-template-columns: repeat(2, 1fr);
  }

  .option-btn {
    padding: 10px 12px;
    font-size: 13px;
  }

  .option-btn i {
    font-size: 18px;
  }
}
</style>

