package scraper

import (
	"errors"
	"fmt"
	"regexp"
	"time"
)

// 错误定义
var (
	ErrNotLoggedIn = errors.New("请先登录")
	ErrLoginFailed = errors.New("登录失败，请检查用户名和密码")
	ErrNetwork     = errors.New("网络请求错误")
	ErrParse       = errors.New("解析错误")
)

// HomeworkWithCourse 带课程信息的作业
type HomeworkWithCourse struct {
	HomeworkInfo
	CourseName string `json:"course_name"`
	LID        string `json:"lid"`
}

// TestWithCourse 带课程信息的测试
type TestWithCourse struct {
	TestInfo
	CourseName string `json:"course_name"`
	LID        string `json:"lid"`
}

// PendingTasksResult 待办任务结果
type PendingTasksResult struct {
	Success bool             `json:"success"`
	Data    PendingTasksData `json:"data"`
	Message string           `json:"message,omitempty"`
}

// PendingTasksData 待办任务数据
type PendingTasksData struct {
	Homework []HomeworkWithCourse `json:"homework"`
	Tests    []TestWithCourse     `json:"tests"`
	Stats    TasksStats           `json:"stats"`
}

// TasksStats 任务统计
type TasksStats struct {
	HomeworkCount int `json:"homework_count"`
	TestsCount    int `json:"tests_count"`
	TotalCount    int `json:"total_count"`
}

// Assignment 作业结构（用于存储到数据库）
type Assignment struct {
	ID            string `json:"id" bson:"id"`
	Title         string `json:"title" bson:"title"`
	CourseName    string `json:"course_name" bson:"course_name"`
	CourseID      string `json:"course_id" bson:"course_id"`
	Deadline      string `json:"deadline" bson:"deadline"`
	DeadlineDate  string `json:"deadline_date,omitempty" bson:"deadline_date,omitempty"`
	Type          string `json:"type" bson:"type"` // homework 或 test
	Status        string `json:"status" bson:"status"`
	Score         string `json:"score,omitempty" bson:"score,omitempty"`
	Publisher     string `json:"publisher,omitempty" bson:"publisher,omitempty"`
	Description   string `json:"description,omitempty" bson:"description,omitempty"` // 作业详细描述
	CanSubmit     bool   `json:"can_submit" bson:"can_submit"`
	DetailHref    string `json:"detail_href,omitempty" bson:"detail_href,omitempty"`
	SubmitHref    string `json:"submit_href,omitempty" bson:"submit_href,omitempty"`
	TimeRemaining string `json:"time_remaining,omitempty" bson:"time_remaining,omitempty"`
	IsUrgent      bool   `json:"is_urgent" bson:"is_urgent"`
	IsGroup       bool   `json:"is_group" bson:"is_group"`
}

// ConvertToAssignments 将爬取的数据转换为Assignment格式
func ConvertToAssignments(homeworkDetails []CourseDetails) []Assignment {
	var assignments []Assignment

	for _, course := range homeworkDetails {
		for _, hw := range course.HomeworkList {
			// 将中文日期转换为 ISO 格式
			isoDeadline := convertChineseDateToISO(hw.Deadline)

			assignment := Assignment{
				ID:            generateAssignmentID(course.LID, hw.HWTID),
				Title:         hw.Title,
				CourseName:    course.CourseName,
				CourseID:      course.LID,
				Deadline:      isoDeadline, // 使用 ISO 格式
				DeadlineDate:  isoDeadline, // 同时设置 deadline_date
				Type:          "homework",
				Status:        hw.Status,
				Score:         hw.Score,
				Publisher:     hw.Publisher,
				Description:   hw.Description, // 作业详细描述
				CanSubmit:     hw.CanSubmit,
				DetailHref:    hw.DetailHref,
				SubmitHref:    hw.SubmitHref,
				TimeRemaining: hw.TimeRemaining,
				IsUrgent:      hw.IsUrgent,
				IsGroup:       hw.IsGroup,
			}

			// 如果状态为空，根据是否可提交设置
			if assignment.Status == "" {
				if hw.CanSubmit {
					assignment.Status = "未提交"
				} else if hw.Score != "" {
					assignment.Status = "已完成"
				} else {
					assignment.Status = "已过期"
				}
			}

			assignments = append(assignments, assignment)
		}
	}

	return assignments
}

// convertChineseDateToISO 将中文日期格式转换为 ISO 格式
// 输入: 2025年12月23日 12:59:00
// 输出: 2025-12-23T12:59:00
func convertChineseDateToISO(chineseDate string) string {
	if chineseDate == "" {
		return ""
	}

	// 匹配中文日期格式
	re := regexp.MustCompile(`(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{1,2}):(\d{1,2})`)
	matches := re.FindStringSubmatch(chineseDate)
	if len(matches) < 7 {
		// 如果无法匹配，尝试解析为已有的 ISO 格式
		if _, err := time.Parse(time.RFC3339, chineseDate); err == nil {
			return chineseDate
		}
		return chineseDate // 返回原值
	}

	// 转换为 ISO 格式
	return fmt.Sprintf("%s-%02s-%02sT%02s:%02s:%02s",
		matches[1], matches[2], matches[3], matches[4], matches[5], matches[6])
}

// ConvertTestsToAssignments 将测试数据转换为Assignment格式
func ConvertTestsToAssignments(testDetails []TestDetails) []Assignment {
	var assignments []Assignment

	for _, course := range testDetails {
		for _, test := range course.TestList {
			// 将日期转换为 ISO 格式
			isoDeadline := convertChineseDateToISO(test.EndTime)

			assignment := Assignment{
				ID:           generateAssignmentID(course.LID, test.TestID),
				Title:        test.Title,
				CourseName:   course.CourseName,
				CourseID:     course.LID,
				Deadline:     isoDeadline, // 使用 ISO 格式
				DeadlineDate: isoDeadline,
				Type:         "test",
				Status:       test.Status,
				CanSubmit:    test.CanStart,
				DetailHref:   test.TestLink,
				SubmitHref:   test.TestLink,
			}

			assignments = append(assignments, assignment)
		}
	}

	return assignments
}

// generateAssignmentID 生成作业ID
func generateAssignmentID(courseID, itemID string) string {
	if itemID != "" {
		return courseID + "_" + itemID
	}
	return courseID
}
