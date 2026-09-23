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

	// 强制加密传输：不接受明文 email
	enc, _ := body["encrypted_data"].(string)
	if enc == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.RequireEncryption})
		return
	}

	rsa := crypto.GetRSAService()
	decrypted, err := rsa.DecryptRequest(enc)
	if err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.DecryptFailed})
		return
	}
	email, _ := decrypted["email"].(string)

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
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.RequestFormatError})
		return
	}

	// 强制加密传输：验证码是账号找回的关键凭证，
	// 明文传输会让同网段攻击者直接读到并抢先使用。
	enc, _ := body["encrypted_data"].(string)
	if enc == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.RequireEncryption})
		return
	}

	rsa := crypto.GetRSAService()
	decrypted, err := rsa.DecryptRequest(enc)
	if err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.DecryptFailed})
		return
	}

	email, _ := decrypted["email"].(string)
	code, _ := decrypted["code"].(string)
	if email == "" || code == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Verification.Empty})
		return
	}

	ok, err := services.VerifyCode(email, code)
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
