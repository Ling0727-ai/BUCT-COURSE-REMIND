package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Todo 待办事项
type Todo struct {
	ID             primitive.ObjectID `bson:"_id,omitempty" json:"_id"`
	UserID         primitive.ObjectID `bson:"user_id" json:"user_id"`
	Title          string             `bson:"title" json:"title"`
	Description    *string            `bson:"description,omitempty" json:"description"`
	Priority       string             `bson:"priority" json:"priority"` // low, medium, high
	DueDate        *time.Time         `bson:"due_date,omitempty" json:"due_date"`
	EstimatedHours *float64           `bson:"estimated_hours,omitempty" json:"estimated_hours"`
	Completed      bool               `bson:"completed" json:"completed"`
	CompletedAt    *time.Time         `bson:"completed_at,omitempty" json:"completed_at"`
	Deleted        bool               `bson:"deleted" json:"deleted"`
	DeletedAt      *time.Time         `bson:"deleted_at,omitempty" json:"deleted_at"`
	CreatedAt      time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt      time.Time          `bson:"updated_at" json:"updated_at"`
}

// TodoResponse 待办响应格式
type TodoResponse struct {
	ID             string   `json:"_id"`
	UserID         string   `json:"user_id"`
	Title          string   `json:"title"`
	Description    *string  `json:"description"`
	Priority       string   `json:"priority"`
	DueDate        *string  `json:"due_date"`
	EstimatedHours *float64 `json:"estimated_hours"`
	Completed      bool     `json:"completed"`
	CompletedAt    *string  `json:"completed_at"`
	CreatedAt      string   `json:"created_at"`
	UpdatedAt      string   `json:"updated_at"`
}

// ToResponse 转换为响应格式
func (t *Todo) ToResponse() TodoResponse {
	resp := TodoResponse{
		ID:             t.ID.Hex(),
		UserID:         t.UserID.Hex(),
		Title:          t.Title,
		Description:    t.Description,
		Priority:       t.Priority,
		EstimatedHours: t.EstimatedHours,
		Completed:      t.Completed,
		CreatedAt:      t.CreatedAt.Format(time.RFC3339),
		UpdatedAt:      t.UpdatedAt.Format(time.RFC3339),
	}

	if t.DueDate != nil {
		dueDate := t.DueDate.Format(time.RFC3339)
		resp.DueDate = &dueDate
	}

	if t.CompletedAt != nil {
		completedAt := t.CompletedAt.Format(time.RFC3339)
		resp.CompletedAt = &completedAt
	}

	return resp
}

// CreateTodoRequest 创建待办请求
type CreateTodoRequest struct {
	Title       string   `json:"title" binding:"required"`
	Description *string  `json:"description"`
	Priority    string   `json:"priority"`
	Hours       *float64 `json:"hours"`
	DueDate     *string  `json:"due_date"`
}

// UpdateTodoRequest 更新待办请求
type UpdateTodoRequest struct {
	Title       *string  `json:"title"`
	Description *string  `json:"description"`
	Priority    *string  `json:"priority"`
	Hours       *float64 `json:"hours"`
	DueDate     *string  `json:"due_date"`
	Completed   *bool    `json:"completed"`
}
