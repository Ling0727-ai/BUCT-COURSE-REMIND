package User

import (
	"errors"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/crypto"
)

func (s *UserServiceImpl) RegisterUser(username, email, password, studentId, sPassword string) (*User, error) {
	// 1. 检查用户名是否已存在
	existingUser, err := s.repo.GetUserByUsername(username)
	if err != nil {
		return nil, err
	}
	if existingUser != nil {
		return nil, errors.New("username already exists")
	}

	// 2. 检查邮箱是否已被注册
	existingByEmail, err := s.repo.GetUserByEmail(email)
	if err != nil {
		return nil, err
	}
	if existingByEmail != nil {
		return nil, errors.New("email already exists")
	}

	// 3. 对密码进行 Hash以及ECC加密
	passwordHash, err := crypto.Crypto.HashPassword(password)
	if err != nil {
		return nil, err
	}

	sPassECC, err := crypto.Crypto.EncryptECC(sPassword)
	if err != nil {
		return nil, err
	}

	// 4. 生成唯一 ID 并构造用户对象
	now := time.Now().Unix()
	user := &User{
		ID:           config.Snowflake.GenerateID(),
		Username:     username,
		Email:        email,
		PasswordHash: passwordHash,
		StudentID:    studentId,
		SPassword:    sPassECC,
		IsAdmin:      false,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	// 5. 持久化到数据库
	if err = s.repo.CreateUser(user); err != nil {
		return nil, err
	}

	return user, nil
}

func (s *UserServiceImpl) LoginUser(username, password string) (*User, error) {
	// 1. 根据用户名查询用户
	user, err := s.repo.GetUserByUsername(username)
	if err != nil {
		return nil, err
	}
	if user == nil {
		return nil, errors.New("invalid username or password")
	}

	// 2. 验证密码
	if !crypto.Crypto.CheckPassword(password, user.PasswordHash) {
		return nil, errors.New("invalid username or password")
	}

	// 3. 登录成功，返回用户信息
	return user, nil
}

func (s *UserServiceImpl) GetUserProfile(id string) (*User, error) {
	return s.repo.GetUserByID(id)
}

func (s *UserServiceImpl) UpdateUserEmail(id string, email string) (*User, error) {
	user, err := s.repo.GetUserByID(id)
	if err != nil {
		return nil, err
	}
	if user == nil {
		return nil, errors.New("user not found")
	}

	user.Email = email
	if err = s.repo.UpdateUser(user); err != nil {
		return nil, err
	}
	return user, nil
}

func (s *UserServiceImpl) UpdateUserPassword(id string, newPassword string) (*User, error) {
	user, err := s.repo.GetUserByID(id)
	if err != nil {
		return nil, err
	}
	if user == nil {
		return nil, errors.New("user not found")
	}

	newHash, err := crypto.Crypto.HashPassword(newPassword)
	if err != nil {
		return nil, err
	}
	user.PasswordHash = newHash

	if err = s.repo.UpdateUser(user); err != nil {
		return nil, err
	}
	return user, nil
}

func (s *UserServiceImpl) UpdateStudentID(id string, studentId string) (*User, error) {
	user, err := s.repo.GetUserByID(id)
	if err != nil {
		return nil, err
	}
	if user == nil {
		return nil, errors.New("user not found")
	}

	user.StudentID = studentId
	if err = s.repo.UpdateUser(user); err != nil {
		return nil, err
	}
	return user, nil
}

func (s *UserServiceImpl) UpdateSPassword(id string, sPassword string) (*User, error) {
	user, err := s.repo.GetUserByID(id)
	if err != nil {
		return nil, err
	}
	if user == nil {
		return nil, errors.New("user not found")
	}

	sPassECC, err := crypto.Crypto.EncryptECC(sPassword)
	if err != nil {
		return nil, err
	}

	user.SPassword = sPassECC
	if err = s.repo.UpdateUser(user); err != nil {
		return nil, err
	}
	return user, nil
}

func (s *UserServiceImpl) DeleteUserAccount(id string) error {
	return s.repo.DeleteUser(id)
}
