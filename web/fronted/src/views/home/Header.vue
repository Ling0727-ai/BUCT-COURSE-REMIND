<template>
  <div class="header">
    <div class="header-content">
      <h1><i class="fas fa-graduation-cap"></i> 作业管理系统</h1>
      <p>智能汇总所有科目作业，永不错过截止日期</p>
    </div>
    <div class="header-actions">
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
  emits: ['show-recycle-bin', 'logout']
}
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
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
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
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

.recycle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9em;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 10px 12px;
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  color: white;
  cursor: pointer;
  min-width: 44px;
  height: 44px;
}

.recycle-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}

.recycle-btn i {
  font-size: 1em;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 10px 18px;
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.current-time:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
  animation: shimmer 6s infinite;
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
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header p {
  opacity: 0.95;
  font-size: 1em;
  position: relative;
  z-index: 2;
  text-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.settings-btn {
  color: white;
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
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
}

.settings-btn i {
  font-size: 1em;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.settings-btn span {
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(255, 255, 255, 0.2);
}

.settings-btn:hover i {
  transform: rotate(90deg);
  color: #ffffff;
  text-shadow: 0 2px 15px rgba(255, 255, 255, 0.5);
}

.settings-btn:hover span {
  color: #ffffff;
  text-shadow: 0 2px 15px rgba(255, 255, 255, 0.5);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
}

.username {
  font-weight: 600;
  font-size: 0.95em;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
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
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
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