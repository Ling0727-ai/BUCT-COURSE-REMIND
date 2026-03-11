// API配置文件

const getApiBaseUrl = (): string => {
    // Vue CLI 下通过 devServer proxy 处理开发环境 API 转发
    return ''
}

export const API_BASE_URL = getApiBaseUrl()

export const API_ENDPOINTS = {
    SEND_VERIFICATION_CODE: '/api/auth/send-verification-code',
    VERIFY_CODE: '/api/auth/verify-code',
    REGISTER: '/api/auth/register',
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    AUTH_STATUS: '/api/auth/status',
    CHECK_EMAIL: '/api/auth/check-email',
    RESET_PASSWORD: '/api/auth/reset-password',
    ASSIGNMENTS: '/api/assignments/',
    ASSIGNMENTS_REFRESH: '/api/assignments/refresh-sync',
    ASSIGNMENT_COMPLETE: '/api/assignments/{id}/complete',
    HEALTH: '/api/health'
} as const

export function createApiUrl(endpoint: string): string {
    return `${API_BASE_URL}${endpoint}`
}

export async function apiRequest<TResponse>(
    endpoint: string,
    options: RequestInit = {}
): Promise<TResponse | string> {
    const url = createApiUrl(endpoint)

    const defaultOptions: RequestInit = {
        headers: {
            'Content-Type': 'application/json'
        }
    }

    const mergedOptions: RequestInit = {
        ...defaultOptions,
        ...options,
        headers: {
            ...(defaultOptions.headers || {}),
            ...(options.headers || {})
        }
    }

    const response = await fetch(url, mergedOptions)
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
        return (await response.json()) as TResponse
    }

    return await response.text()
}

export default {
    API_BASE_URL,
    API_ENDPOINTS,
    createApiUrl,
    apiRequest
}

