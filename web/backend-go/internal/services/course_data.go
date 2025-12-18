package services

import (
	"context"
	"fmt"
	"log"
	"time"

	"buct-course-remind/internal/crypto"
	"buct-course-remind/internal/database"
	"buct-course-remind/internal/models"
	"buct-course-remind/internal/scraper"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// GetUserCourseData 获取用户课程数据
func GetUserCourseData(ctx context.Context, userID string) ([]models.CourseData, error) {
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		return nil, err
	}

	collection := database.GetCollection(database.CourseDataCollection)

	cursor, err := collection.Find(ctx, bson.M{"user_id": objID})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var tasks []models.CourseData
	if err := cursor.All(ctx, &tasks); err != nil {
		return nil, err
	}

	return tasks, nil
}

// GetCompletedAssignmentIDs 获取已完成的作业ID列表
func GetCompletedAssignmentIDs(ctx context.Context, userID string) ([]string, error) {
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		return nil, err
	}

	collection := database.GetCollection(database.AssignmentStatusCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"user_id": objID,
		"status":  "completed",
	})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var ids []string
	for cursor.Next(ctx) {
		var status models.AssignmentStatus
		if err := cursor.Decode(&status); err == nil {
			ids = append(ids, status.AssignmentID)
		}
	}

	return ids, nil
}

// GetDeletedAssignmentIDs 获取已删除的作业ID列表
func GetDeletedAssignmentIDs(ctx context.Context, userID string) ([]string, error) {
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		return nil, err
	}

	collection := database.GetCollection(database.AssignmentStatusCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"user_id": objID,
		"status":  bson.M{"$in": []string{"deleted", "permanent_deleted"}},
	})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var ids []string
	for cursor.Next(ctx) {
		var status models.AssignmentStatus
		if err := cursor.Decode(&status); err == nil {
			ids = append(ids, status.AssignmentID)
		}
	}

	return ids, nil
}

// AutoRefreshAssignments 自动刷新作业数据（后台任务）
func AutoRefreshAssignments(userID string) {
	log.Printf("开始为用户 %s 后台刷新作业数据", userID)
	
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// 检查用户是否有学号和密码
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		log.Printf("无效的用户ID: %v", err)
		return
	}

	collection := database.GetCollection(database.UsersCollection)
	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user); err != nil {
		log.Printf("用户不存在: %v", err)
		return
	}

	if user.StudentID == "" || user.SPassword == "" {
		log.Printf("用户 %s 未设置学号或密码，跳过自动刷新", userID)
		return
	}

	// 调用爬虫服务获取数据
	if count, err := RefreshUserData(userID); err != nil {
		log.Printf("刷新用户 %s 数据失败: %v", userID, err)
	} else {
		log.Printf("用户 %s 数据刷新完成，共 %d 条", userID, count)
	}
}

// RefreshUserData 刷新用户数据，返回刷新的数据条数
func RefreshUserData(userID string) (int, error) {
	log.Printf("开始刷新用户 %s 的课程数据", userID)

	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()

	// 获取用户信息
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		return 0, fmt.Errorf("无效的用户ID: %v", err)
	}

	collection := database.GetCollection(database.UsersCollection)
	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user); err != nil {
		return 0, fmt.Errorf("用户不存在: %v", err)
	}

	if user.StudentID == "" || user.SPassword == "" {
		return 0, fmt.Errorf("用户未设置学号或密码")
	}

	// 解密外部密码
	decryptedPassword, err := DecryptSPassword(user.SPassword)
	if err != nil {
		return 0, fmt.Errorf("解密密码失败: %v", err)
	}

	// 创建爬虫客户端
	client := scraper.NewBUCTClient(user.StudentID, decryptedPassword)

	// 登录
	if err := client.Login(); err != nil {
		return 0, fmt.Errorf("登录课程平台失败: %v", err)
	}
	defer client.Logout()

	log.Printf("用户 %s 登录课程平台成功", userID)

	// 获取所有待办作业详情
	homeworkDetails, err := client.GetAllPendingHomeworkDetails()
	if err != nil {
		log.Printf("获取作业详情失败: %v", err)
	}

	// 获取所有待办测试
	testCourses, _ := client.GetPendingTests()
	var testDetails []scraper.TestDetails
	for _, course := range testCourses {
		if detail, err := client.GetTestList(course.LID); err == nil {
			detail.CourseName = course.CourseName
			testDetails = append(testDetails, *detail)
		}
	}

	// 转换为统一的Assignment格式
	homeworkAssignments := scraper.ConvertToAssignments(homeworkDetails)
	testAssignments := scraper.ConvertTestsToAssignments(testDetails)

	// 合并所有作业
	allAssignments := append(homeworkAssignments, testAssignments...)

	// 保存到数据库
	if err := saveCourseData(ctx, objID, allAssignments); err != nil {
		return 0, fmt.Errorf("保存课程数据失败: %v", err)
	}

	log.Printf("用户 %s 数据刷新完成，共 %d 条作业，%d 条测试",
		userID, len(homeworkAssignments), len(testAssignments))
	return len(allAssignments), nil
}

// saveCourseData 保存课程数据到数据库
func saveCourseData(ctx context.Context, userID primitive.ObjectID, assignments []scraper.Assignment) error {
	collection := database.GetCollection(database.CourseDataCollection)

	for _, assignment := range assignments {
		now := time.Now()

		// 使用 upsert 操作
		filter := bson.M{
			"user_id": userID,
			"task_id": assignment.ID,
		}

		// 分开设置字段，避免 created_at 冲突
		update := bson.M{
			"$set": bson.M{
				"user_id":    userID,
				"task_id":    assignment.ID,
				"subject":    assignment.CourseName,
				"title":      assignment.Title,
				"deadline":   assignment.Deadline,
				"details":    assignment.Description, // 使用作业详细描述
				"url":        assignment.DetailHref,
				"type":       assignment.Type,
				"updated_at": now,
			},
			"$setOnInsert": bson.M{
				"created_at": now,
			},
		}

		opts := options.Update().SetUpsert(true)
		_, err := collection.UpdateOne(ctx, filter, update, opts)
		if err != nil {
			log.Printf("保存课程数据失败 [%s]: %v", assignment.ID, err)
		}
	}

	return nil
}

// DecryptSPassword 解密外部密码
func DecryptSPassword(encryptedPassword string) (string, error) {
	eccCrypto := crypto.GetECCCrypto()
	return eccCrypto.DecryptPassword(encryptedPassword)
}
