package models

import (
	"context"
	"log"
	"os"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// ──────────────────────────────────────────────
// 全局单例连接池
// mongo.Client 内部已经是连接池，整个进程只需要一个实例，
// 所有 goroutine/handler 共享复用，彻底消灭每次 ConnectToDB()
// 都 new 一个新 client 导致的连接泄漏。
// ──────────────────────────────────────────────

var (
	globalClient *mongo.Client
	once         sync.Once
	initErr      error
)

// ConnectToDB 返回全局单例 mongo.Client。
// 第一次调用时建立连接，后续调用直接返回已有实例，不会创建新连接。
func ConnectToDB() (*mongo.Client, error) {
	once.Do(func() {
		dbUri := os.Getenv("MONGODB_URI")
		if dbUri == "" {
			dbUri = "mongodb://localhost:27017"
		}

		clientOptions := options.Client().ApplyURI(dbUri)

		// 连接池配置：限制最大连接数，防止连接风暴
		clientOptions.SetMaxPoolSize(20)
		clientOptions.SetMinPoolSize(2)
		clientOptions.SetMaxConnIdleTime(5 * time.Minute)

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		globalClient, initErr = mongo.Connect(ctx, clientOptions)
		if initErr != nil {
			log.Printf("[db] 连接 MongoDB 失败: %v", initErr)
			return
		}

		if initErr = globalClient.Ping(ctx, nil); initErr != nil {
			log.Printf("[db] MongoDB Ping 失败: %v", initErr)
			globalClient = nil
			return
		}

		log.Println("[db] MongoDB 连接池已初始化")
	})

	return globalClient, initErr
}

// DisconnectDB 在进程退出时（main 的 defer）调用，优雅关闭连接池
func DisconnectDB() {
	if globalClient == nil {
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := globalClient.Disconnect(ctx); err != nil {
		log.Printf("[db] 断开 MongoDB 失败: %v", err)
	} else {
		log.Println("[db] MongoDB 连接池已关闭")
	}
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
