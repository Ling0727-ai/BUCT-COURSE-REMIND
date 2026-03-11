export const SESSION_KEYS = {
    openTabIds: 'app_open_tab_ids',
    lastClosedAt: 'app_last_closed_at',
    justLoggedInAt: 'app_just_logged_in',
    logoutReason: 'logout_reason',
    user: 'user'
} as const

export const SESSION_POLICY = {
    closeExpirationHours: 6,
    justLoggedInGraceMs: 5000,
    routerMarkerCleanupMs: 10000
} as const

export const SESSION_DEFAULTS = {
    openTabIds: [] as string[]
} as const

