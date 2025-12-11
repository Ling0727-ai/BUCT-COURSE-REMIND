// 鼠标拖尾效果管理器 (桌面端)
// 使用元素池减少频繁创建/销毁，CSS 动画负责淡出与缩放

const MAX_DOTS = 40
const DOT_LIFETIME_MS = 900  // 增加到900ms以匹配CSS动画
const DIST_THRESHOLD = 4 // 减小阈值使拖尾更密集

export class MouseTrailManager {
  constructor(container) {
    this.container = container
    this.pool = []
    this.active = new Set()
    this.lastX = null
    this.lastY = null
    this.enabled = true
    this.boundMove = this.onPointerMove.bind(this)
    this.boundVisibility = this.onVisibilityChange.bind(this)
    this.initPool()
    this.attach()
  }

  initPool() {
    for (let i = 0; i < MAX_DOTS; i++) {
      const el = document.createElement('span')
      el.className = 'trail-dot'
      el.style.opacity = '0'
      el.style.pointerEvents = 'none'
      el.style.position = 'absolute'
      // 初始位置设置在屏幕外，避免闪烁
      el.style.left = '-100px'
      el.style.top = '-100px'
      this.pool.push(el)
    }
    // 统一添加到容器，避免频繁 DOM 插入/删除（通过 opacity 控制）
    this.pool.forEach(el => this.container.appendChild(el))
  }

  attach() {
    window.addEventListener('pointermove', this.boundMove, { passive: true })
    // 为Vivaldi浏览器等不支持pointermove的浏览器添加备用事件
    window.addEventListener('mousemove', this.boundMove, { passive: true })
    document.addEventListener('visibilitychange', this.boundVisibility)
  }

  detach() {
    window.removeEventListener('pointermove', this.boundMove)
    window.removeEventListener('mousemove', this.boundMove)
    document.removeEventListener('visibilitychange', this.boundVisibility)
  }

  onVisibilityChange() {
    if (document.visibilityState === 'hidden') {
      this.pause()
    } else if (document.visibilityState === 'visible') {
      this.resume()
    }
  }

  pause() { this.enabled = false }
  resume() { this.enabled = true }

  getDot() {
    for (const el of this.pool) {
      if (!this.active.has(el)) return el
    }
    // 若全部占用，回收最早的一个
    if (this.active.size > 0) {
      const first = this.active.values().next().value
      this.recycle(first)
      return first
    }
    return null
  }

  onPointerMove(e) {
    if (!this.enabled) return
    const x = e.clientX
    const y = e.clientY
    if (this.lastX !== null) {
      const dx = x - this.lastX
      const dy = y - this.lastY
      if ((dx * dx + dy * dy) < DIST_THRESHOLD * DIST_THRESHOLD) return
    }
    this.lastX = x
    this.lastY = y
    this.spawn(x, y)
  }

  spawn(x, y) {
    const dot = this.getDot()
    if (!dot) return
    this.active.add(dot)

    // 随机尺寸 & 轻微偏移 (增大尺寸范围)
    const size = 10 + Math.random() * 8 // 10 - 18px
    dot.style.width = size + 'px'
    dot.style.height = size + 'px'

    const offsetX = (Math.random() - 0.5) * 10
    const offsetY = (Math.random() - 0.5) * 10
    const finalX = x + offsetX - size / 2
    const finalY = y + offsetY - size / 2

    // 设置初始位置（使用left/top而不是transform，避免与动画冲突）
    dot.style.left = finalX + 'px'
    dot.style.top = finalY + 'px'
    dot.style.transform = 'scale(1)' // 重置transform为初始缩放
    dot.style.opacity = '1'

    // 随机颜色变化
    const colorClasses = ['color-1', 'color-2', 'color-3', 'color-4']
    const randomColor = colorClasses[Math.floor(Math.random() * colorClasses.length)]
    dot.classList.remove('color-1', 'color-2', 'color-3', 'color-4')
    dot.classList.add(randomColor)

    // 触发重绘后添加动画类
    dot.classList.remove('trail-anim')
    void dot.offsetWidth // 强制回流以重置动画
    dot.classList.add('trail-anim')

    // 定时回收
    setTimeout(() => this.recycle(dot), DOT_LIFETIME_MS)
  }

  recycle(dot) {
    if (!this.active.has(dot)) return
    this.active.delete(dot)
    dot.style.opacity = '0'
  }

  destroy() {
    this.detach()
    this.pool.forEach(el => {
      if (el.parentNode === this.container) {
        this.container.removeChild(el)
      }
    })
    this.active.clear()
  }
}

export function initMouseTrail() {
  // 用户可通过 localStorage 关闭: setItem('mouse_trail_enabled','false')
  try {
    const flag = localStorage.getItem('mouse_trail_enabled')
    if (flag === 'false') return null
  } catch {}

  // prefers-reduced-motion 时不启用
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return null
  }

  let container = document.getElementById('mouse-trail-container')
  if (!container) {
    container = document.createElement('div')
    container.id = 'mouse-trail-container'
    container.className = 'mouse-trail-container'
    document.body.appendChild(container)
  }
  return new MouseTrailManager(container)
}

