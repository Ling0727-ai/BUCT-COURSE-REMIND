package router

import (
	"github.com/Ling0727-ai/go-buct-course-backend/api/handlers"
	"github.com/gin-gonic/gin"
)

func SetupRoutes(router *gin.Engine) {
	// 健康检查路由（含 DB + 邮件状态检查）
	router.GET("/health", handlers.HealthCheck)

	// API v1 路由组
	v1 := router.Group("/api/v1")
	{
		v1.GET("/ping", handlers.Ping)

		// ── 认证路由，对应 Python /api/auth ──
		authRoutes := v1.Group("/auth")
		{
			authRoutes.POST("/login", handlers.Login)
			authRoutes.POST("/logout", handlers.Logout)
			authRoutes.POST("/register", handlers.Register)
			authRoutes.GET("/status", handlers.AuthStatus)
			authRoutes.GET("/user-info", handlers.GetUserInfo)
			authRoutes.POST("/update-email", handlers.UpdateEmail)
			authRoutes.POST("/update-student-info", handlers.UpdateStudentInfo)
			authRoutes.POST("/check-email", handlers.CheckEmail)
			authRoutes.POST("/reset-password", handlers.ResetPassword)
			authRoutes.POST("/send-verification-code", handlers.SendVerificationCode)
			authRoutes.POST("/verify-code", handlers.VerifyCode)
		}

		// ── 用户路由 ──
		userRoutes := v1.Group("/users")
		{
			userRoutes.GET("", handlers.GetUsers)
			userRoutes.GET("/:id", handlers.GetUser)
			userRoutes.POST("", handlers.CreateUser)
			userRoutes.PUT("/:id", handlers.UpdateUser)
			userRoutes.DELETE("/:id", handlers.DeleteUser)
		}

		// ── 作业路由，对应 Python /api/assignments ──
		assignRoutes := v1.Group("/assignments")
		{
			assignRoutes.GET("", handlers.GetAssignments)
			assignRoutes.GET("/stats", handlers.GetAssignmentStats)
			assignRoutes.GET("/completed", handlers.GetCompletedAssignments)
			assignRoutes.GET("/deleted", handlers.GetDeletedAssignments)
			assignRoutes.DELETE("/clear-deleted", handlers.ClearDeletedAssignments)
			assignRoutes.POST("/:id/complete", handlers.MarkAssignmentComplete)
			assignRoutes.POST("/:id/uncomplete", handlers.MarkAssignmentUncomplete)
			assignRoutes.POST("/:id/delete", handlers.DeleteAssignment)
			assignRoutes.POST("/:id/restore", handlers.RestoreAssignment)
			assignRoutes.DELETE("/:id/permanent-delete", handlers.PermanentDeleteAssignment)
			assignRoutes.POST("/:id/remind", handlers.RemindAssignment)
		}

		// ── 课程数据路由，对应 Python /api/course-data ──
		courseRoutes := v1.Group("/course-data")
		{
			courseRoutes.GET("/list", handlers.GetCourseDataList)
			courseRoutes.GET("/status", handlers.GetCourseDataStatus)
			courseRoutes.POST("/refresh", handlers.RefreshCourseData)
		}

		// ── 待办路由，对应 Python /api/todos ──
		todoRoutes := v1.Group("/todos")
		{
			todoRoutes.GET("", handlers.GetTodos)
			todoRoutes.POST("", handlers.CreateTodo)
			todoRoutes.GET("/stats", handlers.GetTodoStats)
			todoRoutes.GET("/deleted", handlers.GetDeletedTodos)
			todoRoutes.DELETE("/clear-deleted", handlers.ClearDeletedTodos)
			todoRoutes.PUT("/:id", handlers.UpdateTodo)
			todoRoutes.POST("/:id/complete", handlers.CompleteTodo)
			todoRoutes.POST("/:id/uncomplete", handlers.UncompleteTodo)
			todoRoutes.POST("/:id/remind", handlers.RemindTodo)
			todoRoutes.POST("/:id/delete", handlers.DeleteTodo)
			todoRoutes.POST("/:id/restore", handlers.RestoreTodo)
			todoRoutes.DELETE("/:id/permanent-delete", handlers.PermanentDeleteTodo)
		}

		// ── 提醒路由，对应 Python /api/webhooks ──
		reminderRoutes := v1.Group("/reminders")
		{
			reminderRoutes.GET("", handlers.GetReminders)
			reminderRoutes.POST("", handlers.CreateReminder)
			reminderRoutes.DELETE("/:id", handlers.DeleteReminder)
			reminderRoutes.POST("/manual", handlers.ManualReminder)
			reminderRoutes.POST("/test", handlers.TestReminder)
		}

		// ── 设置路由，对应 Python /api/settings ──
		v1.GET("/settings", handlers.GetSettings)
		v1.POST("/settings", handlers.SaveSettings)
		v1.GET("/settings/email", handlers.GetEmailSettings)
		v1.POST("/settings/email", handlers.SaveEmailSettings)

		// ── 全局统计，对应 Python GET /api/stats ──
		v1.GET("/stats", handlers.GetStats)

		// ── 测试路由，对应 Python /api/test（无需登录，调试用）──
		testRoutes := v1.Group("/test")
		{
			testRoutes.POST("/send-test-email", handlers.SendTestEmail)
			testRoutes.POST("/verify-test-code", handlers.VerifyTestCode)
			testRoutes.GET("/config", handlers.GetTestConfig)
		}

		// ── 管理员路由，对应 Python /api/admin ──
		adminRoutes := v1.Group("/admin")
		{
			adminRoutes.POST("/cleanup/trigger", handlers.AdminTriggerCleanup)
			adminRoutes.GET("/completed-assignments", handlers.AdminGetCompletedAssignments)
			adminRoutes.GET("/system/status", handlers.AdminGetSystemStatus)
		}

		// ── 加密路由，对应 Python /api/crypto ──
		cryptoRoutes := v1.Group("/crypto")
		{
			cryptoRoutes.GET("/public-key", handlers.GetPublicKey)
			cryptoRoutes.GET("/challenge", handlers.GetChallenge)
			cryptoRoutes.GET("/status", handlers.GetCryptoStatus)
		}
	}
}
