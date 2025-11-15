<template>
  <div class="header">
    <div class="header-content">
      <h1><i class="fas fa-graduation-cap"></i> 作业管理系统</h1>
      <p>智能汇总所有科目作业，永不错过截止日期</p>
    </div>
    <div class="header-actions">
      <button class="refresh-btn" title="刷新数据" @click="$emit('refresh')">
        <i class="fas fa-sync-alt"></i>
      </button>
      <button class="recycle-btn" title="回收站" @click="$emit('show-recycle-bin')">
        <i class="fas fa-trash-alt"></i>
      </button>
      <div class="current-time">
        <i class="fas fa-clock"></i>
        {{ currentTime }}
      </div>
      <div class="user-info" v-if="user">
        <span class="username">{{ user.username }}</span>
        <button class="logout-btn" @click="$emit('logout')">
          <i class="fas fa-sign-out-alt"></i>
          登出
        </button>
      </div>
      <router-link to="/settings" class="settings-btn">
        <i class="fas fa-cog"></i>
        <span>设置</span>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Header',
  props: {
    currentTime: {
      type: String,
      required: true
    },
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['show-recycle-bin', 'logout', 'refresh']
}
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.1);
  color: #0f172a;
  padding: 25px 35px;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  z-index: 1;
}

.header-content {
  text-align: left;
  flex: 1;
  z-index: 2;
  position: relative;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 2;
  position: relative;
}

.refresh-btn,
.recycle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9em;
  background: rgba(14, 165, 233, 0.1);
  backdrop-filter: blur(10px);
  padding: 10px 12px;
  border-radius: 25px;
  border: 1px solid rgba(14, 165, 233, 0.2);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  color: #0ea5e9;
  cursor: pointer;
  min-width: 44px;
  height: 44px;
}

.refresh-btn:hover,
.recycle-btn:hover {
  background: rgba(14, 165, 233, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

.refresh-btn:active {
  transform: translateY(-2px) rotate(180deg);
}

.refresh-btn i,
.recycle-btn i {
  font-size: 1.1em;
  color: #0ea5e9;
  transition: transform 0.3s ease;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  background: rgba(14, 165, 233, 0.08);
  backdrop-filter: blur(10px);
  padding: 10px 18px;
  border-radius: 25px;
  border: 1px solid rgba(14, 165, 233, 0.15);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  color: #334155;
  font-weight: 500;
}

.current-time i {
  color: #0ea5e9;
}

.current-time:hover {
  background: rgba(14, 165, 233, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(14, 165, 233, 0.05), transparent);
  animation: shimmer 8s infinite;
  z-index: 0;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.header h1 {
  font-size: 2.2em;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
  font-weight: 700;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header h1 i {
  color: #0ea5e9;
}

.header p {
  color: #475569;
  font-size: 1em;
  position: relative;
  z-index: 2;
}

.settings-btn {
  color: #334155;
  text-decoration: none;
  font-size: 0.9em;
  padding: 12px 18px;
  border-radius: 25px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  z-index: 1;
  background: rgba(14, 165, 233, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(14, 165, 233, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
}

.settings-btn i {
  font-size: 1em;
  color: #0ea5e9;
  transition: transform 0.3s ease;
}

.settings-btn span {
  color: #334155;
}

.settings-btn:hover {
  background: rgba(14, 165, 233, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

.settings-btn:hover i {
  transform: rotate(90deg);
  color: #0284c7;
}

.settings-btn:hover span {
  color: #0f172a;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(14, 165, 233, 0.08);
  padding: 10px 20px;
  border-radius: 25px;
  border: 1px solid rgba(14, 165, 233, 0.15);
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(14, 165, 233, 0.12);
}

.username {
  font-weight: 600;
  font-size: 0.95em;
  color: #0f172a;
}

.logout-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-align: center;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

@media (max-width: 768px) {
  .header {
    margin: 15px;
    padding: 20px 25px;
    flex-direction: column;
    gap: 20px;
  }

  .header h1 {
    font-size: 1.8em;
  }

  .header p {
    font-size: 0.9em;
  }

  .header-actions {
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .header {
    margin: 10px;
    padding: 15px 20px;
  }
}
</style>