import { ref, watch } from 'vue'

export interface FontSettings {
  family: string
  size: number // base font size in px
}

const STORAGE_KEY = 'buct-font-settings'

export const FONT_FAMILIES: { label: string; value: string }[] = [
  { label: '系统默认', value: 'default' },
  { label: 'PingFang SC', value: '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif' },
  { label: '微软雅黑', value: '"Microsoft YaHei", "PingFang SC", sans-serif' },
  { label: '宋体', value: '"Songti SC", "SimSun", "NSimSun", serif' },
  { label: '楷体', value: '"Kaiti SC", "KaiTi", "STKaiti", serif' },
  { label: '等宽', value: '"Fira Code", "Cascadia Code", "Consolas", "Monaco", monospace' },
]

const DEFAULT: FontSettings = {
  family: 'default',
  size: 15,
}

function load(): FontSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return { ...DEFAULT, ...JSON.parse(raw) }
  } catch {
    // ignore
  }
  return { ...DEFAULT }
}

function save(s: FontSettings) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
  } catch {
    // ignore
  }
}

function applyFontSize(baseSize: number) {
  const ratio = baseSize / 15
  const scale = (px: number) => `${Math.round(px * ratio)}px`
  const root = document.documentElement.style
  root.setProperty('--font-xs', scale(12))
  root.setProperty('--font-sm', scale(13))
  root.setProperty('--font-base', scale(15))
  root.setProperty('--font-lg', scale(17))
  root.setProperty('--font-xl', scale(20))
  root.setProperty('--font-2xl', scale(24))
  root.setProperty('--font-3xl', scale(30))
}

function applyFontFamily(family: string) {
  if (family === 'default') {
    document.body.style.fontFamily = ''
  } else {
    document.body.style.fontFamily = family
  }
}

// Singleton state
const settings = ref<FontSettings>(load())

watch(settings, (s) => {
  save(s)
  applyFontSize(s.size)
  applyFontFamily(s.family)
}, { deep: true })

// Apply on init
applyFontSize(settings.value.size)
applyFontFamily(settings.value.family)

export function useFontSettings() {
  const updateSize = (size: number) => {
    settings.value.size = Math.max(11, Math.min(22, size))
  }

  const updateFamily = (family: string) => {
    settings.value.family = family
  }

  const resetFont = () => {
    settings.value = { ...DEFAULT }
  }

  return {
    settings,
    updateSize,
    updateFamily,
    resetFont,
  }
}
