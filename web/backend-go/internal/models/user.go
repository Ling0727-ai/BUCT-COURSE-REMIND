package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// User 用户模型
type User struct {
	ID           primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	Username     string             `bson:"username" json:"username"`
	Email        string             `bson:"email" json:"email"`
	PasswordHash string             `bson:"password_hash" json:"-"`
	StudentID    string             `bson:"student_id,omitempty" json:"student_id"`
	SPassword    string             `bson:"s_password,omitempty" json:"-"` // 加密后的外部密码
	SPasswordLen *int               `bson:"s_password_len,omitempty" json:"-"`
	IsAdmin      bool               `bson:"is_admin" json:"is_admin"`
	// 用户提醒设置
	AutoReminder      bool    `bson:"auto_reminder,omitempty" json:"auto_reminder"`           // 是否启用自动提醒
	ReminderHours     float64 `bson:"reminder_hours,omitempty" json:"reminder_hours"`         // 提前多少小时提醒
	EmailNotification bool    `bson:"email_notification,omitempty" json:"email_notification"` // 是否启用邮件通知
	CreatedAt         time.Time `bson:"created_at" json:"created_at"`
	UpdatedAt         time.Time `bson:"updated_at" json:"updated_at"`
}

// UserResponse 用户响应（不包含敏感信息）
type UserResponse struct {
	ID       string `json:"id"`
	Username string `json:"username"`
	IsAdmin  bool   `json:"is_admin"`
}

// ToResponse 转换为响应对象
func (u *User) ToResponse() UserResponse {
	return UserResponse{
		ID:       u.ID.Hex(),
		Username: u.Username,
		IsAdmin:  u.IsAdmin,
	}
}

// VerificationCode 验证码
type VerificationCode struct {
	ID        primitive.ObjectID `bson:"_id,omitempty"`
	Email     string             `bson:"email"`
	Code      string             `bson:"code"`
	Type      string             `bson:"type"` // register, forgot_password, etc.
	CreatedAt time.Time          `bson:"created_at"`
	ExpiresAt time.Time          `bson:"expires_at"`
	Used      bool               `bson:"used"`
}
