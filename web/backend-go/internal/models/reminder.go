package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// ScheduledReminder 定时提醒
type ScheduledReminder struct {
	ID           primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	UserID       primitive.ObjectID `bson:"user_id" json:"user_id"`
	AssignmentID string             `bson:"assignment_id" json:"assignment_id"`
	Title        string             `bson:"title" json:"title"`
	Subject      string             `bson:"subject" json:"subject"`
	ReminderTime time.Time          `bson:"reminder_time" json:"reminder_time"`
	Sent         bool               `bson:"sent" json:"sent"`
	SentAt       *time.Time         `bson:"sent_at,omitempty" json:"sent_at"`
	Type         string             `bson:"type" json:"type"` // manual, auto
	CreatedAt    time.Time          `bson:"created_at" json:"created_at"`
}

// Setting 系统设置
type Setting struct {
	ID        primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	Key       string             `bson:"key" json:"key"`
	Value     string             `bson:"value" json:"value"`
	UpdatedAt time.Time          `bson:"updated_at" json:"updated_at"`
}

// WebhookLog Webhook日志
type WebhookLog struct {
	ID          primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	WebhookType string             `bson:"webhook_type" json:"webhook_type"`
	Message     string             `bson:"message" json:"message"`
	Status      string             `bson:"status" json:"status"`
	CreatedAt   time.Time          `bson:"created_at" json:"created_at"`
}
