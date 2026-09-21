<template>
  <BaseModal
    :model-value="show"
    title="设置提醒时间"
    icon="fas fa-bell"
    width="600px"
    panel-class="reminder-modal"
    @update:model-value="onUpdate"
  >
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
            type="button"
            @click="selectQuickOption(option.value)"
        >
          <i :class="option.icon" aria-hidden="true"></i>
          <span>{{ option.label }}</span>
        </button>
      </div>

      <!-- 自定义小时前 -->
      <div v-if="selectedOption === 'custom-hours-before'" class="custom-hours">
        <label for="reminderHoursBefore">
          <i class="fas fa-hourglass-start" aria-hidden="true"></i>
          截止时间前几小时提醒
        </label>
        <div class="input-with-unit">
          <input
              id="reminderHoursBefore"
              v-model.number="customHours"
              min="0.5"
              placeholder="例如：2"
              step="0.5"
              type="number"
          />
          <span class="unit">小时前</span>
        </div>
        <p class="input-tip">
          <i class="fas fa-info-circle" aria-hidden="true"></i>
          在作业截止时间的前N小时发送提醒
        </p>
      </div>

      <!-- 自定义小时后 -->
      <div v-if="selectedOption === 'custom-hours-after'" class="custom-hours">
        <label for="reminderHoursAfter">
          <i class="fas fa-hourglass-end" aria-hidden="true"></i>
          从现在起几小时后提醒
        </label>
        <div class="input-with-unit">
          <input
              id="reminderHoursAfter"
              v-model.number="customHours"
              min="0.5"
              placeholder="例如：2"
              step="0.5"
              type="number"
          />
          <span class="unit">小时后</span>
        </div>
        <p class="input-tip">
          <i class="fas fa-info-circle" aria-hidden="true"></i>
          从当前时间开始，N小时后发送提醒
        </p>
      </div>

      <!-- 自定义时间 -->
      <div v-if="selectedOption === 'custom-datetime'" class="custom-datetime">
        <label for="reminderDatetime">
          <i class="fas fa-calendar-alt" aria-hidden="true"></i>
          选择具体提醒时间
        </label>
        <input
            id="reminderDatetime"
            v-model="customDatetime"
            :max="maxDatetime"
            type="datetime-local"
        />
      </div>

      <!-- 立即提醒 -->
      <div v-if="selectedOption === 'instant'" class="instant-reminder">
        <p class="tip">
          <i class="fas fa-info-circle" aria-hidden="true"></i>
          将立即发送提醒到您的注册邮箱
        </p>
      </div>
    </div>

    <template #footer>
      <button type="button" class="btn btn-cancel" @click="close">
        <i class="fas fa-times" aria-hidden="true"></i>
        取消
      </button>
      <button
          :disabled="!isValid"
          class="btn btn-confirm"
          @click="confirm"
      >
        <i class="fas fa-check" aria-hidden="true"></i>
        确认设置
      </button>
    </template>
  </BaseModal>
</template>

<script lang="ts">
import {computed, defineComponent, ref, watch} from 'vue'
import type { PropType } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import type { Assignment, ReminderConfig } from '../../home.data'
import { toDatetimeLocalValue, parseDueDate } from '@/utils/datetime'

type ReminderOption =
  | 'instant'
  | '1h'
  | '3h'
  | '6h'
  | '12h'
  | 'custom-hours-before'
  | 'custom-hours-after'
  | 'custom-datetime'

const QUICK_HOURS: Record<string, number> = { '1h': 1, '3h': 3, '6h': 6, '12h': 12 }

export default defineComponent({
  name: 'ReminderModal',
  components: { BaseModal },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    assignment: {
      type: Object as PropType<Assignment | null>,
      default: null
    }
  },
  emits: ['close', 'confirm'],
  setup(props, {emit}) {
    const selectedOption = ref<ReminderOption>('instant')
    const customHours = ref(2)
    const customDatetime = ref('')

    const onUpdate = (value: boolean) => {
      if (!value) {
        emit('close')
      }
    }

    const quickOptions: Array<{ value: ReminderOption; label: string; icon: string }> = [
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
    const maxDatetime = computed(() => toDatetimeLocalValue(props.assignment?.dueDate))

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

    const selectQuickOption = (value: ReminderOption) => {
      selectedOption.value = value
    }

    const formatDueDate = (dateString: string): string => {
      const date = parseDueDate(dateString)
      if (!date) return ''

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

      const reminderConfig: ReminderConfig = {
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
        reminderConfig.hours = QUICK_HOURS[selectedOption.value]
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
      confirm,
      onUpdate
    }
  }
})
</script>

<style scoped>
.assignment-info {
  background: var(--gray-50);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: var(--font-sm);
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: var(--font-semibold);
  color: var(--text-tertiary);
  min-width: 80px;
  flex-shrink: 0;
}

.info-row .value {
  color: var(--text-primary);
}

.reminder-options h4 {
  margin: 0 0 16px 0;
  font-size: var(--font-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.quick-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.option-btn {
  padding: 10px 14px;
  border: 1px solid var(--border);
  background: var(--bg);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.option-btn i {
  font-size: 18px;
  color: var(--primary);
}

.option-btn:hover {
  border-color: var(--primary);
  background: var(--primary-subtle);
}

.option-btn.active {
  border-color: var(--primary);
  background: var(--primary-subtle);
  color: var(--primary);
  font-weight: var(--font-semibold);
}

.custom-hours,
.custom-datetime {
  background: var(--gray-50);
  border: 1px solid var(--border);
  padding: 20px;
  border-radius: var(--radius-lg);
  margin-top: 16px;
}

.custom-hours label,
.custom-datetime label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: var(--font-sm);
}

.custom-hours label i,
.custom-datetime label i {
  color: var(--primary);
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-with-unit input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  transition: all var(--transition);
  background: var(--bg);
  color: var(--text-primary);
}

.input-with-unit .unit {
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
  white-space: nowrap;
  font-size: var(--font-sm);
}

.input-with-unit input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.input-tip {
  margin: 12px 0 0 0;
  padding: 10px 12px;
  background: var(--primary-subtle);
  border-left: 3px solid var(--primary);
  border-radius: var(--radius-sm);
  font-size: var(--font-xs);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.5;
}

.input-tip i {
  font-size: 13px;
  flex-shrink: 0;
  color: var(--primary);
}

.custom-datetime input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  transition: all var(--transition);
  background: var(--bg);
  color: var(--text-primary);
  box-sizing: border-box;
}

.custom-datetime input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.instant-reminder {
  background: var(--primary-subtle);
  padding: 16px;
  border-radius: var(--radius-lg);
  margin-top: 16px;
}

.instant-reminder .tip {
  margin: 0;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--font-sm);
}

.instant-reminder .tip i {
  font-size: 16px;
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
  font-weight: var(--font-medium);
  min-width: 90px;
}

.btn i {
  font-size: 13px;
}

.btn-cancel {
  background: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.btn-cancel:hover {
  background: var(--gray-200);
}

.btn-cancel i {
  color: var(--text-tertiary);
}

.btn-confirm {
  background: var(--primary);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: var(--primary-dark);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
