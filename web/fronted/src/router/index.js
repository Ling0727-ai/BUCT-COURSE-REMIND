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
  console.log(`路由守卫: 从 ${from.path} 到 ${to.path}`)
  
  // 避免无限循环：如果已经在目标路由，直接通过
  if (to.path === from.path) {
    next()
    return
  }
  
  try {
    // 检查认证状态
    const response = await fetch('http://localhost:5000/api/auth/status', {
      method: 'GET',
      credentials: 'include'
    })
    
    let isAuthenticated = false
    let userData = null
    
    if (response.ok) {
      const data = await response.json()
      isAuthenticated = data.authenticated
      userData = data.user
      console.log('认证状态:', isAuthenticated, userData)
    } else {
      console.log('认证检查响应失败:', response.status)
    }
    
    // 处理需要认证的路由
    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (isAuthenticated) {
        console.log('用户已认证，允许访问受保护路由')
        next()
      } else {
        console.log('用户未认证，重定向到登录页')
        next('/login')
      }
      return
    }
    
    // 处理登录/注册页面的访问
    if (to.path === '/login' || to.path === '/register') {
      if (isAuthenticated) {
        console.log('用户已登录，从登录/注册页重定向到首页')
        // 避免从首页重定向回首页
        if (from.path !== '/') {
          next('/')
        } else {
          next()
        }
      } else {
        console.log('用户未登录，允许访问登录/注册页')
        next()
      }
      return
    }
    
    // 处理首页访问
    if (to.path === '/') {
      if (isAuthenticated) {
        console.log('用户已认证，允许访问首页')
        next()
      } else {
        console.log('用户未认证，从首页重定向到登录页')
        next('/login')
      }
      return
    }
    
    // 其他路由直接通过
    console.log('其他路由，直接通过')
    next()
    
  } catch (error) {
    console.error('路由守卫认证检查失败:', error)
    
    // 网络错误时的处理
    if (to.matched.some(record => record.meta.requiresAuth)) {
      next('/login')
    } else if (to.path === '/login' || to.path === '/register') {
      next()
    } else {
      next('/login')
    }
  }
})

export default router