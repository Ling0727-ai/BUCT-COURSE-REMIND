package middleware

import (
	"fmt"
	"net/url"
	"os"
	"strings"
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
// 不能同时用 * + credentials:true，也不能无条件反射请求来源。
//
// 原实现把任意 Origin 原样写回 Access-Control-Allow-Origin 并允许携带凭据，
// 相当于允许任何网站带着用户 Cookie 跨站读取接口响应。
// 现在只放行：同源请求，以及 ALLOWED_ORIGINS 中显式列出的来源。
// 生产部署走 nginx 同源代理，本就不需要跨域。
func CORSMiddleware() gin.HandlerFunc {
	allowed := map[string]bool{}
	if v := os.Getenv("ALLOWED_ORIGINS"); v != "" {
		for _, o := range strings.Split(v, ",") {
			o = strings.TrimSpace(o)
			if o != "" {
				allowed[strings.TrimRight(o, "/")] = true
			}
		}
	}

	return func(c *gin.Context) {
		origin := strings.TrimRight(c.Request.Header.Get("Origin"), "/")

		if origin != "" && isAllowedOrigin(c, origin, allowed) {
			c.Writer.Header().Set("Access-Control-Allow-Origin", origin)
			c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
			c.Writer.Header().Set("Vary", "Origin")
			c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
			c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")
			c.Writer.Header().Set("Access-Control-Max-Age", "600")
		}

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// isAllowedOrigin 判断来源是否为同源，或落在显式白名单内
func isAllowedOrigin(c *gin.Context, origin string, allowed map[string]bool) bool {
	if allowed[origin] {
		return true
	}

	// 同源：Origin 的 host 部分与请求 Host 一致（含协议）
	if u, err := url.Parse(origin); err == nil && u.Host == c.Request.Host {
		scheme := "http"
		if c.Request.TLS != nil || c.Request.Header.Get("X-Forwarded-Proto") == "https" {
			scheme = "https"
		}
		if u.Scheme == scheme {
			return true
		}
	}

	return false
}

// RecoveryMiddleware 恢复中间件（处理panic）
func RecoveryMiddleware() gin.HandlerFunc {
	return gin.Recovery()
}
