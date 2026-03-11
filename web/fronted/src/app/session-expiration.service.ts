import router from '@/router/index'
import {SESSION_DEFAULTS, SESSION_KEYS, SESSION_POLICY} from '@/config/session'
import {logoutSafely} from '@/pages/Auth/auth'

const CLOSE_EXPIRATION_MS = SESSION_POLICY.closeExpirationHours * 60 * 60 * 1000
const tabId = `${Date.now()}_${Math.random().toString(16).slice(2)}`

function getOpenTabIds(): string[] {
    try {
        const raw = localStorage.getItem(SESSION_KEYS.openTabIds)
        if (!raw) {
            return SESSION_DEFAULTS.openTabIds
        }

        const parsed = JSON.parse(raw)
        if (!Array.isArray(parsed)) {
            return SESSION_DEFAULTS.openTabIds
        }

        return parsed.filter((item): item is string => typeof item === 'string')
    } catch {
        return SESSION_DEFAULTS.openTabIds
    }
}

function setOpenTabIds(tabIds: string[]): void {
    try {
        localStorage.setItem(SESSION_KEYS.openTabIds, JSON.stringify(tabIds))
    } catch {
        // ignore storage errors
    }
}

function markTabOpen(): void {
    const tabIds = getOpenTabIds()
    if (!tabIds.includes(tabId)) {
        setOpenTabIds([...tabIds, tabId])
    }
}

function markTabClosed(): void {
    const tabIds = getOpenTabIds().filter((item) => item !== tabId)
    setOpenTabIds(tabIds)

    if (tabIds.length === 0) {
        try {
            localStorage.setItem(SESSION_KEYS.lastClosedAt, String(Date.now()))
        } catch {
            // ignore storage errors
        }
    }
}

function hasLoginInfo(): boolean {
    const localUser = localStorage.getItem(SESSION_KEYS.user)
    const sessionUser = sessionStorage.getItem(SESSION_KEYS.user)
    return Boolean(localUser || sessionUser)
}

async function forceLogout(reason: string): Promise<void> {
    await logoutSafely()

    localStorage.removeItem(SESSION_KEYS.user)
    sessionStorage.removeItem(SESSION_KEYS.user)

    try {
        sessionStorage.setItem(SESSION_KEYS.logoutReason, reason)
    } catch {
        // ignore storage errors
    }

    await router.replace('/login')
}

async function checkClosureExpiration(): Promise<void> {
    if (!hasLoginInfo()) {
        return
    }

    const justLoggedInRaw = localStorage.getItem(SESSION_KEYS.justLoggedInAt)
    if (justLoggedInRaw) {
        const justLoggedInTs = Number.parseInt(justLoggedInRaw, 10)
        if (!Number.isNaN(justLoggedInTs) && Date.now() - justLoggedInTs < SESSION_POLICY.justLoggedInGraceMs) {
            return
        }
        localStorage.removeItem(SESSION_KEYS.justLoggedInAt)
    }

    const lastClosedRaw = localStorage.getItem(SESSION_KEYS.lastClosedAt)
    if (!lastClosedRaw) {
        return
    }

    const lastClosedTs = Number.parseInt(lastClosedRaw, 10)
    if (Number.isNaN(lastClosedTs)) {
        return
    }

    if (Date.now() - lastClosedTs >= CLOSE_EXPIRATION_MS) {
        await forceLogout(`离开页面超过 ${SESSION_POLICY.closeExpirationHours}h，已自动退出`)
    }
}

export function initSessionExpiration(): void {
    markTabOpen()
    void checkClosureExpiration()

    window.addEventListener('beforeunload', () => {
        markTabClosed()
    })

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            void checkClosureExpiration()
        }
    })
}

