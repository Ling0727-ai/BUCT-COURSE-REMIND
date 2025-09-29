<template>
  <div v-if="show" class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content confirm-modal" @click.stop>
      <div class="modal-header">
        <h3><i class="fas fa-exclamation-triangle"></i> 确认操作</h3>
      </div>
      <div class="modal-body">
        <p class="confirm-message">{{ message }}</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('cancel')">取消</button>
        <button class="btn btn-danger" @click="$emit('confirm')">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: ''
    }
  },
  emits: ['confirm', 'cancel']
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  max-width: 450px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.confirm-modal {
  max-width: 450px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 25px 30px 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #667eea;
  font-size: 1.4em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h3 i {
  color: #f39c12;
  text-shadow: 0 2px 10px rgba(243, 156, 18, 0.3);
}

.modal-body {
  padding: 25px 30px;
}

.confirm-message {
  font-size: 16px;
  line-height: 1.6;
  color: #374151;
  text-align: center;
  margin: 0;
  padding: 10px 0;
  white-space: pre-line;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: rgba(248, 250, 252, 0.8);
  border-top: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0 0 20px 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-align: center;
  font-weight: 600;
  min-width: 100px;
}

.btn-secondary {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  color: #64748b;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
  color: #475569;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(100, 116, 139, 0.2);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}
</style>