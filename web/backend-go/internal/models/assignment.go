package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// CourseData 课程数据
type CourseData struct {
	ID        primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	UserID    primitive.ObjectID `bson:"user_id" json:"user_id"`
	TaskID    string             `bson:"task_id" json:"task_id"`
	Subject   string             `bson:"subject" json:"subject"`
	Title     string             `bson:"title" json:"title"`
	Deadline  string             `bson:"deadline" json:"deadline"`
	Details   string             `bson:"details" json:"details"`
	URL       string             `bson:"url" json:"url"`
	Type      string             `bson:"type" json:"type"` // homework, test
	CreatedAt time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt time.Time          `bson:"updated_at" json:"updated_at"`
}

// Assignment 作业（前端显示格式）
type Assignment struct {
	ID        string            `json:"id"`
	Subject   string            `json:"subject"`
	Type      string            `json:"type"`
	Details   AssignmentDetails `json:"details"`
	Completed bool              `json:"completed"`
	HasTasks  bool              `json:"has_tasks"`
	TaskCount int               `json:"tasks_count"`
}

// AssignmentDetails 作业详情
type AssignmentDetails struct {
	Task           string `json:"task"`
	Deadline       string `json:"deadline"`
	URL            string `json:"url"`
	CanSubmit      bool   `json:"can_submit"`
	IsGroup        bool   `json:"is_group"`
	DetailsContent string `json:"details_content"`
}

// AssignmentStatus 作业状态
type AssignmentStatus struct {
	ID           primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	UserID       primitive.ObjectID `bson:"user_id" json:"user_id"`
	AssignmentID string             `bson:"assignment_id" json:"assignment_id"`
	Title        string             `bson:"title,omitempty" json:"title"`
	Subject      string             `bson:"subject,omitempty" json:"subject"`
	Status       string             `bson:"status" json:"status"` // completed, deleted, permanent_deleted
	CreatedAt    time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt    time.Time          `bson:"updated_at" json:"updated_at"`
}

// AssignmentStats 作业统计
type AssignmentStats struct {
	HomeworkCount int `json:"homework_count"`
	TestsCount    int `json:"tests_count"`
	TotalCount    int `json:"total_count"`
}
