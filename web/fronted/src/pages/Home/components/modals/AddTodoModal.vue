<template>
  <BaseModal
    :model-value="show"
    title="添加待办事项"
    icon="fas fa-plus-circle"
    width="600px"
    panel-class="add-todo-modal"
    @update:model-value="onUpdate"
  >
    <div class="form-group">
      <label for="todoTitle">名称 *</label>
      <input 
        id="todoTitle"
        type="text" 
        :value="todo.title" 
        @input="$emit('update:todo', { ...todo, title: $event.target.value })"
        placeholder="请输入待办事项名称"
        maxlength="100"
        data-autofocus
        @keyup.enter="handleAdd"
      >
    </div>

    <div class="form-group">
      <label for="todoDeadline">
        <i class="fas fa-calendar-alt" aria-hidden="true"></i>
        截止时间 (DDL) *
      </label>

      <!-- 快捷选项 -->
      <div class="quick-options">
        <button
            v-for="option in quickTimeOptions"
            :key="option.value"
            :class="['option-btn', { active: selectedQuickOption === option.value }]"
            type="button"
            @click="selectQuickTime(option.value)"
        >
          <i :class="option.icon" aria-hidden="true"></i>
          <span>{{ option.label }}</span>
        </button>
      </div>

      <!-- 日期时间选择器 -->
      <div class="datetime-picker">
        <input
            id="todoDeadline"
            :min="minDatetime"
            :value="deadlineInput"
            class="datetime-input"
            type="datetime-local"
            @input="handleDeadlineInput($event.target.value)"
        >
        <span class="datetime-hint">
          <i class="fas fa-info-circle" aria-hidden="true"></i>
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

    <template #footer>
      <button type="button" class="btn btn-secondary" @click="$emit('close')">
        <i class="fas fa-times" aria-hidden="true"></i>
        取消
      </button>
      <button
          :disabled="!isValid || adding"
          class="btn btn-primary"
        @click="handleAdd"
      >
        <span v-if="!adding">
          <i class="fas fa-plus" aria-hidden="true"></i> 添加
        </span>
        <span v-else>
          <i class="fas fa-spinner fa-spin" aria-hidden="true"></i> 添加中...
        </span>
      </button>
    </template>
  </BaseModal>
</template>

<script lang="ts">
import {computed, defineComponent, ref, watch} from 'vue'
import type { PropType } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import type { Todo } from '../../home.data'

type QuickKey = '1h' | '3h' | '6h' | '12h' | '1d' | '3d' | '1w'

const QUICK_TIME_MS: Record<QuickKey, number> = {
  '1h': 3600000,
  '3h': 10800000,
  '6h': 21600000,
  '12h': 43200000,
  '1d': 86400000,
  '3d': 259200000,
  '1w': 604800000
}

export default defineComponent({
  name: 'AddTodoModal',
  components: { BaseModal },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    todo: {
      type: Object as PropType<Partial<Todo>>,
      required: true
    },
    adding: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'add', 'update:todo'],
  setup(props, {emit}) {
    const selectedQuickOption = ref('')
    const deadlineInput = ref('')

    const onUpdate = (value: boolean) => {
      if (!value) {
        emit('close')
      }
    }

    // 快捷时间选项
    const quickTimeOptions: Array<{ value: QuickKey; label: string; icon: string }> = [
      {value: '1h', label: '1小时后', icon: 'fas fa-clock'},
      {value: '3h', label: '3小时后', icon: 'fas fa-clock'},
      {value: '6h', label: '6小时后', icon: 'fas fa-clock'},
      {value: '12h', label: '12小时后', icon: 'fas fa-clock'},
      {value: '1d', label: '1天后', icon: 'fas fa-calendar-day'},
      {value: '3d', label: '3天后', icon: 'fas fa-calendar-week'},
      {value: '1w', label: '1周后', icon: 'fas fa-calendar-alt'}
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
    const selectQuickTime = (value: QuickKey) => {
      selectedQuickOption.value = value

      const now = new Date()
      const targetDate = new Date(now.getTime() + QUICK_TIME_MS[value])

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
    const handleDeadlineInput = (value: string) => {
      deadlineInput.value = value
      selectedQuickOption.value = '' // 清除快捷选项高亮
      updateTodoDeadline(value)
    }

    // 更新 todo 对象的截止时间
    const updateTodoDeadline = (datetimeStr: string) => {
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
      handleAdd,
      onUpdate
    }
  }
})
</script>

<style scoped>
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: var(--text-primary);
  font-weight: var(--font-medium);
  font-size: var(--font-sm);
}

.form-group label i {
  color: var(--primary);
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  transition: all var(--transition);
  background: var(--bg-secondary);
  box-sizing: border-box;
  color: var(--text-primary);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* Quick options */
.quick-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.option-btn {
  padding: 10px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: var(--font-xs);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.option-btn i {
  font-size: 16px;
  color: var(--text-tertiary);
}

.option-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.option-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.option-btn.active i {
  color: white;
}

/* DateTime */
.datetime-picker {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.datetime-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  transition: all var(--transition);
  background: var(--bg-secondary);
  box-sizing: border-box;
  font-family: inherit;
  color: var(--text-primary);
}

.datetime-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.datetime-hint {
  color: var(--text-tertiary);
  font-size: var(--font-xs);
  display: flex;
  align-items: center;
  gap: 6px;
}

.datetime-hint i {
  color: var(--primary);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-sm);
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-align: center;
  font-weight: var(--font-medium);
  min-width: 90px;
}

.btn i { font-size: 13px; }

.btn-secondary {
  background: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--gray-200);
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 移动端适配 */
@media (max-width: 768px) {
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
  .btn {
    padding: 10px 18px;
    font-size: 13px;
    min-width: 90px;
  }
}
</style>