package handlers

import (
	"net/http"
	"time"

	"buct-course-remind/internal/crypto"

	"github.com/gin-gonic/gin"
)

// CryptoHandler 加密处理器
type CryptoHandler struct{}

// NewCryptoHandler 创建加密处理器
func NewCryptoHandler() *CryptoHandler {
	return &CryptoHandler{}
}

// GetPublicKey 获取RSA公钥
func (h *CryptoHandler) GetPublicKey(c *gin.Context) {
	rsaCrypto := crypto.GetRSACrypto()
	if rsaCrypto == nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   "加密服务不可用",
		})
		return
	}

	publicKey := rsaCrypto.GetPublicKeyPEM()

	// 返回前端期望的格式
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"public_key":     publicKey,
			"timestamp":      time.Now().Unix(),
			"expire_minutes": 30,
		},
	})
}

// TestDecrypt 测试解密（仅用于开发）
func (h *CryptoHandler) TestDecrypt(c *gin.Context) {
	var req struct {
		EncryptedData string `json:"encrypted_data" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "请求格式错误",
		})
		return
	}

	rsaCrypto := crypto.GetRSACrypto()
	if rsaCrypto == nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   "加密服务不可用",
		})
		return
	}

	decrypted, err := rsaCrypto.DecryptData(req.EncryptedData)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "解密失败: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    decrypted,
	})
}
