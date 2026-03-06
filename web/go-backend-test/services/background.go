package services

import (
	"log"

	"github.com/Ling0727-ai/go-buct-course-backend/models/CourseData"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/scraper"
)

// RefreshUserDataAsync 在后台 goroutine 中异步刷新用户课程数据
// 对应 Python: start_background_refresh + refresh_user_data_async
// 调用方无需等待结果，刷新失败只记录日志，不影响主流程（如登录）
func RefreshUserDataAsync(userID string) {
	go func() {
		if err := refreshUserData(userID); err != nil {
			log.Printf("[background] 用户 %s 异步刷新失败: %v", userID, err)
		}
	}()
	log.Printf("[background] 已启动用户 %s 的后台数据刷新 goroutine", userID)
}

// refreshUserData 实际执行刷新逻辑，对应 Python refresh_user_data_async
func refreshUserData(userID string) error {
	log.Printf("[background] 开始异步刷新用户 %s 的作业数据", userID)

	// 1. 检查用户是否设置了学号和密码，对应 Python 中检查 student_id / s_password
	user, err := User.Repository.GetUserByID(userID)
	if err != nil {
		return err
	}
	if user == nil {
		log.Printf("[background] 用户 %s 不存在，跳过数据刷新", userID)
		return nil
	}
	if user.StudentID == "" || user.SPassword == "" {
		log.Printf("[background] 用户 %s 未设置学号或密码，跳过数据刷新", userID)
		return nil
	}

	// 2. 调用 scraper 抓取数据，对应 Python scraper.get_pending_tasks(user_id)
	s := scraper.GetScraper()
	result, err := s.GetPendingTasks(userID)
	if err != nil {
		return err
	}

	// 3. 将 ScrapeResult 转换为 CourseData.TaskInput 并保存
	tasks := make([]CourseData.TaskInput, 0, len(result.Tasks))
	for _, t := range result.Tasks {
		tasks = append(tasks, CourseData.TaskInput{
			Subject:  t.Subject,
			Title:    t.Title,
			Deadline: t.Deadline,
			Details:  t.Details,
			Url:      t.URL,
			Type:     t.Type,
		})
	}

	courseRepo := CourseData.Repository
	saved, err := courseRepo.SaveUserCourseData(userID, tasks)
	if err != nil {
		return err
	}

	log.Printf("[background] 用户 %s 异步刷新完成，保存 %d 条，统计: homework=%d test=%d",
		userID, saved, result.Stats.HomeworkCount, result.Stats.TestsCount)
	return nil
}
