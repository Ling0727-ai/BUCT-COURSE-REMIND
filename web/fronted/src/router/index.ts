import {createRouter, createWebHistory} from 'vue-router'
import {checkAuthenticated} from '@/pages/Auth/auth'
import {SESSION_KEYS, SESSION_POLICY} from '@/config/session'

// 路由级懒加载：登录页不再需要下载 Settings / Terms / Privacy 等代码。
const Home = () => import('@/pages/Home/Home.vue')
const Login = () => import('@/pages/Login/Login.vue')
const Register = () => import('@/pages/Register/Register.vue')
const Settings = () => import('@/pages/Settings/Settings.vue')
const Terms = () => import('@/pages/Legal/Terms.vue')
const Privacy = () => import('@/pages/Legal/Privacy.vue')
const NotFound = () => import('@/pages/Legal/NotFound.vue')

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home,
        meta: {requiresAuth: true}
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
        meta: {requiresAuth: true}
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
    },
    {
        // 兜底：未匹配的路径不再静默落到首页
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: NotFound
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

function cleanupLoginMarker(): void {
    const justLoggedInRaw = localStorage.getItem(SESSION_KEYS.justLoggedInAt)
    if (!justLoggedInRaw) {
        return
    }

    const justLoggedInTs = Number.parseInt(justLoggedInRaw, 10)
    if (!Number.isNaN(justLoggedInTs) && Date.now() - justLoggedInTs > SESSION_POLICY.routerMarkerCleanupMs) {
        localStorage.removeItem(SESSION_KEYS.justLoggedInAt)
    }
}

router.beforeEach(async (to, _from, next) => {
    cleanupLoginMarker()

    const {authenticated} = await checkAuthenticated()

    if (!authenticated) {
        localStorage.removeItem(SESSION_KEYS.user)
        sessionStorage.removeItem(SESSION_KEYS.user)
    }

    if (to.matched.some((record) => record.meta.requiresAuth) && !authenticated) {
        next('/login')
        return
    }

    if ((to.path === '/login' || to.path === '/register') && authenticated) {
        next('/')
        return
    }

    next()
})

export default router
