<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content statistics-modal" @click.stop>
      <div class="modal-header">
        <h3>
          <i :class="getStatIcon(type)"></i> 
          {{ getStatTitle(type) }}
        </h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div v-if="items.length === 0" class="empty-stat">
          <i class="fas fa-inbox"></i>
          <p>暂无{{ getStatTitle(type) }}</p>
        </div>
        <div v-else class="stat-items-grid">
          <AssignmentCard
            v-for="item in items" 
            :key="item.id"
            :assignment="item"
            @open-url="$emit('open-url', $event)"
            @show-preview="$emit('show-preview', $event)"
            @set-reminder="$emit('set-reminder', $event)"
            @delete-assignment="$emit('delete-assignment', $event)"
            @mark-completed="$emit('mark-completed', $event)"
            @undo-completed="$emit('undo-completed', $event)"
            @blacklist-subject="$emit('blacklist-subject', $event)"
          />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
import AssignmentCard from '../AssignmentCard.vue'

export default {
  name: 'StatisticsModal',
  components: {
    AssignmentCard
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: ''
    },
    items: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'open-url', 'show-preview', 'set-reminder', 'delete-assignment', 'mark-completed', 'undo-completed', 'blacklist-subject'],
  methods: {
    getStatTitle(type) {
      const titles = {
        'urgent': '紧急作业',
        'warning': '即将到期',
        'completed': '已完成',
        'todos': '待办事项',
        'all': '全部作业'
      }
      return titles[type] || '作业列表'
    },
    getStatIcon(type) {
      const icons = {
        'urgent': 'fas fa-exclamation-triangle',
        'warning': 'fas fa-clock',
        'completed': 'fas fa-check-circle',
        'todos': 'fas fa-list-check',
        'all': 'fas fa-tasks'
      }
      return icons[type] || 'fas fa-list'
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
  max-width: 90vw;
  width: 1200px;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.statistics-modal {
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
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #667eea;
  font-size: 1.4em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
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
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px 30px;
}

.empty-stat {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-stat i {
  font-size: 3em;
  margin-bottom: 15px;
  opacity: 0.5;
}

.stat-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 25px;
  padding: 10px 0;
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
</style>