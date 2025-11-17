import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Settings from '../views/Settings.vue'
import Terms from '../views/Terms.vue'
import Privacy from '../views/Privacy.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/terms',
    name: 'Terms',
    component: Terms
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: Privacy
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 检查是否刚刚登录成功，清理过期的刚登录标记
  const justLoggedInRaw = localStorage.getItem('app_just_logged_in')
  if (justLoggedInRaw) {
    const justLoggedInTs = parseInt(justLoggedInRaw, 10)
    if (!isNaN(justLoggedInTs) && (Date.now() - justLoggedInTs > 10000)) {
      // 超过10秒，清除标记
      localStorage.removeItem('app_just_logged_in')
    }
  }

  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      // 检查是否已登录
      const response = await fetch('/api/auth/status', {
        method: 'GET',
        credentials: 'include' // 包含cookies以支持session
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.authenticated) {
          next()
        } else {
          next('/login')
        }
      } else {
        next('/login')
      }
    } catch (error) {
      console.error('认证检查失败:', error)
      next('/login')
    }
  } else {
    // 如果用户已登录且访问登录/注册页面，重定向到首页
    if (to.path === '/login' || to.path === '/register') {
      try {
        const response = await fetch('/api/auth/status', {
          method: 'GET',
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.authenticated) {
            next('/')
            return
          }
        }
      } catch (error) {
        console.error('认证检查失败:', error)
      }
    }
    next()
  }
})

export default router