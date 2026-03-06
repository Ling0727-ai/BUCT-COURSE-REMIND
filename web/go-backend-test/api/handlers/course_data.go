package handlers

import (
	"net/http"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/models/CourseData"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/gin-gonic/gin"
)

// RefreshCourseData 手动刷新课程数据
// 对应 Python POST /api/course-data/refresh
func RefreshCourseData(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	services.RefreshUserDataAsync(userID)

	c.JSON(http.StatusOK, gin.H{
		"success":    true,
		"message":    "数据刷新已在后台启动",
		"updated_at": time.Now().Format(time.RFC3339),
	})
}

// GetCourseDataList 从数据库获取课程数据列表
// 对应 Python GET /api/course-data/list
func GetCourseDataList(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	tasks, err := CourseData.Repository.GetCourseDataByUserID(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取数据失败"})
		return
	}

	lastUpdate, _ := CourseData.Repository.GetLastUpdateTimeByUserID(userID)

	var lastUpdateStr interface{} = nil
	if lastUpdate > 0 {
		lastUpdateStr = time.Unix(lastUpdate, 0).Format(time.RFC3339)
	}

	c.JSON(http.StatusOK, gin.H{
		"success":     true,
		"tasks":       tasks,
		"total":       len(tasks),
		"last_update": lastUpdateStr,
		"source":      "database",
	})
}

// GetCourseDataStatus 获取数据状态（最后更新时间、下次刷新时间）
// 对应 Python GET /api/course-data/status
func GetCourseDataStatus(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	lastUpdate, _ := CourseData.Repository.GetLastUpdateTimeByUserID(userID)
	hasData := lastUpdate > 0

	var lastUpdateStr, nextRefreshStr interface{} = nil, nil
	var hoursUntilRefresh interface{} = nil

	if hasData {
		lastUpdateStr = time.Unix(lastUpdate, 0).Format(time.RFC3339)
		nextRefresh := time.Unix(lastUpdate, 0).Add(12 * time.Hour)
		nextRefreshStr = nextRefresh.Format(time.RFC3339)
		h := time.Until(nextRefresh).Hours()
		if h < 0 {
			h = 0
		}
		hoursUntilRefresh = h
	}

	c.JSON(http.StatusOK, gin.H{
		"success":             true,
		"has_data":            hasData,
		"last_update":         lastUpdateStr,
		"next_auto_refresh":   nextRefreshStr,
		"hours_until_refresh": hoursUntilRefresh,
	})
}
