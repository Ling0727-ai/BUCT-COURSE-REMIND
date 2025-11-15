<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content recycle-modal" @click.stop>
      <div class="modal-header">
        <h3>
          <i class="fas fa-trash-alt"></i> 
          回收站
        </h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div v-if="items.length === 0" class="empty-recycle">
          <i class="fas fa-trash-alt"></i>
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
                <i class="fas fa-calendar-alt"></i>
                <span>截止：{{ formatSimpleDate(item.dueDate) }}</span>
              </div>
              <div class="recycle-item-actions">
                <button 
                  class="btn btn-sm btn-success"
                  @click="$emit('restore-item', item)"
                  title="恢复"
                >
                  <i class="fas fa-undo"></i> 恢复
                </button>
                <button 
                  class="btn btn-sm btn-danger"
                  @click="$emit('permanent-delete', item)"
                  title="永久删除"
                >
                  <i class="fas fa-trash"></i> 永久删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button 
          v-if="items.length > 0"
          class="btn btn-success"
          @click="$emit('restore-all')"
        >
          <i class="fas fa-undo-alt"></i> 全部恢复
        </button>
        <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecycleBinModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    items: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'restore-item', 'permanent-delete', 'restore-all'],
  methods: {
    truncateText(text, maxLength) {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    },
    formatDeleteTime(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
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
    },
    formatSimpleDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  max-width: 700px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.recycle-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
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
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(239, 68, 68, 0.1));
  border-bottom: 1px solid rgba(220, 53, 69, 0.2);
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #dc3545;
  font-size: 1.4em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h3 i {
  color: #6c757d;
  text-shadow: 0 2px 10px rgba(108, 117, 125, 0.3);
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

.empty-recycle {
  text-align: center;
  padding: 50px 20px;
  color: #6b7280;
}

.empty-recycle i {
  font-size: 4em;
  margin-bottom: 20px;
  opacity: 0.4;
  color: #9ca3af;
}

.empty-recycle p {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-recycle small {
  font-size: 14px;
  opacity: 0.7;
}

.recycle-items-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recycle-item {
  background: linear-gradient(135deg, rgba(248, 249, 250, 0.8), rgba(255, 255, 255, 0.9));
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #6c757d;
  transition: all 0.3s ease;
  position: relative;
}

.recycle-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.02), transparent);
  border-radius: 12px;
  pointer-events: none;
}

.recycle-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
  border-left-color: #495057;
}

.recycle-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.recycle-item-subject {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
}

.recycle-item-type {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.delete-time {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
  background: rgba(156, 163, 175, 0.1);
  padding: 3px 8px;
  border-radius: 10px;
}

.recycle-item-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.4;
  text-decoration: line-through;
  text-decoration-color: rgba(107, 114, 128, 0.5);
  opacity: 0.8;
}

.recycle-item-content {
  color: #9ca3af;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 15px;
  opacity: 0.8;
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
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.recycle-item-actions {
  display: flex;
  gap: 8px;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  gap: 15px;
  background: rgba(248, 250, 252, 0.8);
  border-top: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0 0 20px 20px;
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
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
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

.btn-success {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-success:hover {
  background: linear-gradient(135deg, #219a52, #27ae60);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: 1px solid rgba(220, 53, 69, 0.3);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c82333, #a71e2a);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(220, 53, 69, 0.4);
}
</style>