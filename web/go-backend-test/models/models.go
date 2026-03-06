package models

import (
	"context"
	"log"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// ConnectToDB 建立数据库连接并返回客户端实例
func ConnectToDB() (*mongo.Client, error) {
	// 统一连接mongodb
	dbUri := os.Getenv("MONGODB_URI")
	dbPassword := os.Getenv("MONGODB_PASSWORD")

	// 这里可以使用 dbUri 和 dbPassword 来连接数据库
	clientOptions := options.Client().ApplyURI(dbUri)
	if dbPassword != "" {
		clientOptions.SetAuth(options.Credential{
			Username: "your_username", // 替换为实际用户名
			Password: dbPassword,
		})
	}

	// 连接数据库
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, clientOptions)

	if err != nil {
		log.Fatal(err)
	}

	// 检查连接
	err = client.Ping(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Connected to MongoDB!")
	return client, nil
}

// APIResponse 通用成功响应结构
type APIResponse struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// ErrorResponse 通用错误响应结构
type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Error   string `json:"error,omitempty"`
}

func disconnectDB(client *mongo.Client) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := client.Disconnect(ctx); err != nil {
		log.Fatal(err)
	}

	log.Println("Disconnected from MongoDB!")
}
