// API配置文件

// 根据环境确定API基础URL
const getApiBaseUrl = () => {
  // 在开发环境中使用代理
  if (import.meta.env.DEV) {
    return ''  // 使用相对路径，通过Vite代理
  }
  
  // 在生产环境中，使用相对路径通过Nginx代理
  // Nginx已配置 location /api/ 代理到后端服务
  return ''
}

export const API_BASE_URL = getApiBaseUrl()

// API端点
export const API_ENDPOINTS = {
  // 认证相关
  SEND_VERIFICATION_CODE: '/api/auth/send-verification-code',
  VERIFY_CODE: '/api/auth/verify-code',
  REGISTER: '/api/auth/register',
  LOGIN: '/api/auth/login',
  LOGOUT: '/api/auth/logout',
  AUTH_STATUS: '/api/auth/status',
  CHECK_EMAIL: '/api/auth/check-email',
  RESET_PASSWORD: '/api/auth/reset-password',
  
  // 作业相关
  ASSIGNMENTS: '/api/assignments/',
  ASSIGNMENTS_REFRESH: '/api/assignments/refresh',
  ASSIGNMENT_COMPLETE: '/api/assignments/{id}/complete',
  
  // 健康检查
  HEALTH: '/api/health'
}

// 创建完整的API URL
export const createApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`
}

// API请求封装
export const apiRequest = async (endpoint, options = {}) => {
  const url = createApiUrl(endpoint)
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  }
  
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  }
  
  try {
    const response = await fetch(url, mergedOptions)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    } else {
      return await response.text()
    }
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  createApiUrl,
  apiRequest
}