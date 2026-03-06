<template>
  <div class="header">
    <div class="header-content">
      <h1>作业管理系统</h1>
      <p>汇总所有科目作业，不错过任何截止日期</p>
    </div>
    <div class="header-actions">
      <button class="refresh-btn" title="刷新数据" @click="$emit('refresh')">
        <i class="fas fa-sync-alt"></i>
      </button>
      <button class="recycle-btn" title="回收站" @click="$emit('show-recycle-bin')">
        <i class="fas fa-trash-alt"></i>
      </button>
      <button class="blacklist-btn" title="管理黑名单科目" @click="$emit('show-blacklist')">
        <i class="fas fa-ban"></i>
      </button>
      <div class="current-time">{{ currentTime }}</div>
      <div class="user-info" v-if="user">
        <span class="username">{{ user.username }}</span>
        <button class="logout-btn" @click="$emit('logout')">退出</button>
      </div>
      <router-link class="settings-btn" to="/settings">设置</router-link>
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
  emits: ['show-recycle-bin', 'logout', 'refresh', 'show-blacklist']
}
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(14, 165, 233, 0.1);
  color: #0f172a;
  padding: 22px 32px;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin: 20px;
  border-radius: 22px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07), 0 1px 4px rgba(0, 0, 0, 0.04);
  z-index: 1;
}

/* 顶部高光线 */
.header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.4), transparent);
  pointer-events: none;
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(14, 165, 233, 0.04), transparent);
  animation: shimmer 9s infinite;
  z-index: 0;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
}

.header-content {
  text-align: left;
  flex: 1;
  z-index: 2;
  position: relative;
}

.header h1 {
  font-size: 1.9em;
  margin-bottom: 5px;
  position: relative;
  z-index: 2;
  font-weight: 800;
  background: linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 11px;
  letter-spacing: -0.3px;
}

.header h1 i {
  -webkit-text-fill-color: #0ea5e9;
  color: #0ea5e9;
  filter: drop-shadow(0 2px 8px rgba(14, 165, 233, 0.3));
}

.header p {
  color: #64748b;
  font-size: 0.92em;
  position: relative;
  z-index: 2;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 2;
  position: relative;
  flex-wrap: wrap;
}

.refresh-btn,
.recycle-btn,
.blacklist-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(14, 165, 233, 0.08);
  backdrop-filter: blur(10px);
  padding: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.18);
  transition: all 0.25s ease;
  color: #0ea5e9;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.refresh-btn:hover,
.recycle-btn:hover {
  background: rgba(14, 165, 233, 0.14);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.18);
  border-color: rgba(14, 165, 233, 0.3);
}

.refresh-btn:active {
  transform: translateY(-1px) rotate(180deg);
}

.refresh-btn i, .recycle-btn i {
  font-size: 1em;
  color: #0ea5e9;
  transition: transform 0.35s ease;
}

.blacklist-btn {
  background: rgba(239, 68, 68, 0.07);
  border-color: rgba(239, 68, 68, 0.18);
  color: #ef4444;
}

.blacklist-btn:hover {
  background: rgba(239, 68, 68, 0.13);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.16);
  border-color: rgba(239, 68, 68, 0.3);
}

.blacklist-btn i {
  font-size: 1em;
  color: #ef4444;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.86em;
  background: rgba(14, 165, 233, 0.06);
  backdrop-filter: blur(10px);
  padding: 9px 16px;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.14);
  color: #475569;
  font-weight: 600;
  letter-spacing: 0.3px;
  transition: all 0.25s ease;
  font-variant-numeric: tabular-nums;
}

.current-time i {
  color: #0ea5e9;
  font-size: 0.95em;
}

.current-time:hover {
  background: rgba(14, 165, 233, 0.1);
  transform: translateY(-1px);
}

.settings-btn {
  color: #334155;
  text-decoration: none;
  font-size: 0.86em;
  padding: 9px 16px;
  border-radius: 12px;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  position: relative;
  z-index: 1;
  background: rgba(14, 165, 233, 0.07);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(14, 165, 233, 0.15);
  font-weight: 600;
  white-space: nowrap;
}

.settings-btn i {
  font-size: 0.95em;
  color: #0ea5e9;
  transition: transform 0.35s ease;
}

.settings-btn span {
  color: #334155;
}

.settings-btn:hover {
  background: rgba(14, 165, 233, 0.13);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.16);
  border-color: rgba(14, 165, 233, 0.28);
}

.settings-btn:hover i {
  transform: rotate(90deg);
}

.settings-btn:hover span {
  color: #0f172a;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(14, 165, 233, 0.07);
  padding: 8px 16px;
  border-radius: 14px;
  border: 1px solid rgba(14, 165, 233, 0.14);
  transition: all 0.25s ease;
}

.user-info:hover {
  background: rgba(14, 165, 233, 0.11);
}

.username {
  font-weight: 700;
  font-size: 0.9em;
  color: #0f172a;
}

.logout-btn {
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.18);
  padding: 7px 13px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 600;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.14);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.18);
}

@media (max-width: 768px) {
  .header {
    margin: 15px;
    padding: 18px 22px;
    flex-direction: column;
    gap: 16px;
  }

  .header h1 {
    font-size: 1.55em;
  }

  .header p {
    font-size: 0.88em;
  }

  .header-actions {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .header {
    margin: 10px;
    padding: 14px 18px;
  }

  .header h1 {
    font-size: 1.35em;
  }

  .current-time {
    font-size: 0.8em;
    padding: 7px 12px;
  }
}
</style>
