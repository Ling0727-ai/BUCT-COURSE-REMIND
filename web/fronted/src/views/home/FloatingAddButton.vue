<template>
  <button class="floating-add" @click="$emit('show-add-todo')" title="添加待办">
    <i class="fas fa-plus"></i>
  </button>
</template>

<script>
export default {
  name: 'FloatingAddButton',
  emits: ['show-add-todo']
}
</script>

<style scoped>
.floating-add {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 58px;
  height: 58px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 60%, #0891b2 100%);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 6px 24px rgba(14, 165, 233, 0.45),
  0 2px 6px rgba(0, 0, 0, 0.12);
  transition: all 0.28s cubic-bezier(0.34, 1.4, 0.64, 1);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 脉冲环 */
.floating-add::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(14, 165, 233, 0.35);
  animation: ring-pulse 2.5s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.14);
    opacity: 0;
  }
}

.floating-add:hover {
  transform: translateY(-4px) scale(1.07);
  box-shadow: 0 14px 36px rgba(14, 165, 233, 0.5),
  0 4px 10px rgba(0, 0, 0, 0.12);
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 60%, #0284c7 100%);
}

.floating-add:active {
  transform: translateY(-1px) scale(0.97);
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
}

@media (max-width: 768px) {
  .floating-add {
    bottom: 22px;
    right: 22px;
    width: 52px;
    height: 52px;
    font-size: 18px;
  }
}
</style>