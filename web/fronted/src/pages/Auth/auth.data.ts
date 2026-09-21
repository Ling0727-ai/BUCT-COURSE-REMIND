export interface AuthStatusResponse {
  authenticated: boolean
}

export interface AuthStatus {
  authenticated: boolean
}

export interface AuthSessionUser {
  id: number | string
  username: string
  is_admin: boolean
}

export interface VerificationCodeResponse {
  success?: boolean
  message?: string
  error?: string
  test_mode?: boolean
  verification_code?: string
}

export interface VerifyCodeResponse {
  success?: boolean
  message?: string
  error?: string
}
