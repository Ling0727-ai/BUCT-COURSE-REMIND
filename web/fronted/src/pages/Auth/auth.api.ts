import {http} from '@/api/http'
import type {AuthStatusResponse, VerificationCodeResponse, VerifyCodeResponse} from './auth.data'

export async function getAuthStatus(): Promise<AuthStatusResponse> {
    return await http.get<AuthStatusResponse>('/auth/status')
}

export async function postLogout(): Promise<void> {
    await http.post('/auth/logout', {})
}

export async function postSendVerificationCode(email: string): Promise<VerificationCodeResponse> {
    return await http.post<VerificationCodeResponse>('/auth/send-verification-code', {email})
}

export async function postVerifyCode(email: string, code: string): Promise<VerifyCodeResponse> {
    return await http.post<VerifyCodeResponse>('/auth/verify-code', {email, code})
}

