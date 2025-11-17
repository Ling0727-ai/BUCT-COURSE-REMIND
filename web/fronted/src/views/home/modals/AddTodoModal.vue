<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3><i class="fas fa-plus-circle"></i> 添加待办事项</h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label for="todoTitle">名称 *</label>
          <input 
            id="todoTitle"
            type="text" 
            :value="todo.title" 
            @input="$emit('update:todo', { ...todo, title: $event.target.value })"
            placeholder="请输入待办事项名称"
            maxlength="100"
            @keyup.enter="handleAdd"
          >
        </div>

        <div class="form-group">
          <label for="todoDeadline">
            <i class="fas fa-calendar-alt"></i>
            截止时间 (DDL) *
          </label>

          <!-- 快捷选项 -->
          <div class="quick-options">
            <button
              v-for="option in quickTimeOptions"
              :key="option.value"
              :class="['option-btn', { active: selectedQuickOption === option.value }]"
              @click="selectQuickTime(option.value)"
              type="button"
            >
              <i :class="option.icon"></i>
              <span>{{ option.label }}</span>
            </button>
          </div>

          <!-- 日期时间选择器 -->
          <div class="datetime-picker">
            <input
              id="todoDeadline"
              type="datetime-local"
              :value="deadlineInput"
              @input="handleDeadlineInput($event.target.value)"
              :min="minDatetime"
              class="datetime-input"
            >
            <span class="datetime-hint">
              <i class="fas fa-info-circle"></i>
              设置待办事项的截止时间
            </span>
          </div>
        </div>

        <div class="form-group">
          <label for="todoDescription">备注</label>
          <textarea 
            id="todoDescription"
            :value="todo.description" 
            @input="$emit('update:todo', { ...todo, description: $event.target.value })"
            placeholder="请输入备注信息（可选）"
            rows="3"
            maxlength="500"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="todoPriority">优先级</label>
          <select 
            id="todoPriority" 
            :value="todo.priority"
            @change="$emit('update:todo', { ...todo, priority: $event.target.value })"
          >
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">
          <i class="fas fa-times"></i>
          取消
        </button>
        <button
          class="btn btn-primary" 
          @click="handleAdd"
          :disabled="!isValid || adding"
        >
          <span v-if="!adding">
            <i class="fas fa-plus"></i> 添加
          </span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> 添加中...
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'AddTodoModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    todo: {
      type: Object,
      required: true
    },
    adding: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'add', 'update:todo'],
  setup(props, { emit }) {
    const selectedQuickOption = ref('')
    const deadlineInput = ref('')

    // 快捷时间选项
    const quickTimeOptions = [
      { value: '1h', label: '1小时后', icon: 'fas fa-clock' },
      { value: '3h', label: '3小时后', icon: 'fas fa-clock' },
      { value: '6h', label: '6小时后', icon: 'fas fa-clock' },
      { value: '12h', label: '12小时后', icon: 'fas fa-clock' },
      { value: '1d', label: '1天后', icon: 'fas fa-calendar-day' },
      { value: '3d', label: '3天后', icon: 'fas fa-calendar-week' },
      { value: '1w', label: '1周后', icon: 'fas fa-calendar-alt' }
    ]

    // 最小可选时间（当前时间）
    const minDatetime = computed(() => {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day}T${hours}:${minutes}`
    })

    // 验证表单是否有效
    const isValid = computed(() => {
      if (!props.todo.title || !props.todo.title.trim()) return false
      if (!deadlineInput.value) return false

      const selectedTime = new Date(deadlineInput.value)
      const now = new Date()
      return selectedTime > now
    })

    // 选择快捷时间
    const selectQuickTime = (value) => {
      selectedQuickOption.value = value

      const now = new Date()

      // 根据选项计算目标时间（毫秒）
      const timeMap = {
        '1h': 3600000,       // 1 hour
        '3h': 10800000,      // 3 hours
        '6h': 21600000,      // 6 hours
        '12h': 43200000,     // 12 hours
        '1d': 86400000,      // 1 day
        '3d': 259200000,     // 3 days
        '1w': 604800000      // 1 week
      }

      const targetDate = new Date(now.getTime() + timeMap[value])

      // 格式化为 datetime-local 格式
      const year = targetDate.getFullYear()
      const month = String(targetDate.getMonth() + 1).padStart(2, '0')
      const day = String(targetDate.getDate()).padStart(2, '0')
      const hours = String(targetDate.getHours()).padStart(2, '0')
      const minutes = String(targetDate.getMinutes()).padStart(2, '0')

      deadlineInput.value = `${year}-${month}-${day}T${hours}:${minutes}`
      updateTodoDeadline(deadlineInput.value)
    }

    // 处理日期时间输入
    const handleDeadlineInput = (value) => {
      deadlineInput.value = value
      selectedQuickOption.value = '' // 清除快捷选项高亮
      updateTodoDeadline(value)
    }

    // 更新 todo 对象的截止时间
    const updateTodoDeadline = (datetimeStr) => {
      if (!datetimeStr) return

      const selectedDate = new Date(datetimeStr)
      const now = new Date()

      // 计算小时差（用于兼容旧的 hours 字段）
      const hoursDiff = (selectedDate.getTime() - now.getTime()) / (1000 * 60 * 60)

      emit('update:todo', {
        ...props.todo,
        deadline: selectedDate.toISOString(),
        hours: Math.max(0.01, hoursDiff), // 保留旧字段以兼容
        timeInput: datetimeStr // 保存输入值
      })
    }

    // 处理添加操作
    const handleAdd = () => {
      if (isValid.value && !props.adding) {
        emit('add')
      }
    }

    // 监听弹窗显示状态，初始化默认值
    watch(() => props.show, (newVal) => {
      if (newVal) {
        if (!props.todo.timeInput) {
          // 默认设置为24小时后
          selectQuickTime('1d')
        } else {
          deadlineInput.value = props.todo.timeInput
        }
      } else {
        // 关闭时重置
        selectedQuickOption.value = ''
        deadlineInput.value = ''
      }
    })

    return {
      selectedQuickOption,
      deadlineInput,
      quickTimeOptions,
      minDatetime,
      isValid,
      selectQuickTime,
      handleDeadlineInput,
      handleAdd
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
  padding: 20px;
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
  width: min(92vw, 600px);
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
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
  flex-shrink: 0;
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
  flex: 1 1 auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.95em;
}

.form-group label i {
  color: #667eea;
}

.form-group input[type="text"],
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

/* 快捷选项按钮 */
.quick-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.option-btn {
  padding: 12px 16px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 2px solid #dee2e6;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #495057;
}

.option-btn i {
  font-size: 18px;
  color: #6c757d;
}

.option-btn:hover {
  background: linear-gradient(135deg, #e9ecef, #dee2e6);
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.option-btn.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: #667eea;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.option-btn.active i {
  color: white;
}

/* 日期时间选择器 */
.datetime-picker {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.datetime-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s ease;
  background: #f8f9fa;
  box-sizing: border-box;
  font-family: inherit;
  color: #2c3e50;
}

.datetime-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.datetime-hint {
  color: #6c757d;
  font-size: 12px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.datetime-hint i {
  color: #3b82f6;
}

.modal-footer {
  padding: 20px 30px 25px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
  font-weight: 600;
  min-width: 110px;
}

.btn i {
  font-size: 14px;
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  color: white;
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #5a6268, #495057);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .modal-content {
    max-width: 95vw;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 20px;
    padding-right: 20px;
  }

  .quick-options {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .option-btn {
    padding: 10px 12px;
    font-size: 12px;
  }

  .option-btn i {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .modal-header h3 {
    font-size: 1.2em;
  }

  .btn {
    padding: 10px 18px;
    font-size: 13px;
    min-width: 90px;
  }
}
</style>