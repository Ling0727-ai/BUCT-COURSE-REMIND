package handlers

import (
	"github.com/Ling0727-ai/go-buct-course-backend/models/Blacklist"
	"github.com/Ling0727-ai/go-buct-course-backend/utils"
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
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"success": false, "error": utils.Defaults.Blacklist.GetSuccess})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{"success": true, "blacklist": list, "count": len(list)})
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
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"success": false, "error": utils.Defaults.Blacklist.SubjectIDEmpty})
		return
	}

	if err := Blacklist.Repository.AddSubject(userID, body.SubjectID); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"success": false, "error": utils.Defaults.Data.CreateFailed})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{"success": true, "message": utils.Defaults.Blacklist.AddSuccess})
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
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"success": false, "error": utils.Defaults.Blacklist.SubjectIDEmpty})
		return
	}

	if err := Blacklist.Repository.RemoveSubject(userID, subjectID); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"success": false, "error": utils.Defaults.Data.DeleteFailed})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{"success": true, "message": utils.Defaults.Blacklist.RemoveSuccess})
}

// ClearBlacklist 清空用户黑名单
// DELETE /api/blacklist/
func ClearBlacklist(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	if err := Blacklist.Repository.ClearBlacklist(userID); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"success": false, "error": utils.Defaults.Data.ClearFailed})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{"success": true, "message": utils.Defaults.Blacklist.ClearSuccess})
}
