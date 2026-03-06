package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdh"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"io"
	"math/big"
	"os"

	"golang.org/x/crypto/hkdf"
)

// ──────────────────────────────────────────────
// ECC / ECDH + AES-GCM 加密，完全对齐 Python 实现
//
// Python 存储格式（Base64编码）：
//   ephemeral_public_bytes(65 字节，未压缩点) + iv(16) + tag(16) + ciphertext
//
// AES key 派生：HKDF-SHA256，info=b'password encryption'，length=32
// ──────────────────────────────────────────────

const hkdfInfo = "password encryption"

// deriveAESKey 用 HKDF-SHA256 从 ECDH 共享密钥派生 32 字节 AES key，对应 Python HKDF
func deriveAESKey(sharedKey []byte) ([]byte, error) {
	reader := hkdf.New(sha256.New, sharedKey, nil, []byte(hkdfInfo))
	key := make([]byte, 32)
	if _, err := io.ReadFull(reader, key); err != nil {
		return nil, err
	}
	return key, nil
}

// getECCPrivateKey 对应 Python ec.derive_private_key(int(ECC_PRIVATE_KEY), ec.SECP256R1())
// ECC_PRIVATE_KEY 是十进制整数字符串，转为 32 字节大端序再构造私钥
func getECCPrivateKey() (*ecdh.PrivateKey, error) {
	privKeyStr := os.Getenv("ECC_PRIVATE_KEY")
	if privKeyStr == "" {
		// 和 Python 一样的默认值
		privKeyStr = "REDACTED_ECC_PRIVATE_KEY"
	}

	n := new(big.Int)
	if _, ok := n.SetString(privKeyStr, 10); !ok {
		return nil, errors.New("ECC_PRIVATE_KEY 不是合法的十进制整数")
	}

	// 转为 32 字节大端序（P-256 私钥固定 32 字节）
	privBytes := make([]byte, 32)
	nBytes := n.Bytes()
	if len(nBytes) > 32 {
		return nil, errors.New("ECC_PRIVATE_KEY 超出 P-256 私钥范围")
	}
	copy(privBytes[32-len(nBytes):], nBytes)

	curve := ecdh.P256()
	return curve.NewPrivateKey(privBytes)
}

// EncryptECC 加密 sPassword，对应 Python _encrypt_password
// 输出：Base64(ephemeral_pub(65) + iv(16) + tag(16) + ciphertext)
func (s *BasicCryptoService) EncryptECC(plainText string) (string, error) {
	if plainText == "" {
		return "", nil
	}

	privKey, err := getECCPrivateKey()
	if err != nil {
		return "", err
	}
	recipientPubKey := privKey.PublicKey() // 收件方公钥 = 自己的公钥（对称场景）

	// 生成临时密钥对
	curve := ecdh.P256()
	ephemeralPriv, err := curve.GenerateKey(rand.Reader)
	if err != nil {
		return "", err
	}
	ephemeralPub := ephemeralPriv.PublicKey()

	// ECDH
	sharedKey, err := ephemeralPriv.ECDH(recipientPubKey)
	if err != nil {
		return "", err
	}

	// HKDF 派生 AES key
	aesKey, err := deriveAESKey(sharedKey)
	if err != nil {
		return "", err
	}

	// AES-GCM 加密，使用 16 字节 IV（对应 Python os.urandom(16)）
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return "", err
	}
	iv := make([]byte, 16)
	if _, err = io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}
	// 使用 NonceSize=16 的 GCM
	gcm, err := cipher.NewGCMWithNonceSize(block, 16)
	if err != nil {
		return "", err
	}
	// Seal 将 tag 附在密文尾部，需要手动拆分
	sealed := gcm.Seal(nil, iv, []byte(plainText), nil)
	// sealed = ciphertext + tag(16)
	tagOffset := len(sealed) - 16
	cipherText := sealed[:tagOffset]
	tag := sealed[tagOffset:]

	// 组合：ephemeral_pub(65) + iv(16) + tag(16) + ciphertext
	ephemeralPubBytes := ephemeralPub.Bytes() // 未压缩点，65 字节
	result := make([]byte, 0, 65+16+16+len(cipherText))
	result = append(result, ephemeralPubBytes...)
	result = append(result, iv...)
	result = append(result, tag...)
	result = append(result, cipherText...)

	return base64.StdEncoding.EncodeToString(result), nil
}

// DecryptECC 解密 sPassword，对应 Python _decrypt_password
// 输入：Base64(ephemeral_pub(65) + iv(16) + tag(16) + ciphertext)
func (s *BasicCryptoService) DecryptECC(encryptedText string) (string, error) {
	if encryptedText == "" {
		return "", nil
	}

	privKey, err := getECCPrivateKey()
	if err != nil {
		return "", err
	}

	data, err := base64.StdEncoding.DecodeString(encryptedText)
	if err != nil {
		data, err = base64.RawStdEncoding.DecodeString(encryptedText)
		if err != nil {
			return "", errors.New("Base64 解码失败")
		}
	}

	if len(data) < 65+16+16 {
		return "", errors.New("加密数据长度不足")
	}

	ephemeralPubBytes := data[:65]
	iv := data[65:81]
	tag := data[81:97]
	cipherText := data[97:]

	curve := ecdh.P256()
	ephemeralPub, err := curve.NewPublicKey(ephemeralPubBytes)
	if err != nil {
		return "", errors.New("解析临时公钥失败: " + err.Error())
	}

	// ECDH
	sharedKey, err := privKey.ECDH(ephemeralPub)
	if err != nil {
		return "", err
	}

	// HKDF 派生 AES key
	aesKey, err := deriveAESKey(sharedKey)
	if err != nil {
		return "", err
	}

	// AES-GCM 解密
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return "", err
	}
	gcm, err := cipher.NewGCMWithNonceSize(block, 16)
	if err != nil {
		return "", err
	}

	// 重新组合为 Seal 格式：ciphertext + tag
	sealedData := append(cipherText, tag...)
	plainBytes, err := gcm.Open(nil, iv, sealedData, nil)
	if err != nil {
		return "", errors.New("解密失败: " + err.Error())
	}

	return string(plainBytes), nil
}
