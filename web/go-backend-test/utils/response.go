package utils

import (
	"net/http"

	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"github.com/gin-gonic/gin"
)

// SuccessResponse 返回成功响应
func SuccessResponse(c *gin.Context, code int, message string, data interface{}) {
	c.JSON(code, models.APIResponse{
		Code:    code,
		Message: message,
		Data:    data,
	})
}

// ErrorResponse 返回错误响应
func ErrorResponse(c *gin.Context, code int, message string, err string) {
	c.JSON(code, models.ErrorResponse{
		Code:    code,
		Message: message,
		Error:   err,
	})
}

// SuccessResponseOK 返回200成功响应
func SuccessResponseOK(c *gin.Context, message string, data interface{}) {
	SuccessResponse(c, http.StatusOK, message, data)
}

// SuccessResponseCreated 返回201创建成功响应
func SuccessResponseCreated(c *gin.Context, message string, data interface{}) {
	SuccessResponse(c, http.StatusCreated, message, data)
}

// ErrorResponseBadRequest 返回400错误响应
func ErrorResponseBadRequest(c *gin.Context, err string) {
	ErrorResponse(c, http.StatusBadRequest, "请求参数错误", err)
}

// ErrorResponseNotFound 返回404错误响应
func ErrorResponseNotFound(c *gin.Context, message string) {
	ErrorResponse(c, http.StatusNotFound, message, "")
}

// ErrorResponseServerError 返回500错误响应
func ErrorResponseServerError(c *gin.Context, err string) {
	ErrorResponse(c, http.StatusInternalServerError, "服务器内部错误", err)
}
