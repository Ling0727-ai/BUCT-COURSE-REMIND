package routes

import (
	"buct-course-remind/internal/handlers"
	"buct-course-remind/internal/middleware"

	"github.com/gin-gonic/gin"
)

// RegisterRoutes 注册所有路由
func RegisterRoutes(r *gin.Engine) {
	// 健康检查（无需认证）- 支持 GET 和 HEAD 方法
	healthHandler := handlers.NewHealthHandler()
	r.GET("/health", healthHandler.Health)
	r.HEAD("/health", healthHandler.Health)
	r.GET("/api/health", healthHandler.Health)
	r.HEAD("/api/health", healthHandler.Health)
	r.GET("/api/health/detailed", healthHandler.DetailedHealth)

	// 加密相关（无需认证）
	cryptoHandler := handlers.NewCryptoHandler()
	r.GET("/api/crypto/public-key", cryptoHandler.GetPublicKey)
	r.POST("/api/crypto/test-decrypt", cryptoHandler.TestDecrypt)

	// 认证相关
	authHandler := handlers.NewAuthHandler()
	authGroup := r.Group("/api/auth")
	{
		authGroup.POST("/login", authHandler.Login)
		authGroup.POST("/logout", authHandler.Logout)
		authGroup.GET("/status", authHandler.Status)
		authGroup.POST("/send-code", authHandler.SendVerificationCode)
		authGroup.POST("/send-verification-code", authHandler.SendVerificationCode) // 前端兼容
		authGroup.POST("/verify-code", authHandler.VerifyCode)                       // 验证验证码
		authGroup.POST("/register", authHandler.Register)
		authGroup.POST("/forgot-password", authHandler.ForgotPassword)
		authGroup.POST("/reset-password", authHandler.ForgotPassword) // 前端兼容别名
		authGroup.POST("/check-email", authHandler.CheckEmail)        // 检查邮箱是否存在
		
		// 需要登录
		authGroup.GET("/profile", middleware.LoginRequired(), authHandler.GetProfile)
		authGroup.GET("/user-info", middleware.LoginRequired(), authHandler.GetProfile)                      // 前端兼容别名
		authGroup.POST("/update-credentials", middleware.LoginRequired(), authHandler.UpdateStudentCredentials)
		authGroup.POST("/update-student-info", middleware.LoginRequired(), authHandler.UpdateStudentCredentials) // 前端兼容别名
		authGroup.POST("/update-email", middleware.LoginRequired(), authHandler.UpdateEmail)
	}

	// 课程数据相关（需要登录）
	courseDataHandler := handlers.NewCourseDataHandler()
	courseDataGroup := r.Group("/api/course-data")
	courseDataGroup.Use(middleware.LoginRequired())
	{
		courseDataGroup.GET("/status", courseDataHandler.GetStatus)
		courseDataGroup.POST("/refresh", courseDataHandler.Refresh)
	}

	// 作业相关（需要登录）
	assignmentsHandler := handlers.NewAssignmentsHandler()
	assignmentsGroup := r.Group("/api/assignments")
	assignmentsGroup.Use(middleware.LoginRequired())
	{
		assignmentsGroup.GET("/standard", assignmentsHandler.GetStandardAssignments)
		assignmentsGroup.GET("/completed", assignmentsHandler.GetCompletedAssignments)
		assignmentsGroup.POST("/:id/complete", assignmentsHandler.MarkAssignmentComplete)
		assignmentsGroup.POST("/:id/uncomplete", assignmentsHandler.MarkAssignmentUncomplete)
		assignmentsGroup.DELETE("/:id", assignmentsHandler.DeleteAssignment)
		assignmentsGroup.POST("/:id/delete", assignmentsHandler.DeleteAssignment) // 前端兼容（POST 方式删除）
		assignmentsGroup.POST("/:id/restore", assignmentsHandler.RestoreAssignment)
		assignmentsGroup.POST("/:id/permanent-delete", assignmentsHandler.PermanentDeleteAssignment)
		assignmentsGroup.POST("/:id/remind", assignmentsHandler.RemindAssignment) // 提醒作业
		assignmentsGroup.GET("/deleted", assignmentsHandler.GetDeletedAssignments)
		assignmentsGroup.POST("/refresh", assignmentsHandler.RefreshAssignments)
		assignmentsGroup.POST("/refresh-sync", assignmentsHandler.RefreshAssignmentsSync)
	}

	// 待办事项（需要登录）
	todosHandler := handlers.NewTodosHandler()
	todosGroup := r.Group("/api/todos")
	todosGroup.Use(middleware.LoginRequired())
	{
		todosGroup.GET("/", todosHandler.GetTodos)
		todosGroup.POST("/", todosHandler.CreateTodo)
		todosGroup.PUT("/:id", todosHandler.UpdateTodo)
		todosGroup.DELETE("/:id", todosHandler.DeleteTodo)
		todosGroup.POST("/:id/delete", todosHandler.DeleteTodo) // 前端兼容（POST 方式删除）
		todosGroup.POST("/:id/complete", todosHandler.CompleteTodo)
		todosGroup.POST("/:id/uncomplete", todosHandler.UncompleteTodo)
		todosGroup.GET("/deleted", todosHandler.GetDeletedTodos)
		todosGroup.POST("/:id/restore", todosHandler.RestoreTodo)
		todosGroup.POST("/:id/permanent-delete", todosHandler.PermanentDeleteTodo)
	}

	// 提醒相关（需要登录）
	reminderHandler := handlers.NewReminderHandler()
	reminderGroup := r.Group("/api/reminders")
	reminderGroup.Use(middleware.LoginRequired())
	{
		reminderGroup.GET("/", reminderHandler.GetReminders)
		reminderGroup.POST("/", reminderHandler.CreateReminder)
		reminderGroup.DELETE("/:id", reminderHandler.DeleteReminder)
		reminderGroup.POST("/test", reminderHandler.SendTestReminder)
	}

	// 设置
	settingsHandler := handlers.NewSettingsHandler()
	settingsGroup := r.Group("/api/settings")
	settingsGroup.Use(middleware.LoginRequired())
	{
		settingsGroup.GET("", settingsHandler.GetSettings)
		settingsGroup.POST("", settingsHandler.SaveSettings)
		settingsGroup.GET("/email", settingsHandler.GetEmailSettings)
		settingsGroup.POST("/email", settingsHandler.SaveEmailSettings)
	}

	// 用户设置
	userSettingsHandler := handlers.NewUserSettingsHandler()
	r.GET("/api/user/settings", middleware.LoginRequired(), userSettingsHandler.GetUserSettings)
	r.POST("/api/user/settings", middleware.LoginRequired(), userSettingsHandler.SaveUserSettings)

	// 管理员相关（需要登录 + 管理员权限）
	adminHandler := handlers.NewAdminHandler()
	adminGroup := r.Group("/api/admin")
	adminGroup.Use(middleware.LoginRequired(), middleware.AdminRequired())
	{
		adminGroup.GET("/users", adminHandler.GetUsers)
		adminGroup.GET("/users/:id", adminHandler.GetUserDetail)
		adminGroup.PUT("/users/:id", adminHandler.UpdateUser)
		adminGroup.DELETE("/users/:id", adminHandler.DeleteUser)
		adminGroup.GET("/stats", adminHandler.GetSystemStats)
	}
}
