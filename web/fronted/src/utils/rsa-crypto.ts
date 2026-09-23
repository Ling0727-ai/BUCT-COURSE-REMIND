import JSEncrypt from 'jsencrypt'

type EncryptableData = Record<string, unknown>

type PublicKeyResponse = {
    disabled?: boolean
    success?: boolean
    error?: string
    data?: {
        public_key: string
        timestamp: number
        expire_minutes: number
    }
}

class RSACrypto {
    private jsencrypt: JSEncrypt
    private publicKey: string | null
    private keyTimestamp: number | null
    private keyExpireMinutes: number
    private rsaDisabled: boolean

    constructor() {
        this.jsencrypt = new JSEncrypt()
        this.publicKey = null
        this.keyTimestamp = null
        this.keyExpireMinutes = 30
        this.rsaDisabled = false
    }

    async getPublicKey(): Promise<boolean> {
        try {
            const response = await fetch('/api/crypto/public-key', {
                method: 'GET',
                credentials: 'include'
            })

            const result = (await response.json()) as PublicKeyResponse

            if (result.disabled) {
                this.rsaDisabled = true
                return false
            }

            if (result.success && result.data) {
                this.publicKey = result.data.public_key
                this.keyTimestamp = result.data.timestamp
                this.keyExpireMinutes = result.data.expire_minutes
                this.rsaDisabled = false
                this.jsencrypt.setPublicKey(this.publicKey)
                return true
            }

            return false
        } catch {
            return false
        }
    }

    isKeyExpired(): boolean {
        if (!this.keyTimestamp) {
            return true
        }

        const now = Math.floor(Date.now() / 1000)
        const bufferSeconds = 120
        const expireTime = this.keyTimestamp + this.keyExpireMinutes * 60 - bufferSeconds
        return now > expireTime
    }

    async ensureValidKey(): Promise<boolean> {
        if (this.rsaDisabled) {
            return false
        }

        if (!this.publicKey || this.isKeyExpired()) {
            return await this.getPublicKey()
        }

        return true
    }

    /** 生成一次性随机数，让每次请求的明文都不同 */
    private createNonce(): string {
        const bytes = new Uint8Array(16)
        if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
            crypto.getRandomValues(bytes)
        } else {
            for (let i = 0; i < bytes.length; i++) {
                bytes[i] = Math.floor(Math.random() * 256)
            }
        }
        return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
    }

    async encryptData(data: EncryptableData, isRetry = false): Promise<string | null> {
        try {
            const hasValidKey = await this.ensureValidKey()
            if (!hasValidKey) {
                throw new Error('无法获取有效的RSA公钥')
            }

            // nonce 不可省略：RSA PKCS#1 v1.5 是确定性加密，若明文完全一致，
            // 密文也完全一致，后端的一次性密文防重放会误判为攻击（例如重复提交）。
            const payload = {
                ...data,
                timestamp: Math.floor(Date.now() / 1000),
                nonce: this.createNonce()
            }

            const encrypted = this.jsencrypt.encrypt(JSON.stringify(payload))
            if (!encrypted) {
                if (!isRetry) {
                    this.publicKey = null
                    this.keyTimestamp = null
                    return await this.encryptData(data, true)
                }
                throw new Error('RSA加密失败')
            }

            return encrypted
        } catch {
            return null
        }
    }

    async encryptLoginData(username: string, password: string): Promise<string | null> {
        return await this.encryptData({username, password})
    }

    async encryptRegisterData(registerData: EncryptableData): Promise<string | null> {
        return await this.encryptData(registerData)
    }

    async createEncryptedRequest(data: EncryptableData): Promise<EncryptableData> {
        // 后端已强制要求 encrypted_data（RSA_ENABLE=false 时登录/注册等接口一律 400），
        // 因此这里不再保留明文降级分支：静默发明文只会让密码在网络上裸奔，
        // 而且后端本来就收不下。直接抛错，让问题在部署阶段暴露。
        if (this.rsaDisabled) {
            throw new Error('服务端已关闭传输加密，出于安全考虑已中止请求，请联系管理员')
        }

        const encryptedData = await this.encryptData(data)

        // 加密失败绝不能降级为明文：在未启用 HTTPS 的部署下，那等于让密码在网络上裸奔。
        // 宁可让本次请求失败并提示用户，也不能静默泄露。
        if (!encryptedData) {
            throw new Error('加密失败，已中止请求，请检查网络后重试')
        }

        return {
            encrypted_data: encryptedData
        }
    }

    async testEncryption(): Promise<boolean | 'disabled'> {
        const keyResult = await this.getPublicKey()

        if (this.rsaDisabled) {
            return 'disabled'
        }

        if (!keyResult) {
            return false
        }

        const encrypted = await this.encryptData({
            test: 'hello world',
            timestamp: Math.floor(Date.now() / 1000)
        })

        return Boolean(encrypted)
    }
}

const rsaCrypto = new RSACrypto()

export default rsaCrypto

