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

    async encryptData(data: EncryptableData, isRetry = false): Promise<string | null> {
        try {
            const hasValidKey = await this.ensureValidKey()
            if (!hasValidKey) {
                throw new Error('无法获取有效的RSA公钥')
            }

            const payload = {
                ...data,
                timestamp: Math.floor(Date.now() / 1000)
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
        if (this.rsaDisabled) {
            return data
        }

        const encryptedData = await this.encryptData(data)
        if (!encryptedData) {
            return data
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

