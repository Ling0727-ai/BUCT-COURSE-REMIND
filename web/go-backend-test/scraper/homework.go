package scraper

import (
	"fmt"
	"log"
	"strings"

	buct "github.com/Ling0727-ai/go-buct-course/client"
)

// scrapeHomework 获取用户所有待提交作业，对应 Python get_pending_tasks 中 2.1 部分
func scrapeHomework(c *buct.BUCTClient, userID string) ([]TaskInfo, error) {
	log.Printf("[scraper] 用户 %s 开始获取作业...", userID)

	hwDetails, err := c.CourseMgr.GetAllPendingHomeworkDetails()
	if err != nil {
		log.Printf("[scraper] 用户 %s 获取作业数据失败: %v", userID, err)
		return nil, nil // 对应 Python: homework_courses = []
	}

	var tasks []TaskInfo

	for _, courseDetail := range hwDetails {
		lid := courseDetail.LID
		courseName := courseDetail.CourseName

		for _, hw := range courseDetail.HomeworkList {
			if !hw.CanSubmit {
				continue
			}

			// 获取作业详情文本
			detailsText := ""
			if hw.HwTID != "" {
				hwDetail, err := c.CourseMgr.GetHomeworkDetail(hw.HwTID)
				if err != nil {
					log.Printf("[scraper] 获取作业详情失败 (hwtid=%s): %v", hw.HwTID, err)
					detailsText = hw.Title
				} else if hwDetail != nil {
					// 拼接描述和任务内容，对应 Python: ''.join(tasks)
					parts := []string{}
					if hwDetail.Description != "" {
						parts = append(parts, hwDetail.Description)
					}
					for _, t := range hwDetail.Tasks {
						parts = append(parts, t)
					}
					detailsText = strings.Join(parts, "")
				}
			}

			// 格式化截止时间，对应 Python: _format_deadline
			deadline := formatDeadline(hw.Deadline)

			// 生成作业链接，对应 Python 中 homework_url
			hwURL := fmt.Sprintf(
				"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId=%s",
				lid,
			)

			tasks = append(tasks, TaskInfo{
				Subject:  courseName,
				Title:    hw.Title,
				Deadline: deadline,
				Details:  detailsText,
				URL:      hwURL,
				Type:     "homework",
			})

			log.Printf("[scraper] ✅ 作业: %s - %s (截止: %s)", courseName, hw.Title, deadline)
		}
	}

	return tasks, nil
}
