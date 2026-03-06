package CourseData

import (
	"context"
	"crypto/md5"
	"fmt"
	"strings"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// NewMongoCourseDataRepository 创建并初始化仓库，同时建立索引
func NewMongoCourseDataRepository(col *mongo.Collection) *MongoCourseDataRepository {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 对应 Python: create_index([("user_id", 1), ("updated_at", -1)])
	col.Indexes().CreateOne(ctx, mongo.IndexModel{
		Keys: bson.D{
			{Key: "user_id", Value: 1},
			{Key: "updated_at", Value: -1},
		},
	})
	// 对应 Python: create_index([("user_id", 1), ("task_id", 1)], unique=True)
	col.Indexes().CreateOne(ctx, mongo.IndexModel{
		Keys: bson.D{
			{Key: "user_id", Value: 1},
			{Key: "task_id", Value: 1},
		},
		Options: options.Index().SetUnique(true),
	})

	return &MongoCourseDataRepository{collection: col}
}

// generateTaskID 生成确定性任务ID，对应 Python 中的 MD5 哈希逻辑
func generateTaskID(taskType, subject, title, deadline, details string) string {
	// 校验并修正 taskType
	switch taskType {
	case "homework", "test", "todo":
		// 合法，保持不变
	default:
		if strings.TrimSpace(details) != "" {
			taskType = "homework"
		} else {
			taskType = "test"
		}
	}
	// content_str = f"{subject}|{title}|{deadline}|{details}"
	contentStr := fmt.Sprintf("%s|%s|%s|%s", subject, title, deadline, details)
	hash := md5.Sum([]byte(contentStr))
	// 取前 16 个十六进制字符（即前 8 字节）
	contentHash := fmt.Sprintf("%x", hash)[:16]
	return fmt.Sprintf("%s_%s", taskType, contentHash)
}

// nowUnix 返回当前 Unix 时间戳（秒）
func nowUnix() int64 {
	return time.Now().Unix()
}

// ──────────────────────────────────────────────
//  CRUD 基础操作
// ──────────────────────────────────────────────

// CreateCourseData 插入单条课程数据
func (r *MongoCourseDataRepository) CreateCourseData(courseData *CourseData) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	now := nowUnix()
	courseData.ID = config.Snowflake.GenerateID()
	courseData.CreatedAt = now
	courseData.UpdatedAt = now

	_, err := r.collection.InsertOne(ctx, courseData)
	return err
}

// GetCourseDataByID 通过 Snowflake ID 查询单条数据
func (r *MongoCourseDataRepository) GetCourseDataByID(id string) (*CourseData, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var result CourseData
	err := r.collection.FindOne(ctx, bson.M{"_id": id}).Decode(&result)
	if err != nil {
		return nil, err
	}
	return &result, nil
}

// GetCourseDataByUserID 获取某用户的全部课程数据，按 updated_at 降序
func (r *MongoCourseDataRepository) GetCourseDataByUserID(userID string) ([]*CourseData, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	opts := options.Find().SetSort(bson.D{{Key: "updated_at", Value: -1}})
	cursor, err := r.collection.Find(ctx, bson.M{"user_id": userID}, opts)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var results []*CourseData
	if err = cursor.All(ctx, &results); err != nil {
		return nil, err
	}
	return results, nil
}

// UpdateCourseData 更新一条课程数据（以 ID 为条件）
func (r *MongoCourseDataRepository) UpdateCourseData(courseData *CourseData) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	courseData.UpdatedAt = nowUnix()
	_, err := r.collection.ReplaceOne(ctx,
		bson.M{"_id": courseData.ID},
		courseData,
	)
	return err
}

// DeleteCourseData 删除单条课程数据（by Snowflake ID）
func (r *MongoCourseDataRepository) DeleteCourseData(id string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := r.collection.DeleteOne(ctx, bson.M{"_id": id})
	return err
}

// GetLastUpdateTimeByUserID 获取用户数据的最后更新时间戳（Unix 秒）
// 对应 Python: get_last_update_time
func (r *MongoCourseDataRepository) GetLastUpdateTimeByUserID(userID string) (int64, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	opts := options.FindOne().SetSort(bson.D{{Key: "updated_at", Value: -1}})
	var result CourseData
	err := r.collection.FindOne(ctx, bson.M{"user_id": userID}, opts).Decode(&result)
	if err == mongo.ErrNoDocuments {
		return 0, nil
	}
	if err != nil {
		return 0, err
	}
	return result.UpdatedAt, nil
}

// ClearCourseDataByUserID 清空用户的全部课程数据
// 对应 Python: clear_user_data
func (r *MongoCourseDataRepository) ClearCourseDataByUserID(userID string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, err := r.collection.DeleteMany(ctx, bson.M{"user_id": userID})
	return err
}

// SaveUserCourseData 批量保存用户课程数据
// 对应 Python: save_user_course_data
// 流程：先删除该用户所有旧数据，再批量插入新数据
// 返回实际插入的条数
func (r *MongoCourseDataRepository) SaveUserCourseData(userID string, tasks []TaskInput) (int, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	now := nowUnix()

	// 构建待插入文档
	docs := make([]interface{}, 0, len(tasks))
	for _, task := range tasks {
		taskID := generateTaskID(task.Type, task.Subject, task.Title, task.Deadline, task.Details)

		doc := CourseData{
			ID:        config.Snowflake.GenerateID(),
			UserID:    userID,
			TaskID:    taskID,
			Subject:   task.Subject,
			Title:     task.Title,
			Deadline:  task.Deadline,
			Details:   task.Details,
			Url:       task.Url,
			Type:      strings.Split(taskID, "_")[0], // 取修正后的 type
			CreatedAt: now,
			UpdatedAt: now,
		}
		docs = append(docs, doc)
	}

	// 删除旧数据
	if _, err := r.collection.DeleteMany(ctx, bson.M{"user_id": userID}); err != nil {
		return 0, err
	}

	// 插入新数据
	if len(docs) == 0 {
		return 0, nil
	}

	result, err := r.collection.InsertMany(ctx, docs)
	if err != nil {
		return 0, err
	}
	return len(result.InsertedIDs), nil
}
