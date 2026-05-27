import {createRouter, createWebHistory} from 'vue-router'
import Home from '@/pages/Home/Home.vue'
import Login from '@/pages/Login/Login.vue'
import Register from '@/pages/Register/Register.vue'
import Settings from '@/pages/Settings/Settings.vue'
import Terms from '@/pages/Legal/Terms.vue'
import Privacy from '@/pages/Legal/Privacy.vue'
import {checkAuthenticated} from '@/pages/Auth/auth'
import {SESSION_KEYS, SESSION_POLICY} from '@/config/session'

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

