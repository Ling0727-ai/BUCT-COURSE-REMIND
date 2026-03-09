package handlers

import (
	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/Ling0727-ai/go-buct-course-backend/utils"
	"github.com/gin-gonic/gin"
)

// SendVerificationCode 发送验证码，对应 Python POST /api/auth/send-verification-code
func SendVerificationCode(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.RequestFormatError})
		return
	}

	var email string

	// 优先尝试 RSA 解密，对应 Python encrypted_data 分支
	if enc, ok := body["encrypted_data"].(string); ok && enc != "" {
		rsa := crypto.GetRSAService()
		decrypted, err := rsa.DecryptRequest(enc)
		if err != nil {
			c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.DecryptFailed})
			return
		}
		email, _ = decrypted["email"].(string)
	} else {
		email, _ = body["email"].(string)
	}

	if email == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.Empty})
		return
	}
	if !services.EmailRegexp.MatchString(email) {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.InvalidFormat})
		return
	}

	// 频率限制：1 分钟内只能发送一次，对应 Python recent_code 判断
	limited, err := services.IsRateLimited(email)
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.Verification.ServiceError})
		return
	}
	if limited {
		c.JSON(utils.Defaults.Status.TooManyRequests, gin.H{"error": utils.Defaults.Verification.RateLimited})
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
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.Verification.SendFailed})
		return
	}

	// 邮件发送成功
	if !testMode {
		c.JSON(utils.Defaults.Status.OK, gin.H{"message": utils.Defaults.Verification.SendSuccess})
		return
	}

	// 邮件不可用，降级测试模式，对应 Python test_mode 回退响应
	c.JSON(utils.Defaults.Status.OK, gin.H{
		"message":           utils.Defaults.Verification.SendSuccess,
		"test_mode":         true,
		"verification_code": code,
		"username":          username,
		"note":              utils.Defaults.Verification.TestModeNote,
	})
}

// VerifyCode 校验验证码，对应 Python POST /api/auth/verify-code
func VerifyCode(c *gin.Context) {
	var body struct {
		Email string `json:"email" binding:"required"`
		Code  string `json:"code"  binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Verification.Empty})
		return
	}

	ok, err := services.VerifyCode(body.Email, body.Code)
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.Verification.VerifyFailed})
		return
	}
	if !ok {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Verification.InvalidOrExpired})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{"message": utils.Defaults.Verification.VerifySuccess})
}
