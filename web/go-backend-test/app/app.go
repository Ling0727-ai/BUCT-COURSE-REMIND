package app

import (
	"log"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
	"github.com/Ling0727-ai/go-buct-course-backend/middleware"
	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"github.com/Ling0727-ai/go-buct-course-backend/models/AssignmentStatus"
	"github.com/Ling0727-ai/go-buct-course-backend/models/CourseData"
	"github.com/Ling0727-ai/go-buct-course-backend/models/Reminder"
	"github.com/Ling0727-ai/go-buct-course-backend/models/Todo"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/router"
	"github.com/Ling0727-ai/go-buct-course-backend/scheduler"
	"github.com/gin-gonic/gin"
)

func NewRouter(cfg *config.Config) *gin.Engine {
	config.LoadMailConfig()

	if cfg.Debug {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()
	r.Use(middleware.LoggingMiddleware())
	r.Use(middleware.CORSMiddleware())
	r.Use(middleware.RecoveryMiddleware())
	r.Use(middleware.SessionMiddleware())

	router.SetupRoutes(r)
	return r
}

func Start(cfg *config.Config) {
	// 1. 初始化 Snowflake ID 生成器
	sfGen, err := config.NewSnowflakeGenerator()
	if err != nil {
		log.Fatalf("[snowflake] 初始化失败: %v", err)
	}
	config.Snowflake = sfGen
	log.Println("[snowflake] ID 生成器已就绪")

	// 2. 预热 MongoDB 连接池
	client, err := models.ConnectToDB()
	if err != nil {
		log.Fatalf("[db] 无法连接 MongoDB: %v", err)
	}
	defer models.DisconnectDB()

	// 3. 初始化所有 model 包（绑定 collection，避免 nil pointer panic）
	db := client.Database("buct-course")
	User.Init(db)
	CourseData.Init(db)
	AssignmentStatus.Init(db)
	Todo.Init(db)
	Reminder.Init(db)
	log.Println("[app] 所有 Repository 已初始化")

	// 4. 预生成 RSA 密钥对（服务启动时完成，避免第一次请求时阻塞）
	rsaSvc := crypto.GetRSAService()
	if rsaSvc.IsEnabled() {
		log.Println("[rsa] 正在预生成 RSA 密钥对...")
		if err := rsaSvc.GenerateKeyPair(); err != nil {
			log.Printf("[rsa] 密钥生成失败（RSA 功能将不可用）: %v", err)
		} else {
			log.Println("[rsa] RSA 密钥对已就绪")
		}
	}

	// 5. 启动定时调度器
	s := scheduler.GetScheduler()
	s.Start()
	defer s.Stop()

	// 6. 启动 HTTP 服务
	r := NewRouter(cfg)
	log.Printf("服务器启动在 http://localhost%s (环境: %s)\n", cfg.Port, cfg.Env)
	if err := r.Run(cfg.Port); err != nil {
		log.Fatalf("服务器启动失败: %v", err)
	}
}
