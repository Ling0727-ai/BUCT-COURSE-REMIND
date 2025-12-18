package config

import (
	"os"
	"strconv"
	"strings"
)

// Config 应用配置
type Config struct {
	// JWT密钥
	SecretKey string

	// MongoDB连接URI
	MongoURI string

	// 服务器端口
	Port string

	// 验证码配置
	CaptchaExpireTime int

	// 邮件配置
	MailSMTPServer   string
	MailSMTPPort     int
	MailSender       string
	MailPassword     string
	VerifyCodeExpire int

	// CORS配置
	CORSAllowedOrigins     []string
	CORSRefreshIntervalHrs int

	// ECC密钥配置
	ECCPrivateKey string
	ECCPublicKey  string
}

// Load 加载配置
func Load() *Config {
	cfg := &Config{
		SecretKey:              getEnv("SECRET_KEY", "dev_secret_key_for_jwt"),
		MongoURI:               getEnv("MONGO_URI", "mongodb://localhost:27017/buct-course"),
		Port:                   getEnv("PORT", "5000"),
		CaptchaExpireTime:      getEnvInt("CAPTCHA_EXPIRE_TIME", 300),
		MailSMTPServer:         getEnv("MAIL_SMTP_SERVER", "smtp.163.com"),
		MailSMTPPort:           getEnvInt("MAIL_SMTP_PORT", 465),
		MailSender:             getEnv("MAIL_SENDER", "buct_course_remind@163.com"),
		MailPassword:           getEnv("MAIL_PASSWORD", "dummy_password_for_dev"),
		VerifyCodeExpire:       getEnvInt("VERIFY_CODE_EXPIRE", 180),
		CORSRefreshIntervalHrs: getEnvInt("CORS_REFRESH_INTERVAL_HOURS", 6),
		ECCPrivateKey:          getEnv("ECC_PRIVATE_KEY", ""),
		ECCPublicKey:           getEnv("ECC_PUBLIC_KEY", ""),
	}

	// 解析CORS允许的来源
	corsOrigins := getEnv("CORS_ALLOWED_ORIGINS", "http://localhost:8080")
	cfg.CORSAllowedOrigins = strings.Split(corsOrigins, ",")
	for i := range cfg.CORSAllowedOrigins {
		cfg.CORSAllowedOrigins[i] = strings.TrimSpace(cfg.CORSAllowedOrigins[i])
	}

	return cfg
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intVal, err := strconv.Atoi(value); err == nil {
			return intVal
		}
	}
	return defaultValue
}

// GlobalConfig 全局配置实例
var GlobalConfig *Config

func init() {
	GlobalConfig = Load()
}
