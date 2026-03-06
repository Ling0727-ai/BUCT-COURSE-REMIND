package main

import (
	"github.com/Ling0727-ai/go-buct-course-backend/app"
	"github.com/Ling0727-ai/go-buct-course-backend/config"
)

func main() {
	// 加载配置
	cfg := config.LoadConfig()

	// 启动应用
	app.Start(cfg)
}
