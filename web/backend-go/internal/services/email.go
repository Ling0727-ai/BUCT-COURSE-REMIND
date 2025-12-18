package services

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/smtp"
	"os"
)

// SendVerificationEmail 发送验证码邮件
func SendVerificationEmail(email, code string) error {
	smtpServer := getEnv("MAIL_SMTP_SERVER", "smtp.163.com")
	smtpPort := getEnv("MAIL_SMTP_PORT", "465")
	senderEmail := getEnv("MAIL_SENDER", "buct_course_remind@163.com")
	senderPassword := getEnv("MAIL_PASSWORD", "")

	if senderPassword == "" || senderPassword == "dummy_password_for_dev" {
		// 测试模式，只打印日志
		log.Printf("[测试模式] 验证码已生成: %s", code)
		log.Printf("[测试模式] 目标邮箱: %s", email)
		return nil
	}

	subject := "BUCT课程提醒 - 邮箱验证码"
	body := fmt.Sprintf(`
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">BUCT课程提醒系统</h2>
            <p>您的邮箱验证码为：</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #007bff;">%s</span>
            </div>
            <p>验证码有效期 3 分钟，请尽快使用。</p>
            <p style="color: #666; font-size: 12px;">如果不是您本人操作，请忽略此邮件。</p>
        </div>
    `, code)

	return sendEmail(smtpServer, smtpPort, senderEmail, senderPassword, email, subject, body)
}

// SendReminderEmail 发送提醒邮件
func SendReminderEmail(email, subject, content string) error {
	smtpServer := getEnv("MAIL_SMTP_SERVER", "smtp.163.com")
	smtpPort := getEnv("MAIL_SMTP_PORT", "465")
	senderEmail := getEnv("MAIL_SENDER", "buct_course_remind@163.com")
	senderPassword := getEnv("MAIL_PASSWORD", "")

	if senderPassword == "" || senderPassword == "dummy_password_for_dev" {
		log.Printf("[测试模式] 提醒邮件: %s -> %s", subject, email)
		return nil
	}

	body := fmt.Sprintf(`
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">BUCT课程提醒系统</h2>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                %s
            </div>
            <p style="color: #666; font-size: 12px;">这是一封自动发送的邮件，请勿回复。</p>
        </div>
    `, content)

	return sendEmail(smtpServer, smtpPort, senderEmail, senderPassword, email, subject, body)
}

func sendEmail(smtpServer, smtpPort, from, password, to, subject, body string) error {
	// 构建邮件头
	headers := make(map[string]string)
	headers["From"] = from
	headers["To"] = to
	headers["Subject"] = subject
	headers["Content-Type"] = "text/html; charset=UTF-8"

	message := ""
	for k, v := range headers {
		message += fmt.Sprintf("%s: %s\r\n", k, v)
	}
	message += "\r\n" + body

	// 使用TLS连接
	tlsConfig := &tls.Config{
		InsecureSkipVerify: true,
		ServerName:         smtpServer,
	}

	conn, err := tls.Dial("tcp", smtpServer+":"+smtpPort, tlsConfig)
	if err != nil {
		return fmt.Errorf("TLS连接失败: %v", err)
	}
	defer conn.Close()

	client, err := smtp.NewClient(conn, smtpServer)
	if err != nil {
		return fmt.Errorf("创建SMTP客户端失败: %v", err)
	}
	defer client.Close()

	// 认证
	auth := smtp.PlainAuth("", from, password, smtpServer)
	if err := client.Auth(auth); err != nil {
		return fmt.Errorf("SMTP认证失败: %v", err)
	}

	// 发送邮件
	if err := client.Mail(from); err != nil {
		return fmt.Errorf("设置发件人失败: %v", err)
	}

	if err := client.Rcpt(to); err != nil {
		return fmt.Errorf("设置收件人失败: %v", err)
	}

	w, err := client.Data()
	if err != nil {
		return fmt.Errorf("获取数据写入器失败: %v", err)
	}

	_, err = w.Write([]byte(message))
	if err != nil {
		return fmt.Errorf("写入邮件内容失败: %v", err)
	}

	if err := w.Close(); err != nil {
		return fmt.Errorf("关闭数据写入器失败: %v", err)
	}

	return client.Quit()
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
