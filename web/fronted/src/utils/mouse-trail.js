// 鼠标拖尾效果 - Canvas 连续曲线版
// 使用 canvas + requestAnimationFrame 绘制平滑、连续、轻薄的拖尾

const TRAIL_LENGTH = 28        // 拖尾保留的历史点数
const TRAIL_MAX_WIDTH = 3.5    // 拖尾最粗处宽度(px)
const TRAIL_MIN_WIDTH = 0.4    // 拖尾末端最细宽度(px)
const POINT_LIFETIME_MS = 2000 // 每个点从生成到完全消失的时长(ms)，即拖尾存在2s

// 默认主题色系 - 与 global.css 保持一致的蓝绿色
const DEFAULT_COLORS = [
  {r: 34, g: 211, b: 238}, // 亮青色
  {r: 6, g: 182, b: 212}, // 中青色
  {r: 20, g: 184, b: 166}, // 青绿色
  {r: 45, g: 212, b: 191}, // 浅青绿色
]

const CUSTOM_COLOR_KEY = 'mouse_trail_custom_color' // localStorage key

/** 将自定义 RGB 生成渐变色组（基色 + 略深/略浅变体，保持拖尾有层次感） */
function buildCustomColors(r, g, b) {
  return [
    {r, g, b},
    {r: Math.round(r * 0.85), g: Math.round(g * 0.85), b: Math.round(b * 0.85)},
    {
      r: Math.min(255, Math.round(r * 1.1)),
      g: Math.min(255, Math.round(g * 1.1)),
      b: Math.min(255, Math.round(b * 1.1))
    },
    {r, g, b},
  ]
}

/** 读取持久化的自定义颜色，返回 COLORS 数组或 null */
function loadCustomColors() {
  try {
    const raw = localStorage.getItem(CUSTOM_COLOR_KEY)
    if (!raw) return null
    const {r, g, b} = JSON.parse(raw)
    if ([r, g, b].every(v => Number.isInteger(v) && v >= 0 && v <= 255)) {
      return buildCustomColors(r, g, b)
    }
  } catch {
  }
  return null
}

export class MouseTrailManager {
  constructor(canvas) {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')
    this.points = []
    this.raf = null
    this.colorIdx = 0
    this.enabled = true
    this.activeColors = loadCustomColors() || DEFAULT_COLORS  // 优先使用自定义色
    this._bound = {
      move: this.onMove.bind(this),
      resize: this.onResize.bind(this),
      visibility: this.onVisibility.bind(this),
    }
    this.onResize()
    this.attach()
    this.loop()
  }

  onResize() {
    const dpr = window.devicePixelRatio || 1
    this.canvas.width = window.innerWidth * dpr
    this.canvas.height = window.innerHeight * dpr
    this.canvas.style.width = window.innerWidth + 'px'
    this.canvas.style.height = window.innerHeight + 'px'
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  attach() {
    window.addEventListener('pointermove', this._bound.move, {passive: true})
    window.addEventListener('mousemove', this._bound.move, {passive: true})
    window.addEventListener('resize', this._bound.resize, {passive: true})
    document.addEventListener('visibilitychange', this._bound.visibility)
  }

  detach() {
    window.removeEventListener('pointermove', this._bound.move)
    window.removeEventListener('mousemove', this._bound.move)
    window.removeEventListener('resize', this._bound.resize)
    document.removeEventListener('visibilitychange', this._bound.visibility)
  }

  onMove(e) {
    if (!this.enabled) return
    const x = e.clientX
    const y = e.clientY
    const now = performance.now()
    const last = this.points[this.points.length - 1]
    if (last) {
      const dx = x - last.x, dy = y - last.y
      if (dx * dx + dy * dy < 4) return
    }
    this.points.push({x, y, t: now})
    if (this.points.length > TRAIL_LENGTH) this.points.shift()
    if (this.points.length % 8 === 0) {
      this.colorIdx = (this.colorIdx + 1) % this.activeColors.length
    }
  }

  onVisibility() {
    if (document.visibilityState === 'hidden') {
      this.enabled = false
      this.points = []
    } else {
      this.enabled = true
    }
  }

  pause() {
    this.enabled = false
  }

  resume() {
    this.enabled = true
  }

  /** 设置自定义颜色并持久化，r/g/b 均为 0-255 整数 */
  setCustomColor(r, g, b) {
    this.activeColors = buildCustomColors(r, g, b)
    try {
      localStorage.setItem(CUSTOM_COLOR_KEY, JSON.stringify({r, g, b}))
    } catch {
    }
  }

  /** 恢复默认主题色 */
  resetColor() {
    this.activeColors = DEFAULT_COLORS
    try {
      localStorage.removeItem(CUSTOM_COLOR_KEY)
    } catch {
    }
  }

  loop() {
    this.raf = requestAnimationFrame(() => this.loop())
    const now = performance.now()
    const ctx = this.ctx
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)

    // 剔除已超出生命周期的旧点
    while (this.points.length > 0 && now - this.points[0].t > POINT_LIFETIME_MS) {
      this.points.shift()
    }

    const pts = this.points
    if (pts.length < 2) return

    const c1 = this.activeColors[this.colorIdx]
    const c2 = this.activeColors[(this.colorIdx + 1) % this.activeColors.length]
    const n = pts.length

    ctx.save()
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'

    for (let i = 1; i < n; i++) {
      const posT = i / n  // 0=尾端 → 1=头部，控制线宽

      // 用线段中点的时间戳计算存活比例（0=刚生成, 1=即将消失）
      const age = now - pts[i - 1].t
      const lifeRatio = Math.min(age / POINT_LIFETIME_MS, 1)  // 0→1
      const fadeAlpha = 1 - lifeRatio  // 越老越透明

      if (fadeAlpha <= 0) continue

      const w = TRAIL_MIN_WIDTH + (TRAIL_MAX_WIDTH - TRAIL_MIN_WIDTH) * posT
      const segAlpha = fadeAlpha * posT * 0.85

      const r = Math.round(c1.r + (c2.r - c1.r) * posT)
      const g = Math.round(c1.g + (c2.g - c1.g) * posT)
      const b = Math.round(c1.b + (c2.b - c1.b) * posT)

      // Catmull-Rom → Bezier 控制点
      const p0 = pts[Math.max(i - 2, 0)]
      const p1 = pts[i - 1]
      const p2 = pts[i]
      const p3 = pts[Math.min(i + 1, n - 1)]
      const cp1x = p1.x + (p2.x - p0.x) / 6
      const cp1y = p1.y + (p2.y - p0.y) / 6
      const cp2x = p2.x - (p3.x - p1.x) / 6
      const cp2y = p2.y - (p3.y - p1.y) / 6

      ctx.beginPath()
      ctx.moveTo(p1.x, p1.y)
      ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y)
      ctx.strokeStyle = `rgba(${r},${g},${b},${segAlpha})`
      ctx.lineWidth = w
      ctx.stroke()
    }

    // 笔尖发光圆点（只在最新点未过期时显示）
    const head = pts[n - 1]
    const headAge = now - head.t
    const headFade = Math.max(0, 1 - headAge / POINT_LIFETIME_MS)
    if (headFade > 0) {
      const grd = ctx.createRadialGradient(head.x, head.y, 0, head.x, head.y, TRAIL_MAX_WIDTH * 3)
      grd.addColorStop(0, `rgba(${c2.r},${c2.g},${c2.b},${headFade * 0.65})`)
      grd.addColorStop(1, `rgba(${c2.r},${c2.g},${c2.b},0)`)
      ctx.beginPath()
      ctx.arc(head.x, head.y, TRAIL_MAX_WIDTH * 3, 0, Math.PI * 2)
      ctx.fillStyle = grd
      ctx.fill()
    }

    ctx.restore()
  }

  destroy() {
    this.detach()
    if (this.raf) cancelAnimationFrame(this.raf)
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
  }
}

export function initMouseTrail() {
  // 用户可通过 localStorage 关闭: setItem('mouse_trail_enabled','false')
  try {
    const flag = localStorage.getItem('mouse_trail_enabled')
    if (flag === 'false') return null
  } catch {}

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return null
  }

  // 移除旧容器（div 版本）
  const old = document.getElementById('mouse-trail-container')
  if (old) old.remove()

  let canvas = document.getElementById('mouse-trail-canvas')
  if (!canvas) {
    canvas = document.createElement('canvas')
    canvas.id = 'mouse-trail-canvas'
    canvas.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9999;display:block;'
    document.body.appendChild(canvas)
  }

  return new MouseTrailManager(canvas)
}
