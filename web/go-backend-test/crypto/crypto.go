package crypto

type CryptoService interface {
	HashPassword(password string) (string, error)
	CheckPassword(password, hash string) bool

	EncryptECC(plainText string) (string, error)
	DecryptECC(encryptedText string) (string, error)

	EncryptAES(plainText string) (string, error)
	DecryptAES(encryptedText string) (string, error)
}

// RSACryptoService RSA 加密服务接口（独立于 CryptoService，因为 RSA 是有状态的服务）
type RSACryptoService interface {
	IsEnabled() bool
	GetPublicKeyPEM() (string, error)
	GetPublicKeyInfo() (map[string]interface{}, error)
	DecryptRequest(encryptedBase64 string) (map[string]interface{}, error)
	CreateChallenge() (*ChallengeData, error)
}

type BasicCryptoService struct{}

var Crypto = &BasicCryptoService{}
