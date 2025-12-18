package utils

import (
	"time"
)

// BeijingLocation 北京时区
var BeijingLocation *time.Location

func init() {
	var err error
	BeijingLocation, err = time.LoadLocation("Asia/Shanghai")
	if err != nil {
		// 如果无法加载时区，使用固定偏移
		BeijingLocation = time.FixedZone("CST", 8*60*60)
	}
}

// GetBeijingTime 获取北京时间
func GetBeijingTime() time.Time {
	return time.Now().In(BeijingLocation)
}

// ToBeijingTime 转换为北京时间
func ToBeijingTime(t time.Time) time.Time {
	return t.In(BeijingLocation)
}
