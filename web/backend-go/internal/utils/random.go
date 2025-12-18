package utils

import (
	"math/rand"
	"time"
)

const (
	letters       = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	digits        = "0123456789"
	alphanumeric  = letters + digits
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

// GenerateVerificationCode 生成验证码
func GenerateVerificationCode(length int) string {
	if length <= 0 {
		length = 6
	}
	
	code := make([]byte, length)
	for i := range code {
		code[i] = digits[rand.Intn(len(digits))]
	}
	return string(code)
}

// GenerateRandomString 生成随机字符串
func GenerateRandomString(length int) string {
	if length <= 0 {
		length = 32
	}
	
	result := make([]byte, length)
	for i := range result {
		result[i] = alphanumeric[rand.Intn(len(alphanumeric))]
	}
	return string(result)
}
