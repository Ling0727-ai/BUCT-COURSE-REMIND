package handlers

import (
	"net/http"

	"github.com/Ling0727-ai/go-buct-course-backend/models/Blacklist"
	"github.com/gin-gonic/gin"
)

// GetBlacklist 获取用户黑名单列表
// GET /api/blacklist/
func GetBlacklist(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	list, err := Blacklist.Repository.GetBlacklist(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取黑名单失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "blacklist": list, "count": len(list)})
}

// AddBlacklist 添加科目到黑名单
// POST /api/blacklist/  body: { "subject_id": "12345" }
func AddBlacklist(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	var body struct {
		SubjectID string `json:"subject_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "subject_id 不能为空"})
		return
	}

	if err := Blacklist.Repository.AddSubject(userID, body.SubjectID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "添加失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "已加入黑名单"})
}

// RemoveBlacklist 从黑名单移除科目
// DELETE /api/blacklist/:subject_id
func RemoveBlacklist(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	subjectID := c.Param("subject_id")
	if subjectID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "subject_id 不能为空"})
		return
	}

	if err := Blacklist.Repository.RemoveSubject(userID, subjectID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "移除失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "已从黑名单移除"})
}

// ClearBlacklist 清空用户黑名单
// DELETE /api/blacklist/
func ClearBlacklist(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	if err := Blacklist.Repository.ClearBlacklist(userID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "清空失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "黑名单已清空"})
}
