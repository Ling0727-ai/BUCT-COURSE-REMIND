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
          <div class="time-input-wrapper">
            <input
              id="todoHours"
              :value="todo.timeInput"
              class="time-input"
              maxlength="8"
              placeholder="24:00:00"
              type="text"
              @input="handleTimeInput($event.target.value)"
            >
            <span class="time-hint">格式: 时:分:秒 (不输入默认24h)</span>
          </div>
          <div class="time-examples">
            <span class="example-tag" @click="setQuickTime('01:00:00')">1小时</span>
            <span class="example-tag" @click="setQuickTime('03:00:00')">3小时</span>
            <span class="example-tag" @click="setQuickTime('12:00:00')">12小时</span>
            <span class="example-tag" @click="setQuickTime('24:00:00')">1天</span>
            <span class="example-tag" @click="setQuickTime('72:00:00')">3天</span>
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
  emits: ['close', 'add', 'update:todo'],
  methods: {
    handleTimeInput(value) {
      // 保存原始输入
      const timeInput = value.trim()

      // 解析时间输入，支持多种格式
      let hours = 24 // 默认24小时

      if (!timeInput) {
        // 空输入，使用默认值24小时
        hours = 24
      } else if (/^\d+:\d+:\d+$/.test(timeInput)) {
        // HH:MM:SS 格式
        const [h, m, s] = timeInput.split(':').map(Number)
        hours = h + m / 60 + s / 3600
      } else if (/^\d+:\d+$/.test(timeInput)) {
        // HH:MM 格式
        const [h, m] = timeInput.split(':').map(Number)
        hours = h + m / 60
      } else if (/^\d+$/.test(timeInput)) {
        // 纯数字，视为小时数
        hours = parseFloat(timeInput)
      } else if (/^\d+\.?\d*$/.test(timeInput)) {
        // 小数格式的小时数
        hours = parseFloat(timeInput)
      } else {
        // 无法解析的格式，保持默认24小时
        hours = 24
      }

      // 限制范围 0.01-8760小时（最多1年）
      hours = Math.max(0.01, Math.min(8760, hours))

      this.$emit('update:todo', {
        ...this.todo,
        hours: hours,
        timeInput: timeInput // 保存用户的原始输入以供显示
      })
    },

    setQuickTime(timeStr) {
      // 快捷设置时间
      this.handleTimeInput(timeStr)
    }
  },
  watch: {
    show(newVal) {
      if (newVal && !this.todo.timeInput) {
        // 弹窗打开时，如果没有timeInput，设置默认值
        this.$emit('update:todo', {
          ...this.todo,
          hours: 24,
          timeInput: '24:00:00'
        })
      }
    }
  }
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

.time-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-input {
  width: 100%;
  font-family: 'Courier New', monospace;
  font-size: 16px !important;
  letter-spacing: 1px;
}

.time-hint {
  color: #6c757d;
  font-size: 12px;
  padding: 0 4px;
  display: block;
}

.time-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.example-tag {
  display: inline-block;
  padding: 6px 12px;
  background: linear-gradient(135deg, #e9ecef, #dee2e6);
  color: #495057;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ced4da;
}

.example-tag:hover {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
  border-color: #667eea;
}

.example-tag:active {
  transform: translateY(0);
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