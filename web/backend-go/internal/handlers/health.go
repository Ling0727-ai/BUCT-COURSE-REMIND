package handlers

import (
	"net/http"
	"runtime"
	"time"

	"buct-course-remind/internal/database"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
)

// HealthHandler 健康检查处理器
type HealthHandler struct{}

// NewHealthHandler 创建健康检查处理器
func NewHealthHandler() *HealthHandler {
	return &HealthHandler{}
}

var startTime = time.Now()

// Health 健康检查
func (h *HealthHandler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"time":    time.Now().Format(time.RFC3339),
		"version": "1.0.0-go",
	})
}

// DetailedHealth 详细健康检查
func (h *HealthHandler) DetailedHealth(c *gin.Context) {
	// 检查MongoDB连接
	dbStatus := "connected"
	collection := database.GetCollection(database.UsersCollection)
	if err := collection.FindOne(nil, bson.M{}).Err(); err != nil {
		// 空集合也算正常
		if err.Error() != "mongo: no documents in result" {
			dbStatus = "error"
		}
	}

	// 获取内存统计
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"time":   time.Now().Format(time.RFC3339),
		"uptime": time.Since(startTime).String(),
		"database": gin.H{
			"status": dbStatus,
		},
		"memory": gin.H{
			"alloc":       memStats.Alloc / 1024 / 1024,
			"total_alloc": memStats.TotalAlloc / 1024 / 1024,
			"sys":         memStats.Sys / 1024 / 1024,
			"num_gc":      memStats.NumGC,
		},
		"goroutines": runtime.NumGoroutine(),
		"version":    "1.0.0-go",
	})
}
