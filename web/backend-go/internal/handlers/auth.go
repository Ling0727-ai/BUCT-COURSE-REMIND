package handlers

import (
	"context"
	"log"
	"net/http"
	"strings"
	"time"

	"buct-course-remind/internal/crypto"
	"buct-course-remind/internal/database"
	"buct-course-remind/internal/middleware"
	"buct-course-remind/internal/models"
	"buct-course-remind/internal/services"
	"buct-course-remind/internal/utils"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// AuthHandler 认证处理器
type AuthHandler struct{}

// NewAuthHandler 创建认证处理器
func NewAuthHandler() *AuthHandler {
	return &AuthHandler{}
}

// LoginRequest 登录请求
type LoginRequest struct {
	Username      string `json:"username"`
	Password      string `json:"password"`
	EncryptedData string `json:"encrypted_data"`
}

// RegisterRequest 注册请求
type RegisterRequest struct {
	Username      string `json:"username"`
	Email         string `json:"email"`
	Password      string `json:"password"`
	Code          string `json:"code"`
	EncryptedData string `json:"encrypted_data"`
}

// Login 用户登录
func (h *AuthHandler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	var username, password string

	// 检查是否为加密数据
	if req.EncryptedData != "" {
		rsaCrypto := crypto.GetRSACrypto()
		decrypted, err := rsaCrypto.DecryptData(req.EncryptedData)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "数据解密失败"})
			return
		}
		username = decrypted["username"]
		password = decrypted["password"]
	} else {
		username = req.Username
		password = req.Password
	}

	if username == "" || password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "用户名/邮箱和密码不能为空"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	// 尝试通过用户名或邮箱查找用户
	var user models.User
	filter := bson.M{
		"$or": []bson.M{
			{"username": username},
			{"email": username},
		},
	}

	err := collection.FindOne(ctx, filter).Decode(&user)
	if err != nil {
		log.Printf("用户 %s 登录失败：账号不存在", username)
		c.JSON(http.StatusUnauthorized, gin.H{"error": "账号不存在，请检查用户名或邮箱"})
		return
	}

	// 验证密码
	if !utils.CheckPasswordHash(password, user.PasswordHash) {
		log.Printf("用户 %s 登录失败：密码错误", username)
		c.JSON(http.StatusUnauthorized, gin.H{"error": "密码错误"})
		return
	}

	// 登录成功，设置session
	session := sessions.Default(c)
	session.Set("user_id", user.ID.Hex())
	session.Set("username", user.Username)
	session.Set("is_admin", user.IsAdmin)
	if err := session.Save(); err != nil {
		log.Printf("保存session失败: %v", err)
	}

	loginMethod := "用户名"
	if strings.Contains(username, "@") {
		loginMethod = "邮箱"
	}
	log.Printf("用户 %s 登录成功（使用%s登录）", user.Username, loginMethod)

	// 启动后台刷新任务
	go services.AutoRefreshAssignments(user.ID.Hex())

	c.JSON(http.StatusOK, gin.H{
		"message": "登录成功",
		"user":    user.ToResponse(),
		"data_refresh": gin.H{
			"success": true,
			"message": "作业数据正在后台更新中...",
		},
	})
}

// Logout 用户登出
func (h *AuthHandler) Logout(c *gin.Context) {
	session := sessions.Default(c)
	username := session.Get("username")

	session.Clear()
	if err := session.Save(); err != nil {
		log.Printf("清除session失败: %v", err)
	}

	log.Printf("用户 %v 已登出", username)
	c.JSON(http.StatusOK, gin.H{"message": "登出成功"})
}

// Status 检查登录状态
func (h *AuthHandler) Status(c *gin.Context) {
	session := sessions.Default(c)
	userID := session.Get("user_id")

	if userID == nil {
		c.JSON(http.StatusOK, gin.H{"authenticated": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	objID, err := primitive.ObjectIDFromHex(userID.(string))
	if err != nil {
		c.JSON(http.StatusOK, gin.H{"authenticated": false})
		return
	}

	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user); err != nil {
		c.JSON(http.StatusOK, gin.H{"authenticated": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"authenticated": true,
		"user":          user.ToResponse(),
	})
}

// SendVerificationCode 发送验证码
func (h *AuthHandler) SendVerificationCode(c *gin.Context) {
	var req struct {
		Email string `json:"email" binding:"required,email"`
		Type  string `json:"type"` // register, forgot_password
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}

	// 默认类型为注册
	if req.Type == "" {
		req.Type = "register"
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	// 检查邮箱是否已注册
	var existingUser models.User
	err := collection.FindOne(ctx, bson.M{"email": req.Email}).Decode(&existingUser)

	if req.Type == "register" && err == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "该邮箱已被注册"})
		return
	}

	if req.Type == "forgot_password" && err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "该邮箱未注册"})
		return
	}

	// 生成验证码
	code := utils.GenerateVerificationCode(6)

	// 保存验证码
	verifyCollection := database.GetCollection(database.VerificationCodesCollection)
	verifyCode := models.VerificationCode{
		Email:     req.Email,
		Code:      code,
		Type:      req.Type,
		CreatedAt: utils.GetBeijingTime(),
		ExpiresAt: utils.GetBeijingTime().Add(3 * time.Minute),
		Used:      false,
	}

	_, err = verifyCollection.InsertOne(ctx, verifyCode)
	if err != nil {
		log.Printf("保存验证码失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "发送验证码失败"})
		return
	}

	// 发送邮件
	if err := services.SendVerificationEmail(req.Email, code); err != nil {
		log.Printf("发送验证码邮件失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "发送验证码失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "验证码已发送"})
}

// VerifyCode 验证验证码（不消耗，仅验证有效性）
func (h *AuthHandler) VerifyCode(c *gin.Context) {
	var req struct {
		Email string `json:"email" binding:"required,email"`
		Code  string `json:"code" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	verifyCollection := database.GetCollection(database.VerificationCodesCollection)
	var verifyCode models.VerificationCode

	err := verifyCollection.FindOne(ctx, bson.M{
		"email": req.Email,
		"code":  req.Code,
		"used":  false,
		"expires_at": bson.M{"$gt": utils.GetBeijingTime()},
	}).Decode(&verifyCode)

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "验证码无效或已过期"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "验证码有效",
	})
}

// Register 用户注册
func (h *AuthHandler) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		log.Printf("注册请求解析失败: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	var username, email, password, studentID, sPassword string

	// 检查是否为加密数据
	if req.EncryptedData != "" {
		rsaCrypto := crypto.GetRSACrypto()
		decrypted, err := rsaCrypto.DecryptData(req.EncryptedData)
		if err != nil {
			log.Printf("注册数据解密失败: %v", err)
			c.JSON(http.StatusBadRequest, gin.H{"error": "数据解密失败"})
			return
		}
		username = decrypted["username"]
		email = decrypted["email"]
		password = decrypted["password"]
		studentID = decrypted["student_id"]
		sPassword = decrypted["s_password"]
	} else {
		username = req.Username
		email = req.Email
		password = req.Password
	}

	log.Printf("注册请求: username=%s, email=%s", username, email)

	if username == "" || email == "" || password == "" {
		log.Printf("注册失败: 必填字段为空")
		c.JSON(http.StatusBadRequest, gin.H{"error": "用户名、邮箱和密码不能为空"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 验证该邮箱最近有有效验证码（前端已通过 verify-code 验证）
	verifyCollection := database.GetCollection(database.VerificationCodesCollection)
	var verifyCode models.VerificationCode
	err := verifyCollection.FindOne(ctx, bson.M{
		"email":      email,
		"used":       false,
		"expires_at": bson.M{"$gt": utils.GetBeijingTime()},
	}).Decode(&verifyCode)

	if err != nil {
		log.Printf("注册失败: 未找到有效验证码 email=%s", email)
		c.JSON(http.StatusBadRequest, gin.H{"error": "请先获取并验证验证码"})
		return
	}

	// 检查用户名和邮箱是否已存在
	collection := database.GetCollection(database.UsersCollection)
	var existingUser models.User

	err = collection.FindOne(ctx, bson.M{"username": username}).Decode(&existingUser)
	if err == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "用户名已存在"})
		return
	}

	err = collection.FindOne(ctx, bson.M{"email": email}).Decode(&existingUser)
	if err == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱已被注册"})
		return
	}

	// 创建用户
	passwordHash, err := utils.HashPassword(password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "密码加密失败"})
		return
	}

	now := utils.GetBeijingTime()
	user := models.User{
		Username:     username,
		Email:        email,
		PasswordHash: passwordHash,
		IsAdmin:      false,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	// 如果提供了学号信息，加密保存
	if studentID != "" {
		user.StudentID = studentID
	}
	if sPassword != "" {
		eccCrypto := crypto.GetECCCrypto()
		if eccCrypto != nil {
			encryptedPassword, err := eccCrypto.EncryptPassword(sPassword)
			if err == nil {
				user.SPassword = encryptedPassword
				pwdLen := len(sPassword)
				user.SPasswordLen = &pwdLen
			}
		}
	}

	result, err := collection.InsertOne(ctx, user)
	if err != nil {
		log.Printf("创建用户失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "注册失败"})
		return
	}

	// 标记验证码已使用
	verifyCollection.UpdateOne(ctx,
		bson.M{"_id": verifyCode.ID},
		bson.M{"$set": bson.M{"used": true}},
	)

	log.Printf("用户 %s 注册成功", username)
	c.JSON(http.StatusOK, gin.H{
		"message": "注册成功",
		"user_id": result.InsertedID.(primitive.ObjectID).Hex(),
	})
}

// ForgotPassword 忘记密码
func (h *AuthHandler) ForgotPassword(c *gin.Context) {
	var req struct {
		Email       string `json:"email" binding:"required"`
		Code        string `json:"code" binding:"required"`
		NewPassword string `json:"new_password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 验证验证码
	verifyCollection := database.GetCollection(database.VerificationCodesCollection)
	var verifyCode models.VerificationCode
	err := verifyCollection.FindOne(ctx, bson.M{
		"email":      req.Email,
		"code":       req.Code,
		"type":       "forgot_password",
		"used":       false,
		"expires_at": bson.M{"$gt": utils.GetBeijingTime()},
	}).Decode(&verifyCode)

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "验证码无效或已过期"})
		return
	}

	// 更新密码
	collection := database.GetCollection(database.UsersCollection)
	passwordHash, err := utils.HashPassword(req.NewPassword)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "密码加密失败"})
		return
	}

	_, err = collection.UpdateOne(ctx,
		bson.M{"email": req.Email},
		bson.M{"$set": bson.M{
			"password_hash": passwordHash,
			"updated_at":    utils.GetBeijingTime(),
		}},
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "密码重置失败"})
		return
	}

	// 标记验证码已使用
	verifyCollection.UpdateOne(ctx,
		bson.M{"_id": verifyCode.ID},
		bson.M{"$set": bson.M{"used": true}},
	)

	c.JSON(http.StatusOK, gin.H{"message": "密码重置成功"})
}

// GetProfile 获取用户资料
func (h *AuthHandler) GetProfile(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)
	objID, _ := primitive.ObjectIDFromHex(userID)

	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "用户不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user": gin.H{
			"id":         user.ID.Hex(),
			"username":   user.Username,
			"email":      user.Email,
			"student_id": user.StudentID,
			"is_admin":   user.IsAdmin,
			"created_at": user.CreatedAt,
		},
	})
}

// UpdateStudentCredentials 更新学生凭据
func (h *AuthHandler) UpdateStudentCredentials(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	var req struct {
		StudentID string `json:"student_id"`
		SPassword string `json:"s_password"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)
	objID, _ := primitive.ObjectIDFromHex(userID)

	updateData := bson.M{"updated_at": utils.GetBeijingTime()}

	if req.StudentID != "" {
		updateData["student_id"] = req.StudentID
	}

	if req.SPassword != "" {
		eccCrypto := crypto.GetECCCrypto()
		encryptedPassword, err := eccCrypto.EncryptPassword(req.SPassword)
		if err != nil {
			log.Printf("加密密码失败: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "加密密码失败"})
			return
		}
		updateData["s_password"] = encryptedPassword
		pwdLen := len(req.SPassword)
		updateData["s_password_len"] = pwdLen
	}

	_, err := collection.UpdateOne(ctx,
		bson.M{"_id": objID},
		bson.M{"$set": updateData},
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "更新成功"})
}

// CheckEmail 检查邮箱是否已注册
func (h *AuthHandler) CheckEmail(c *gin.Context) {
	var req struct {
		Email string `json:"email" binding:"required,email"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)
	var user models.User
	err := collection.FindOne(ctx, bson.M{"email": req.Email}).Decode(&user)

	if err != nil {
		c.JSON(http.StatusOK, gin.H{"exists": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"exists": true})
}

// UpdateEmail 更新用户邮箱
func (h *AuthHandler) UpdateEmail(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	var req struct {
		Email string `json:"email" binding:"required,email"`
		Code  string `json:"code" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 验证验证码
	verifyCollection := database.GetCollection(database.VerificationCodesCollection)
	var verifyCode models.VerificationCode
	err := verifyCollection.FindOne(ctx, bson.M{
		"email":      req.Email,
		"code":       req.Code,
		"used":       false,
		"expires_at": bson.M{"$gt": utils.GetBeijingTime()},
	}).Decode(&verifyCode)

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "验证码无效或已过期"})
		return
	}

	// 检查邮箱是否已被其他用户使用
	collection := database.GetCollection(database.UsersCollection)
	objID, _ := primitive.ObjectIDFromHex(userID)

	var existingUser models.User
	err = collection.FindOne(ctx, bson.M{
		"email": req.Email,
		"_id":   bson.M{"$ne": objID},
	}).Decode(&existingUser)

	if err == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "该邮箱已被其他用户使用"})
		return
	}

	// 更新邮箱
	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": objID},
		bson.M{"$set": bson.M{
			"email":      req.Email,
			"updated_at": utils.GetBeijingTime(),
		}},
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败"})
		return
	}

	// 标记验证码已使用
	verifyCollection.UpdateOne(ctx,
		bson.M{"_id": verifyCode.ID},
		bson.M{"$set": bson.M{"used": true}},
	)

	c.JSON(http.StatusOK, gin.H{"message": "邮箱更新成功"})
}
