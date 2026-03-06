package handlers

import (
	"net/http"

	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/gin-gonic/gin"
)

// SendVerificationCode 发送验证码，对应 Python POST /api/auth/send-verification-code
func SendVerificationCode(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	var email string

	// 优先尝试 RSA 解密，对应 Python encrypted_data 分支
	if enc, ok := body["encrypted_data"].(string); ok && enc != "" {
		rsa := crypto.GetRSAService()
		decrypted, err := rsa.DecryptRequest(enc)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "数据解密失败"})
			return
		}
		email, _ = decrypted["email"].(string)
	} else {
		email, _ = body["email"].(string)
	}

	if email == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱地址不能为空"})
		return
	}
	if !services.EmailRegexp.MatchString(email) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}

	// 频率限制：1 分钟内只能发送一次，对应 Python recent_code 判断
	limited, err := services.IsRateLimited(email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务异常，请重试"})
		return
	}
	if limited {
		c.JSON(http.StatusTooManyRequests, gin.H{"error": "请等待 1 分钟后再次发送验证码"})
		return
	}

	// 查找用户名（用于邮件正文），对应 Python user.get('username')
	var username string
	user, _ := User.Repository.GetUserByEmail(email)
	if user != nil {
		username = user.Username
	}

	code, testMode, err := services.SendVerificationEmail(email, username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "验证码发送失败，请稍后重试"})
		return
	}

	// 邮件发送成功
	if !testMode {
		c.JSON(http.StatusOK, gin.H{"message": "验证码已发送到您的邮箱"})
		return
	}

	// 邮件不可用，降级测试模式，对应 Python test_mode 回退响应
	c.JSON(http.StatusOK, gin.H{
		"message":           "验证码已发送到您的邮箱",
		"test_mode":         true,
		"verification_code": code,
		"username":          username,
		"note":              "邮件服务暂时不可用，使用测试模式",
	})
}

// VerifyCode 校验验证码，对应 Python POST /api/auth/verify-code
func VerifyCode(c *gin.Context) {
	var body struct {
		Email string `json:"email" binding:"required"`
		Code  string `json:"code"  binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱和验证码不能为空"})
		return
	}

	ok, err := services.VerifyCode(body.Email, body.Code)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "验证失败，请重试"})
		return
	}
	if !ok {
		c.JSON(http.StatusBadRequest, gin.H{"error": "验证码无效或已过期"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "验证成功"})
}
