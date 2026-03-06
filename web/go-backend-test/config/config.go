package config

import (
	"os"
	"strings"
)

type Config struct {
	Port  string
	Env   string
	Debug bool
}

var AppConfig *Config

func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = ":5000"
	}

	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}

	debug := env == "development"

	AppConfig = &Config{
		Port:  port,
		Env:   env,
		Debug: debug,
	}

	return AppConfig
}

// GetDBName 从 MONGODB_URI 解析数据库名，与 Python 保持一致
// URI 格式: mongodb://user:pass@host:port/dbname?authSource=admin
// 默认返回 "buct-course"（与 Python 后端一致）
func GetDBName() string {
	uri := os.Getenv("MONGODB_URI")
	if uri == "" {
		return "buct-course"
	}
	// 找最后一个 / 之后、? 之前的部分
	if idx := strings.LastIndex(uri, "/"); idx != -1 {
		dbPart := uri[idx+1:]
		if q := strings.Index(dbPart, "?"); q != -1 {
			dbPart = dbPart[:q]
		}
		if dbPart != "" {
			return dbPart
		}
	}
	return "buct-course"
}
