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
        <span>重置</span>
      </button>
    </div>
    
    <div v-if="searchTerm || subjectFilter || statusFilter" class="filter-info">
      <span>当前筛选结果</span>
    </div>
    
    <div class="stats">
      <div class="stat-card urgent" @click="$emit('show-stat-modal', 'urgent')">
        <h3>{{ urgentCount }}</h3>
        <p>紧急</p>
      </div>
      <div class="stat-card soon" @click="$emit('show-stat-modal', 'warning')">
        <h3>{{ soonCount }}</h3>
        <p>即将到期</p>
      </div>
      <div class="stat-card total" @click="$emit('show-stat-modal', 'all')">
        <h3>{{ totalCount }}</h3>
        <p>全部作业</p>
      </div>
      <div class="stat-card completed hide-mobile" @click="$emit('show-stat-modal', 'completed')">
        <h3>{{ completedCount }}</h3>
        <p>已完成</p>
      </div>
      <div class="stat-card todos" @click="$emit('show-stat-modal', 'todos')">
        <h3>{{ todoCount }}</h3>
        <p>待办</p>
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
  padding: 24px 35px 28px;
  background: transparent;
  position: relative;
  z-index: 1;
}

.controls-row {
  display: flex;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

/* ── 搜索框 ── */
.search-box {
  flex: 1;
  min-width: 260px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 13px 44px 13px 46px;
  border: 1.5px solid rgba(14, 165, 233, 0.18);
  border-radius: 16px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(12px);
  color: #1e293b;
  font-weight: 500;
  transition: all 0.25s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.search-box input::placeholder {
  color: #94a3b8;
}

.search-box input:focus {
  outline: none;
  border-color: #0ea5e9;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1), 0 4px 16px rgba(0, 0, 0, 0.07);
}

.search-box > i {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 15px;
  pointer-events: none;
  transition: color 0.25s;
}

.search-box:focus-within > i {
  color: #0ea5e9;
}

.clear-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(148, 163, 184, 0.12);
  border: none;
  color: #94a3b8;
  cursor: pointer;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-search:hover {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
}

.clear-search i {
  font-size: 12px;
}

/* ── 下拉筛选 ── */
.filter-select {
  padding: 13px 18px;
  border: 1.5px solid rgba(14, 165, 233, 0.18);
  border-radius: 16px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(12px);
  cursor: pointer;
  color: #334155;
  font-weight: 500;
  transition: all 0.25s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%2394a3b8' d='M1 1l5 5 5-5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 38px;
}

.filter-select:focus {
  outline: none;
  border-color: #0ea5e9;
  background-color: rgba(255, 255, 255, 0.97);
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

.filter-select:hover {
  border-color: #38bdf8;
}

/* ── 重置按钮 ── */
.reset-filters {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 13px 20px;
  background: rgba(14, 165, 233, 0.08);
  border: 1.5px solid rgba(14, 165, 233, 0.2);
  border-radius: 16px;
  color: #0ea5e9;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.reset-filters:hover {
  background: rgba(14, 165, 233, 0.14);
  border-color: #0ea5e9;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.18);
}

.reset-filters i {
  font-size: 13px;
  transition: transform 0.3s ease;
}

.reset-filters:hover i {
  transform: rotate(180deg);
}

/* ── 筛选提示栏 ── */
.filter-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(14, 165, 233, 0.07);
  border: 1px solid rgba(14, 165, 233, 0.15);
  border-radius: 12px;
  color: #0284c7;
  font-size: 13px;
  font-weight: 600;
  margin-top: 10px;
  margin-bottom: 10px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 统计卡片 ── */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  padding: 20px 16px 16px;
  border-radius: 18px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
}

/* 彩色顶部细线 */
.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 18px 18px 0 0;
}

.stat-card.urgent::before {
  background: linear-gradient(90deg, #ef4444, #f87171);
}

.stat-card.soon::before {
  background: linear-gradient(90deg, #f97316, #fb923c);
}

.stat-card.total::before {
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
}

.stat-card.completed::before {
  background: linear-gradient(90deg, #22c55e, #4ade80);
}

.stat-card.todos::before {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.stat-card:hover {
  transform: translateY(-5px) scale(1.02);
  border-color: rgba(255, 255, 255, 0.9);
}

.stat-card.urgent:hover {
  box-shadow: 0 14px 32px rgba(239, 68, 68, 0.14);
}

.stat-card.soon:hover {
  box-shadow: 0 14px 32px rgba(249, 115, 22, 0.14);
}

.stat-card.total:hover {
  box-shadow: 0 14px 32px rgba(14, 165, 233, 0.14);
}

.stat-card.completed:hover {
  box-shadow: 0 14px 32px rgba(34, 197, 94, 0.14);
}

.stat-card.todos:hover {
  box-shadow: 0 14px 32px rgba(139, 92, 246, 0.14);
}

.stat-card:active {
  transform: translateY(-3px) scale(1.01);
}

.stat-card h3 {
  font-size: 2.2em;
  margin: 0 0 4px;
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1;
}

.stat-card.urgent h3 {
  color: #ef4444;
}

.stat-card.soon h3 {
  color: #f97316;
}

.stat-card.total h3 {
  color: #0ea5e9;
}

.stat-card.completed h3 {
  color: #22c55e;
}

.stat-card.todos h3 {
  color: #8b5cf6;
}

.stat-card p {
  color: #64748b;
  font-weight: 500;
  font-size: 0.82em;
  margin: 0;
  letter-spacing: 0.2px;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .stat-card.hide-mobile {
    display: none;
  }

  .controls {
    margin: 0 15px 15px;
    padding: 18px 20px;
  }

  .controls-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-box {
    min-width: auto;
  }

  .search-box input {
    padding: 12px 40px 12px 42px;
    font-size: 14px;
    border-radius: 14px;
  }

  .filter-select {
    padding: 12px 36px 12px 14px;
    font-size: 14px;
    border-radius: 14px;
  }

  .reset-filters {
    padding: 11px 16px;
    font-size: 13px;
    justify-content: center;
    border-radius: 14px;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px 12px 14px;
    border-radius: 16px;
  }

  .stat-card i {
    font-size: 1.7em;
    margin-bottom: 8px;
  }

  .stat-card h3 {
    font-size: 1.6em;
    margin-bottom: 4px;
  }

  .stat-card p {
    font-size: 0.82em;
  }
}

@media (min-width: 340px) and (max-width: 768px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .controls {
    margin: 10px;
    padding: 14px 16px;
  }

  .stats {
    gap: 10px;
  }

  .stat-card {
    padding: 14px 10px 12px;
  }

  .stat-card i {
    font-size: 1.5em;
  }

  .stat-card h3 {
    font-size: 1.4em;
  }

  .stat-card p {
    font-size: 0.78em;
  }

  .reset-filters span {
    display: none;
  }

  .reset-filters {
    padding: 11px;
    min-width: 42px;
    border-radius: 12px;
  }
}
</style>