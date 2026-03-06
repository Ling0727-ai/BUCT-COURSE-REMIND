package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"io"
	"os"
)

// getAESKey 从环境变量 AES_KEY 读取并派生 32 字节 AES-256 密钥
// 对任意长度的原始值做 SHA-256，保证输出固定 32 字节
func getAESKey() ([]byte, error) {
	raw := os.Getenv("AES_KEY")
	if raw == "" {
		return nil, errors.New("AES_KEY 环境变量未设置")
	}
	key := sha256.Sum256([]byte(raw))
	return key[:], nil
}

// EncryptAES 使用 AES-256-GCM 加密明文
// 输出格式（Base64）：nonce(12B) + ciphertext + tag(16B)
func (s *BasicCryptoService) EncryptAES(plainText string) (string, error) {
	key, err := getAESKey()
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonce := make([]byte, gcm.NonceSize()) // 12 字节
	if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
		return "", err
	}

	// gcm.Seal 将 ciphertext+tag 追加到 nonce 后面
	sealed := gcm.Seal(nonce, nonce, []byte(plainText), nil)
	return base64.StdEncoding.EncodeToString(sealed), nil
}

// DecryptAES 解密 EncryptAES 产生的密文
func (s *BasicCryptoService) DecryptAES(encryptedText string) (string, error) {
	key, err := getAESKey()
	if err != nil {
		return "", err
	}

	data, err := base64.StdEncoding.DecodeString(encryptedText)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonceSize := gcm.NonceSize()
	if len(data) < nonceSize+gcm.Overhead() {
		return "", errors.New("密文长度不合法")
	}

	nonce, cipherText := data[:nonceSize], data[nonceSize:]
	plainText, err := gcm.Open(nil, nonce, cipherText, nil)
	if err != nil {
		return "", err
	}

	return string(plainText), nil
}
