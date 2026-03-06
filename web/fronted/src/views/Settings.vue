<template>
  <div class="container">
    <div class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>系统设置</h1>
    </div>

    <div class="content">
      <!-- 学生信息设置 -->
      <div class="section">
        <h2 class="section-title">学生信息配置</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学号</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="studentInfo.studentId" 
              placeholder="请输入学号"
            >
          </div>
          <div class="form-group">
            <label class="form-label">外部系统密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="studentInfo.sPassword" 
              placeholder="用于访问教务系统的密码"
            >
          </div>
        </div>
        <div class="info-tip">
          此信息用于自动登录教务系统获取作业和考试信息，请确保信息准确
        </div>
        <button class="btn btn-primary" @click="saveStudentInfo" style="margin-top: 15px;">
          保存学生信息
        </button>
      </div>

      <!-- 邮箱设置 -->
      <div class="section">
        <h2 class="section-title">邮箱设置</h2>
        <div class="form-group">
          <label class="form-label">账号邮箱</label>
          <input
            type="email" 
            v-model="emailSettings.email"
            class="form-input"
            placeholder="请输入新的邮箱地址"
          >
        </div>
        <div class="info-tip">
          修改邮箱将同时更新账号恢复邮箱和作业提醒接收邮箱。系统默认使用注册邮箱发送提醒。
        </div>
        <button class="btn btn-primary" @click="saveEmailSettings" style="margin-top: 15px;">
          修改邮箱
        </button>
      </div>

      <!-- 数据管理设置 -->
      <div class="section">
        <h2 class="section-title">数据管理</h2>
        <div class="data-status-card">
          <div class="status-info">
            <div class="status-item">
              <span class="status-label">数据状态:</span>
              <span :class="['status-value', dataStatus.hasData ? 'status-active' : 'status-inactive']">
                {{ dataStatus.hasData ? '已同步' : '未同步' }}
              </span>
            </div>
            <div class="status-item" v-if="dataStatus.lastUpdate">
              <span class="status-label">最后更新:</span>
              <span class="status-value">{{ formatDateTime(dataStatus.lastUpdate) }}</span>
            </div>
            <div class="status-item" v-if="dataStatus.hoursUntilRefresh !== null">
              <span class="status-label">下次自动刷新:</span>
              <span class="status-value">{{ formatNextRefresh(dataStatus.hoursUntilRefresh) }}</span>
            </div>
          </div>
          <div class="refresh-actions">
            <button 
              class="btn btn-refresh" 
              @click="refreshCourseData" 
              :disabled="refreshing"
              :class="{ 'refreshing': refreshing }"
            >
              <i v-if="refreshing" class="fas fa-spinner fa-spin"></i>
              {{ refreshing ? '刷新中...' : '手动刷新数据' }}
            </button>
            <div class="refresh-tip">数据每12小时自动刷新一次，也可手动刷新</div>
          </div>
        </div>
      </div>

      <!-- 鼠标拖尾颜色设置 -->
      <div class="section">
        <h2 class="section-title">
          鼠标拖尾颜色
          <span class="beta-badge">测试版</span>
        </h2>

        <div class="color-picker-wrap">
          <!-- 色环 Canvas -->
          <div class="wheel-area">
            <canvas
                ref="wheelCanvas"
                class="color-wheel"
                height="200" width="200"
                @mousedown="onWheelDown"
                @touchstart.prevent="onWheelTouch"
            ></canvas>
            <!-- 色相环指示点 -->
            <div
                :style="{
                left: wheelCursorPos.x + 'px',
                top:  wheelCursorPos.y + 'px',
                background: `hsl(${trailColor.h},100%,50%)`
              }"
                class="wheel-cursor"
            ></div>

            <canvas
                ref="svCanvas"
                class="sv-square"
                height="120" width="120"
                @mousedown="onSVDown"
                @touchstart.prevent="onSVTouch"
            ></canvas>
            <!-- SV 方块指示点 -->
            <div
                :style="{
                left: svCursorPos.x + 'px',
                top:  svCursorPos.y + 'px'
              }"
                class="sv-cursor"
            ></div>
          </div>

          <!-- 右侧控制区 -->
          <div class="color-controls">
            <!-- 颜色预览 -->
            <div class="color-preview-row">
              <div :style="{ background: previewHex }" class="color-swatch"></div>
              <span class="color-hex-label">{{ previewHex.toUpperCase() }}</span>
            </div>

            <!-- RGB 输入 -->
            <div class="rgb-inputs">
              <div class="rgb-input-item">
                <label>R</label>
                <input v-model.number="trailColor.r" class="rgb-input" max="255" min="0" type="number"
                       @input="onRGBInput"/>
              </div>
              <div class="rgb-input-item">
                <label>G</label>
                <input v-model.number="trailColor.g" class="rgb-input" max="255" min="0" type="number"
                       @input="onRGBInput"/>
              </div>
              <div class="rgb-input-item">
                <label>B</label>
                <input v-model.number="trailColor.b" class="rgb-input" max="255" min="0" type="number"
                       @input="onRGBInput"/>
              </div>
            </div>

            <!-- HEX 输入 -->
            <div class="hex-input-row">
              <span class="hex-prefix">#</span>
              <input
                  v-model="hexInput" class="hex-input"
                  maxlength="6"
                  placeholder="00BBCC"
                  type="text"
                  @blur="syncHexInput"
                  @input="onHexInput"
              />
            </div>

            <!-- 操作按钮 -->
            <div class="color-btn-row">
              <button class="btn btn-primary" @click="applyTrailColor">应用</button>
              <button class="btn btn-outline" @click="resetTrailColor">重置默认</button>
            </div>

            <div class="info-tip" style="margin-top:14px;">
              颜色偏好存储于浏览器本地，清除缓存后将恢复默认
            </div>
          </div>
        </div>
      </div>


    </div>
    <div v-if="toast.show" :class="['toast', toast.type]">
      <div style="display: flex; align-items: center; gap: 10px;">
        <i :class="toastIcon"></i>
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
import {computed, nextTick, onMounted, onUnmounted, reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useToast} from './home/composables/useToast.js'
import './home/styles/toast.css'

export default {
  name: 'Settings',
  setup() {
    const router = useRouter()
    // 引入全局悬浮 Toast
    const {showToast: showTopToast} = useToast()

    // 设置数据
    const settings = reactive({
      serverUrl: ''
    })

    // 学生信息数据
    const studentInfo = reactive({
      studentId: '',
      sPassword: ''
    })

    // 邮箱设置
    const emailSettings = reactive({
      email: ''
    })
    const toast = reactive({ show: false, message: '', type: 'success' })
    
    // 数据状态相关
    const dataStatus = reactive({
      hasData: false,
      lastUpdate: null,
      nextAutoRefresh: null,
      hoursUntilRefresh: null
    })
    const refreshing = ref(false)

    const toastIcon = computed(() => {
      const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return icons[toast.type]
    })

    // 返回上一页
    const goBack = () => {
      router.back()
    }

    // 保存邮箱设置
    const saveEmailSettings = async () => {
      if (!emailSettings.email) {
        showToast('请填写邮箱地址', 'error')
        return
      }

      // 验证邮箱格式
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailPattern.test(emailSettings.email)) {
        showToast('邮箱格式不正确', 'error')
        return
      }

      showToast('正在修改邮箱...', 'info')

      try {
        const response = await fetch('/api/auth/update-email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: emailSettings.email
          })
        })

        const data = await response.json()

        if (response.ok) {
          showToast('邮箱修改成功！账号恢复和提醒邮箱已同步更新', 'success')
          await loadUserInfo() // 重新加载用户信息
        } else {
          showToast(data.error || '修改失败', 'error')
        }
      } catch (error) {
        showToast('网络错误：' + error.message, 'error')
      }
    }

    // 保存学生信息
    const saveStudentInfo = async () => {
      // 允许部分更新：只改学号或只改密码
      const payload = {}
      if (studentInfo.studentId && studentInfo.studentId.trim() !== '') {
        payload.student_id = studentInfo.studentId.trim()
      }
      if (studentInfo.sPassword && !/^•+$/.test(studentInfo.sPassword.trim())) {
        // 只有在不是掩码占位时才发送密码
        payload.s_password = studentInfo.sPassword
      }

      if (Object.keys(payload).length === 0) {
        showToast('请填写学号或新密码', 'error')
        return
      }

      showToast('正在保存学生信息...', 'info')

      try {
        const response = await fetch('/api/auth/update-student-info', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        const data = await response.json()

        if (response.ok) {
          // 保存成功后，若更新了密码，则使用新长度生成掩码
          if ('s_password' in payload) {
            studentInfo.sPassword = '•'.repeat(Math.min(payload.s_password.length, 100))
          }
          showToast(data.message || '学生信息保存成功！', 'success')
        } else {
          showToast(data.error || data.message || '保存失败', 'error')
        }
      } catch (error) {
        showToast('网络错误：' + error.message, 'error')
      }
    }


    // 显示提示消息（改为调用全局顶部悬浮 Toast）
    const showToast = (message, type = 'success', title) => {
      const titleMap = {success: '成功', error: '错误', info: '提示', warning: '提示'}
      // 统一使用顶部悬浮窗；不再使用本地内嵌 Toast
      showTopToast(type, title || titleMap[type] || '提示', message)
    }

    // 格式化日期时间
    const formatDateTime = (dateString) => {
      if (!dateString) return '未知'
      try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZone: 'Asia/Shanghai'
        })
      } catch (error) {
        return '格式错误'
      }
    }

    // 格式化下次刷新时间
    const formatNextRefresh = (hours) => {
      if (hours === null || hours === undefined) return '未知'
      if (hours <= 0) return '即将刷新'
      if (hours < 1) {
        const minutes = Math.round(hours * 60)
        return `${minutes}分钟后`
      }
      return `${Math.round(hours * 10) / 10}小时后`
    }

    // 获取数据状态
    const loadDataStatus = async () => {
      try {
        const response = await fetch('/api/course-data/status', {
          method: 'GET',
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            dataStatus.hasData = data.has_data
            dataStatus.lastUpdate = data.last_update
            dataStatus.nextAutoRefresh = data.next_auto_refresh
            dataStatus.hoursUntilRefresh = data.hours_until_refresh
          }
        } else {
          console.warn('获取数据状态失败')
        }
      } catch (error) {
        console.error('获取数据状态错误:', error)
      }
    }

    // 手动刷新课程数据
    const refreshCourseData = async () => {
      if (refreshing.value) return
      
      refreshing.value = true
      showToast('正在刷新课程数据...', 'info')
      
      try {
        const response = await fetch('/api/course-data/refresh', {
          method: 'POST',
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            showToast(`数据刷新成功！共更新 ${data.count} 条记录`, 'success')
            // 重新加载数据状态
            await loadDataStatus()
          } else {
            showToast(data.error || '刷新失败', 'error')
          }
        } else {
          const errorData = await response.json()
          showToast(errorData.error || '刷新失败，请重试', 'error')
        }
      } catch (error) {
        console.error('刷新数据错误:', error)
        showToast('网络错误，请检查连接后重试', 'error')
      } finally {
        refreshing.value = false
      }
    }

    // 加载用户信息
    const loadUserInfo = async () => {
      try {
        const response = await fetch('/api/auth/user-info', {credentials: 'include'})
        if (response.ok) {
          const data = await response.json()
          studentInfo.studentId = data.student_id || ''
          // 根据后端返回的长度渲染掩码
          if (data.has_student_password && data.student_password_length > 0) {
            studentInfo.sPassword = '•'.repeat(Math.min(data.student_password_length, 100))
          } else {
            studentInfo.sPassword = ''
          }
          // 加载用户邮箱
          emailSettings.email = data.email || ''
        }
      } catch (error) {
        console.error('加载用户信息失败:', error)
      }
    }

    // 初始化
    loadUserInfo()
    loadDataStatus()

    // ── 鼠标拖尾颜色设置 ──────────────────────────────────────────
    const CUSTOM_COLOR_KEY = 'mouse_trail_custom_color'
    const wheelCanvas = ref(null)
    const svCanvas = ref(null)

    // 从 localStorage 读取初始颜色，否则用默认青色
    function loadInitColor() {
      try {
        const raw = localStorage.getItem(CUSTOM_COLOR_KEY)
        if (raw) {
          const {r, g, b} = JSON.parse(raw)
          if ([r, g, b].every(v => Number.isInteger(v) && v >= 0 && v <= 255)) {
            return rgbToHsv(r, g, b)
          }
        }
      } catch {
      }
      return {h: 188, s: 0.86, v: 0.93} // 默认青色
    }

    const initHsv = loadInitColor()
    const trailColor = reactive({
      h: initHsv.h, s: initHsv.s, v: initHsv.v,
      ...hsvToRgb(initHsv.h, initHsv.s, initHsv.v)
    })
    const hexInput = ref(rgbToHex(trailColor.r, trailColor.g, trailColor.b))

    // ── HSV ↔ RGB ↔ HEX 工具函数 ──
    function hsvToRgb(h, s, v) {
      const c = v * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = v - c
      let r = 0, g = 0, b = 0
      if (h < 60) {
        r = c;
        g = x;
        b = 0
      } else if (h < 120) {
        r = x;
        g = c;
        b = 0
      } else if (h < 180) {
        r = 0;
        g = c;
        b = x
      } else if (h < 240) {
        r = 0;
        g = x;
        b = c
      } else if (h < 300) {
        r = x;
        g = 0;
        b = c
      } else {
        r = c;
        g = 0;
        b = x
      }
      return {r: Math.round((r + m) * 255), g: Math.round((g + m) * 255), b: Math.round((b + m) * 255)}
    }

    function rgbToHsv(r, g, b) {
      r /= 255;
      g /= 255;
      b /= 255
      const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min
      let h = 0, s = max === 0 ? 0 : d / max, v = max
      if (d !== 0) {
        if (max === r) h = ((g - b) / d + 6) % 6
        else if (max === g) h = (b - r) / d + 2
        else h = (r - g) / d + 4
        h = h * 60
      }
      return {h, s, v}
    }

    function rgbToHex(r, g, b) {
      return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('')
    }

    function hexToRgb(hex) {
      hex = hex.replace(/^#/, '')
      if (hex.length === 3) hex = hex.split('').map(c => c + c).join('')
      if (hex.length !== 6) return null
      const n = parseInt(hex, 16)
      if (isNaN(n)) return null
      return {r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255}
    }

    const previewHex = computed(() => rgbToHex(trailColor.r, trailColor.g, trailColor.b))

    // ── Canvas 绘制 ──
    const WHEEL_SIZE = 200
    const WHEEL_RADIUS = 90    // 色环外径
    const WHEEL_INNER = 62    // 色环内径（中心空心）
    const SV_SIZE = 120

    function drawWheel() {
      const canvas = wheelCanvas.value;
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      const cx = WHEEL_SIZE / 2, cy = WHEEL_SIZE / 2
      ctx.clearRect(0, 0, WHEEL_SIZE, WHEEL_SIZE)
      // 绘制色相环（一圈扇形段）
      const steps = 360
      for (let i = 0; i < steps; i++) {
        const start = (i / steps) * Math.PI * 2 - Math.PI / 2
        const end = ((i + 1) / steps) * Math.PI * 2 - Math.PI / 2
        ctx.beginPath()
        ctx.moveTo(cx, cy)
        ctx.arc(cx, cy, WHEEL_RADIUS, start, end)
        ctx.closePath()
        ctx.fillStyle = `hsl(${i},100%,50%)`
        ctx.fill()
      }
      // 挖空中心
      ctx.save()
      ctx.globalCompositeOperation = 'destination-out'
      ctx.beginPath()
      ctx.arc(cx, cy, WHEEL_INNER, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    }

    function drawSV() {
      const canvas = svCanvas.value;
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, SV_SIZE, SV_SIZE)
      // 底色：纯色 hue
      ctx.fillStyle = `hsl(${trailColor.h},100%,50%)`
      ctx.fillRect(0, 0, SV_SIZE, SV_SIZE)
      // 白色横向渐变（S轴）
      const wGrd = ctx.createLinearGradient(0, 0, SV_SIZE, 0)
      wGrd.addColorStop(0, 'rgba(255,255,255,1)')
      wGrd.addColorStop(1, 'rgba(255,255,255,0)')
      ctx.fillStyle = wGrd
      ctx.fillRect(0, 0, SV_SIZE, SV_SIZE)
      // 黑色纵向渐变（V轴）
      const bGrd = ctx.createLinearGradient(0, 0, 0, SV_SIZE)
      bGrd.addColorStop(0, 'rgba(0,0,0,0)')
      bGrd.addColorStop(1, 'rgba(0,0,0,1)')
      ctx.fillStyle = bGrd
      ctx.fillRect(0, 0, SV_SIZE, SV_SIZE)
    }

    // ── 指示点位置 ──
    const wheelCursorPos = computed(() => {
      const cx = WHEEL_SIZE / 2, cy = WHEEL_SIZE / 2
      const r = (WHEEL_INNER + WHEEL_RADIUS) / 2
      const a = (trailColor.h - 90) * Math.PI / 180
      return {x: cx + r * Math.cos(a) - 7, y: cy + r * Math.sin(a) - 7}
    })
    const svCursorPos = computed(() => {
      // SV 方块在 wheel canvas 正中心
      const offset = (WHEEL_SIZE - SV_SIZE) / 2
      return {
        x: offset + trailColor.s * SV_SIZE - 6,
        y: offset + (1 - trailColor.v) * SV_SIZE - 6
      }
    })

    // ── 色环拖拽 ──
    function pickHue(e, canvas) {
      const rect = canvas.getBoundingClientRect()
      const cx = WHEEL_SIZE / 2, cy = WHEEL_SIZE / 2
      const x = (e.clientX - rect.left) - cx, y = (e.clientY - rect.top) - cy
      let h = Math.atan2(y, x) * 180 / Math.PI + 90
      if (h < 0) h += 360
      trailColor.h = h % 360
      const rgb = hsvToRgb(trailColor.h, trailColor.s, trailColor.v)
      Object.assign(trailColor, rgb)
      hexInput.value = rgbToHex(trailColor.r, trailColor.g, trailColor.b).replace('#', '')
      drawSV()
    }

    let wheelDragging = false

    function onWheelDown(e) {
      wheelDragging = true;
      pickHue(e, wheelCanvas.value)
    }

    function onWheelMove(e) {
      if (wheelDragging) pickHue(e, wheelCanvas.value)
    }

    function onWheelUp() {
      wheelDragging = false
    }

    function onWheelTouch(e) {
      pickHue(e.touches[0], wheelCanvas.value)
    }

    // ── SV 方块拖拽 ──
    function pickSV(e, canvas) {
      const rect = canvas.getBoundingClientRect()
      let s = (e.clientX - rect.left) / SV_SIZE
      let v = 1 - (e.clientY - rect.top) / SV_SIZE
      s = Math.max(0, Math.min(1, s))
      v = Math.max(0, Math.min(1, v))
      trailColor.s = s;
      trailColor.v = v
      const rgb = hsvToRgb(trailColor.h, s, v)
      Object.assign(trailColor, rgb)
      hexInput.value = rgbToHex(trailColor.r, trailColor.g, trailColor.b).replace('#', '')
    }

    let svDragging = false

    function onSVDown(e) {
      svDragging = true;
      pickSV(e, svCanvas.value)
    }

    function onSVMove(e) {
      if (svDragging) pickSV(e, svCanvas.value)
    }

    function onSVUp() {
      svDragging = false
    }

    function onSVTouch(e) {
      pickSV(e.touches[0], svCanvas.value)
    }

    // ── RGB 输入同步 ──
    function onRGBInput() {
      trailColor.r = Math.max(0, Math.min(255, trailColor.r || 0))
      trailColor.g = Math.max(0, Math.min(255, trailColor.g || 0))
      trailColor.b = Math.max(0, Math.min(255, trailColor.b || 0))
      const hsv = rgbToHsv(trailColor.r, trailColor.g, trailColor.b)
      trailColor.h = hsv.h;
      trailColor.s = hsv.s;
      trailColor.v = hsv.v
      hexInput.value = rgbToHex(trailColor.r, trailColor.g, trailColor.b).replace('#', '')
      drawSV()
    }

    // ── HEX 输入同步 ──
    function onHexInput() {
      const rgb = hexToRgb(hexInput.value)
      if (!rgb) return
      Object.assign(trailColor, rgb)
      const hsv = rgbToHsv(rgb.r, rgb.g, rgb.b)
      trailColor.h = hsv.h;
      trailColor.s = hsv.s;
      trailColor.v = hsv.v
      drawSV()
    }

    function syncHexInput() {
      hexInput.value = rgbToHex(trailColor.r, trailColor.g, trailColor.b).replace('#', '')
    }

    // ── 应用 / 重置 ──
    function applyTrailColor() {
      const mgr = window.__MOUSE_TRAIL_MANAGER
      if (mgr && mgr.setCustomColor) mgr.setCustomColor(trailColor.r, trailColor.g, trailColor.b)
      else {
        // manager 不存在时直接写 localStorage，下次刷新生效
        try {
          localStorage.setItem(CUSTOM_COLOR_KEY, JSON.stringify({r: trailColor.r, g: trailColor.g, b: trailColor.b}))
        } catch {
        }
      }
      showToast('拖尾颜色已应用', 'success')
    }

    function resetTrailColor() {
      const mgr = window.__MOUSE_TRAIL_MANAGER
      if (mgr && mgr.resetColor) mgr.resetColor()
      else {
        try {
          localStorage.removeItem(CUSTOM_COLOR_KEY)
        } catch {
        }
      }
      // 恢复默认青色
      const hsv = {h: 188, s: 0.86, v: 0.93}
      trailColor.h = hsv.h;
      trailColor.s = hsv.s;
      trailColor.v = hsv.v
      const rgb = hsvToRgb(hsv.h, hsv.s, hsv.v)
      Object.assign(trailColor, rgb)
      hexInput.value = rgbToHex(rgb.r, rgb.g, rgb.b).replace('#', '')
      drawSV()
      showToast('已恢复默认颜色', 'info')
    }

    // ── 全局鼠标抬起（拖拽结束）──
    function onGlobalMouseUp() {
      wheelDragging = false;
      svDragging = false
    }

    function onGlobalMouseMove(e) {
      if (wheelDragging) pickHue(e, wheelCanvas.value)
      if (svDragging) pickSV(e, svCanvas.value)
    }

    // 锁定 body 滚动，防止双滚动条
    onMounted(() => {
      document.body.style.overflow = 'hidden'
      window.addEventListener('mousemove', onGlobalMouseMove)
      window.addEventListener('mouseup', onGlobalMouseUp)
      nextTick(() => {
        drawWheel();
        drawSV()
      })
    })
    onUnmounted(() => {
      document.body.style.overflow = ''
      window.removeEventListener('mousemove', onGlobalMouseMove)
      window.removeEventListener('mouseup', onGlobalMouseUp)
    })

    return {
      settings,
      studentInfo,
      emailSettings,
      toast,
      toastIcon,
      goBack,
      saveEmailSettings,
      saveStudentInfo,
      showToast,
      dataStatus,
      refreshing,
      formatDateTime,
      formatNextRefresh,
      loadDataStatus,
      refreshCourseData,
      // 颜色选择器
      wheelCanvas,
      svCanvas,
      trailColor,
      hexInput,
      previewHex,
      wheelCursorPos,
      svCursorPos,
      onWheelDown,
      onWheelTouch,
      onSVDown,
      onSVTouch,
      onRGBInput,
      onHexInput,
      syncHexInput,
      applyTrailColor,
      resetTrailColor,
    }
  }
}
</script>

<style scoped>
/* 全局容器 */
.container {
  height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdfa 100%);
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
}

/* 装饰性浮动元素 */
.container::before {
  content: '';
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  animation: float 30s linear infinite;
  pointer-events: none;
  z-index: 0;
}

.container::after {
  content: '';
  position: fixed;
  top: 10%;
  right: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.05), transparent 70%);
  border-radius: 50%;
  animation: pulse 6s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes float {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-30px, -30px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.1); opacity: 0.2; }
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.1);
  color: #0f172a;
  padding: 25px 35px;
  margin: 20px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}


.header h1 {
  font-size: 1.6em;
  margin: 0;
  font-weight: 700;
  color: #0f172a;
  position: relative;
  z-index: 2;
  letter-spacing: -0.3px;
}

.back-btn {
  background: transparent;
  border: 1.5px solid #e5e7eb;
  color: #475569;
  padding: 9px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
  font-size: 14px;
  position: relative;
  z-index: 2;
}

.back-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
}

.content {
  padding: 20px 35px 40px 35px;
  position: relative;
  z-index: 1;
}

.section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(14, 165, 233, 0.1);
  border-left: 4px solid #0ea5e9;
  position: relative;
  overflow: hidden;
}

.section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(14, 165, 233, 0.02));
  pointer-events: none;
  z-index: 0;
}

.section-title {
  font-size: 1.1em;
  color: #0f172a;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  letter-spacing: -0.1px;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid rgba(229, 231, 235, 0.8);
  border-radius: 12px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  color: #1f2937;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.form-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.form-input::placeholder {
  color: #6b7280;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.webhook-item {
  background: rgba(248, 249, 250, 0.9);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(233, 236, 239, 0.8);
  border-radius: 18px;
  padding: 25px;
  margin-bottom: 20px;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
}

.webhook-item:hover {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
  transform: translateY(-3px);
}

.webhook-item.active {
  border-color: rgba(39, 174, 96, 0.6);
  background: linear-gradient(135deg, rgba(248, 255, 248, 0.9), rgba(232, 245, 232, 0.9));
  box-shadow: 0 15px 35px rgba(39, 174, 96, 0.15);
}

.webhook-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.webhook-title {
  font-size: 1.1em;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.webhook-title i {
  color: #667eea;
}

.webhook-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 5px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.webhook-status.active {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.webhook-status.inactive {
  background: linear-gradient(135deg, #e74c3c, #ec7063);
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.webhook-status i {
  font-size: 0.9em;
}

.webhook-actions {
  display: flex;
  gap: 8px;
  margin-top: 15px;
  justify-content: flex-end;
  flex-wrap: wrap;
  align-items: center;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
  background: linear-gradient(135deg, #0284c7, #0891b2);
}

.btn-success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}

.btn-success:hover {
  background: linear-gradient(135deg, #16a34a, #15803d);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(14, 165, 233, 0.3);
  color: #0ea5e9;
}

.btn-outline:hover {
  background: #0ea5e9;
  color: white;
  border-color: #0ea5e9;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.3);
}

.btn-small {
  padding: 8px 14px;
  font-size: 12px;
}

.add-webhook-btn {
  width: 100%;
  padding: 25px;
  border: 2px dashed rgba(102, 126, 234, 0.4);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #667eea;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.add-webhook-btn:hover {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
}

.webhook-type-select {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.webhook-type {
  padding: 20px 15px;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.9));
  backdrop-filter: blur(10px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.1);
  color: #1e293b;
  font-weight: 600;
}

.webhook-type:hover {
  border-color: rgba(102, 126, 234, 0.7);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.1));
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25);
  color: #667eea;
}

.webhook-type.selected {
  border-color: rgba(102, 126, 234, 0.9);
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.webhook-type i {
  font-size: 2.2em;
  margin-bottom: 12px;
  display: block;
  opacity: 0.8;
}

.webhook-type:hover i,
.webhook-type.selected i {
  opacity: 1;
}

.info-tip {
  background: rgba(14, 165, 233, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 15px;
  padding: 18px;
  margin-top: 20px;
  font-size: 14px;
  color: #0284c7;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
}

.info-tip i {
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}



/* 对话框样式 */
.webhook-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  animation: fadeIn 0.3s ease;
}

.webhook-dialog {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 35px;
  border-radius: 20px;
  max-width: 550px;
  width: 90%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.3s ease;
}

.webhook-dialog h3 {
  color: #1f2937;
  font-size: 1.5em;
  font-weight: 600;
  margin-bottom: 25px;
  text-align: center;
}

.dialog-actions {
  text-align: center;
  margin-top: 25px;
  position: relative;
  z-index: 1;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    transform: translateY(30px);
    opacity: 0;
  }
  to { 
    transform: translateY(0);
    opacity: 1;
  }
}

/* Toast样式 */
.toast {
  position: fixed;
  top: 25px;
  right: 25px;
  padding: 18px 28px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border-radius: 15px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 999999;
  animation: toastSlideIn 0.4s ease;
  font-weight: 500;
  pointer-events: auto;
}

.toast.error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.toast.info {
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
}

@keyframes toastSlideIn {
  from {
    transform: translateX(100%) translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateX(0) translateY(0);
    opacity: 1;
  }
}

/* 数据状态卡片样式 */
.data-status-card {
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(226, 232, 240, 0.8);
  border-radius: 18px;
  padding: 25px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 30px;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.data-status-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(14, 165, 233, 0.02));
  pointer-events: none;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  font-weight: 600;
  color: #475569;
  min-width: 100px;
}

.status-value {
  font-weight: 500;
  color: #1e293b;
}

.status-active {
  color: #22c55e !important;
  font-weight: 600;
}

.status-inactive {
  color: #ef4444 !important;
  font-weight: 600;
}

.refresh-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.btn-refresh {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  padding: 14px 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 160px;
  justify-content: center;
}

.btn-refresh:hover:not(:disabled) {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
}

.btn-refresh:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-refresh.refreshing {
  background: linear-gradient(135deg, #6b7280, #9ca3af);
}

.refresh-tip {
  font-size: 12px;
  color: #64748b;
  text-align: center;
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 200px;
}

.refresh-tip i {
  color: #0ea5e9;
  font-size: 11px;
}

@media (max-width: 768px) {
  .container::before,
  .container::after {
    display: none;
  }

  .header {
    margin: 15px;
    padding: 20px 25px;
    gap: 15px;
  }

  .header h1 {
    font-size: 1.6em;
  }

  .content {
    padding: 15px 30px 30px 30px;
  }

  .section {
    padding: 25px 20px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .webhook-type-select {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .webhook-type {
    padding: 15px 10px;
  }

  .webhook-actions {
    position: static;
    margin-top: 20px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .webhook-dialog {
    padding: 25px 20px;
    margin: 20px;
  }

  .save-section {
    padding: 25px 20px;
  }

  .btn {
    padding: 10px 16px;
    font-size: 13px;
  }

  .btn-small {
    padding: 6px 10px;
    font-size: 11px;
  }

  .data-status-card {
    grid-template-columns: 1fr;
    gap: 20px;
    text-align: center;
  }

  .status-info {
    align-items: center;
  }

  .status-item {
    justify-content: center;
  }

  .refresh-actions {
    align-items: center;
  }
}

@media (max-width: 480px) {
  .header,
  .content {
    margin: 10px;
    padding: 15px 20px;
  }

  .section {
    padding: 20px 15px;
  }

  .webhook-type-select {
    grid-template-columns: 1fr;
  }

  .webhook-actions {
    flex-direction: column;
    gap: 8px;
  }

  .form-input {
    padding: 12px 16px;
    font-size: 14px;
  }
}

/* ── 测试版徽标 ── */
.beta-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  color: #fff;
  margin-left: 10px;
  vertical-align: middle;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.35);
  text-transform: uppercase;
}

/* ── 颜色选择器整体布局 ── */
.color-picker-wrap {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  flex-wrap: wrap;
}

/* ── 色环 + SV 方块区域 ── */
.wheel-area {
  position: relative;
  width: 200px;
  height: 200px;
  flex-shrink: 0;
}

.color-wheel {
  position: absolute;
  top: 0;
  left: 0;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  cursor: crosshair;
  touch-action: none;
}

.sv-square {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 120px;
  transform: translate(-50%, -50%);
  border-radius: 6px;
  cursor: crosshair;
  touch-action: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
}

/* 色环指示点 */
.wheel-cursor {
  position: absolute;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2.5px solid #fff;
  box-shadow: 0 0 0 1.5px rgba(0, 0, 0, 0.25), 0 2px 6px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  z-index: 5;
}

/* SV 方块指示点 */
.sv-cursor {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2.5px solid #fff;
  box-shadow: 0 0 0 1.5px rgba(0, 0, 0, 0.3), 0 2px 6px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  z-index: 6;
}

/* ── 右侧控制区 ── */
.color-controls {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.color-preview-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.color-swatch {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
}

.color-hex-label {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: 1px;
  font-family: 'SF Mono', 'Consolas', monospace;
}

/* RGB 输入 */
.rgb-inputs {
  display: flex;
  gap: 10px;
}

.rgb-input-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.rgb-input-item label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.5px;
}

.rgb-input {
  width: 100%;
  padding: 8px 6px;
  border: 2px solid rgba(229, 231, 235, 0.8);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  color: #1f2937;
  transition: border-color 0.2s;
}

.rgb-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}

/* HEX 输入 */
.hex-input-row {
  display: flex;
  align-items: center;
  border: 2px solid rgba(229, 231, 235, 0.8);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
  transition: border-color 0.2s;
}

.hex-input-row:focus-within {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}

.hex-prefix {
  padding: 0 10px;
  font-size: 15px;
  font-weight: 700;
  color: #94a3b8;
  font-family: 'SF Mono', 'Consolas', monospace;
  background: rgba(241, 245, 249, 0.8);
  align-self: stretch;
  display: flex;
  align-items: center;
}

.hex-input {
  flex: 1;
  padding: 10px 10px;
  border: none;
  outline: none;
  font-size: 15px;
  font-weight: 600;
  background: transparent;
  color: #1f2937;
  font-family: 'SF Mono', 'Consolas', monospace;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.color-btn-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .color-picker-wrap {
    flex-direction: column;
    align-items: center;
  }

  .color-controls {
    width: 100%;
  }
}
</style>