import { ref, watch } from 'vue'

const DB_NAME = 'buct-bg'
const STORE_NAME = 'media'
const DB_VERSION = 1
const SETTINGS_KEY = 'buct-bg-settings'

export type BgPreset = 'light' | 'dark' | 'custom' | 'none'

export interface BackgroundSettings {
  preset: BgPreset
  bgOpacity: number
  cardOpacity: number
}

const DEFAULT_SETTINGS: BackgroundSettings = {
  preset: 'light',
  bgOpacity: 1,
  cardOpacity: 1
}

function loadSettings(): BackgroundSettings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      // Migrate old format
      if (!parsed.preset) {
        if (parsed.enabled && parsed.type) {
          return { preset: 'custom', bgOpacity: parsed.bgOpacity ?? 1, cardOpacity: parsed.cardOpacity ?? 1 }
        }
        return { ...DEFAULT_SETTINGS, bgOpacity: parsed.bgOpacity ?? 1, cardOpacity: parsed.cardOpacity ?? 1 }
      }
      return { ...DEFAULT_SETTINGS, ...parsed }
    }
  } catch {
    // ignore
  }
  return { ...DEFAULT_SETTINGS }
}

function saveSettings(s: BackgroundSettings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(s))
  } catch {
    // ignore
  }
}

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME)
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function saveMedia(type: string, dataUrl: string) {
  const db = await openDB()
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    store.put({ type, data: dataUrl }, 'background')
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

async function loadMedia(): Promise<{ type: string; data: string } | null> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const store = tx.objectStore(STORE_NAME)
    const req = store.get('background')
    req.onsuccess = () => resolve(req.result || null)
    req.onerror = () => reject(req.error)
  })
}

async function clearMedia() {
  const db = await openDB()
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    store.delete('background')
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

// Singleton state
const settings = ref<BackgroundSettings>(loadSettings())
const mediaUrl = ref<string>('')
const mediaType = ref<string>('')

function applyPreset(preset: BgPreset) {
  document.documentElement.setAttribute('data-bg-preset', preset)
}

/**
 * 只调整卡片透明度，不再直接写 --bg。
 * 直接写内联 --bg 会盖掉深色预设里的 --surface-rgb，导致深色模式下卡片变白。
 */
function applyCardOpacity(opacity: number) {
  const alpha = Math.max(0.1, Math.min(1, opacity))
  document.documentElement.style.setProperty('--card-alpha', String(alpha))
}

function clearInlineOverrides() {
  document.documentElement.style.removeProperty('--card-alpha')
  document.documentElement.style.removeProperty('--bg')
}

watch(
  settings,
  (s) => {
    saveSettings(s)
    applyPreset(s.preset)
    applyCardOpacity(s.cardOpacity)
  },
  { deep: true }
)

// Initial load
clearInlineOverrides()
loadMedia().then((media) => {
  if (media) {
    mediaUrl.value = media.data
    mediaType.value = media.type
    // If settings were migrated from old format with custom media, ensure preset is custom
    if (settings.value.preset !== 'custom' && media.data) {
      // Media exists but preset isn't custom — user might have switched away
    }
  }
})
applyPreset(settings.value.preset)
applyCardOpacity(settings.value.cardOpacity)

export function useBackground() {
  const setPreset = (preset: BgPreset) => {
    settings.value.preset = preset
  }

  const handleFileUpload = async (file: File) => {
    const reader = new FileReader()
    reader.onload = async () => {
      const dataUrl = reader.result as string
      const type = file.type.startsWith('video') ? 'video' : 'image'
      await saveMedia(type, dataUrl)
      mediaUrl.value = dataUrl
      mediaType.value = type
      settings.value.preset = 'custom'
    }
    reader.readAsDataURL(file)
  }

  const resetBackground = async () => {
    await clearMedia()
    mediaUrl.value = ''
    mediaType.value = ''
    settings.value = { ...DEFAULT_SETTINGS }
    clearInlineOverrides()
    applyCardOpacity(DEFAULT_SETTINGS.cardOpacity)
  }

  return {
    settings,
    mediaUrl,
    mediaType,
    setPreset,
    handleFileUpload,
    resetBackground
  }
}
