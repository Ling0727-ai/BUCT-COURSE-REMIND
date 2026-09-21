<template>
  <button class="fab" @click="$emit('show-add-todo')" title="添加待办">
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
.fab {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 52px;
  height: 52px;
  border: none;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-size: 18px;
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.fab:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.fab:active {
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .fab {
    bottom: 20px;
    right: 20px;
    width: 48px;
    height: 48px;
    font-size: 16px;
  }
}
</style>
