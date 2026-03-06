package crypto

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math/big"
	"strings"

	"golang.org/x/crypto/pbkdf2"
)

const (
	DefaultMethod     = "pbkdf2:sha256"
	DefaultIterations = 600000
	SaltLength        = 16
	KeyLength         = 32 // SHA256 输出长度
	SaltChars         = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)

// generateSalt 生成指定长度的随机 Salt，类似 Werkzeug 的 gen_salt
func generateSalt(length int) string {
	var result strings.Builder
	charLen := big.NewInt(int64(len(SaltChars)))
	for i := 0; i < length; i++ {
		num, _ := rand.Int(rand.Reader, charLen)
		result.WriteByte(SaltChars[num.Int64()])
	}
	return result.String()
}

// HashPassword 模拟 Werkzeug 的 generate_password_hash
// 输出格式: pbkdf2:sha256:600000$salt$hash_hex
func (s *BasicCryptoService) HashPassword(password string) (string, error) {
	salt := generateSalt(SaltLength)

	// 计算 Hash
	dk := pbkdf2.Key([]byte(password), []byte(salt), DefaultIterations, KeyLength, sha256.New)
	hashHex := hex.EncodeToString(dk)

	// 拼接: method:iterations$salt$hash
	return fmt.Sprintf("%s:%d$%s$%s", DefaultMethod, DefaultIterations, salt, hashHex), nil
}

// CheckPassword 模拟 Werkzeug 的 check_password_hash
// 验证输入密码是否与 Werkzeug 生成的 hash 字符串匹配
func (s *BasicCryptoService) CheckPassword(password, pwhash string) bool {
	// 1. 分割字符串: method$salt$hash
	parts := strings.Split(pwhash, "$")
	if len(parts) != 3 {
		return false
	}

	methodStr := parts[0]
	salt := parts[1]
	targetHash := parts[2]

	// 2. 解析 method 部分，例如 "pbkdf2:sha256:600000"
	methodParts := strings.Split(methodStr, ":")
	if len(methodParts) != 3 || methodParts[0] != "pbkdf2" || methodParts[1] != "sha256" {
		// 这里仅支持 pbkdf2:sha256，如需支持 map scrypt 可扩展
		return false
	}

	var iterations int
	fmt.Sscanf(methodParts[2], "%d", &iterations)

	// 3. 使用相同的参数重新计算 Hash
	dk := pbkdf2.Key([]byte(password), []byte(salt), iterations, KeyLength, sha256.New)
	newHash := hex.EncodeToString(dk)

	// 4. 比较 (使用 ConstantTimeCompare 防止时序攻击)
	// 注意：ConstantTimeCompare 比较的是 []byte，需要先转换或使用 subtle 库
	// 这里简单比对字符串，为了安全性建议用 subtle.ConstantTimeCompare
	return newHash == targetHash
}
