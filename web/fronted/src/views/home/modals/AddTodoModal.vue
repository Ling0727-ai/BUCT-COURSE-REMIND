<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3><i class="fas fa-plus-circle"></i> 添加待办事项</h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label for="todoTitle">名称 *</label>
          <input 
            id="todoTitle"
            type="text" 
            :value="todo.title" 
            @input="$emit('update:todo', { ...todo, title: $event.target.value })"
            placeholder="请输入待办事项名称"
            maxlength="100"
            @keyup.enter="$emit('add')"
          >
        </div>
        <div class="form-group">
          <label for="todoHours">预计时间</label>
          <div class="hours-input-group">
            <input 
              id="todoHours"
              type="number" 
              :value="todo.hours"
              @input="$emit('update:todo', { ...todo, hours: parseFloat($event.target.value) || 1 })"
              placeholder="1"
              min="0.5"
              max="168"
              step="0.5"
            >
            <span class="hours-suffix">小时后</span>
          </div>
        </div>
        <div class="form-group">
          <label for="todoDescription">备注</label>
          <textarea 
            id="todoDescription"
            :value="todo.description" 
            @input="$emit('update:todo', { ...todo, description: $event.target.value })"
            placeholder="请输入备注信息（可选）"
            rows="3"
            maxlength="500"
          ></textarea>
        </div>
        <div class="form-group">
          <label for="todoPriority">优先级</label>
          <select 
            id="todoPriority" 
            :value="todo.priority"
            @change="$emit('update:todo', { ...todo, priority: $event.target.value })"
          >
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">取消</button>
        <button 
          class="btn btn-primary" 
          @click="$emit('add')"
          :disabled="!todo.title.trim() || adding"
        >
          <span v-if="!adding">
            <i class="fas fa-plus"></i> 添加
          </span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> 添加中...
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddTodoModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    todo: {
      type: Object,
      required: true
    },
    adding: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'add', 'update:todo']
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
  z-index: 1000;
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
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
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
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h3 i {
  color: #667eea;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2em;
  color: #6c757d;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #495057;
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.95em;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: #f8f9fa;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.hours-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hours-input-group input {
  flex: 1;
  min-width: 0;
}

.hours-suffix {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  padding: 0 4px;
}

.modal-footer {
  padding: 20px 30px 25px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-align: center;
  font-weight: 500;
  min-width: 100px;
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #5a6268, #3d4043);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}
</style>