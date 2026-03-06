package User

import (
	"context"
	"errors"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

// NewMongoUserRepository 创建一个新的 Repository 实例
func NewMongoUserRepository() (UserRepository, error) {
	client, err := models.ConnectToDB()
	if err != nil {
		return nil, err
	}

	db := client.Database("REDACTED_MONGO_USER")

	return &MongoUserRepository{
		collection: db.Collection("users"),
	}, nil
}

// CreateUser 创建用户
func (r *MongoUserRepository) CreateUser(user *User) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// ID 已由 Snowflake 在 service 层生成，直接插入，不回填 MongoDB ObjectID
	_, err := r.collection.InsertOne(ctx, user)
	return err
}

// GetUserByID 根据 Snowflake ID 查询用户
func (r *MongoUserRepository) GetUserByID(id string) (*User, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var user User
	err := r.collection.FindOne(ctx, bson.M{"_id": id}).Decode(&user)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return nil, nil
		}
		return nil, err
	}
	return &user, nil
}

// GetUserByUsername 根据用户名查询用户
func (r *MongoUserRepository) GetUserByUsername(username string) (*User, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var user User
	err := r.collection.FindOne(ctx, bson.M{"username": username}).Decode(&user)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return nil, nil
		}
		return nil, err
	}
	return &user, nil
}

// GetUserByEmail 根据邮箱查询用户
func (r *MongoUserRepository) GetUserByEmail(email string) (*User, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var user User
	err := r.collection.FindOne(ctx, bson.M{"email": email}).Decode(&user)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return nil, nil
		}
		return nil, err
	}
	return &user, nil
}

// UpdateUser 更新用户信息
func (r *MongoUserRepository) UpdateUser(user *User) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	user.UpdatedAt = time.Now().Unix()

	update := bson.M{
		"$set": bson.M{
			"email":        user.Email,
			"studentId":    user.StudentID,
			"passwordHash": user.PasswordHash,
			"sPassword":    user.SPassword,
			"isAdmin":      user.IsAdmin,
			"updatedAt":    user.UpdatedAt,
		},
	}

	_, err := r.collection.UpdateOne(ctx, bson.M{"_id": user.ID}, update)
	return err
}

// DeleteUser 删除用户
func (r *MongoUserRepository) DeleteUser(id string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := r.collection.DeleteOne(ctx, bson.M{"_id": id})
	return err
}
