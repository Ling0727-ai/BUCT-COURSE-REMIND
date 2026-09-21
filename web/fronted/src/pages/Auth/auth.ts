import { SESSION_KEYS } from '@/config/session'
import { getAuthStatus, postLogout, postSendVerificationCode, postVerifyCode } from './auth.api'
import type { AuthSessionUser, AuthStatus, VerificationCodeResponse, VerifyCodeResponse } from './auth.data'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export async function checkAuthenticated(): Promise<AuthStatus> {
  try {
    return await getAuthStatus()
  } catch {
    return { authenticated: false }
  }
}

export async function logoutSafely(): Promise<void> {
  try {
    await postLogout()
  } catch {
    // ignore network errors and clear local state in callers
  }
}

export function mapAuthError(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) {
    return error.message
  }
  return fallback
}

export function isValidEmail(email: string): boolean {
  return EMAIL_REGEX.test(email)
}

export async function sendVerificationCode(email: string): Promise<VerificationCodeResponse> {
  return await postSendVerificationCode(email)
}

export async function verifyVerificationCode(email: string, code: string): Promise<VerifyCodeResponse> {
  return await postVerifyCode(email, code)
}

export function persistLoginState(user: AuthSessionUser, rememberUser: boolean): void {
  const serialized = JSON.stringify({ ...user, remember: rememberUser })
  if (rememberUser) {
    localStorage.setItem(SESSION_KEYS.user, serialized)
    return
  }
  sessionStorage.setItem(SESSION_KEYS.user, serialized)
}

export function markLoginSuccess(): void {
  localStorage.removeItem(SESSION_KEYS.lastClosedAt)
  localStorage.setItem(SESSION_KEYS.justLoggedInAt, String(Date.now()))
}

export function consumeAutoLogoutReason(): string | null {
  const reason = sessionStorage.getItem(SESSION_KEYS.logoutReason)
  if (!reason) {
    return null
  }
  sessionStorage.removeItem(SESSION_KEYS.logoutReason)
  return reason
}
