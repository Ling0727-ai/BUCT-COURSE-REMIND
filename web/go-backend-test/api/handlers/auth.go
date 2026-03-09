package handlers

import (
	"log"

	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
	"github.com/Ling0727-ai/go-buct-course-backend/middleware"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/Ling0727-ai/go-buct-course-backend/utils"
	"github.com/gin-gonic/gin"
)

// Login 用户登录，对应 Python POST /api/auth/login
func Login(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.RequestFormatError})
		return
	}

	var username, password string

	if encryptedData, ok := body["encrypted_data"].(string); ok && encryptedData != "" {
		rsaSvc := crypto.GetRSAService()
		decrypted, err := rsaSvc.DecryptRequest(encryptedData)
		if err != nil {
			log.Printf("[auth] Login 解密失败: %v", err)
			c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.DecryptFailed + ": " + err.Error()})
			return
		}
		username, _ = decrypted["username"].(string)
		password, _ = decrypted["password"].(string)
	} else {
		username, _ = body["username"].(string)
		password, _ = body["password"].(string)
	}

	if username == "" || password == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.InvalidCredentials})
		return
	}

	user, err := User.Service.LoginUser(username, password)
	if err != nil {
		c.JSON(utils.Defaults.Status.Unauthorized, gin.H{"error": err.Error()})
		return
	}

	middleware.IssueSessionCookie(c, user.ID, user.Username, user.IsAdmin)
	services.RefreshUserDataAsync(user.ID)

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"message": utils.Defaults.Auth.LoginSuccess,
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"is_admin": user.IsAdmin,
		},
		"data_refresh": gin.H{
			"success": true,
			"message": "作业数据正在后台更新中...",
		},
	})
}

// Register 用户注册，对应 Python POST /api/auth/register
func Register(c *gin.Context) {
	var raw map[string]interface{}
	if err := c.ShouldBindJSON(&raw); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.RequestFormatError})
		return
	}

	var fields map[string]interface{}

	if enc, ok := raw["encrypted_data"].(string); ok && enc != "" {
		rsaSvc := crypto.GetRSAService()
		decrypted, err := rsaSvc.DecryptRequest(enc)
		if err != nil {
			log.Printf("[auth] Register 解密失败: %v", err)
			c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.DecryptFailed + ": " + err.Error()})
			return
		}
		fields = decrypted
	} else {
		fields = raw
	}

	username, _ := fields["username"].(string)
	email, _ := fields["email"].(string)
	password, _ := fields["password"].(string)
	studentID, _ := fields["student_id"].(string)
	sPassword, _ := fields["s_password"].(string)

	if username == "" || email == "" || password == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.InvalidCredentials})
		return
	}

	user, err := User.Service.RegisterUser(username, email, password, studentID, sPassword)
	if err != nil {
		c.JSON(utils.Defaults.Status.Conflict, gin.H{"error": err.Error()})
		return
	}

	c.JSON(utils.Defaults.Status.Created, gin.H{
		"message": utils.Defaults.Auth.RegisterSuccess,
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
		},
	})
}

// AuthStatus 检查登录状态，对应 Python GET /api/auth/status
// SessionMiddleware 已把 user_id 注入 context，直接读取即可
func AuthStatus(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists || userID == "" {
		c.JSON(utils.Defaults.Status.OK, gin.H{"authenticated": false})
		return
	}

	user, err := User.Repository.GetUserByID(userID.(string))
	if err != nil || user == nil {
		c.JSON(utils.Defaults.Status.OK, gin.H{"authenticated": false})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"authenticated": true,
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"is_admin": user.IsAdmin,
		},
	})
}

// GetUserInfo 获取当前用户详情，对应 Python GET /api/auth/user-info
func GetUserInfo(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	user, err := User.Repository.GetUserByID(userID)
	if err != nil || user == nil {
		c.JSON(utils.Defaults.Status.NotFound, gin.H{"error": utils.Defaults.User.NotFound})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"id":                   user.ID,
		"username":             user.Username,
		"email":                user.Email,
		"student_id":           user.StudentID,
		"has_student_password": user.SPassword != "",
		"is_admin":             user.IsAdmin,
	})
}

// UpdateEmail 更新用户邮箱，对应 Python POST /api/auth/update-email
func UpdateEmail(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	var body struct {
		Email string `json:"email" binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.Empty})
		return
	}
	if !services.EmailRegexp.MatchString(body.Email) {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.InvalidFormat})
		return
	}

	// 检查邮箱是否被其他用户使用
	existing, _ := User.Repository.GetUserByEmail(body.Email)
	if existing != nil && existing.ID != userID {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.AlreadyUsed})
		return
	}

	user, _ := User.Repository.GetUserByID(userID)
	if user == nil {
		c.JSON(utils.Defaults.Status.NotFound, gin.H{"error": utils.Defaults.User.NotFound})
		return
	}
	user.Email = body.Email

	if err := User.Repository.UpdateUser(user); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.User.UpdateFailed})
		return
	}
	c.JSON(utils.Defaults.Status.OK, gin.H{"message": utils.Defaults.Email.UpdateSuccess})
}

// UpdateStudentInfo 更新学号和外部系统密码，对应 Python POST /api/auth/update-student-info
func UpdateStudentInfo(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	var body struct {
		StudentID *string `json:"student_id"`
		SPassword *string `json:"s_password"`
	}
	if err := c.ShouldBindJSON(&body); err != nil || (body.StudentID == nil && body.SPassword == nil) {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Misc.NoUpdatedFields})
		return
	}

	user, _ := User.Repository.GetUserByID(userID)
	if user == nil {
		c.JSON(utils.Defaults.Status.NotFound, gin.H{"error": utils.Defaults.User.NotFound})
		return
	}

	if body.StudentID != nil {
		user.StudentID = *body.StudentID
	}
	if body.SPassword != nil {
		// 过滤掩码占位符（全是 • 的字符串），对应 Python masked 检测
		masked := true
		for _, ch := range *body.SPassword {
			if ch != '•' {
				masked = false
				break
			}
		}
		if !masked && *body.SPassword != "" {
			enc, err := crypto.Crypto.EncryptECC(*body.SPassword)
			if err == nil {
				user.SPassword = enc
			}
		}
	}

	if err := User.Repository.UpdateUser(user); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.User.UpdateFailed})
		return
	}
	c.JSON(utils.Defaults.Status.OK, gin.H{"message": utils.Defaults.Auth.StudentInfoSuccess})
}

// CheckEmail 检查邮箱是否已注册，对应 Python POST /api/auth/check-email
func CheckEmail(c *gin.Context) {
	var body struct {
		Email string `json:"email" binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.Empty})
		return
	}
	if !services.EmailRegexp.MatchString(body.Email) {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Email.InvalidFormat})
		return
	}

	user, _ := User.Repository.GetUserByEmail(body.Email)
	c.JSON(utils.Defaults.Status.OK, gin.H{"exists": user != nil})
}

// ResetPassword 重置密码（强制 RSA 加密），对应 Python POST /api/auth/reset-password
func ResetPassword(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.RequestFormatError})
		return
	}

	encryptedData, _ := body["encrypted_data"].(string)
	if encryptedData == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.RequireEncryption})
		return
	}

	rsa := crypto.GetRSAService()
	decrypted, err := rsa.DecryptRequest(encryptedData)
	if err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Crypto.DecryptFailed})
		return
	}

	email, _ := decrypted["email"].(string)
	newPassword, _ := decrypted["new_password"].(string)
	if email == "" || newPassword == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.User.EmailAndPwdRequired})
		return
	}
	if len(newPassword) < 6 {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.User.PasswordTooShort})
		return
	}

	user, _ := User.Repository.GetUserByEmail(email)
	if user == nil {
		c.JSON(utils.Defaults.Status.NotFound, gin.H{"error": utils.Defaults.Email.NotFound})
		return
	}

	hash, err := crypto.Crypto.HashPassword(newPassword)
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.User.PasswordProcessFail})
		return
	}
	user.PasswordHash = hash

	if err = User.Repository.UpdateUser(user); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": utils.Defaults.User.UpdateFailed})
		return
	}
	c.JSON(utils.Defaults.Status.OK, gin.H{"message": utils.Defaults.Auth.ResetPasswordSuccess})
}

// Logout 用户登出，对应 Python POST /api/auth/logout
func Logout(c *gin.Context) {
	middleware.ClearSessionCookie(c)
	c.JSON(utils.Defaults.Status.OK, gin.H{"message": utils.Defaults.Auth.LogoutSuccess})
}
