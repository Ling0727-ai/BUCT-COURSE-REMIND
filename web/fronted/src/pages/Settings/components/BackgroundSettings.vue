<template>
  <div class="bg-settings">
    <!-- 预设选择 -->
    <div class="preset-section">
      <label class="section-label">内置背景</label>
      <div class="preset-grid">
        <button
          class="preset-card"
          :class="{ active: settings.preset === 'light' }"
          @click="setPreset('light')"
        >
          <div class="preset-preview preset-light">
            <div class="preview-blob p1"></div>
            <div class="preview-blob p2"></div>
          </div>
          <div class="preset-info">
            <span class="preset-name">浅色模式</span>
            <span v-if="settings.preset === 'light'" class="preset-check">✓</span>
          </div>
        </button>

        <button
          class="preset-card"
          :class="{ active: settings.preset === 'dark' }"
          @click="setPreset('dark')"
        >
          <div class="preset-preview preset-dark">
            <div class="preview-blob p1"></div>
            <div class="preview-blob p2"></div>
          </div>
          <div class="preset-info">
            <span class="preset-name">深色模式</span>
            <span v-if="settings.preset === 'dark'" class="preset-check">✓</span>
          </div>
        </button>

        <button
          class="preset-card"
          :class="{ active: settings.preset === 'custom' }"
          @click="setPreset('custom')"
        >
          <div class="preset-preview preset-custom">
            <div class="custom-icon">
              <i class="fas fa-image"></i>
            </div>
          </div>
          <div class="preset-info">
            <span class="preset-name">自定义</span>
            <span v-if="settings.preset === 'custom'" class="preset-check">✓</span>
          </div>
        </button>
      </div>
    </div>

    <!-- 自定义上传区域 - 仅在 custom 模式下显示 -->
    <div v-if="settings.preset === 'custom'" class="upload-section">
      <label class="section-label">上传背景文件</label>
      <div
        class="upload-area"
        :class="{ 'has-file': mediaUrl }"
        @click="triggerUpload"
        @dragover.prevent
        @drop.prevent="handleDrop"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*,video/*"
          style="display: none"
          @change="handleFileChange"
        />
        <div v-if="!mediaUrl" class="upload-placeholder">
          <i class="fas fa-cloud-upload-alt"></i>
          <p>点击或拖拽上传背景图片 / GIF / 视频</p>
          <span>支持 JPG、PNG、GIF、MP4、WebM</span>
        </div>
        <div v-else class="upload-preview">
          <img v-if="mediaType !== 'video'" :src="mediaUrl" alt="background preview" />
          <video v-else :src="mediaUrl" autoplay loop muted playsinline />
          <div class="upload-overlay">
            <i class="fas fa-sync-alt"></i>
            <span>点击更换</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 滑块 -->
    <div class="slider-group">
      <label class="section-label">显示设置</label>
      <div class="slider-row">
        <label>背景不透明度</label>
        <div class="slider-wrap">
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.05"
            v-model.number="settings.bgOpacity"
          />
          <span class="slider-value">{{ Math.round(settings.bgOpacity * 100) }}%</span>
        </div>
      </div>
      <div class="slider-row">
        <label>卡片不透明度</label>
        <div class="slider-wrap">
          <input
            type="range"
            min="0.3"
            max="1"
            step="0.05"
            v-model.number="settings.cardOpacity"
          />
          <span class="slider-value">{{ Math.round(settings.cardOpacity * 100) }}%</span>
        </div>
      </div>
    </div>

    <!-- 重置 -->
    <button class="btn-reset" @click="resetBackground">
      <i class="fas fa-undo-alt"></i>
      恢复默认
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useBackground } from '@/composables/useBackground'

export default defineComponent({
  name: 'BackgroundSettings',
  setup() {
    const { settings, mediaUrl, mediaType, setPreset, handleFileUpload, resetBackground } = useBackground()
    const fileInput = ref<HTMLInputElement | null>(null)

    const triggerUpload = () => {
      fileInput.value?.click()
    }

    const handleFileChange = (e: Event) => {
      const target = e.target as HTMLInputElement
      const file = target.files?.[0]
      if (file) {
        handleFileUpload(file)
      }
      target.value = ''
    }

    const handleDrop = (e: DragEvent) => {
      const file = e.dataTransfer?.files?.[0]
      if (file) {
        handleFileUpload(file)
      }
    }

    return {
      settings,
      mediaUrl,
      mediaType,
      setPreset,
      fileInput,
      triggerUpload,
      handleFileChange,
      handleDrop,
      resetBackground
    }
  }
})
</script>

<style scoped>
.bg-settings {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* ─── 区块标签 ─── */
.section-label {
  display: block;
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ─── 预设选择 ─── */
.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.preset-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: 0;
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all 0.25s ease;
  overflow: hidden;
  text-align: left;
  font-family: inherit;
}

.preset-card:hover {
  border-color: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.preset-card.active {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

/* ─── 预设预览 ─── */
.preset-preview {
  width: 100%;
  height: 80px;
  position: relative;
  overflow: hidden;
}

.preset-light {
  background:
    radial-gradient(ellipse 70% 70% at 60% -10%, rgba(59, 130, 246, 0.25) 0%, transparent 100%),
    radial-gradient(ellipse 50% 60% at 90% 90%, rgba(139, 92, 246, 0.15) 0%, transparent 100%),
    linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.preset-dark {
  background:
    radial-gradient(ellipse 70% 60% at 60% -10%, rgba(59, 130, 246, 0.3) 0%, transparent 100%),
    radial-gradient(ellipse 50% 50% at 80% 80%, rgba(139, 92, 246, 0.2) 0%, transparent 100%),
    linear-gradient(180deg, #0b1120 0%, #111827 100%);
}

.preset-custom {
  background:
    linear-gradient(135deg, #e8ecf1 0%, #dcdfe4 50%, #e8ecf1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font-size: 14px;
  box-shadow: var(--shadow-sm);
}

.preview-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(20px);
  pointer-events: none;
}

.preset-light .p1 {
  width: 60px;
  height: 60px;
  background: rgba(59, 130, 246, 0.3);
  top: -20px;
  right: -10px;
}

.preset-light .p2 {
  width: 45px;
  height: 45px;
  background: rgba(139, 92, 246, 0.2);
  bottom: -15px;
  left: 20px;
}

.preset-dark .p1 {
  width: 60px;
  height: 60px;
  background: rgba(59, 130, 246, 0.35);
  top: -20px;
  right: -15px;
}

.preset-dark .p2 {
  width: 50px;
  height: 50px;
  background: rgba(139, 92, 246, 0.25);
  bottom: -20px;
  left: 15px;
}

/* ─── 预设信息行 ─── */
.preset-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3) var(--space-3);
}

.preset-name {
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.preset-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: var(--font-bold);
}

/* ─── 上传区域 ─── */
.upload-section {
  display: flex;
  flex-direction: column;
}

.upload-area {
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition);
  background: var(--bg-secondary);
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.upload-area:hover {
  border-color: var(--primary);
  background: var(--primary-subtle);
}

.upload-placeholder i {
  font-size: 32px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-3);
}

.upload-placeholder p {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.upload-placeholder span {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.upload-preview {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 140px;
}

.upload-preview img,
.upload-preview video {
  width: 100%;
  height: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.upload-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: var(--radius-md);
  opacity: 0;
  transition: opacity var(--transition);
}

.upload-area:hover .upload-overlay {
  opacity: 1;
}

.upload-overlay i {
  font-size: 20px;
}

.upload-overlay span {
  font-size: var(--font-xs);
}

/* ─── 滑块 ─── */
.slider-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.slider-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.slider-row > label {
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.slider-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.slider-wrap input[type="range"] {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  background: var(--gray-200);
  border-radius: 3px;
  outline: none;
}

.slider-wrap input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: var(--primary);
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.slider-wrap input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: var(--primary);
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.slider-value {
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  min-width: 42px;
  text-align: right;
}

/* ─── 重置按钮 ─── */
.btn-reset {
  padding: 10px 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
  font-size: var(--font-sm);
  cursor: pointer;
  transition: all var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
}

.btn-reset:hover {
  border-color: var(--red);
  background: var(--red-subtle);
  color: var(--red);
}

@media (max-width: 640px) {
  .preset-grid {
    grid-template-columns: 1fr;
  }

  .preset-preview {
    height: 56px;
  }

  .upload-area {
    padding: var(--space-4);
    min-height: 120px;
  }

  .upload-placeholder i {
    font-size: 24px;
  }
}
</style>
