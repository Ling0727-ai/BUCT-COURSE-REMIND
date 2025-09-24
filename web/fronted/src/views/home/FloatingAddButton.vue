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
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-add:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}

.floating-add:active {
  transform: translateY(-1px) scale(0.98);
}

@media (max-width: 768px) {
  .floating-add {
    bottom: 20px;
    right: 20px;
    width: 55px;
    height: 55px;
    font-size: 18px;
  }
}
</style>