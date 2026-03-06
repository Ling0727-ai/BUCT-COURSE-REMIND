package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// ============ 基础处理函数 ============

func HealthCheckBasic(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "ok",
	})
}

func Ping(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "pong",
	})
}

// ============ 用户处理函数 ============

func GetUsers(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"data": []map[string]interface{}{},
	})
}

func GetUser(c *gin.Context) {
	id := c.Param("id")
	c.JSON(http.StatusOK, gin.H{
		"id": id,
	})
}

func CreateUser(c *gin.Context) {
	var json map[string]interface{}
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": err.Error(),
		})
		return
	}
	c.JSON(http.StatusCreated, gin.H{
		"message": "用户创建成功",
	})
}

func UpdateUser(c *gin.Context) {
	id := c.Param("id")
	var json map[string]interface{}
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": err.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"id":      id,
		"message": "用户更新成功",
	})
}

func DeleteUser(c *gin.Context) {
	id := c.Param("id")
	c.JSON(http.StatusOK, gin.H{
		"id":      id,
		"message": "用户删除成功",
	})
}

// ============ 课程处理函数 ============

func GetCourses(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"data": []map[string]interface{}{},
	})
}

func GetCourse(c *gin.Context) {
	id := c.Param("id")
	c.JSON(http.StatusOK, gin.H{
		"id": id,
	})
}

func CreateCourse(c *gin.Context) {
	var json map[string]interface{}
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": err.Error(),
		})
		return
	}
	c.JSON(http.StatusCreated, gin.H{
		"message": "课程创建成功",
	})
}
