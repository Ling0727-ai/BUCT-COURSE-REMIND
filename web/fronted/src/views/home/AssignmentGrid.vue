<template>
  <div class="main-content">
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <h3>加载中...</h3>
      <p>正在获取最新的作业数据</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="$emit('refresh', true)">重新加载</button>
    </div>
    
    <div v-else class="assignments-grid">
      <div v-if="assignments.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <h3>暂无作业</h3>
        <p>没有找到符合条件的作业</p>
      </div>
      <AssignmentCard
        v-for="assignment in assignments" 
        :key="assignment.id"
        :assignment="assignment"
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
</template>

<script>
import AssignmentCard from './AssignmentCard.vue'

export default {
  name: 'AssignmentGrid',
  components: {
    AssignmentCard
  },
  props: {
    assignments: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    }
  },
  emits: ['refresh', 'open-url', 'show-preview', 'set-reminder', 'delete-assignment', 'mark-completed', 'undo-completed', 'blacklist-subject']
}
</script>

<style scoped>
.main-content {
  padding: 0 35px 40px;
  position: relative;
  z-index: 1;
}

/* ── 加载/错误状态 ── */
.loading-state, .error-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
}

.loading-state i {
  font-size: 3em;
  margin-bottom: 20px;
  color: #0ea5e9;
  filter: drop-shadow(0 4px 12px rgba(14, 165, 233, 0.3));
}

.error-state i {
  font-size: 3em;
  margin-bottom: 20px;
  color: #ef4444;
  filter: drop-shadow(0 4px 12px rgba(239, 68, 68, 0.3));
}

.loading-state h3, .error-state h3 {
  font-size: 1.4em;
  margin-bottom: 10px;
  color: #1e293b;
  font-weight: 700;
}

.loading-state p, .error-state p {
  color: #64748b;
  font-size: 0.95em;
  margin-bottom: 20px;
}

/* ── 作业网格 ── */
.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
  gap: 20px;
}

/* ── 空状态 ── */
.empty-state {
  text-align: center;
  padding: 70px 20px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border-radius: 22px;
  border: 1px solid rgba(14, 165, 233, 0.12);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  grid-column: 1 / -1;
}

.empty-state i {
  font-size: 4em;
  margin-bottom: 20px;
  display: block;
  color: #94a3b8;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.08));
}

.empty-state h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
  font-weight: 700;
  color: #334155;
}

.empty-state p {
  color: #64748b;
  font-size: 0.95em;
}

/* ── 按钮 ── */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.4);
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .main-content {
    padding: 0 15px 30px;
  }

  .assignments-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0 10px 24px;
  }

  .assignments-grid {
    gap: 12px;
  }
}
</style>
