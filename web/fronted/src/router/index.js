import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Settings from '../views/Settings.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
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