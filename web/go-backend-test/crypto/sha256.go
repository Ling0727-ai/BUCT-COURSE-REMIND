package crypto

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"math/big"
	"strconv"
	"strings"

	"golang.org/x/crypto/pbkdf2"
	goscrypt "golang.org/x/crypto/scrypt"
)

const (
	SaltLength = 16
	SaltChars  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

	// scrypt 参数，与 Werkzeug 2.x 默认值一致
	scryptN     = 32768 // 2^15
	scryptR     = 8
	scryptP     = 1
	scryptDKLen = 32

	// pbkdf2 参数（旧版 Werkzeug 兼容）
	pbkdf2Iterations = 600000
	pbkdf2KeyLen     = 32
)

// generateSalt 生成随机 Salt，与 Werkzeug gen_salt 一致
func generateSalt(length int) string {
	var result strings.Builder
	charLen := big.NewInt(int64(len(SaltChars)))
	for i := 0; i < length; i++ {
		num, _ := rand.Int(rand.Reader, charLen)
		result.WriteByte(SaltChars[num.Int64()])
	}
	return result.String()
}

// HashPassword 使用 scrypt 生成密码 hash，与 Werkzeug 2.x generate_password_hash 一致
// 输出格式: scrypt:32768:8:1$salt$hash_hex
func (s *BasicCryptoService) HashPassword(password string) (string, error) {
	salt := generateSalt(SaltLength)

	dk, err := goscrypt.Key([]byte(password), []byte(salt), scryptN, scryptR, scryptP, scryptDKLen)
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("scrypt:%d:%d:%d$%s$%s", scryptN, scryptR, scryptP, salt, hex.EncodeToString(dk)), nil
}

// CheckPassword 验证密码，自动识别 scrypt（Werkzeug 2.x）和 pbkdf2（旧版）
// 对应 Werkzeug check_password_hash
func (s *BasicCryptoService) CheckPassword(password, pwhash string) bool {
	parts := strings.SplitN(pwhash, "$", 3)
	if len(parts) != 3 {
		return false
	}

	method := parts[0]
	salt := parts[1]
	targetHex := parts[2]

	target, err := hex.DecodeString(targetHex)
	if err != nil {
		return false
	}

	methodParts := strings.Split(method, ":")
	switch methodParts[0] {
	case "scrypt":
		// scrypt:N:r:p
		if len(methodParts) != 4 {
			return false
		}
		n, _ := strconv.Atoi(methodParts[1])
		r, _ := strconv.Atoi(methodParts[2])
		p, _ := strconv.Atoi(methodParts[3])
		if n == 0 || r == 0 || p == 0 {
			return false
		}
		dk, err := goscrypt.Key([]byte(password), []byte(salt), n, r, p, len(target))
		if err != nil {
			return false
		}
		return subtle.ConstantTimeCompare(dk, target) == 1

	case "pbkdf2":
		// pbkdf2:sha256:iterations
		if len(methodParts) != 3 || methodParts[1] != "sha256" {
			return false
		}
		iterations, _ := strconv.Atoi(methodParts[2])
		if iterations == 0 {
			return false
		}
		dk := pbkdf2.Key([]byte(password), []byte(salt), iterations, len(target), sha256.New)
		return subtle.ConstantTimeCompare(dk, target) == 1

	default:
		return false
	}
}
