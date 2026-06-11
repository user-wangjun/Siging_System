import random
import string
from flask import current_app
from flask_mail import Message
from app.extensions import mail, get_redis_client


def generate_verification_code(length=6):
    """生成数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(to_email: str, code: str):
    """发送验证码邮件"""
    subject = "【WaytoAGI】邮箱验证码"
    body = f"""
您好，

您的验证码是：{code}

该验证码 30 分钟内有效，请勿泄露给他人。

如非本人操作，请忽略此邮件。

WaytoAGI 团队
"""
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    mail.send(msg)


def get_email_code_key(email: str) -> str:
    """获取验证码 Redis Key"""
    return f"email:code:{email.lower()}"


def get_email_limit_key(email: str) -> str:
    """获取发送频率限制 Redis Key"""
    return f"email:limit:{email.lower()}"


def store_verification_code(email: str, code: str, expire_seconds: int = 1800):
    """将验证码存入 Redis"""
    key = get_email_code_key(email)
    get_redis_client().setex(key, expire_seconds, code)


def get_stored_code(email: str) -> str | None:
    """从 Redis 获取验证码"""
    key = get_email_code_key(email)
    code = get_redis_client().get(key)
    return code.decode('utf-8') if code else None


def delete_stored_code(email: str):
    """删除已使用的验证码"""
    key = get_email_code_key(email)
    get_redis_client().delete(key)


def check_send_limit(email: str, interval_seconds: int = 60) -> bool:
    """
    检查是否超过发送频率限制
    返回 True 表示可以发送，False 表示受限
    """
    key = get_email_limit_key(email)
    if get_redis_client().exists(key):
        return False
    get_redis_client().setex(key, interval_seconds, '1')
    return True


def get_remaining_ttl(email: str) -> int:
    """获取发送限制剩余时间（秒）"""
    key = get_email_limit_key(email)
    ttl = get_redis_client().ttl(key)
    return ttl if ttl and ttl > 0 else 0
