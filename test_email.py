#!/usr/bin/env python3
"""
邮件配置测试脚本
用法: python test_email.py
功能: 验证 .env 中的邮件配置是否正确，发送一封测试邮件
注意: 此脚本不会修改任何项目文件
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def load_env():
    """从 .env 文件加载环境变量（不依赖 python-dotenv）"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"❌ 未找到 .env 文件，请先从 .env.example 复制: cp .env.example .env")
        sys.exit(1)

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key, value)


def check_config():
    """检查邮件配置是否完整"""
    required = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing = []
    values = {}

    for key in required:
        value = os.getenv(key, '').strip()
        values[key] = value
        if not value or value == 'your-email@example.com' or value == 'your-email-password':
            missing.append(key)

    print("=" * 50)
    print("📧 邮件配置检查")
    print("=" * 50)

    for key in required:
        val = values[key]
        # 密码只显示前3位和后3位
        display = val
        if 'PASSWORD' in key and len(val) > 6:
            display = val[:3] + '***' + val[-3:]
        print(f"  {key}: {display}")

    tls = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', '1', 'yes')
    ssl = os.getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 'yes')
    print(f"  MAIL_USE_TLS: {tls}")
    print(f"  MAIL_USE_SSL: {ssl}")

    if missing:
        print(f"\n❌ 以下配置项未设置或仍为默认值: {', '.join(missing)}")
        print("   请编辑 .env 文件填写真实配置")
        return False

    print("\n✅ 配置项检查通过")
    return True


def test_smtp_connection():
    """测试 SMTP 连接"""
    server = os.getenv('MAIL_SERVER')
    port = int(os.getenv('MAIL_PORT', 587))
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    use_tls = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', '1', 'yes')
    use_ssl = os.getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 'yes')

    print("\n" + "=" * 50)
    print("🔗 SMTP 连接测试")
    print("=" * 50)

    try:
        if use_ssl:
            print(f"  正在连接 {server}:{port} (SSL)...")
            smtp = smtplib.SMTP_SSL(server, port, timeout=10)
        else:
            print(f"  正在连接 {server}:{port}...")
            smtp = smtplib.SMTP(server, port, timeout=10)

        if use_tls:
            print("  启动 TLS 加密...")
            smtp.starttls()

        print(f"  正在登录 {username}...")
        smtp.login(username, password)
        print("  ✅ SMTP 登录成功")
        smtp.quit()
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"  ❌ 登录失败: 用户名或密码错误")
        print(f"     提示: 邮箱密码请使用「授权码」而非登录密码")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"  ❌ 连接失败: 无法连接到 {server}:{port}")
        print(f"     请检查服务器地址和端口是否正确")
        return False
    except Exception as e:
        print(f"  ❌ 连接异常: {e}")
        return False


def send_test_email():
    """发送测试邮件"""
    server = os.getenv('MAIL_SERVER')
    port = int(os.getenv('MAIL_PORT', 587))
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    sender = os.getenv('MAIL_DEFAULT_SENDER', username)
    use_tls = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', '1', 'yes')
    use_ssl = os.getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 'yes')

    print("\n" + "=" * 50)
    print("📨 测试邮件发送")
    print("=" * 50)
    print(f"  发件人: {sender}")
    print(f"  收件人: {username} (即发件人自己)")

    # 构建邮件内容
    subject = "【WaytoAGI】邮件配置测试"
    body = f"""您好，

这是一封测试邮件，用于验证 WaytoAGI 活动报名平台的邮件配置。

如果您收到这封邮件，说明邮件服务配置正确！

配置信息：
- SMTP 服务器: {server}:{port}
- 发件账号: {username}
- TLS: {use_tls}
- SSL: {use_ssl}

WaytoAGI 团队
"""

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = sender
    msg['To'] = username
    msg['Subject'] = Header(subject, 'utf-8')

    try:
        if use_ssl:
            smtp = smtplib.SMTP_SSL(server, port, timeout=10)
        else:
            smtp = smtplib.SMTP(server, port, timeout=10)

        if use_tls:
            smtp.starttls()

        smtp.login(username, password)
        smtp.sendmail(sender, [username], msg.as_string())
        smtp.quit()

        print(f"  ✅ 测试邮件发送成功！")
        print(f"  📬 请检查 {username} 的收件箱（包括垃圾邮件文件夹）")
        return True

    except Exception as e:
        print(f"  ❌ 发送失败: {e}")
        return False


def main():
    print("\n" + "🚀 WaytoAGI 邮件配置测试工具".center(50))
    print("   此脚本仅用于测试，不会修改任何文件\n")

    load_env()

    # 步骤1: 检查配置
    if not check_config():
        print("\n" + "=" * 50)
        print("⛔ 测试终止，请先完善 .env 配置")
        print("=" * 50)
        sys.exit(1)

    # 步骤2: 测试 SMTP 连接
    if not test_smtp_connection():
        print("\n" + "=" * 50)
        print("⛔ 测试终止，SMTP 连接失败")
        print("=" * 50)
        sys.exit(1)

    # 步骤3: 发送测试邮件
    print("\n" + "-" * 50)
    choice = input("  是否发送测试邮件? (y/n): ").strip().lower()
    if choice in ('y', 'yes', '是'):
        if send_test_email():
            print("\n" + "=" * 50)
            print("🎉 全部测试通过！邮件功能已就绪")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("⚠️ 连接成功但发送失败，请检查配置")
            print("=" * 50)
            sys.exit(1)
    else:
        print("\n  已跳过邮件发送测试")
        print("\n" + "=" * 50)
        print("✅ SMTP 连接测试通过")
        print("=" * 50)


if __name__ == '__main__':
    main()
