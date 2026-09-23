import {http} from '@/api/http'
import rsaCrypto from '@/utils/rsa-crypto'
import type {AuthStatusResponse, VerificationCodeResponse, VerifyCodeResponse} from './auth.data'

export async function getAuthStatus(): Promise<AuthStatusResponse> {
    return await http.get<AuthStatusResponse>('/auth/status')
}

export async function postLogout(): Promise<void> {
    await http.post('/auth/logout', {})
}

export async function postSendVerificationCode(email: string): Promise<VerificationCodeResponse> {
    const payload = await rsaCrypto.createEncryptedRequest({email})
    return await http.post<VerificationCodeResponse>('/auth/send-verification-code', payload)
}

export async function postVerifyCode(email: string, code: string): Promise<VerifyCodeResponse> {
    const payload = await rsaCrypto.createEncryptedRequest({email, code})
    return await http.post<VerifyCodeResponse>('/auth/verify-code', payload)
}

