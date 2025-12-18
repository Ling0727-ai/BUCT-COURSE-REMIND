package middleware

import (
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

// LoginRequired 登录验证中间件
func LoginRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		session := sessions.Default(c)
		userID := session.Get("user_id")

		if userID == nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
			c.Abort()
			return
		}

		// 将用户ID添加到上下文
		c.Set("user_id", userID.(string))
		c.Set("username", session.Get("username"))
		c.Next()
	}
}

// AdminRequired 管理员验证中间件
func AdminRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		session := sessions.Default(c)
		isAdmin := session.Get("is_admin")

		if isAdmin == nil || !isAdmin.(bool) {
			c.JSON(http.StatusForbidden, gin.H{"error": "需要管理员权限"})
			c.Abort()
			return
		}

		c.Next()
	}
}

// GetUserID 从上下文获取用户ID
func GetUserID(c *gin.Context) string {
	if userID, exists := c.Get("user_id"); exists {
		return userID.(string)
	}
	return ""
}
