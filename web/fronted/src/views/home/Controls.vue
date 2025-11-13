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
        <button 
          v-if="searchTerm" 
          class="clear-search" 
          @click="$emit('update:searchTerm', '')"
          title="清空搜索"
        >
          <i class="fas fa-times"></i>
        </button>
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
      <button 
        v-if="searchTerm || subjectFilter || statusFilter" 
        class="reset-filters"
        @click="resetFilters"
        title="重置筛选"
      >
        <i class="fas fa-redo"></i>
        <span>重置</span>
      </button>
    </div>
    
    <div v-if="searchTerm || subjectFilter || statusFilter" class="filter-info">
      <i class="fas fa-filter"></i>
      <span>当前筛选结果</span>
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
      <div class="stat-card completed hide-mobile" @click="$emit('show-stat-modal', 'completed')">
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
  emits: ['update:searchTerm', 'update:subjectFilter', 'update:statusFilter', 'show-stat-modal'],
  methods: {
    resetFilters() {
      this.$emit('update:searchTerm', '')
      this.$emit('update:subjectFilter', '')
      this.$emit('update:statusFilter', '')
    }
  }
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
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

.search-box i {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  transition: color 0.3s ease;
}

.search-box input:focus ~ i {
  color: #0ea5e9;
}

.clear-search {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.clear-search:hover {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
}

.clear-search i {
  font-size: 14px;
}

.reset-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(14, 165, 233, 0.1);
  border: 2px solid rgba(14, 165, 233, 0.2);
  border-radius: 25px;
  color: #0ea5e9;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.reset-filters:hover {
  background: rgba(14, 165, 233, 0.15);
  border-color: #0ea5e9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

.reset-filters i {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.reset-filters:hover i {
  transform: rotate(180deg);
}

.filter-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(14, 165, 233, 0.08);
  border-radius: 16px;
  color: #0ea5e9;
  font-size: 14px;
  font-weight: 600;
  margin-top: 12px;
  margin-bottom: 12px;
  animation: fadeIn 0.3s ease;
}

.filter-info i {
  font-size: 14px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-select {
  padding: 15px 20px;
  border: 2px solid #ddd;
  border-radius: 25px;
  font-size: 16px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #334155;
  font-weight: 500;
}

.filter-select:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

.filter-select:hover {
  border-color: #0ea5e9;
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
  background: linear-gradient(135deg, transparent, rgba(14, 165, 233, 0.03));
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
  color: #ef4444;
  text-shadow: 0 2px 10px rgba(239, 68, 68, 0.2);
}
.stat-card.soon i { 
  color: #f97316;
  text-shadow: 0 2px 10px rgba(249, 115, 22, 0.2);
}
.stat-card.total i { 
  color: #0ea5e9;
  text-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
}
.stat-card.completed i { 
  color: #22c55e;
  text-shadow: 0 2px 10px rgba(34, 197, 94, 0.2);
}
.stat-card.todos i { 
  color: #8b5cf6;
  text-shadow: 0 2px 10px rgba(139, 92, 246, 0.2);
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

/* 移动端隐藏"已完成"卡片 */
@media (max-width: 768px) {
  .stat-card.hide-mobile {
    display: none;
  }
}

/* 中等屏幕优化布局 (340-768px) */
@media (min-width: 340px) and (max-width: 768px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
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

  .search-box input {
    padding: 12px 16px 12px 45px;
    font-size: 14px;
  }
  
  .filter-select {
    padding: 12px 16px;
    font-size: 14px;
  }
  
  .reset-filters {
    padding: 10px 16px;
    font-size: 14px;
    justify-content: center;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 18px 12px;
  }

  .stat-card i {
    font-size: 1.8em;
    margin-bottom: 10px;
  }

  .stat-card h3 {
    font-size: 1.6em;
    margin-bottom: 6px;
  }

  .stat-card p {
    font-size: 0.85em;
  }
  
  .filter-info {
    font-size: 13px;
    padding: 10px 16px;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .controls {
    margin: 10px;
    padding: 15px 20px;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-card {
    padding: 16px 10px;
  }

  .stat-card i {
    font-size: 1.6em;
    margin-bottom: 8px;
  }

  .stat-card h3 {
    font-size: 1.5em;
    margin-bottom: 4px;
  }

  .stat-card p {
    font-size: 0.8em;
  }
  
  .reset-filters span {
    display: none;
  }
  
  .reset-filters {
    padding: 10px;
    min-width: 40px;
  }
}
</style>