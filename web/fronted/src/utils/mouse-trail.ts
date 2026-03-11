// 鼠标拖尾效果 - Canvas 连续曲线版

type TrailColor = { r: number; g: number; b: number }
type TrailPoint = { x: number; y: number; t: number }

type TrailBindings = {
    move: (event: MouseEvent | PointerEvent) => void
    resize: () => void
    visibility: () => void
}

const TRAIL_LENGTH = 28
const TRAIL_MAX_WIDTH = 3.5
const TRAIL_MIN_WIDTH = 0.4
const POINT_LIFETIME_MS = 2000

const DEFAULT_COLORS: TrailColor[] = [
    {r: 34, g: 211, b: 238},
    {r: 6, g: 182, b: 212},
    {r: 20, g: 184, b: 166},
    {r: 45, g: 212, b: 191}
]

const CUSTOM_COLOR_KEY = 'mouse_trail_custom_color'

function buildCustomColors(r: number, g: number, b: number): TrailColor[] {
    return [
        {r, g, b},
        {r: Math.round(r * 0.85), g: Math.round(g * 0.85), b: Math.round(b * 0.85)},
        {
            r: Math.min(255, Math.round(r * 1.1)),
            g: Math.min(255, Math.round(g * 1.1)),
            b: Math.min(255, Math.round(b * 1.1))
        },
        {r, g, b}
    ]
}

function loadCustomColors(): TrailColor[] | null {
    try {
        const raw = localStorage.getItem(CUSTOM_COLOR_KEY)
        if (!raw) {
            return null
        }

        const payload = JSON.parse(raw) as Partial<TrailColor>
        const r = payload.r
        const g = payload.g
        const b = payload.b

        if ([r, g, b].every((v) => Number.isInteger(v) && (v as number) >= 0 && (v as number) <= 255)) {
            return buildCustomColors(r as number, g as number, b as number)
        }
    } catch {
        // ignore invalid storage payload
    }

    return null
}

export class MouseTrailManager {
    private canvas: HTMLCanvasElement
    private ctx: CanvasRenderingContext2D
    private points: TrailPoint[]
    private raf: number | null
    private colorIdx: number
    private enabled: boolean
    private activeColors: TrailColor[]
    private _bound: TrailBindings

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas
        const ctx = canvas.getContext('2d')
        if (!ctx) {
            throw new Error('Canvas 2D context is not available')
        }

        this.ctx = ctx
        this.points = []
        this.raf = null
        this.colorIdx = 0
        this.enabled = true
        this.activeColors = loadCustomColors() || DEFAULT_COLORS
        this._bound = {
            move: this.onMove.bind(this),
            resize: this.onResize.bind(this),
            visibility: this.onVisibility.bind(this)
        }

        this.onResize()
        this.attach()
        this.loop()
    }

    onResize(): void {
        const dpr = window.devicePixelRatio || 1
        this.canvas.width = window.innerWidth * dpr
        this.canvas.height = window.innerHeight * dpr
        this.canvas.style.width = `${window.innerWidth}px`
        this.canvas.style.height = `${window.innerHeight}px`
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }

    attach(): void {
        window.addEventListener('pointermove', this._bound.move, {passive: true})
        window.addEventListener('mousemove', this._bound.move, {passive: true})
        window.addEventListener('resize', this._bound.resize, {passive: true})
        document.addEventListener('visibilitychange', this._bound.visibility)
    }

    detach(): void {
        window.removeEventListener('pointermove', this._bound.move)
        window.removeEventListener('mousemove', this._bound.move)
        window.removeEventListener('resize', this._bound.resize)
        document.removeEventListener('visibilitychange', this._bound.visibility)
    }

    onMove(event: MouseEvent | PointerEvent): void {
        if (!this.enabled) {
            return
        }

        const x = event.clientX
        const y = event.clientY
        const now = performance.now()
        const last = this.points[this.points.length - 1]

        if (last) {
            const dx = x - last.x
            const dy = y - last.y
            if (dx * dx + dy * dy < 4) {
                return
            }
        }

        this.points.push({x, y, t: now})
        if (this.points.length > TRAIL_LENGTH) {
            this.points.shift()
        }

        if (this.points.length % 8 === 0) {
            this.colorIdx = (this.colorIdx + 1) % this.activeColors.length
        }
    }

    onVisibility(): void {
        if (document.visibilityState === 'hidden') {
            this.enabled = false
            this.points = []
            return
        }

        this.enabled = true
    }

    pause(): void {
        this.enabled = false
    }

    resume(): void {
        this.enabled = true
    }

    setCustomColor(r: number, g: number, b: number): void {
        this.activeColors = buildCustomColors(r, g, b)
        try {
            localStorage.setItem(CUSTOM_COLOR_KEY, JSON.stringify({r, g, b}))
        } catch {
            // ignore storage write failures
        }
    }

    resetColor(): void {
        this.activeColors = DEFAULT_COLORS
        try {
            localStorage.removeItem(CUSTOM_COLOR_KEY)
        } catch {
            // ignore storage write failures
        }
    }

    loop(): void {
        this.raf = requestAnimationFrame(() => this.loop())
        const now = performance.now()
        const ctx = this.ctx
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)

        while (this.points.length > 0 && now - this.points[0].t > POINT_LIFETIME_MS) {
            this.points.shift()
        }

        const pts = this.points
        if (pts.length < 2) {
            return
        }

        const c1 = this.activeColors[this.colorIdx]
        const c2 = this.activeColors[(this.colorIdx + 1) % this.activeColors.length]
        const n = pts.length

        ctx.save()
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'

        for (let i = 1; i < n; i += 1) {
            const posT = i / n
            const age = now - pts[i - 1].t
            const lifeRatio = Math.min(age / POINT_LIFETIME_MS, 1)
            const fadeAlpha = 1 - lifeRatio

            if (fadeAlpha <= 0) {
                continue
            }

            const w = TRAIL_MIN_WIDTH + (TRAIL_MAX_WIDTH - TRAIL_MIN_WIDTH) * posT
            const segAlpha = fadeAlpha * posT * 0.85

            const r = Math.round(c1.r + (c2.r - c1.r) * posT)
            const g = Math.round(c1.g + (c2.g - c1.g) * posT)
            const b = Math.round(c1.b + (c2.b - c1.b) * posT)

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

        const head = pts[n - 1]
        const headAge = now - head.t
        const headFade = Math.max(0, 1 - headAge / POINT_LIFETIME_MS)
        if (headFade > 0) {
            const gradient = ctx.createRadialGradient(head.x, head.y, 0, head.x, head.y, TRAIL_MAX_WIDTH * 3)
            gradient.addColorStop(0, `rgba(${c2.r},${c2.g},${c2.b},${headFade * 0.65})`)
            gradient.addColorStop(1, `rgba(${c2.r},${c2.g},${c2.b},0)`)
            ctx.beginPath()
            ctx.arc(head.x, head.y, TRAIL_MAX_WIDTH * 3, 0, Math.PI * 2)
            ctx.fillStyle = gradient
            ctx.fill()
        }

        ctx.restore()
    }

    destroy(): void {
        this.detach()
        if (this.raf !== null) {
            cancelAnimationFrame(this.raf)
        }
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    }
}

export function initMouseTrail(): MouseTrailManager | null {
    try {
        const flag = localStorage.getItem('mouse_trail_enabled')
        if (flag === 'false') {
            return null
        }
    } catch {
        // ignore storage read failures
    }

    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return null
    }

    const oldContainer = document.getElementById('mouse-trail-container')
    if (oldContainer) {
        oldContainer.remove()
    }

    let canvas = document.getElementById('mouse-trail-canvas') as HTMLCanvasElement | null
    if (!canvas) {
        canvas = document.createElement('canvas')
        canvas.id = 'mouse-trail-canvas'
        canvas.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9999;display:block;'
        document.body.appendChild(canvas)
    }

    return new MouseTrailManager(canvas)
}

