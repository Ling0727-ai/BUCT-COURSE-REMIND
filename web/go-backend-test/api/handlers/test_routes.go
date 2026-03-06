package handlers

import (
	"net/http"
	"os"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/gin-gonic/gin"
)

// SendTestEmail 发送测试验证码邮件（无需登录）
// 对应 Python POST /api/test/send-test-email
func SendTestEmail(c *gin.Context) {
	var body struct {
		Email string `json:"email" binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱地址不能为空"})
		return
	}

	// 生成验证码、存库、发邮件（复用 vercode service）
	code, testMode, err := services.SendVerificationEmail(body.Email, "")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "邮件发送失败: " + err.Error(),
			"config": gin.H{
				"smtp_server":  os.Getenv("MAIL_SMTP_SERVER"),
				"smtp_port":    os.Getenv("MAIL_SMTP_PORT"),
				"sender_email": os.Getenv("MAIL_SENDER"),
				"password_set": config.Mail != nil && config.Mail.IsReady(),
			},
		})
		return
	}

	resp := gin.H{
		"message":   "测试邮件发送成功",
		"email":     body.Email,
		"test_mode": testMode,
	}
	if testMode {
		resp["test_code"] = code // 邮件不可用时返回验证码，方便调试
	}
	c.JSON(http.StatusOK, resp)
}

// VerifyTestCode 验证测试验证码，对应 Python POST /api/test/verify-test-code
// 直接复用 services.VerifyCode，无需重复实现
func VerifyTestCode(c *gin.Context) {
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
		c.JSON(http.StatusInternalServerError, gin.H{"error": "验证失败: " + err.Error()})
		return
	}
	if !ok {
		c.JSON(http.StatusBadRequest, gin.H{"error": "验证码无效或已过期"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "验证成功"})
}

// GetTestConfig 获取当前邮件/数据库配置信息（调试用）
// 对应 Python GET /api/test/config
func GetTestConfig(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"smtp_server":  os.Getenv("MAIL_SMTP_SERVER"),
		"smtp_port":    os.Getenv("MAIL_SMTP_PORT"),
		"sender_email": os.Getenv("MAIL_SENDER"),
		"password_set": config.Mail != nil && config.Mail.IsReady(),
		"mongo_uri":    os.Getenv("MONGODB_URI"),
	})
}
