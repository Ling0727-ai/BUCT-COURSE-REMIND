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
  emits: ['refresh', 'open-url', 'show-preview', 'set-reminder', 'delete-assignment', 'mark-completed', 'undo-completed']
}
</script>

<style scoped>
.main-content {
  padding: 40px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading-state i {
  font-size: 3em;
  margin-bottom: 20px;
  color: #667eea;
}

.error-state i {
  font-size: 3em;
  margin-bottom: 20px;
  color: #e74c3c;
}

.loading-state h3, .error-state h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 25px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  color: white;
  grid-column: 1 / -1;
}

.empty-state i {
  font-size: 4.5em;
  margin-bottom: 25px;
  opacity: 0.6;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
}

.empty-state h3 {
  font-size: 1.6em;
  margin-bottom: 12px;
  font-weight: 600;
  text-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  opacity: 0.9;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px 30px 30px 30px;
  }

  .assignments-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 10px 25px 25px 25px;
  }
}
</style>