package User

import (
	"time"

	"go.mongodb.org/mongo-driver/mongo"
)

// User 用户表结构
type User struct {
	ID           string    `bson:"_id,omitempty"    json:"id,omitempty"`
	Username     string    `bson:"username"         json:"username"`
	Email        string    `bson:"email"            json:"email"`
	PasswordHash string    `bson:"password_hash"    json:"-"`
	StudentID    string    `bson:"student_id"       json:"student_id"`
	SPassword    string    `bson:"s_password"       json:"-"`
	SPasswordLen *int      `bson:"s_password_len"   json:"-"`
	IsAdmin      bool      `bson:"is_admin"         json:"is_admin"`
	CreatedAt    time.Time `bson:"created_at"       json:"created_at"`
	UpdatedAt    time.Time `bson:"updated_at"       json:"updated_at"`
}

// UserRepository 定义用户数据库操作接口
type UserRepository interface {
	CreateUser(user *User) error
	GetUserByID(id string) (*User, error)
	GetUserByUsername(username string) (*User, error)
	GetUserByEmail(email string) (*User, error)
	UpdateUser(user *User) error
	DeleteUser(id string) error
}

type MongoUserRepository struct {
	collection *mongo.Collection
}

var Repository = &MongoUserRepository{}

// UserService 定义用户业务逻辑接口
type UserService interface {
	RegisterUser(username, email, password, studentId, sPassword string) (*User, error)
	LoginUser(username, password string) (*User, error)

	GetUserProfile(id string) (*User, error)

	UpdateUserEmail(id string, email string) (*User, error)
	UpdateUserPassword(id string, newPassword string) (*User, error)
	UpdateStudentID(id string, studentId string) (*User, error)
	UpdateSPassword(id string, sPassword string) (*User, error)

	DeleteUserAccount(id string) error
}

type UserServiceImpl struct {
	repo UserRepository
}

var Service = &UserServiceImpl{}

// Init 在服务启动时绑定 MongoDB collection，必须在接收任何请求前调用
func Init(db *mongo.Database) {
	Repository.collection = db.Collection("users")
	Service.repo = Repository
}
