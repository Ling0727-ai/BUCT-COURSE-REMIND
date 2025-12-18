package main

import (
	"log"
	"os"

	"buct-course-remind/internal/config"
	"buct-course-remind/internal/database"
	"buct-course-remind/internal/routes"
	"buct-course-remind/internal/scheduler"

	"github.com/gin-contrib/cors"
	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// 加载环境变量
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// 加载配置
	cfg := config.Load()

	// 连接数据库
	if err := database.Connect(cfg.MongoURI); err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer database.Disconnect()

	// 创建Gin引擎
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}
	r := gin.Default()

	// 配置Session
	store := cookie.NewStore([]byte(cfg.SecretKey))
	store.Options(sessions.Options{
		Path:     "/",
		HttpOnly: true,
		SameSite: 2, // Lax
		MaxAge:   86400 * 7,
	})
	r.Use(sessions.Sessions("session", store))

	// 配置CORS
	corsConfig := cors.Config{
		AllowOrigins:     cfg.CORSAllowedOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
	}
	r.Use(cors.New(corsConfig))

	// 注册路由
	routes.RegisterRoutes(r)

	// 初始化调度器
	scheduler.InitScheduler()

	// 启动服务器
	port := cfg.Port
	if port == "" {
		port = "5000"
	}

	log.Printf("Server starting on port %s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
