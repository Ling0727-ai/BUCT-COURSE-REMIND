#!/usr/bin/env python3
"""
邮箱配置检查和修复工具
帮助诊断和修复163邮箱发送问题
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_email_config():
    """检查邮箱配置"""
    print("=== 邮箱配置检查 ===")
    
    smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
    smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
    sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
    sender_password = os.getenv('MAIL_PASSWORD')
    
    print(f"SMTP服务器: {smtp_server}")
    print(f"SMTP端口: {smtp_port}")
    print(f"发件邮箱: {sender_email}")
    print(f"密码设置: {'已设置' if sender_password and sender_password != 'dummy_password_for_dev' else '未设置或使用默认值'}")
    
    if not sender_password or sender_password == 'dummy_password_for_dev':
        print("\n❌ 问题：邮箱密码未正确配置")
        print("解决方案：")
        print("1. 登录163邮箱 (mail.163.com)")
        print("2. 进入设置 -> POP3/SMTP/IMAP")
        print("3. 开启SMTP服务")
        print("4. 生成授权码")
        print("5. 在.env文件中设置 MAIL_PASSWORD=你的授权码")
        return False
    
    return True

def test_smtp_connection():
    """测试SMTP连接"""
    print("\n=== SMTP连接测试 ===")
    
    smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
    smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
    sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
    sender_password = os.getenv('MAIL_PASSWORD')
    
    # 测试多种配置
    configs = [
        {'name': '163邮箱SSL (推荐)', 'server': 'smtp.163.com', 'port': 465, 'ssl': True},
        {'name': '163邮箱STARTTLS', 'server': 'smtp.163.com', 'port': 587, 'ssl': False},
        {'name': '163邮箱标准SMTP', 'server': 'smtp.163.com', 'port': 25, 'ssl': False},
    ]
    
    for config in configs:
        print(f"\n测试配置: {config['name']}")
        print(f"  服务器: {config['server']}:{config['port']}")
        print(f"  SSL: {config['ssl']}")
        
        try:
            if config['ssl']:
                server = smtplib.SMTP_SSL(config['server'], config['port'])
            else:
                server = smtplib.SMTP(config['server'], config['port'])
                if config['port'] in [587, 25]:
                    server.starttls()
            
            print("  ✅ 连接成功")
            
            # 尝试登录
            server.login(sender_email, sender_password)
            print("  ✅ 登录成功")
            
            server.quit()
            print(f"  🎉 配置 '{config['name']}' 可用！")
            
            # 更新.env文件
            update_env_config(config)
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"  ❌ 认证失败: {e}")
            if "User has no permission" in str(e):
                print("     可能原因: 163邮箱未开启SMTP服务或授权码不正确")
        except smtplib.SMTPConnectError as e:
            print(f"  ❌ 连接失败: {e}")
        except Exception as e:
            print(f"  ❌ 其他错误: {e}")
    
    return False

def update_env_config(config):
    """更新.env文件配置"""
    print(f"\n=== 更新配置文件 ===")
    
    env_file = '.env'
    if not os.path.exists(env_file):
        print("❌ .env文件不存在")
        return
    
    # 读取现有配置
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新配置
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('MAIL_SMTP_SERVER='):
            lines[i] = f"MAIL_SMTP_SERVER={config['server']}\n"
            updated = True
        elif line.startswith('MAIL_SMTP_PORT='):
            lines[i] = f"MAIL_SMTP_PORT={config['port']}\n"
            updated = True
    
    if updated:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ 已更新.env文件配置")
        print(f"   MAIL_SMTP_SERVER={config['server']}")
        print(f"   MAIL_SMTP_PORT={config['port']}")
    else:
        print("❌ 未找到需要更新的配置项")

def send_test_email():
    """发送测试邮件"""
    test_email = input("\n请输入测试邮箱地址 (按回车使用默认): ").strip()
    if not test_email:
        test_email = "test@example.com"
    
    print(f"\n=== 发送测试邮件到 {test_email} ===")
    
    smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
    smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
    sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
    sender_password = os.getenv('MAIL_PASSWORD')
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = test_email
        msg['Subject'] = "邮箱配置测试 - 北化课程提醒系统"
        
        html_content = """
        <html>
        <body>
            <h2>邮箱配置测试成功！</h2>
            <p>如果您收到这封邮件，说明邮箱配置已经正确。</p>
            <p>北化课程提醒系统现在可以正常发送邮件了。</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print("✅ 测试邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试邮件发送失败: {e}")
        return False

def main():
    """主函数"""
    print("北化课程提醒系统 - 邮箱配置修复工具")
    print("=" * 50)
    
    # 检查配置
    if not check_email_config():
        print("\n请先配置正确的邮箱密码后再运行此工具")
        return
    
    # 测试连接
    if test_smtp_connection():
        print("\n🎉 SMTP配置测试成功！")
        
        # 询问是否发送测试邮件
        send_test = input("\n是否发送测试邮件？(y/n): ").strip().lower()
        if send_test == 'y':
            send_test_email()
    else:
        print("\n❌ 所有SMTP配置都失败了")
        print("\n可能的解决方案：")
        print("1. 确认163邮箱已开启SMTP服务")
        print("2. 确认使用的是授权码而不是登录密码")
        print("3. 检查网络连接")
        print("4. 尝试使用其他邮箱服务商（如QQ邮箱、Gmail等）")

if __name__ == "__main__":
    main()