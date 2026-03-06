package app

import (
	"log"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/middleware"
	"github.com/Ling0727-ai/go-buct-course-backend/router"
	"github.com/Ling0727-ai/go-buct-course-backend/scheduler"
	"github.com/gin-gonic/gin"
)

func NewRouter(cfg *config.Config) *gin.Engine {
	// 初始化邮件配置
	config.LoadMailConfig()

	// ...existing code...
	if cfg.Debug {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// 创建路由
	r := gin.New()

	// 应用全局中间件
	r.Use(middleware.LoggingMiddleware())
	r.Use(middleware.CORSMiddleware())
	r.Use(middleware.RecoveryMiddleware())

	// 设置路由
	router.SetupRoutes(r)

	return r
}

func Start(cfg *config.Config) {
	// 启动定时调度器，对应 Python init_scheduler()
	s := scheduler.GetScheduler()
	s.Start()
	defer s.Stop()

	// 创建路由
	r := NewRouter(cfg)

	// 启动服务器
	log.Printf("服务器启动在 http://localhost%s (环境: %s)\n", cfg.Port, cfg.Env)
	if err := r.Run(cfg.Port); err != nil {
		log.Fatalf("服务器启动失败: %v", err)
	}
}
