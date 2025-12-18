package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdh"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"log"
	"math/big"
	"os"

	"golang.org/x/crypto/hkdf"
)

// RSACrypto RSA加密工具
type RSACrypto struct {
	privateKey *rsa.PrivateKey
	publicKey  *rsa.PublicKey
}

var rsaCryptoInstance *RSACrypto

// GetRSACrypto 获取RSA加密实例
func GetRSACrypto() *RSACrypto {
	if rsaCryptoInstance == nil {
		rsaCryptoInstance = NewRSACrypto()
	}
	return rsaCryptoInstance
}

// NewRSACrypto 创建RSA加密实例
func NewRSACrypto() *RSACrypto {
	// 尝试从环境变量加载密钥
	privateKeyPEM := os.Getenv("RSA_PRIVATE_KEY")
	if privateKeyPEM != "" {
		block, _ := pem.Decode([]byte(privateKeyPEM))
		if block != nil {
			privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
			if err == nil {
				return &RSACrypto{
					privateKey: privateKey,
					publicKey:  &privateKey.PublicKey,
				}
			}
		}
	}

	// 生成新的密钥对
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Printf("Failed to generate RSA key: %v", err)
		return nil
	}

	return &RSACrypto{
		privateKey: privateKey,
		publicKey:  &privateKey.PublicKey,
	}
}

// GetPublicKeyPEM 获取公钥PEM格式
func (r *RSACrypto) GetPublicKeyPEM() string {
	pubKeyBytes := x509.MarshalPKCS1PublicKey(r.publicKey)
	pemBlock := &pem.Block{
		Type:  "RSA PUBLIC KEY",
		Bytes: pubKeyBytes,
	}
	return string(pem.EncodeToMemory(pemBlock))
}

// DecryptData 解密数据
func (r *RSACrypto) DecryptData(encryptedData string) (map[string]string, error) {
	// Base64解码
	ciphertext, err := base64.StdEncoding.DecodeString(encryptedData)
	if err != nil {
		log.Printf("Base64解码失败: %v", err)
		return nil, err
	}

	// RSA PKCS1v15 解密（JSEncrypt 使用的是 PKCS#1 v1.5 填充）
	plaintext, err := rsa.DecryptPKCS1v15(rand.Reader, r.privateKey, ciphertext)
	if err != nil {
		log.Printf("RSA解密失败: %v", err)
		return nil, err
	}

	// 解析JSON - 使用 interface{} 兼容不同类型（如 timestamp 是数字）
	var rawResult map[string]interface{}
	if err := json.Unmarshal(plaintext, &rawResult); err != nil {
		log.Printf("JSON解析失败: %v, plaintext: %s", err, string(plaintext))
		return nil, err
	}

	// 转换为 map[string]string
	result := make(map[string]string)
	for k, v := range rawResult {
		switch val := v.(type) {
		case string:
			result[k] = val
		case float64:
			// JSON 数字默认解析为 float64
			result[k] = fmt.Sprintf("%.0f", val)
		case bool:
			result[k] = fmt.Sprintf("%v", val)
		default:
			result[k] = fmt.Sprintf("%v", val)
		}
	}

	return result, nil
}

// ECCCrypto ECC加密工具（用于密码存储）
type ECCCrypto struct {
	privateKey *ecdsa.PrivateKey
	publicKey  *ecdsa.PublicKey
}

var eccCryptoInstance *ECCCrypto

// GetECCCrypto 获取ECC加密实例
func GetECCCrypto() *ECCCrypto {
	if eccCryptoInstance == nil {
		eccCryptoInstance = NewECCCrypto()
	}
	return eccCryptoInstance
}

// NewECCCrypto 创建ECC加密实例
func NewECCCrypto() *ECCCrypto {
	privateKeyEnv := os.Getenv("ECC_PRIVATE_KEY")

	var privateKey *ecdsa.PrivateKey

	if privateKeyEnv != "" {
		// 从环境变量加载私钥（十进制格式）
		d := new(big.Int)
		d.SetString(privateKeyEnv, 10)

		curve := elliptic.P256()
		x, y := curve.ScalarBaseMult(d.Bytes())

		privateKey = &ecdsa.PrivateKey{
			PublicKey: ecdsa.PublicKey{
				Curve: curve,
				X:     x,
				Y:     y,
			},
			D: d,
		}
	} else {
		// 使用默认密钥
		defaultKey := new(big.Int)
		defaultKey.SetString("1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", 16)

		curve := elliptic.P256()
		x, y := curve.ScalarBaseMult(defaultKey.Bytes())

		privateKey = &ecdsa.PrivateKey{
			PublicKey: ecdsa.PublicKey{
				Curve: curve,
				X:     x,
				Y:     y,
			},
			D: defaultKey,
		}
	}

	return &ECCCrypto{
		privateKey: privateKey,
		publicKey:  &privateKey.PublicKey,
	}
}

// EncryptPassword 使用ECC加密密码
func (e *ECCCrypto) EncryptPassword(password string) (string, error) {
	if password == "" {
		return "", nil
	}

	// 生成临时密钥对用于ECDH
	ephemeralPriv, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return "", err
	}

	// 使用ECDH生成共享密钥
	curve := ecdh.P256()
	ephemeralECDH, err := curve.NewPrivateKey(ephemeralPriv.D.Bytes())
	if err != nil {
		return "", err
	}

	publicBytes := elliptic.Marshal(e.publicKey.Curve, e.publicKey.X, e.publicKey.Y)
	publicECDH, err := curve.NewPublicKey(publicBytes)
	if err != nil {
		return "", err
	}

	sharedSecret, err := ephemeralECDH.ECDH(publicECDH)
	if err != nil {
		return "", err
	}

	// 使用HKDF派生AES密钥
	hkdfReader := hkdf.New(sha256.New, sharedSecret, nil, []byte("password encryption"))
	derivedKey := make([]byte, 32)
	if _, err := io.ReadFull(hkdfReader, derivedKey); err != nil {
		return "", err
	}

	// 生成随机IV
	iv := make([]byte, 16)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}

	// 使用AES-GCM加密
	block, err := aes.NewCipher(derivedKey)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return "", err
	}

	ciphertext := gcm.Seal(nonce, nonce, []byte(password), nil)

	// 编码临时公钥
	ephemeralPubBytes := elliptic.Marshal(ephemeralPriv.Curve, ephemeralPriv.X, ephemeralPriv.Y)

	// 组合结果：临时公钥 + IV + 密文
	result := make([]byte, len(ephemeralPubBytes)+len(iv)+len(ciphertext))
	copy(result[:len(ephemeralPubBytes)], ephemeralPubBytes)
	copy(result[len(ephemeralPubBytes):len(ephemeralPubBytes)+len(iv)], iv)
	copy(result[len(ephemeralPubBytes)+len(iv):], ciphertext)

	return base64.StdEncoding.EncodeToString(result), nil
}

// DecryptPassword 使用ECC解密密码
func (e *ECCCrypto) DecryptPassword(encryptedPassword string) (string, error) {
	if encryptedPassword == "" {
		return "", nil
	}

	// Base64解码
	data, err := base64.StdEncoding.DecodeString(encryptedPassword)
	if err != nil {
		return "", err
	}

	if len(data) < 65+16 { // 最小长度：公钥(65) + IV(16)
		return "", errors.New("invalid encrypted data")
	}

	// 提取临时公钥
	ephemeralPubBytes := data[:65]
	x, _ := elliptic.Unmarshal(elliptic.P256(), ephemeralPubBytes)
	if x == nil {
		return "", errors.New("invalid ephemeral public key")
	}

	// 提取IV和密文
	iv := data[65 : 65+16]
	ciphertext := data[65+16:]

	// 使用ECDH生成共享密钥
	curve := ecdh.P256()
	privateECDH, err := curve.NewPrivateKey(e.privateKey.D.Bytes())
	if err != nil {
		return "", err
	}

	publicECDH, err := curve.NewPublicKey(ephemeralPubBytes)
	if err != nil {
		return "", err
	}

	sharedSecret, err := privateECDH.ECDH(publicECDH)
	if err != nil {
		return "", err
	}

	// 使用HKDF派生AES密钥
	hkdfReader := hkdf.New(sha256.New, sharedSecret, nil, []byte("password encryption"))
	derivedKey := make([]byte, 32)
	if _, err := io.ReadFull(hkdfReader, derivedKey); err != nil {
		return "", err
	}

	// 使用AES-GCM解密
	block, err := aes.NewCipher(derivedKey)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return "", errors.New("ciphertext too short")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return "", err
	}

	// 忽略IV，因为AES-GCM使用nonce
	_ = iv

	return string(plaintext), nil
}
