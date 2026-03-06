package middleware

import (
	"fmt"
	"time"

	"github.com/gin-gonic/gin"
)

// LoggingMiddleware 日志中间件
func LoggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		startTime := time.Now()

		// 处理请求
		c.Next()

		// 计算执行时间
		duration := time.Since(startTime)
		statusCode := c.Writer.Status()

		fmt.Printf("[%s] %s %s - %d (%v)\n",
			time.Now().Format("2006-01-02 15:04:05"),
			c.Request.Method,
			c.Request.URL.Path,
			statusCode,
			duration,
		)
	}
}

// CORSMiddleware CORS中间件
// 不能同时用 * + credentials:true，改为动态反射请求来源
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		origin := c.Request.Header.Get("Origin")
		if origin == "" {
			origin = "*"
		}
		c.Writer.Header().Set("Access-Control-Allow-Origin", origin)
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// RecoveryMiddleware 恢复中间件（处理panic）
func RecoveryMiddleware() gin.HandlerFunc {
	return gin.Recovery()
}
