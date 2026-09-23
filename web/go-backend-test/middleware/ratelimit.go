package middleware

import (
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

// 登录/注册等敏感接口的固定窗口限流。
// 之前只有验证码发送有频率限制，Login 完全没有任何限制，
// 攻击者可以对单个账号做无限次密码爆破。

type rateEntry struct {
	count       int
	windowStart time.Time
}

type rateLimiter struct {
	mu      sync.Mutex
	entries map[string]*rateEntry
	limit   int
	window  time.Duration
}

// allow 返回是否放行，以及建议的 Retry-After 秒数
func (r *rateLimiter) allow(key string) (bool, int) {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()
	e, ok := r.entries[key]
	if !ok || now.Sub(e.windowStart) >= r.window {
		r.entries[key] = &rateEntry{count: 1, windowStart: now}
		return true, 0
	}

	if e.count >= r.limit {
		retry := int((r.window - now.Sub(e.windowStart)).Seconds())
		if retry < 1 {
			retry = 1
		}
		return false, retry
	}

	e.count++
	return true, 0
}

// gc 清理过期条目，避免 map 无限增长
func (r *rateLimiter) gc() {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()
	for k, e := range r.entries {
		if now.Sub(e.windowStart) >= r.window {
			delete(r.entries, k)
		}
	}
}

// RateLimit 返回一个按客户端 IP 计数的固定窗口限流中间件。
// limit 为窗口内允许的请求数，window 为窗口长度。
func RateLimit(limit int, window time.Duration) gin.HandlerFunc {
	rl := &rateLimiter{
		entries: make(map[string]*rateEntry),
		limit:   limit,
		window:  window,
	}

	// 后台定期清理，防止被大量不同 IP 撑爆内存
	go func() {
		ticker := time.NewTicker(window)
		defer ticker.Stop()
		for range ticker.C {
			rl.gc()
		}
	}()

	return func(c *gin.Context) {
		key := c.ClientIP()
		if key == "" {
			key = "unknown"
		}

		ok, retry := rl.allow(key)
		if !ok {
			c.Header("Retry-After", itoa(retry))
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"error":       "请求过于频繁，请稍后再试",
				"retry_after": retry,
			})
			return
		}

		c.Next()
	}
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	neg := n < 0
	if neg {
		n = -n
	}
	var buf [20]byte
	i := len(buf)
	for n > 0 {
		i--
		buf[i] = byte('0' + n%10)
		n /= 10
	}
	if neg {
		i--
		buf[i] = '-'
	}
	return string(buf[i:])
}
