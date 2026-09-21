<template>
  <div class="font-settings">
    <!-- Font Family -->
    <div class="setting-group">
      <label class="setting-label">字体</label>
      <div class="family-grid">
        <button
          v-for="f in families"
          :key="f.value"
          :class="['family-btn', { active: settings.family === f.value }]"
          @click="updateFamily(f.value)"
        >
          <span class="family-preview" :style="{ fontFamily: f.value === 'default' ? 'inherit' : f.value }">
            Aa
          </span>
          <span class="family-name">{{ f.label }}</span>
        </button>
      </div>
    </div>

    <!-- Font Size -->
    <div class="setting-group">
      <label class="setting-label">字号</label>
      <div class="size-presets">
        <button
          v-for="preset in presets"
          :key="preset.size"
          :class="['preset-btn', { active: settings.size === preset.size }]"
          @click="updateSize(preset.size)"
        >
          {{ preset.label }}
        </button>
      </div>
      <div class="slider-wrap">
        <span class="slider-icon">A</span>
        <input
          type="range"
          min="11"
          max="22"
          step="1"
          :value="settings.size"
          @input="updateSize(Number(($event.target as HTMLInputElement).value))"
        />
        <span class="slider-icon slider-icon-lg">A</span>
        <span class="size-value">{{ settings.size }}px</span>
      </div>
      <div class="preview-text" :style="{ fontSize: settings.size + 'px' }">
        预览效果 - 敏捷的棕色狐狸跳过了懒狗
      </div>
    </div>

    <!-- Reset -->
    <button class="btn btn-reset" @click="resetFont">
      <i class="fas fa-undo-alt"></i>
      恢复默认字体
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useFontSettings, FONT_FAMILIES } from '@/composables/useFontSettings'

export default defineComponent({
  name: 'FontSettings',
  setup() {
    const { settings, updateSize, updateFamily, resetFont } = useFontSettings()

    const presets = [
      { label: '小', size: 13 },
      { label: '默认', size: 15 },
      { label: '大', size: 17 },
      { label: '特大', size: 20 },
    ]

    return {
      settings,
      families: FONT_FAMILIES,
      presets,
      updateSize,
      updateFamily,
      resetFont,
    }
  },
})
</script>

<style scoped>
.font-settings {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.setting-label {
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

/* Font Family Grid */
.family-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-2);
}

.family-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: var(--space-3);
  border: 2px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg);
  cursor: pointer;
  transition: all var(--transition);
}

.family-btn:hover {
  border-color: var(--primary-light);
}

.family-btn.active {
  border-color: var(--primary);
  background: var(--primary-subtle);
}

.family-preview {
  font-size: 22px;
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: 1;
}

.family-name {
  font-size: 11px;
  color: var(--text-tertiary);
}

.family-btn.active .family-name {
  color: var(--primary);
  font-weight: var(--font-medium);
}

/* Size Presets */
.size-presets {
  display: flex;
  gap: var(--space-2);
}

.preset-btn {
  flex: 1;
  padding: 8px 4px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg);
  color: var(--text-secondary);
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--transition);
}

.preset-btn:hover {
  border-color: var(--primary-light);
}

.preset-btn.active {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

/* Slider */
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

.slider-icon {
  font-size: 13px;
  font-weight: var(--font-bold);
  color: var(--text-tertiary);
}

.slider-icon-lg {
  font-size: 18px;
}

.size-value {
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  min-width: 36px;
  text-align: right;
}

/* Preview */
.preview-text {
  padding: var(--space-3) var(--space-4);
  background: var(--gray-50);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Reset */
.btn-reset {
  padding: 10px 20px;
  border: 1px solid var(--red);
  border-radius: var(--radius-md);
  background: var(--red-subtle);
  color: var(--red);
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
  background: var(--red);
  color: white;
}

@media (max-width: 480px) {
  .family-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
