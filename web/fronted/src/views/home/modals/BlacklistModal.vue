<template>
  <!-- 遮罩层 -->
  <Teleport to="body">
    <div v-if="show" class="bl-overlay" @click.self="$emit('close')">
      <div class="bl-panel">
        <!-- 标题栏 -->
        <div class="bl-header">
          <div class="bl-title">
            <i class="fas fa-ban"></i>
            科目黑名单管理
          </div>
          <button class="bl-close" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <!-- 提示 -->
        <div class="bl-tip">
          <i class="fas fa-info-circle"></i>
          被拉黑的科目将从主界面隐藏，且下次刷新时不再抓取该科目的作业/测试
        </div>

        <!-- 黑名单列表 -->
        <div class="bl-body">
          <div v-if="loading" class="bl-loading">
            <i class="fas fa-spinner fa-spin"></i> 加载中...
          </div>

          <div v-else-if="blacklist.length === 0" class="bl-empty">
            <i class="fas fa-check-circle"></i>
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
                  title="移出黑名单"
                  @click="removeItem(item)"
              >
                <i :class="removing === item.subject_id ? 'fas fa-spinner fa-spin' : 'fas fa-trash-restore'"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- 底部操作 -->
        <div class="bl-footer">
          <button
              v-if="blacklist.length > 0"
              :disabled="clearing"
              class="bl-btn bl-btn-clear"
              @click="clearAll"
          >
            <i :class="clearing ? 'fas fa-spinner fa-spin' : 'fas fa-trash-alt'"></i>
            {{ clearing ? '清空中...' : '清空黑名单' }}
          </button>
          <button class="bl-btn bl-btn-close" @click="$emit('close')">
            <i class="fas fa-check"></i>
            完成
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import {ref, watch} from 'vue'

export default {
  name: 'BlacklistModal',
  props: {
    show: {type: Boolean, default: false}
  },
  emits: ['close', 'updated'],
  setup(props, {emit}) {
    const blacklist = ref([])
    const loading = ref(false)
    const removing = ref(null)
    const clearing = ref(false)

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

    const removeItem = async (item) => {
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

    return {blacklist, loading, removing, clearing, removeItem, clearAll}
  }
}
</script>

<style scoped>
/* 遮罩 - z-index 高于所有卡片/Header/Controls */
.bl-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 面板 */
.bl-panel {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  width: 100%;
  max-width: 480px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.15);
  overflow: hidden;
}

/* 标题栏 */
.bl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(239, 68, 68, 0.1);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.06), rgba(248, 113, 113, 0.04));
}

.bl-title {
  font-size: 1.15em;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.bl-title i {
  color: #ef4444;
  font-size: 1em;
}

.bl-close {
  background: rgba(239, 68, 68, 0.08);
  border: none;
  border-radius: 10px;
  width: 34px;
  height: 34px;
  cursor: pointer;
  color: #ef4444;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.bl-close:hover {
  background: rgba(239, 68, 68, 0.18);
}

/* 提示 */
.bl-tip {
  margin: 14px 24px 0;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(251, 191, 36, 0.1);
  border-left: 3px solid #f59e0b;
  font-size: 12.5px;
  color: #78350f;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.bl-tip i {
  margin-top: 1px;
  flex-shrink: 0;
  color: #f59e0b;
}

/* 内容区 */
.bl-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 24px;
  min-height: 80px;
}

.bl-loading,
.bl-empty {
  text-align: center;
  padding: 28px 0;
  color: #94a3b8;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.bl-empty i {
  color: #22c55e;
  font-size: 1.2em;
}

/* 黑名单条目 */
.bl-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bl-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.12);
  transition: background 0.2s;
}

.bl-item:hover {
  background: rgba(239, 68, 68, 0.09);
}

.bl-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bl-subject-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.bl-subject-id {
  font-size: 11px;
  color: #94a3b8;
}

.bl-remove-btn {
  background: rgba(239, 68, 68, 0.1);
  border: none;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  color: #ef4444;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.bl-remove-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

.bl-remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 底部 */
.bl-footer {
  padding: 14px 24px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.bl-btn {
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-size: 13.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 7px;
  transition: all 0.2s;
}

.bl-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bl-btn-clear {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.bl-btn-clear:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.18);
}

.bl-btn-close {
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
  color: white;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.bl-btn-close:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
}

@media (max-width: 520px) {
  .bl-panel {
    max-width: 100%;
    border-radius: 16px 16px 0 0;
  }

  .bl-overlay {
    align-items: flex-end;
    padding: 0;
  }
}
</style>

