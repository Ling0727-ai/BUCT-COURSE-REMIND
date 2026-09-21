import { reactive } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface ToastAction {
  label: string
  handler: () => void
}

export interface ToastItem {
  id: number
  type: ToastType
  title: string
  message: string
  /** 毫秒；0 表示不自动关闭。 */
  duration: number
  action?: ToastAction
}

export interface ToastOptions {
  duration?: number
  action?: ToastAction
}

/** 同时显示的 Toast 上限，超出时挤掉最早的一条。 */
const MAX_VISIBLE = 4
const MIN_DURATION = 4000
const MAX_DURATION = 10000

interface TimerState {
  handle: number
  /** 本次计时开始时刻。 */
  startedAt: number
  /** 剩余毫秒数（暂停时冻结）。 */
  remaining: number
}

const items = reactive<ToastItem[]>([])
const timers = new Map<number, TimerState>()
/** 暂停期间冻结的剩余时间，恢复计时时使用。 */
const paused = new Map<number, number>()

let nextId = 0

/** 文案越长停留越久，保证读得完；错误类至少 6 秒。 */
function resolveDuration(type: ToastType, message: string, explicit?: number): number {
  if (explicit !== undefined) {
    return Math.max(0, explicit)
  }
  const base = type === 'error' ? 6000 : MIN_DURATION
  return Math.min(MAX_DURATION, Math.max(base, MIN_DURATION + message.length * 80))
}

function clearTimer(id: number): void {
  const state = timers.get(id)
  if (state) {
    window.clearTimeout(state.handle)
    timers.delete(id)
  }
}

function armTimer(item: ToastItem, remaining: number): void {
  if (item.duration <= 0 || remaining <= 0) {
    return
  }
  const handle = window.setTimeout(() => dismiss(item.id), remaining)
  timers.set(item.id, { handle, startedAt: Date.now(), remaining })
}

function dismiss(id: number): void {
  clearTimer(id)
  paused.delete(id)
  const index = items.findIndex((item) => item.id === id)
  if (index !== -1) {
    // 退出动画由 ToastHost 的 TransitionGroup 负责。
    items.splice(index, 1)
  }
}

/** 悬停时暂停计时，移开后按剩余时间继续。 */
function pause(id: number): void {
  const state = timers.get(id)
  if (!state) {
    return
  }
  window.clearTimeout(state.handle)
  timers.delete(id)
  paused.set(id, Math.max(0, state.remaining - (Date.now() - state.startedAt)))
}

function resume(id: number): void {
  const item = items.find((entry) => entry.id === id)
  if (!item || timers.has(id)) {
    return
  }
  const remaining = paused.get(id) ?? item.duration
  paused.delete(id)
  armTimer(item, remaining)
}

function push(type: ToastType, title: string, message: string, options: ToastOptions = {}): number {
  const id = (nextId += 1)
  const item: ToastItem = {
    id,
    type,
    title,
    message,
    duration: resolveDuration(type, message, options.duration),
    action: options.action
  }

  items.push(item)

  while (items.length > MAX_VISIBLE) {
    const oldest = items[0]
    if (!oldest) {
      break
    }
    dismiss(oldest.id)
  }

  armTimer(item, item.duration)
  return id
}

/**
 * 全局 Toast。状态是模块级单例，由 App 中挂载的 ToastHost 统一渲染。
 */
export function useToast() {
  return {
    toasts: items,
    dismiss,
    pause,
    resume,
    showToast: (type: ToastType, title: string, message: string, options?: ToastOptions) =>
      push(type, title, message, options),
    success: (title: string, message = '', options?: ToastOptions) => push('success', title, message, options),
    error: (title: string, message = '', options?: ToastOptions) => push('error', title, message, options),
    info: (title: string, message = '', options?: ToastOptions) => push('info', title, message, options),
    warning: (title: string, message = '', options?: ToastOptions) => push('warning', title, message, options)
  }
}
