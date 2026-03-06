package middleware

import (
	"errors"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

const (
	sessionCookieName  = "session"
	contextUserIDKey   = "user_id"
	contextUsernameKey = "username"
	contextIsAdminKey  = "is_admin"
)

// jwtSecret 从环境变量读取，与 Python SECRET_KEY 保持一致
func jwtSecret() []byte {
	s := os.Getenv("SECRET_KEY")
	if s == "" {
		s = "dev-secret-key-change-in-production"
	}
	return []byte(s)
}

// Claims JWT payload，对应 Python session 里存的字段
type Claims struct {
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	IsAdmin  bool   `json:"is_admin"`
	jwt.RegisteredClaims
}

// IssueSessionCookie 登录成功后签发 JWT，写入 HttpOnly Cookie
// 对应 Python session['user_id'] = user_id
func IssueSessionCookie(c *gin.Context, userID, username string, isAdmin bool) {
	expiry := 6 * time.Hour // 对应 Python 6小时无操作自动登出
	claims := &Claims{
		UserID:   userID,
		Username: username,
		IsAdmin:  isAdmin,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(expiry)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString(jwtSecret())
	if err != nil {
		return
	}

	// 写入 HttpOnly Cookie，SameSite=Lax，与 Python 的 session cookie 行为一致
	c.SetCookie(
		sessionCookieName,
		signed,
		int(expiry.Seconds()),
		"/",
		"",    // domain：空 = 当前域
		false, // secure：本地开发不强制 HTTPS
		true,  // httpOnly
	)
}

// ClearSessionCookie 登出时清除 cookie
func ClearSessionCookie(c *gin.Context) {
	c.SetCookie(sessionCookieName, "", -1, "/", "", false, true)
}

// parseSessionCookie 从请求里解析 JWT cookie，返回 Claims
func parseSessionCookie(c *gin.Context) (*Claims, error) {
	tokenStr, err := c.Cookie(sessionCookieName)
	if err != nil {
		return nil, errors.New("未登录")
	}

	claims := &Claims{}
	token, err := jwt.ParseWithClaims(tokenStr, claims, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("签名方法非法")
		}
		return jwtSecret(), nil
	})
	if err != nil || !token.Valid {
		return nil, errors.New("会话已过期，请重新登录")
	}
	return claims, nil
}

// SessionMiddleware 可选鉴权：把用户信息注入 context，不强制拦截
// 放在全局，让所有 handler 都能通过 c.Get("user_id") 取到用户信息
func SessionMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		claims, err := parseSessionCookie(c)
		if err == nil {
			c.Set(contextUserIDKey, claims.UserID)
			c.Set(contextUsernameKey, claims.Username)
			c.Set(contextIsAdminKey, claims.IsAdmin)
		}
		c.Next()
	}
}

// AuthRequired 强制鉴权中间件：未登录直接返回 401。
// 当前使用 SessionMiddleware 全局注入，handler 内用 getUserID 校验；
// 若后续需要对某个路由组统一强制鉴权，可在 router.go 中对该组使用此中间件：
//
//	adminRoutes := api.Group("/admin", middleware.AuthRequired())
func AuthRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		claims, err := parseSessionCookie(c)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			return
		}
		c.Set(contextUserIDKey, claims.UserID)
		c.Set(contextUsernameKey, claims.Username)
		c.Set(contextIsAdminKey, claims.IsAdmin)
		c.Next()
	}
}
