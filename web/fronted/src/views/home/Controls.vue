<template>
  <div class="controls">
    <div class="controls-row">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          :value="searchTerm" 
          @input="$emit('update:searchTerm', $event.target.value)"
          placeholder="搜索作业标题或科目..."
        >
      </div>
      <select 
        class="filter-select" 
        :value="subjectFilter" 
        @change="$emit('update:subjectFilter', $event.target.value)"
      >
        <option value="">全部科目</option>
        <option v-for="subject in subjects" :key="subject" :value="subject">{{ subject }}</option>
      </select>
      <select 
        class="filter-select" 
        :value="statusFilter" 
        @change="$emit('update:statusFilter', $event.target.value)"
      >
        <option value="">全部状态</option>
        <option value="urgent">紧急</option>
        <option value="warning">即将到期</option>
        <option value="normal">正常</option>
        <option value="completed">已完成</option>
      </select>
    </div>
    
    <div class="stats">
      <div class="stat-card urgent" @click="$emit('show-stat-modal', 'urgent')">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>{{ urgentCount }}</h3>
        <p>紧急作业</p>
      </div>
      <div class="stat-card soon" @click="$emit('show-stat-modal', 'warning')">
        <i class="fas fa-clock"></i>
        <h3>{{ soonCount }}</h3>
        <p>即将到期</p>
      </div>
      <div class="stat-card total" @click="$emit('show-stat-modal', 'all')">
        <i class="fas fa-tasks"></i>
        <h3>{{ totalCount }}</h3>
        <p>总作业数</p>
      </div>
      <div class="stat-card completed" @click="$emit('show-stat-modal', 'completed')">
        <i class="fas fa-check-circle"></i>
        <h3>{{ completedCount }}</h3>
        <p>已完成</p>
      </div>
      <div class="stat-card todos" @click="$emit('show-stat-modal', 'todos')">
        <i class="fas fa-list-check"></i>
        <h3>{{ todoCount }}</h3>
        <p>待办事项</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Controls',
  props: {
    searchTerm: {
      type: String,
      required: true
    },
    subjectFilter: {
      type: String,
      required: true
    },
    statusFilter: {
      type: String,
      required: true
    },
    subjects: {
      type: Array,
      required: true
    },
    urgentCount: {
      type: Number,
      required: true
    },
    soonCount: {
      type: Number,
      required: true
    },
    totalCount: {
      type: Number,
      required: true
    },
    completedCount: {
      type: Number,
      required: true
    },
    todoCount: {
      type: Number,
      required: true
    }
  },
  emits: ['update:searchTerm', 'update:subjectFilter', 'update:statusFilter', 'show-stat-modal']
}
</script>

<style scoped>
.controls {
  padding: 30px 40px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.controls-row {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  min-width: 300px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 15px 20px 15px 50px;
  border: 2px solid #ddd;
  border-radius: 25px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.search-box i {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.filter-select {
  padding: 15px 20px;
  border: 2px solid #ddd;
  border-radius: 25px;
  font-size: 16px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 25px 20px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(102, 126, 234, 0.05));
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.stat-card:active {
  transform: translateY(-6px) scale(1.01);
}

.stat-card i {
  font-size: 2.2em;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.stat-card.urgent i { 
  color: #e74c3c;
  text-shadow: 0 2px 10px rgba(231, 76, 60, 0.3);
}
.stat-card.soon i { 
  color: #f39c12;
  text-shadow: 0 2px 10px rgba(243, 156, 18, 0.3);
}
.stat-card.total i { 
  color: #667eea;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}
.stat-card.completed i { 
  color: #27ae60;
  text-shadow: 0 2px 10px rgba(39, 174, 96, 0.3);
}
.stat-card.todos i { 
  color: #9b59b6;
  text-shadow: 0 2px 10px rgba(155, 89, 182, 0.3);
}

.stat-card h3 {
  font-size: 2.2em;
  margin-bottom: 8px;
  color: #1f2937;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.stat-card p {
  color: #6b7280;
  font-weight: 500;
  font-size: 0.95em;
  position: relative;
  z-index: 1;
  margin: 0;
}

@media (max-width: 768px) {
  .controls {
    margin: 0 15px 15px 15px;
    padding: 20px 25px;
  }

  .controls-row {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .search-box {
    min-width: auto;
  }

  .search-box input,
  .filter-select {
    padding: 12px 16px 12px 45px;
    font-size: 14px;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }

  .stat-card {
    padding: 20px 15px;
  }

  .stat-card h3 {
    font-size: 1.8em;
  }
}

@media (max-width: 480px) {
  .controls {
    margin: 10px;
    padding: 15px 20px;
  }

  .stats {
    grid-template-columns: 1fr;
  }
}
</style>