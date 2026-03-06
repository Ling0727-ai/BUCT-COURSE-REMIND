package handlers

import (
	"net/http"

	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/gin-gonic/gin"
)

// Login 用户登录，对应 Python POST /api/auth/login
// 支持明文和 RSA 加密两种请求格式
func Login(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	var username, password string

	// 优先尝试 RSA 解密，对应 Python 中 encrypted_data 分支
	if encryptedData, ok := body["encrypted_data"].(string); ok && encryptedData != "" {
		rsa := crypto.GetRSAService()
		decrypted, err := rsa.DecryptRequest(encryptedData)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "数据解密失败"})
			return
		}
		username, _ = decrypted["username"].(string)
		password, _ = decrypted["password"].(string)
	} else {
		// 明文兼容（开发阶段），对应 Python else 分支
		username, _ = body["username"].(string)
		password, _ = body["password"].(string)
	}

	if username == "" || password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "用户名/邮箱和密码不能为空"})
		return
	}

	// 调用 service 登录
	user, err := User.Service.LoginUser(username, password)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 登录成功后异步刷新作业数据，对应 Python auto_refresh_assignments_on_login
	// 不阻塞登录响应，刷新失败不影响登录
	services.RefreshUserDataAsync(user.ID)

	c.JSON(http.StatusOK, gin.H{
		"message": "登录成功",
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
	var body struct {
		Username  string `json:"username" binding:"required"`
		Email     string `json:"email"    binding:"required"`
		Password  string `json:"password" binding:"required"`
		StudentID string `json:"student_id"`
		SPassword string `json:"s_password"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := User.Service.RegisterUser(
		body.Username, body.Email, body.Password,
		body.StudentID, body.SPassword,
	)
	if err != nil {
		c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message": "注册成功",
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
		},
	})
}

// AuthStatus 检查登录状态，对应 Python GET /api/auth/status
// Go 使用 JWT/session 中间件，这里简单示意从 context 取用户信息
func AuthStatus(c *gin.Context) {
	// 实际项目中由 JWT 中间件注入 userID 到 context
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusOK, gin.H{"authenticated": false})
		return
	}

	user, err := User.Repository.GetUserByID(userID.(string))
	if err != nil || user == nil {
		c.JSON(http.StatusOK, gin.H{"authenticated": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{
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
		c.JSON(http.StatusNotFound, gin.H{"error": "用户不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱地址不能为空"})
		return
	}
	if !services.EmailRegexp.MatchString(body.Email) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}

	// 检查邮箱是否被其他用户使用
	existing, _ := User.Repository.GetUserByEmail(body.Email)
	if existing != nil && existing.ID != userID {
		c.JSON(http.StatusBadRequest, gin.H{"error": "该邮箱已被其他用户使用"})
		return
	}

	user, _ := User.Repository.GetUserByID(userID)
	if user == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "用户不存在"})
		return
	}
	user.Email = body.Email

	if err := User.Repository.UpdateUser(user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败，请重试"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "邮箱修改成功"})
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "无可更新的字段"})
		return
	}

	user, _ := User.Repository.GetUserByID(userID)
	if user == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "用户不存在"})
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
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败，请重试"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "学生信息更新成功"})
}

// CheckEmail 检查邮箱是否已注册，对应 Python POST /api/auth/check-email
func CheckEmail(c *gin.Context) {
	var body struct {
		Email string `json:"email" binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱地址不能为空"})
		return
	}
	if !services.EmailRegexp.MatchString(body.Email) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}

	user, _ := User.Repository.GetUserByEmail(body.Email)
	c.JSON(http.StatusOK, gin.H{"exists": user != nil})
}

// ResetPassword 重置密码（强制 RSA 加密），对应 Python POST /api/auth/reset-password
func ResetPassword(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	encryptedData, _ := body["encrypted_data"].(string)
	if encryptedData == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "必须使用加密传输"})
		return
	}

	rsa := crypto.GetRSAService()
	decrypted, err := rsa.DecryptRequest(encryptedData)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "数据解密失败"})
		return
	}

	email, _ := decrypted["email"].(string)
	newPassword, _ := decrypted["new_password"].(string)
	if email == "" || newPassword == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱和新密码不能为空"})
		return
	}
	if len(newPassword) < 6 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "密码长度至少6位"})
		return
	}

	user, _ := User.Repository.GetUserByEmail(email)
	if user == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "该邮箱未注册"})
		return
	}

	hash, err := crypto.Crypto.HashPassword(newPassword)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "密码处理失败"})
		return
	}
	user.PasswordHash = hash

	if err = User.Repository.UpdateUser(user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "重置失败，请重试"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "密码重置成功"})
}

// Logout 用户登出，对应 Python POST /api/auth/logout
func Logout(c *gin.Context) {
	// JWT 无状态，前端直接丢弃 token 即可；服务端可选加黑名单
	c.JSON(http.StatusOK, gin.H{"message": "登出成功"})
}
