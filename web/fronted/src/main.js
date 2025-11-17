import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import './assets/global.css'
import {initMobileOptimizations} from './utils/mobile-utils'

const app = createApp(App).use(router)
app.mount('#app')
initMobileOptimizations()

console.info('[main.js] 应用入口加载时间:', new Date().toISOString())
window.__APP_MAIN_LOADED = true
// 若需要调试，可取消下一行注释以在页面顶部弹出原生提示
// alert('main.js 已执行')

// ====== 会话关闭后计时处理（关闭页面开始计时 6h 重新登录） ======
// 配置：可在此调整关闭后强制重新登录的小时数
const CLOSE_EXPIRATION_HOURS = 6
const CLOSE_EXPIRATION_MS = CLOSE_EXPIRATION_HOURS * 60 * 60 * 1000
const OPEN_TAB_STORAGE_KEY = 'app_open_tab_ids'
const LAST_CLOSED_AT_KEY = 'app_last_closed_at'
const LOGIN_INFO_KEYS = ['user', 'user'] // localStorage key

// 生成本标签唯一ID
const thisTabId = `${Date.now()}_${Math.random().toString(16).slice(2)}`

function getOpenTabIds() {
  try {
    const raw = localStorage.getItem(OPEN_TAB_STORAGE_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    if (!Array.isArray(arr)) return []
    return arr.filter(id => typeof id === 'string')
  } catch {
    return []
  }
}

function setOpenTabIds(ids) {
  try {
    localStorage.setItem(OPEN_TAB_STORAGE_KEY, JSON.stringify(ids))
  } catch {
  }
}

function markTabOpen() {
  const ids = getOpenTabIds()
  if (!ids.includes(thisTabId)) {
    ids.push(thisTabId)
    setOpenTabIds(ids)
  }
}

function markTabClosed() {
  const ids = getOpenTabIds().filter(id => id !== thisTabId)
  setOpenTabIds(ids)
  if (ids.length === 0) {
    // 最后一个标签被关闭，记录关闭时间
    try {
      localStorage.setItem(LAST_CLOSED_AT_KEY, String(Date.now()))
    } catch {
    }
  }
}

function hasLoginInfo() {
  // 检查是否仍有登录信息（localStorage 或 sessionStorage 中）
  const localUser = localStorage.getItem('user')
  const sessionUser = sessionStorage.getItem('user')
  return !!(localUser || sessionUser)
}

async function forceLogout(reason) {
  try {
    await fetch('/api/auth/logout', {method: 'POST', credentials: 'include'})
  } catch {
  }
  // 清理存储
  localStorage.removeItem('user')
  sessionStorage.removeItem('user')
  // 可附带原因以供登录页提示
  try {
    sessionStorage.setItem('logout_reason', reason)
  } catch {
  }
  // 重定向登录
  router.replace('/login')
}

function checkClosureExpiration() {
  // 如果未登录则不处理
  if (!hasLoginInfo()) return

  // 检查是否刚刚登录成功（5秒内）
  const justLoggedInRaw = localStorage.getItem('app_just_logged_in')
  if (justLoggedInRaw) {
    const justLoggedInTs = parseInt(justLoggedInRaw, 10)
    if (!isNaN(justLoggedInTs) && (Date.now() - justLoggedInTs < 5000)) {
      // 刚登录，跳过检查
      return
    }
    // 超过5秒，清除标记
    localStorage.removeItem('app_just_logged_in')
  }

  const lastClosedRaw = localStorage.getItem(LAST_CLOSED_AT_KEY)
  if (!lastClosedRaw) return
  const lastClosedTs = parseInt(lastClosedRaw, 10)
  if (isNaN(lastClosedTs)) return
  const diff = Date.now() - lastClosedTs
  if (diff >= CLOSE_EXPIRATION_MS) {
    forceLogout(`离开页面超过 ${CLOSE_EXPIRATION_HOURS}h，已自动退出`) // 可在登录页显示
  }
}

// 初始化：标记当前标签开启，并检查是否需要强制退出
markTabOpen()
checkClosureExpiration()

// 监听标签关闭
window.addEventListener('beforeunload', () => {
  markTabClosed()
})

// 可选：监听可见性变化（避免系统挂起长时间、再回到页面时立即检查）
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    checkClosureExpiration()
  }
})
// ====== 结束 ======
