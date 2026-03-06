package crypto

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"errors"
	"log"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

// ──────────────────────────────────────────────
//  配置常量
// ──────────────────────────────────────────────

const (
	defaultKeySize           = 2048
	defaultExpireMinutes     = 30
	oldKeyGracePeriodMinutes = 5
	replayWindowSeconds      = 600 // 10 分钟防重放窗口，对应 Python
)

// ──────────────────────────────────────────────
//  RSA 服务结构体
// ──────────────────────────────────────────────

// RSAService RSA 加密服务，对应 Python RSACrypto 类
type RSAService struct {
	mu sync.RWMutex

	privateKey     *rsa.PrivateKey
	publicKey      *rsa.PublicKey
	keyGeneratedAt time.Time

	// 过渡期旧密钥（防止密钥刷新时前端还在用旧公钥）
	oldPrivateKey   *rsa.PrivateKey
	oldKeyExpiresAt time.Time

	keySize       int
	expireMinutes int
	enabled       bool
}

// rsaInstance 全局单例
var (
	rsaInstance *RSAService
	rsaOnce     sync.Once
)

// GetRSAService 获取 RSA 服务单例，对应 Python get_rsa_crypto()
func GetRSAService() *RSAService {
	rsaOnce.Do(func() {
		keySize := defaultKeySize
		if v := os.Getenv("RSA_KEY_SIZE"); v != "" {
			if n, err := strconv.Atoi(v); err == nil {
				keySize = n
			}
		}

		expireMinutes := defaultExpireMinutes
		if v := os.Getenv("RSA_KEY_EXPIRE_MINUTES"); v != "" {
			if n, err := strconv.Atoi(v); err == nil {
				expireMinutes = n
			}
		}

		enabled := true
		if v := os.Getenv("RSA_ENABLE"); v != "" {
			enabled = v == "true"
		}

		rsaInstance = &RSAService{
			keySize:       keySize,
			expireMinutes: expireMinutes,
			enabled:       enabled,
		}
	})
	return rsaInstance
}

// ──────────────────────────────────────────────
//  密钥管理
// ──────────────────────────────────────────────

// IsEnabled 检查 RSA 是否启用
func (r *RSAService) IsEnabled() bool {
	return r.enabled
}

// isKeyExpiredLocked 检查密钥是否过期，调用方须持有任意锁
func (r *RSAService) isKeyExpiredLocked() bool {
	if r.privateKey == nil {
		return true
	}
	return time.Now().After(r.keyGeneratedAt.Add(time.Duration(r.expireMinutes) * time.Minute))
}

// generateKeyPairLocked 不加锁版本，调用方须已持有写锁
func (r *RSAService) generateKeyPairLocked() error {
	// 双重检查
	if r.privateKey != nil && !r.isKeyExpiredLocked() {
		return nil
	}

	// 保存旧密钥用于过渡期
	if r.privateKey != nil {
		r.oldPrivateKey = r.privateKey
		r.oldKeyExpiresAt = time.Now().Add(oldKeyGracePeriodMinutes * time.Minute)
		log.Println("[RSA] 旧密钥已保留，用于过渡期解密")
	}

	key, err := rsa.GenerateKey(rand.Reader, r.keySize)
	if err != nil {
		return err
	}

	r.privateKey = key
	r.publicKey = &key.PublicKey
	r.keyGeneratedAt = time.Now()

	log.Println("[RSA] 新密钥对生成成功")
	return nil
}

// GenerateKeyPair 公开 API，自己加写锁，对应 Python generate_key_pair
func (r *RSAService) GenerateKeyPair() error {
	if !r.enabled {
		return errors.New("RSA 加密已禁用")
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	return r.generateKeyPairLocked()
}

// ensureKeyLocked 确保密钥可用，调用方须已持有写锁
func (r *RSAService) ensureKeyLocked() error {
	if !r.enabled {
		return errors.New("RSA 加密已禁用")
	}
	if r.privateKey == nil || r.isKeyExpiredLocked() {
		return r.generateKeyPairLocked()
	}
	return nil
}

// ──────────────────────────────────────────────
//  公钥导出
// ──────────────────────────────────────────────

// GetPublicKeyPEM 获取 PEM 格式公钥，对应 Python get_public_key_pem
func (r *RSAService) GetPublicKeyPEM() (string, error) {
	if !r.enabled {
		return "", errors.New("RSA 加密已禁用")
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	// 使用不加锁版本，避免死锁
	if err := r.ensureKeyLocked(); err != nil {
		return "", err
	}

	pubBytes, err := x509.MarshalPKIXPublicKey(r.publicKey)
	if err != nil {
		return "", err
	}

	pemBlock := &pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: pubBytes,
	}
	return string(pem.EncodeToMemory(pemBlock)), nil
}

// GetPublicKeyInfo 获取公钥信息（含过期时间），对应 Python get_public_key_info
func (r *RSAService) GetPublicKeyInfo() (map[string]interface{}, error) {
	pubPEM, err := r.GetPublicKeyPEM()
	if err != nil {
		return nil, err
	}

	r.mu.RLock()
	generatedAt := r.keyGeneratedAt
	expireMinutes := r.expireMinutes
	r.mu.RUnlock()

	return map[string]interface{}{
		"public_key":     pubPEM,
		"timestamp":      generatedAt.Unix(),
		"expire_minutes": expireMinutes,
	}, nil
}

// ──────────────────────────────────────────────
//  解密请求数据
// ──────────────────────────────────────────────

// DecryptRequest 解密前端传来的 RSA 加密数据，对应 Python decrypt_data
// 输入：Base64(RSA-PKCS1v15 加密的 JSON)
// 输出：解析后的 map，含防重放时间戳校验
func (r *RSAService) DecryptRequest(encryptedBase64 string) (map[string]interface{}, error) {
	r.mu.RLock()
	priKey := r.privateKey
	oldPriKey := r.oldPrivateKey
	oldExpires := r.oldKeyExpiresAt
	r.mu.RUnlock()

	if priKey == nil {
		return nil, errors.New("私钥未初始化")
	}

	// Base64 解码
	encryptedBytes, err := decodeBase64(encryptedBase64)
	if err != nil {
		return nil, errors.New("Base64 解码失败: " + err.Error())
	}

	// 先用当前私钥解密
	plainBytes, err := rsa.DecryptPKCS1v15(rand.Reader, priKey, encryptedBytes)
	if err != nil {
		// 当前密钥失败，尝试过渡期旧密钥
		if oldPriKey != nil && time.Now().Before(oldExpires) {
			log.Println("[RSA] 当前密钥解密失败，尝试旧密钥（过渡期）")
			plainBytes, err = rsa.DecryptPKCS1v15(rand.Reader, oldPriKey, encryptedBytes)
			if err != nil {
				return nil, errors.New("解密失败（当前密钥和旧密钥均失败）: " + err.Error())
			}
		} else {
			// 旧密钥已过期，清理
			r.mu.Lock()
			r.oldPrivateKey = nil
			r.mu.Unlock()
			return nil, errors.New("解密失败: " + err.Error())
		}
	}

	// 解析 JSON
	var data map[string]interface{}
	if err = json.Unmarshal(plainBytes, &data); err != nil {
		return nil, errors.New("JSON 解析失败")
	}

	// 防重放时间戳校验
	if tsRaw, ok := data["timestamp"]; ok {
		var ts int64
		switch v := tsRaw.(type) {
		case float64:
			ts = int64(v)
		case json.Number:
			ts, _ = v.Int64()
		}
		diff := time.Now().Unix() - ts
		if diff > replayWindowSeconds || diff < -60 {
			return nil, errors.New("请求已过期或时间戳异常")
		}
	}

	return data, nil
}

// ──────────────────────────────────────────────
//  挑战码
// ──────────────────────────────────────────────

// ChallengeData 挑战码响应，对应 Python create_challenge 返回值
type ChallengeData struct {
	Challenge string `json:"challenge"`
	Hash      string `json:"hash"`
	Timestamp int64  `json:"timestamp"`
}

// CreateChallenge 创建挑战码，对应 Python create_challenge
func (r *RSAService) CreateChallenge() (*ChallengeData, error) {
	// 生成 16 字节随机数
	raw := make([]byte, 16)
	if _, err := rand.Read(raw); err != nil {
		return nil, err
	}
	b64 := encodeBase64(raw)
	return &ChallengeData{
		Challenge: b64,
		Hash:      hashSHA256Hex([]byte(b64)),
		Timestamp: time.Now().Unix(),
	}, nil
}

// ──────────────────────────────────────────────
//  工具函数（内部使用）
// ──────────────────────────────────────────────

func decodeBase64(s string) ([]byte, error) {
	// JSEncrypt 产出带换行的 Base64，Python b64decode 忽略换行，Go 需手动清理
	cleaned := strings.NewReplacer("\n", "", "\r", "", " ", "").Replace(strings.TrimSpace(s))
	if b, err := base64.StdEncoding.DecodeString(cleaned); err == nil {
		return b, nil
	}
	return base64.RawStdEncoding.DecodeString(cleaned)
}

func encodeBase64(b []byte) string {
	return base64.StdEncoding.EncodeToString(b)
}

func hashSHA256Hex(b []byte) string {
	h := sha256.Sum256(b)
	return hex.EncodeToString(h[:])
}
