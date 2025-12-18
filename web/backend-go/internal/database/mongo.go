package database

import (
	"context"
	"log"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	client   *mongo.Client
	database *mongo.Database
)

// Connect 连接到MongoDB
func Connect(uri string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	clientOptions := options.Client().ApplyURI(uri)
	var err error
	client, err = mongo.Connect(ctx, clientOptions)
	if err != nil {
		return err
	}

	// 测试连接
	if err = client.Ping(ctx, nil); err != nil {
		return err
	}

	// 从URI中提取数据库名称，默认使用buct-course
	database = client.Database("buct-course")

	log.Println("Connected to MongoDB successfully")
	return nil
}

// Disconnect 断开MongoDB连接
func Disconnect() {
	if client != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := client.Disconnect(ctx); err != nil {
			log.Printf("Error disconnecting from MongoDB: %v", err)
		}
	}
}

// GetDB 获取数据库实例
func GetDB() *mongo.Database {
	return database
}

// GetCollection 获取集合
func GetCollection(name string) *mongo.Collection {
	return database.Collection(name)
}

// Collections 常用集合名称
const (
	UsersCollection              = "users"
	VerificationCodesCollection  = "verification_codes"
	AssignmentsCollection        = "assignments"
	CourseDataCollection         = "course_data"
	AssignmentStatusCollection   = "assignment_status"
	TodosCollection              = "todos"
	SettingsCollection           = "settings"
	ScheduledRemindersCollection = "scheduled_reminders"
	WebhookLogsCollection        = "webhook_logs"
)
