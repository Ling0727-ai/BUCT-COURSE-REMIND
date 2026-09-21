<template>
  <div class="trail-settings">
    <label class="toggle-row">
      <input type="checkbox" :checked="enabled" @change="onToggle">
      <span class="toggle-text">
        启用鼠标拖尾
        <small>装饰性效果，默认关闭以节省电量</small>
      </span>
    </label>

    <div v-if="enabled" class="color-picker-wrap">
      <label class="picker-label" for="trailHex">拖尾颜色</label>
      <input id="trailHex" v-model="hexInput" class="hex-input" type="text" maxlength="7" @blur="normalizeHex" />
      <input class="native-color" type="color" :value="hexColor" aria-label="选择拖尾颜色" @input="onNativeColorInput" />
      <div class="actions">
        <button type="button" class="btn btn-primary" @click="applyTrailColor">应用</button>
        <button type="button" class="btn btn-outline" @click="resetTrailColor">重置默认</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted, ref } from 'vue'
import { useToast } from '@/composables/useToast'
import { initMouseTrail } from '@/utils/mouse-trail'

const CUSTOM_COLOR_KEY = 'mouse_trail_custom_color'
const ENABLED_KEY = 'mouse_trail_enabled'
const DEFAULT_COLOR = '#00bbcc'

type TrailManager = {
  setCustomColor?: (r: number, g: number, b: number) => void
  resetColor?: () => void
  destroy?: () => void
}

export default defineComponent({
  name: 'SettingsColorPicker',
  setup() {
    const { showToast } = useToast()
    const hexInput = ref(DEFAULT_COLOR)
    const enabled = ref(false)

    const manager = () => window.__MOUSE_TRAIL_MANAGER as TrailManager | undefined

    onMounted(() => {
      try {
        enabled.value = localStorage.getItem(ENABLED_KEY) === 'true'
        const saved = localStorage.getItem(CUSTOM_COLOR_KEY)
        if (saved) {
          const { r, g, b } = JSON.parse(saved)
          hexInput.value = `#${[r, g, b].map((v: number) => v.toString(16).padStart(2, '0')).join('')}`
        }
      } catch {
        // 读取失败时使用默认值
      }
    })

    const onToggle = (event: Event) => {
      const checked = (event.target as HTMLInputElement).checked
      enabled.value = checked
      try {
        localStorage.setItem(ENABLED_KEY, checked ? 'true' : 'false')
      } catch {
        // 忽略写入失败
      }

      if (checked) {
        window.__MOUSE_TRAIL_MANAGER = initMouseTrail() ?? undefined
        showToast('success', '已启用', '鼠标拖尾已开启')
      } else {
        manager()?.destroy?.()
        window.__MOUSE_TRAIL_MANAGER = undefined
        showToast('info', '已关闭', '鼠标拖尾已关闭')
      }
    }

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

      const mgr = manager()
      if (mgr && typeof mgr.setCustomColor === 'function') {
        mgr.setCustomColor(r, g, b)
      }
      try {
        localStorage.setItem(CUSTOM_COLOR_KEY, JSON.stringify({ r, g, b }))
      } catch {
        // 忽略写入失败
      }

      showToast('success', '成功', '拖尾颜色已应用')
    }

    const resetTrailColor = () => {
      const mgr = manager()
      if (mgr && typeof mgr.resetColor === 'function') {
        mgr.resetColor()
      }
      try {
        localStorage.removeItem(CUSTOM_COLOR_KEY)
      } catch {
        // 忽略删除失败
      }
      hexInput.value = DEFAULT_COLOR
      showToast('info', '提示', '已恢复默认颜色')
    }

    return {
      enabled,
      onToggle,
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
.trail-settings {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.toggle-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  cursor: pointer;
}

.toggle-row input {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: var(--primary);
  cursor: pointer;
  flex-shrink: 0;
}

.toggle-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: var(--font-sm);
  color: var(--text-primary);
}

.toggle-text small {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.color-picker-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.picker-label {
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
}

.hex-input {
  width: 110px;
  min-height: 40px;
  padding: 8px 10px;
  font-size: var(--font-sm);
  color: var(--text-primary);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}

.hex-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-subtle);
}

.native-color {
  width: 44px;
  height: 40px;
  padding: 0;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.actions {
  display: flex;
  gap: var(--space-2);
}

.btn {
  min-height: 40px;
  padding: 8px 14px;
  font-size: var(--font-sm);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition);
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-white);
}

.btn-primary:hover { background: var(--primary-dark); }

.btn-outline {
  background: var(--bg);
  color: var(--text-secondary);
}

.btn-outline:hover {
  border-color: var(--primary);
  color: var(--primary);
}
</style>
