<template>
  <div class="color-picker-wrap">
    <label class="picker-label">拖尾颜色</label>
    <input v-model="hexInput" class="hex-input" type="text" maxlength="7" @blur="normalizeHex" />
    <input class="native-color" type="color" :value="hexColor" @input="onNativeColorInput" />
    <div class="actions">
      <button class="btn btn-primary" @click="applyTrailColor">应用</button>
      <button class="btn btn-outline" @click="resetTrailColor">重置默认</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from 'vue'
import { useToast } from '@/composables/useToast'

const CUSTOM_COLOR_KEY = 'mouse_trail_custom_color'
const DEFAULT_COLOR = '#00bbcc'

type TrailManager = {
  setCustomColor?: (r: number, g: number, b: number) => void
  resetColor?: () => void
}

export default defineComponent({
  name: 'SettingsColorPicker',
  setup() {
    const { showToast } = useToast()
    const hexInput = ref(DEFAULT_COLOR)

    const normalizeHex = () => {
      let value = (hexInput.value || '').trim()
      if (!value.startsWith('#')) value = `#${value}`
      if (!/^#[0-9a-fA-F]{6}$/.test(value)) {
        value = DEFAULT_COLOR
      }
      hexInput.value = value.toLowerCase()
    }

    const hexColor = computed(() => {
      normalizeHex()
      return hexInput.value
    })

    const onNativeColorInput = (event: Event) => {
      const target = event.target as HTMLInputElement
      hexInput.value = target.value
    }

    const applyTrailColor = () => {
      normalizeHex()
      const r = parseInt(hexInput.value.slice(1, 3), 16)
      const g = parseInt(hexInput.value.slice(3, 5), 16)
      const b = parseInt(hexInput.value.slice(5, 7), 16)

      const mgr = window.__MOUSE_TRAIL_MANAGER as TrailManager | undefined
      if (mgr && typeof mgr.setCustomColor === 'function') {
        mgr.setCustomColor(r, g, b)
      } else {
        localStorage.setItem(CUSTOM_COLOR_KEY, JSON.stringify({ r, g, b }))
      }

      showToast('success', '成功', '拖尾颜色已应用')
    }

    const resetTrailColor = () => {
      const mgr = window.__MOUSE_TRAIL_MANAGER as TrailManager | undefined
      if (mgr && typeof mgr.resetColor === 'function') {
        mgr.resetColor()
      } else {
        localStorage.removeItem(CUSTOM_COLOR_KEY)
      }
      hexInput.value = DEFAULT_COLOR
      showToast('info', '提示', '已恢复默认颜色')
    }

    return {
      hexInput,
      hexColor,
      normalizeHex,
      onNativeColorInput,
      applyTrailColor,
      resetTrailColor
    }
  }
})
</script>

<style scoped>
.color-picker-wrap { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.picker-label { color: var(--card-text-secondary); font-size: 14px; font-weight: 600; }
.hex-input {
  width: 110px;
  padding: 8px 10px;
  border: 1px solid var(--stroke-strong);
  border-radius: 8px;
  background: #ffffff;
  color: var(--card-text-primary);
}
.hex-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: var(--focus-ring);
}
.native-color { width: 40px; height: 36px; border: 0; background: transparent; }
.actions { display: flex; gap: 8px; }
.btn { padding: 8px 12px; border-radius: 8px; border: 1px solid var(--stroke-strong); cursor: pointer; }
.btn-primary { background: var(--primary-gradient); border-color: var(--primary-color); color: var(--text-white); }
.btn-outline { background: #ffffff; color: var(--card-text-primary); }
</style>
