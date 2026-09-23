package services

import (
	"context"
	"crypto/rand"
	"fmt"
	"log"
	"math/big"
	"regexp"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

const verificationCodesCollection = "verification_codes"

// EmailRegexp 邮箱格式校验，对应 Python email_pattern
var EmailRegexp = regexp.MustCompile(`^[^\s@]+@[^\s@]+\.[^\s@]+$`)

// verCodeDoc verification_codes 集合文档结构
type verCodeDoc struct {
	Email     string    `bson:"email"`
	Code      string    `bson:"code"`
	CreatedAt time.Time `bson:"created_at"`
	ExpiresAt time.Time `bson:"expires_at"`
	Attempts  int       `bson:"attempts"`
}

// maxVerifyAttempts 单个验证码允许的最大校验失败次数。
// 6 位数字码只有 100 万种组合，若不做次数限制，
// 在 3 分钟有效期内足以被枚举，进而通过重置密码接管账号。
const maxVerifyAttempts = 5

// getVerCodeCollection 获取 verification_codes 集合
func getVerCodeCollection() (*mongo.Collection, error) {
	client, err := models.ConnectToDB()
	if err != nil {
		return nil, err
	}
	return client.Database("buct-course").Collection(verificationCodesCollection), nil
}

// GenerateVerificationCode 生成 6 位纯数字验证码
// 对应 Python generate_verification_code
func GenerateVerificationCode() (string, error) {
	const digits = "0123456789"
	code := make([]byte, 6)
	for i := range code {
		n, err := rand.Int(rand.Reader, big.NewInt(int64(len(digits))))
		if err != nil {
			return "", err
		}
		code[i] = digits[n.Int64()]
	}
	return string(code), nil
}

// IsRateLimited 检查 1 分钟内是否已发送过验证码
// 对应 Python 中 recent_code 频率限制逻辑
func IsRateLimited(email string) (bool, error) {
	col, err := getVerCodeCollection()
	if err != nil {
		return false, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	count, err := col.CountDocuments(ctx, bson.M{
		"email":      email,
		"created_at": bson.M{"$gt": time.Now().Add(-1 * time.Minute)},
	})
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

// SaveVerificationCode 存储验证码（upsert），对应 Python update_one upsert
func SaveVerificationCode(email, code string) error {
	col, err := getVerCodeCollection()
	if err != nil {
		return err
	}

	expire := 180 // 默认 3 分钟
	if config.Mail != nil {
		expire = config.Mail.VerifyCodeExpire
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	now := time.Now()
	_, err = col.UpdateOne(ctx,
		bson.M{"email": email},
		bson.M{"$set": bson.M{
			"code":       code,
			"created_at": now,
			"expires_at": now.Add(time.Duration(expire) * time.Second),
			"attempts":   0,
		}},
		options.Update().SetUpsert(true),
	)
	return err
}

// VerifyCode 校验验证码是否有效，成功后删除记录
// 对应 Python verify_code 路由逻辑，并增加了失败次数限制
func VerifyCode(email, code string) (bool, error) {
	col, err := getVerCodeCollection()
	if err != nil {
		return false, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var doc verCodeDoc
	err = col.FindOne(ctx, bson.M{
		"email":      email,
		"expires_at": bson.M{"$gt": time.Now()},
	}).Decode(&doc)

	if err == mongo.ErrNoDocuments {
		return false, nil // 验证码不存在或已过期
	}
	if err != nil {
		return false, err
	}

	// 已超过尝试上限：直接作废该验证码，要求重新发送
	if doc.Attempts >= maxVerifyAttempts {
		_, _ = col.DeleteOne(ctx, bson.M{"email": email})
		return false, nil
	}

	if doc.Code != code {
		// 记录一次失败；达到上限时顺手删除，避免继续被尝试
		if doc.Attempts+1 >= maxVerifyAttempts {
			_, _ = col.DeleteOne(ctx, bson.M{"email": email})
		} else {
			_, _ = col.UpdateOne(ctx,
				bson.M{"email": email},
				bson.M{"$inc": bson.M{"attempts": 1}},
			)
		}
		return false, nil
	}

	// 验证成功后删除记录，对应 Python delete_one
	_, _ = col.DeleteOne(ctx, bson.M{"email": email})
	return true, nil
}

// SendVerificationEmail 生成验证码、存库、发送邮件，三步合一
// 对应 Python send_verification_code 路由中的完整流程
// 返回 (code, testMode, error)
//   - code: 仅 testMode=true 时有意义，返回给前端（邮件服务不可用的回退）
//   - testMode: true 表示邮件发送失败，降级为测试模式
func SendVerificationEmail(email, username string) (code string, testMode bool, err error) {
	code, err = GenerateVerificationCode()
	if err != nil {
		return "", false, fmt.Errorf("生成验证码失败: %w", err)
	}

	if err = SaveVerificationCode(email, code); err != nil {
		return "", false, fmt.Errorf("存储验证码失败: %w", err)
	}

	// 构造 HTML 邮件内容，对应 Python html_content
	greeting := "您好"
	if username != "" {
		greeting = "您好，" + username
	}
	usernameHint := `<p style="color: #999; font-size: 14px;">温馨提示：如果您忘记了用户名，请联系管理员</p>`
	if username != "" {
		usernameHint = fmt.Sprintf(`<p style="color: #666;">您的用户名：<strong>%s</strong></p>`, username)
	}

	htmlBody := fmt.Sprintf(`
<html><body>
<div style="max-width:600px;margin:0 auto;padding:20px;font-family:Arial,sans-serif;">
  <h2 style="color:#333;text-align:center;">北化课程提醒系统</h2>
  <div style="background-color:#f8f9fa;padding:20px;border-radius:8px;margin:20px 0;">
    <h3 style="color:#007bff;margin-top:0;">邮箱验证码</h3>
    <p>%s！</p>
    <p>您的验证码是：</p>
    <div style="text-align:center;margin:20px 0;">
      <span style="font-size:32px;font-weight:bold;color:#007bff;
                   background-color:#e3f2fd;padding:10px 20px;
                   border-radius:5px;letter-spacing:5px;">%s</span>
    </div>
    %s
    <p style="color:#666;">验证码有效期为 %d 秒，请及时使用。</p>
    <p style="color:#666;">如果您没有申请此验证码，请忽略此邮件。</p>
  </div>
</div>
</body></html>`, greeting, code, usernameHint, config.Mail.VerifyCodeExpire)

	if config.Mail == nil || !config.Mail.IsReady() {
		log.Printf("[vercode] 邮件服务不可用，降级为测试模式，验证码: %s", code)
		return code, true, nil
	}

	if sendErr := config.Mail.SendMail(email, "北化课程提醒 - 邮箱验证码", htmlBody); sendErr != nil {
		log.Printf("[vercode] 邮件发送失败，降级为测试模式: %v", sendErr)
		return code, true, nil
	}

	log.Printf("[vercode] 验证码邮件发送成功: %s", email)
	return code, false, nil
}
