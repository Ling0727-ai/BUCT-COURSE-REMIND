package handlers

import (
	"net/http"
	"os"

	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
	"github.com/gin-gonic/gin"
)

// GetPublicKey 下发 RSA 公钥给前端，对应 Python GET /api/crypto/public-key
func GetPublicKey(c *gin.Context) {
	rsa := crypto.GetRSAService()

	if !rsa.IsEnabled() {
		c.JSON(http.StatusOK, gin.H{
			"success":  false,
			"error":    "RSA加密已禁用",
			"disabled": true,
		})
		return
	}

	info, err := rsa.GetPublicKeyInfo()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   "无法生成RSA密钥对",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    info,
	})
}

// GetChallenge 获取挑战码，对应 Python GET /api/crypto/challenge
func GetChallenge(c *gin.Context) {
	rsa := crypto.GetRSAService()

	challenge, err := rsa.CreateChallenge()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   "生成挑战失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    challenge,
	})
}

// GetCryptoStatus 告知前端当前加密方式和启用状态（AES 对称加密场景）
func GetCryptoStatus(c *gin.Context) {
	enabled := os.Getenv("AES_KEY") != ""

	if !enabled {
		c.JSON(http.StatusOK, gin.H{
			"success":  false,
			"error":    "AES加密已禁用",
			"disabled": true,
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"type":    "AES-256-GCM",
			"enabled": true,
		},
	})
}
