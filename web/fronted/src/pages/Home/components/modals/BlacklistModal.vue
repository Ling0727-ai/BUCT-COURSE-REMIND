<template>
  <BaseModal
    :model-value="show"
    title="科目黑名单管理"
    icon="fas fa-ban"
    tone="danger"
    width="480px"
    panel-class="blacklist-modal"
    @update:model-value="onUpdate"
  >
    <!-- 提示 -->
    <div class="bl-tip">
      <i class="fas fa-info-circle" aria-hidden="true"></i>
      被拉黑的科目将从主界面隐藏，且下次刷新时不再抓取该科目的作业/测试
    </div>

    <!-- 黑名单列表 -->
    <div class="bl-body">
      <div v-if="loading" class="bl-loading">
        <i class="fas fa-spinner fa-spin" aria-hidden="true"></i> 加载中...
      </div>

      <div v-else-if="blacklist.length === 0" class="bl-empty">
        <i class="fas fa-check-circle" aria-hidden="true"></i>
        暂无拉黑科目
      </div>

      <div v-else class="bl-list">
        <div
            v-for="item in blacklist"
            :key="item.subject_id"
            class="bl-item"
        >
          <div class="bl-item-info">
            <span class="bl-subject-name">{{ item.subject_name || item.subject_id }}</span>
            <span class="bl-subject-id">ID: {{ item.subject_id }}</span>
          </div>
          <button
              :disabled="removing === item.subject_id"
              class="bl-remove-btn"
              :aria-label="`将 ${item.subject_name || item.subject_id} 移出黑名单`"
              title="移出黑名单"
              @click="removeItem(item)"
          >
            <i :class="removing === item.subject_id ? 'fas fa-spinner fa-spin' : 'fas fa-trash-restore'" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    </div>

    <template #footer>
      <button
          v-if="blacklist.length > 0"
          :disabled="clearing"
          class="bl-btn bl-btn-clear"
          @click="clearAll"
      >
        <i :class="clearing ? 'fas fa-spinner fa-spin' : 'fas fa-trash-alt'" aria-hidden="true"></i>
        {{ clearing ? '清空中...' : '清空黑名单' }}
      </button>
      <button type="button" class="bl-btn bl-btn-close" @click="$emit('close')">
        <i class="fas fa-check" aria-hidden="true"></i>
        完成
      </button>
    </template>
  </BaseModal>
</template>

<script lang="ts">
import {defineComponent, ref, watch} from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import type { BlacklistEntry } from '../../home.data'

export default defineComponent({
  name: 'BlacklistModal',
  components: { BaseModal },
  props: {
    show: {type: Boolean, default: false}
  },
  emits: ['close', 'updated'],
  setup(props, {emit}) {
    const blacklist = ref<BlacklistEntry[]>([])
    const loading = ref(false)
    const removing = ref<string | null>(null)
    const clearing = ref(false)

    const onUpdate = (value: boolean) => {
      if (!value) {
        emit('close')
      }
    }

    const fetchBlacklist = async () => {
      loading.value = true
      try {
        const res = await fetch('/api/blacklist', {credentials: 'include'})
        if (res.ok) {
          const data = await res.json()
          blacklist.value = data.blacklist || []
        }
      } catch (e) {
        console.error('[BlacklistModal] 获取黑名单失败', e)
      } finally {
        loading.value = false
      }
    }

    const removeItem = async (item: BlacklistEntry) => {
      removing.value = item.subject_id
      try {
        const res = await fetch(`/api/blacklist/${item.subject_id}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        if (res.ok) {
          blacklist.value = blacklist.value.filter(b => b.subject_id !== item.subject_id)
          emit('updated')
        }
      } catch (e) {
        console.error('[BlacklistModal] 移除黑名单失败', e)
      } finally {
        removing.value = null
      }
    }

    const clearAll = async () => {
      clearing.value = true
      try {
        const res = await fetch('/api/blacklist', {
          method: 'DELETE',
          credentials: 'include'
        })
        if (res.ok) {
          blacklist.value = []
          emit('updated')
        }
      } catch (e) {
        console.error('[BlacklistModal] 清空黑名单失败', e)
      } finally {
        clearing.value = false
      }
    }

    watch(() => props.show, (val) => {
      if (val) fetchBlacklist()
    })

    return {blacklist, loading, removing, clearing, removeItem, clearAll, onUpdate}
  }
})
</script>

<style scoped>
.bl-tip {
  margin: 14px 24px 0;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: rgba(251, 191, 36, 0.08);
  border-left: 3px solid var(--orange);
  font-size: var(--font-xs);
  color: var(--text-secondary);
  display: flex;
  align-items: flex-start;
  gap: 8px;
  line-height: 1.5;
}

.bl-tip i {
  margin-top: 2px;
  flex-shrink: 0;
  color: var(--orange);
}

.bl-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  min-height: 80px;
}

.bl-loading,
.bl-empty {
  text-align: center;
  padding: 28px 0;
  color: var(--text-tertiary);
  font-size: var(--font-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.bl-empty i {
  color: var(--green);
  font-size: 1.2em;
}

.bl-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bl-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: var(--gray-50);
  border: 1px solid var(--border);
  transition: all var(--transition);
}

.bl-item:hover {
  background: var(--gray-100);
}

.bl-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bl-subject-name {
  font-weight: var(--font-semibold);
  font-size: var(--font-sm);
  color: var(--text-primary);
}

.bl-subject-id {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.bl-remove-btn {
  background: rgba(239, 68, 68, 0.08);
  border: none;
  border-radius: var(--radius-sm);
  width: 32px;
  height: 32px;
  cursor: pointer;
  color: var(--red);
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  flex-shrink: 0;
}

.bl-remove-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.16);
}

.bl-remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bl-btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  display: flex;
  align-items: center;
  gap: 7px;
  transition: all var(--transition);
}

.bl-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bl-btn-clear {
  background: rgba(239, 68, 68, 0.08);
  color: var(--red);
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.bl-btn-clear:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.15);
}

.bl-btn-close {
  background: var(--primary);
  color: white;
}

.bl-btn-close:hover {
  background: var(--primary-dark);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>
