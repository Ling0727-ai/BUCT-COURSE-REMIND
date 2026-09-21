<template>
  <BaseModal
    :model-value="show"
    title="回收站"
    icon="fas fa-trash-alt"
    tone="danger"
    width="700px"
    panel-class="recycle-modal"
    @update:model-value="onUpdate"
  >
    <div v-if="items.length === 0" class="empty-recycle">
      <i class="fas fa-trash-alt" aria-hidden="true"></i>
      <p>回收站为空</p>
      <small>已删除的项目将显示在这里</small>
    </div>
    <div v-else class="recycle-items-list">
      <div
        v-for="item in items"
        :key="item.id"
        class="recycle-item"
      >
        <div class="recycle-item-header">
          <span class="recycle-item-subject">{{ item.subject }}</span>
          <span :class="['recycle-item-type', item.type]">{{ item.type }}</span>
          <span class="delete-time">{{ formatDeleteTime(item.deletedAt) }}</span>
        </div>
        <h4 class="recycle-item-title">{{ item.title }}</h4>
        <p class="recycle-item-content">{{ truncateText(item.content, 60) }}</p>
        <div class="recycle-item-footer">
          <div v-if="item.dueDate" class="recycle-item-date">
            <i class="fas fa-calendar-alt" aria-hidden="true"></i>
            <span>截止：{{ formatSimpleDate(item.dueDate) }}</span>
          </div>
          <div class="recycle-item-actions">
            <button
              class="btn btn-sm btn-success"
              @click="$emit('restore-item', item)"
              title="恢复"
            >
              <i class="fas fa-undo" aria-hidden="true"></i> 恢复
            </button>
            <button
              class="btn btn-sm btn-danger"
              @click="$emit('permanent-delete', item)"
              title="永久删除"
            >
              <i class="fas fa-trash" aria-hidden="true"></i> 永久删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        v-if="items.length > 0"
        type="button"
        class="btn btn-success"
        @click="$emit('restore-all')"
      >
        <i class="fas fa-undo-alt" aria-hidden="true"></i> 全部恢复
      </button>
      <button type="button" class="btn btn-secondary" @click="$emit('close')">关闭</button>
    </template>
  </BaseModal>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import type { RecycleBinItem } from '../../home.data'
import { parseDueDate } from '@/utils/datetime'

export default defineComponent({
  name: 'RecycleBinModal',
  components: { BaseModal },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    items: {
      type: Array as PropType<RecycleBinItem[]>,
      default: () => []
    }
  },
  emits: ['close', 'restore-item', 'permanent-delete', 'restore-all'],
  setup(_props, { emit }) {
    const onUpdate = (value: boolean) => {
      if (!value) {
        emit('close')
      }
    }

    const truncateText = (text: string | undefined, maxLength: number): string => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    const formatDeleteTime = (dateString: string): string => {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / (1000 * 60))
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

      if (diffMins < 1) return '刚刚删除'
      if (diffMins < 60) return `${diffMins}分钟前删除`
      if (diffHours < 24) return `${diffHours}小时前删除`
      if (diffDays < 7) return `${diffDays}天前删除`

      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
      }) + '删除'
    }

    const formatSimpleDate = (dateString?: string): string => {
      const date = parseDueDate(dateString)
      if (!date) return ''
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    return { onUpdate, truncateText, formatDeleteTime, formatSimpleDate }
  }
})
</script>

<style scoped>
.empty-recycle {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.empty-recycle i {
  font-size: 3em;
  margin-bottom: 15px;
  opacity: 0.5;
}

.empty-recycle p {
  font-size: var(--font-base);
  font-weight: var(--font-medium);
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.empty-recycle small {
  font-size: var(--font-sm);
  opacity: 0.7;
}

.recycle-items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recycle-item {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  border-left: 4px solid var(--gray-400);
  transition: all var(--transition);
}

.recycle-item:hover {
  box-shadow: var(--shadow-md);
}

.recycle-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.recycle-item-subject {
  background: var(--gray-500);
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: var(--font-xs);
  font-weight: var(--font-semibold);
}

.recycle-item-type {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: var(--font-semibold);
  background: var(--gray-100);
  color: var(--text-tertiary);
}

.delete-time {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-left: auto;
}

.recycle-item-title {
  font-size: var(--font-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
  text-decoration: line-through;
  text-decoration-color: var(--gray-400);
  opacity: 0.8;
}

.recycle-item-content {
  color: var(--text-tertiary);
  font-size: var(--font-sm);
  line-height: 1.5;
  margin-bottom: 12px;
}

.recycle-item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.recycle-item-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.recycle-item-actions {
  display: flex;
  gap: 8px;
}

.modal-footer {
  padding: 16px 28px 24px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 10px;
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
  min-width: 80px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: var(--font-xs);
  min-width: auto;
}

.btn-secondary {
  background: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--gray-200);
}

.btn-success {
  background: var(--green);
  color: white;
}

.btn-success:hover {
  background: #16a34a;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.btn-danger {
  background: var(--red);
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

@media (max-width: 640px) {
  .modal-header, .modal-body, .modal-footer {
    padding-left: 20px;
    padding-right: 20px;
  }
}
</style>
