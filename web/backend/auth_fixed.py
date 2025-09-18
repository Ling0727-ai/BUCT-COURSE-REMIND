#!/usr/bin/env python3
"""
修复后的auth.py文件，包含正确的SMTP配置
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email, code):
    """发送验证码邮件 - 使用正确的163邮箱配置"""
    try:
        # 邮箱配置 - 使用正确的授权码
        smtp_server = 'smtp.163.com'
        smtp_port = 465
        sender_email = 'buct_course_remind@163.com'
        sender_password = '***REMOVED***'  # 正确的163邮箱授权码
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 连接到SMTP服务器并发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            # 登录
            server.login(sender_email, sender_password)
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = '北化课程提醒 - 邮箱验证码'
            
            # 邮件内容
            html_content = f"""
            <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #333; text-align: center;">北化课程提醒系统</h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #007bff; margin-top: 0;">邮箱验证码</h3>
                        <p>您好！</p>
                        <p>您正在注册北化课程提醒系统，您的验证码是：</p>
                        <div style="text-align: center; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; color: #007bff; background-color: #e3f2fd; padding: 10px 20px; border-radius: 5px; letter-spacing: 5px;">{code}</span>
                        </div>
                        <p style="color: #666;">验证码有效期为3分钟，请及时使用。</p>
                        <p style="color: #666;">如果您没有申请此验证码，请忽略此邮件。</p>
                    </div>
                    <div style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
                        <p>此邮件由系统自动发送，请勿回复。</p>
                        <p>北化课程提醒系统</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 发送邮件
            server.send_message(msg)
            
        print(f"✅ 验证码邮件已成功发送到 {email}")
        return True
        
    except Exception as e:
        print(f'❌ 邮件发送失败: {e}')
        return False

# 测试函数
if __name__ == "__main__":
    # 测试发送验证码
    test_email = "1163840260@qq.com"
    test_code = "123456"
    
    print("🧪 测试验证码邮件发送...")
    result = send_verification_email(test_email, test_code)
    
    if result:
        print("🎉 测试成功！")
    else:
        print("❌ 测试失败！")