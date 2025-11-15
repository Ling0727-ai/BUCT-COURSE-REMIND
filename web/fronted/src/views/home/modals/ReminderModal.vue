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
          <div v-if="assignment?.dueDate" class="info-row">
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

          <!-- 自定义小时前 -->
          <div v-if="selectedOption === 'custom-hours-before'" class="custom-hours">
            <label>
              <i class="fas fa-hourglass-start"></i>
              截止时间前几小时提醒
            </label>
            <div class="input-with-unit">
              <input
                  v-model.number="customHours"
                  min="0.5"
                  placeholder="例如：2"
                  step="0.5"
                  type="number"
              />
              <span class="unit">小时前</span>
            </div>
            <p class="input-tip">
              <i class="fas fa-info-circle"></i>
              在作业截止时间的前N小时发送提醒
            </p>
          </div>

          <!-- 自定义小时后 -->
          <div v-if="selectedOption === 'custom-hours-after'" class="custom-hours">
            <label>
              <i class="fas fa-hourglass-end"></i>
              从现在起几小时后提醒
            </label>
            <div class="input-with-unit">
              <input
                  v-model.number="customHours"
                  min="0.5"
                  placeholder="例如：2"
                  step="0.5"
                  type="number"
              />
              <span class="unit">小时后</span>
            </div>
            <p class="input-tip">
              <i class="fas fa-info-circle"></i>
              从当前时间开始，N小时后发送提醒
            </p>
          </div>

          <!-- 自定义时间 -->
          <div v-if="selectedOption === 'custom-datetime'" class="custom-datetime">
            <label>
              <i class="fas fa-calendar-alt"></i>
              选择具体提醒时间
            </label>
            <input
                v-model="customDatetime"
                :max="maxDatetime"
                type="datetime-local"
            />
          </div>

          <!-- 立即提醒 -->
          <div v-if="selectedOption === 'instant'" class="instant-reminder">
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
            :disabled="!isValid"
            class="btn btn-confirm"
            @click="confirm"
        >
          <i class="fas fa-check"></i>
          确认设置
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {computed, ref, watch} from 'vue'

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
  setup(props, {emit}) {
    const selectedOption = ref('instant')
    const customHours = ref(2)
    const customDatetime = ref('')

    const quickOptions = [
      {value: 'instant', label: '立即提醒', icon: 'fas fa-bolt'},
      {value: '1h', label: '1小时前', icon: 'fas fa-clock'},
      {value: '3h', label: '3小时前', icon: 'fas fa-clock'},
      {value: '6h', label: '6小时前', icon: 'fas fa-clock'},
      {value: '12h', label: '12小时前', icon: 'fas fa-clock'},
      {value: 'custom-hours-before', label: '自定义小时前', icon: 'fas fa-hourglass-start'},
      {value: 'custom-hours-after', label: '自定义小时后', icon: 'fas fa-hourglass-end'},
      {value: 'custom-datetime', label: '具体时间', icon: 'fas fa-calendar-alt'}
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
      if (selectedOption.value === 'custom-hours-before' || selectedOption.value === 'custom-hours-after') {
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
      } else if (selectedOption.value === 'custom-hours-before') {
        reminderConfig.hours = customHours.value
        reminderConfig.timing = 'before' // 标记为"截止前"
      } else if (selectedOption.value === 'custom-hours-after') {
        reminderConfig.hours = customHours.value
        reminderConfig.timing = 'after' // 标记为"从现在起"
      } else if (selectedOption.value === 'custom-datetime') {
        reminderConfig.datetime = customDatetime.value
      } else {
        // 快捷选项（1h, 3h, 6h, 12h）
        const hoursMap = {
          '1h': 1,
          '3h': 3,
          '6h': 6,
          '12h': 12
        }
        reminderConfig.hours = hoursMap[selectedOption.value]
        reminderConfig.timing = 'before' // 快捷选项默认为"截止前"
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
  padding: 20px; /* 四周留白 */
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
  width: min(92vw, 600px);
  max-height: 88vh; /* 略小于视口，保证可见 */
  overflow: hidden; /* 由body滚动 */
  animation: slideUp 0.3s ease-out;
  display: flex;
  flex-direction: column;
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
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
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
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1 1 auto;
  min-height: 260px;
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

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-with-unit input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s;
}

.input-with-unit .unit {
  color: #6b7280;
  font-weight: 500;
  white-space: nowrap;
  font-size: 15px;
}

.input-with-unit input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-tip {
  margin: 12px 0 0 0;
  padding: 10px 12px;
  background: #e0f2fe;
  border-left: 3px solid #3b82f6;
  border-radius: 6px;
  font-size: 13px;
  color: #1e40af;
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.5;
}

.input-tip i {
  font-size: 14px;
  flex-shrink: 0;
}

.custom-datetime input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s;
}

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
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: linear-gradient(to top, #fafbfc, #ffffff);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  min-width: 120px;
  -webkit-tap-highlight-color: transparent;
}

.btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn:active::before {
  width: 300px;
  height: 300px;
}

.btn i {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.btn-cancel {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #4b5563;
  border: 1px solid #d1d5db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.btn-cancel:hover {
  background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
  color: #1f2937;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.btn-cancel:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.btn-confirm {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  position: relative;
}

.btn-confirm::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
      45deg,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
  );
  transform: translateX(-100%) translateY(-100%) rotate(45deg);
  transition: transform 0.6s;
}

.btn-confirm:hover::after {
  transform: translateX(100%) translateY(100%) rotate(45deg);
}

.btn-confirm:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-confirm:hover i {
  transform: scale(1.1) rotate(5deg);
}

.btn-confirm:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3);
}

.btn-confirm:disabled {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  color: #6b7280;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  opacity: 0.6;
}

.btn-confirm:disabled::after {
  display: none;
}

.btn-confirm:disabled:hover {
  transform: none;
  box-shadow: none;
}

.btn-cancel i {
  color: #6b7280;
}

.btn-cancel:hover i {
  color: #1f2937;
  transform: rotate(-5deg);
}

.btn-confirm i {
  color: white;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 16px;
  }

  .modal-container {
    width: 94vw;
    max-height: 90vh;
    border-radius: 14px;
  }

  .modal-header, .modal-body, .modal-footer {
    padding-left: 18px;
    padding-right: 18px;
  }

  .modal-body {
    min-height: 300px;
  }

  .modal-footer {
    padding: 16px 18px;
  }

  .btn {
    padding: 11px 20px;
    font-size: 14px;
    min-width: 110px;
  }

  .btn i {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 14px;
  }

  .modal-container {
    width: 95vw;
    max-height: 92vh;
    border-radius: 12px;
  }

  .modal-body {
    min-height: 320px;
  }

  .modal-footer {
    padding: 14px 16px;
    gap: 10px;
  }

  .btn {
    padding: 10px 18px;
    font-size: 13px;
    min-width: 100px;
    border-radius: 10px;
  }

  .btn i {
    font-size: 14px;
  }
}

@media (max-width: 340px) {
  .modal-overlay {
    padding: 10px;
  }

  .modal-container {
    width: 96vw;
    max-height: 92vh;
    border-radius: 12px;
  }

  .modal-body {
    min-height: 320px;
  }

  .modal-footer {
    padding: 12px 14px;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn {
    padding: 9px 16px;
    font-size: 12px;
    min-width: 90px;
    flex: 1;
  }

  .btn i {
    font-size: 13px;
  }
}
</style>
