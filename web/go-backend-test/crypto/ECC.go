package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdh"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"io"
	"os"
)

func (s *BasicCryptoService) EncryptECC(plainText string) (string, error) {
	// 这里可以使用 ECC 加密算法来实现加密
	// 这只是一个示例，实际实现需要使用 ECC 库
	privateKey := os.Getenv("ECC_PRIVATE_KEY")
	publicKey := os.Getenv("ECC_PUBLIC_KEY")

	pubKeyBytes, err := hex.DecodeString(publicKey)
	if err != nil {
		return "", err
	}

	priKeyBytes, err := hex.DecodeString(privateKey)
	if err != nil {
		return "", err
	}

	// 解析P-256曲线的公钥和私钥
	curve := ecdh.P256()
	recipentPubKey, err := curve.NewPublicKey(pubKeyBytes)
	if err != nil {
		return "", err
	}

	ephemeralPrivKey, err := curve.NewPrivateKey(priKeyBytes)
	if err != nil {
		return "", err
	}

	// ECDH生成共享密钥
	sharedKey, err := ephemeralPrivKey.ECDH(recipentPubKey)
	if err != nil {
		return "", err
	}

	// sha-256派生AES密钥
	aesKey := sha256.Sum256(sharedKey)

	// AES-GCM加密
	block, err := aes.NewCipher(aesKey[:])
	if err != nil {
		return "", err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
		return "", err
	}

	cipherText := gcm.Seal(nil, nonce, []byte(plainText), nil)

	// 打包临时公钥（65B）+nonce（12B）+密文+tag (16B) -> Base64
	ephemeralPubKeyBytes := ephemeralPrivKey.Bytes()
	result := make([]byte, 0, len(ephemeralPubKeyBytes)+len(nonce)+len(cipherText))
	result = append(result, ephemeralPubKeyBytes...)
	result = append(result, nonce...)
	result = append(result, cipherText...)

	return hex.EncodeToString(result), nil
}

func (s *BasicCryptoService) DecryptECC(encryptedText string) (string, error) {
	// 这里可以使用 ECC 加密算法来实现解密
	// 这只是一个示例，实际实现需要使用 ECC 库
	privateKey := os.Getenv("ECC_PRIVATE_KEY")

	priKeyBytes, err := hex.DecodeString(privateKey)
	if err != nil {
		return "", err
	}

	curve := ecdh.P256()
	recentPriKey, err := curve.NewPrivateKey(priKeyBytes)
	if err != nil {
		return "", err
	}

	// base64解码
	data, err := base64.StdEncoding.DecodeString(encryptedText)
	if err != nil {
		return "", err
	}

	// 解包：临时公钥（65B）+nonce（12B）+密文+tag (16B)
	if len(data) < 65+12+16 {
		return "", err
	}

	ephemeralPubKey, err := curve.NewPublicKey(data[:65])
	if err != nil {
		return "", err
	}
	nonce := data[65 : 65+12]
	cipherText := data[65+12:]

	// ECDH 计算共享密钥
	sharedSecret, err := recentPriKey.ECDH(ephemeralPubKey)
	if err != nil {
		return "", err
	}

	aesKey := sha256.Sum256(sharedSecret)

	block, err := aes.NewCipher(aesKey[:])
	if err != nil {
		return "", err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	plainText, err := gcm.Open(nil, nonce, cipherText, nil)
	if err != nil {
		return "", err
	}

	return string(plainText), nil
}
