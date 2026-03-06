package Blacklist

import (
	"time"

	"go.mongodb.org/mongo-driver/mongo"
)

type Blacklist struct {
	ID        string    `bson:"_id,omitempty" json:"id,omitempty"`
	UserID    string    `bson:"user_id"       json:"user_id"`
	SubjectID string    `bson:"subject_id"    json:"subject_id"` // 由 course_data 的 url 字段解析，正则 (?<=courseId=)\d+
	CreatedAt time.Time `bson:"created_at"    json:"created_at"`
	UpdatedAt time.Time `bson:"updated_at"    json:"updated_at"`
}

// BlacklistRepository 黑名单数据库操作接口
type BlacklistRepository interface {
	// AddSubject 添加一个 subjectID 到黑名单（幂等）
	AddSubject(userID, subjectID string) error
	// RemoveSubject 从黑名单移除一个 subjectID
	RemoveSubject(userID, subjectID string) error
	// GetBlacklist 获取用户全部黑名单记录
	GetBlacklist(userID string) ([]*Blacklist, error)
	// GetBlacklistedIDs 获取用户黑名单中的所有 subjectID（用于过滤）
	GetBlacklistedIDs(userID string) ([]string, error)
	// IsBlacklisted 判断某 subjectID 是否在黑名单中
	IsBlacklisted(userID, subjectID string) (bool, error)
	// ClearBlacklist 清空用户的全部黑名单
	ClearBlacklist(userID string) error
}

type MongoBlacklistRepository struct {
	collection *mongo.Collection
}

var Repository = &MongoBlacklistRepository{}

// Init 在服务启动时绑定 MongoDB collection
func Init(db *mongo.Database) {
	col := db.Collection("blacklist")
	Repository = NewMongoBlacklistRepository(col)
}
