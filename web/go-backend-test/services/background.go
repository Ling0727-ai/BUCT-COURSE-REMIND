package services

import (
	"log"

	"github.com/Ling0727-ai/go-buct-course-backend/models/CourseData"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/scraper"
)

// RefreshUserDataAsync 后台异步刷新，不阻塞调用方（用于登录后自动刷新）
func RefreshUserDataAsync(userID string) {
	go func() {
		if _, err := refreshUserData(userID); err != nil {
			log.Printf("[background] 用户 %s 异步刷新失败: %v", userID, err)
		}
	}()
	log.Printf("[background] 已启动用户 %s 的后台数据刷新 goroutine", userID)
}

// RefreshUserDataSync 同步刷新，返回保存条数，对应 Python POST /api/course-data/refresh
func RefreshUserDataSync(userID string) (int, error) {
	return refreshUserData(userID)
}

// refreshUserData 实际刷新逻辑，返回 (保存条数, error)
func refreshUserData(userID string) (int, error) {
	log.Printf("[background] 开始刷新用户 %s 的作业数据", userID)

	user, err := User.Repository.GetUserByID(userID)
	if err != nil {
		return 0, err
	}
	if user == nil {
		log.Printf("[background] 用户 %s 不存在，跳过", userID)
		return 0, nil
	}
	if user.StudentID == "" || user.SPassword == "" {
		log.Printf("[background] 用户 %s 未设置学号或密码，跳过", userID)
		return 0, nil
	}

	s := scraper.GetScraper()
	result, err := s.GetPendingTasks(userID)
	if err != nil {
		return 0, err
	}

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

	saved, err := CourseData.Repository.SaveUserCourseData(userID, tasks)
	if err != nil {
		return 0, err
	}

	log.Printf("[background] 用户 %s 刷新完成，保存 %d 条，homework=%d test=%d",
		userID, saved, result.Stats.HomeworkCount, result.Stats.TestsCount)
	return saved, nil
}
