from app.models.user import User, UserAuth
from app.extensions import db
from app.utils.exceptions import AuthenticationError, ValidationError, ConflictError
from app.utils.email_sender import (
    generate_verification_code,
    send_verification_email,
    store_verification_code,
    get_stored_code,
    delete_stored_code,
    check_send_limit,
    get_remaining_ttl,
)
from app.utils.validators import validate_email
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import current_app


def send_email_code(email: str):
    """发送邮箱验证码"""
    # 校验邮箱格式
    if not email or not validate_email(email):
        raise ValidationError('邮箱格式不正确')

    # 频率限制检查
    interval = current_app.config.get('EMAIL_SEND_INTERVAL_SECONDS', 60)
    if not check_send_limit(email, interval):
        remaining = get_remaining_ttl(email)
        raise ValidationError(f'发送过于频繁，请 {remaining} 秒后再试')

    # 生成验证码
    code = generate_verification_code(6)

    # 存入 Redis（30分钟有效）
    expire = current_app.config.get('EMAIL_CODE_EXPIRE_SECONDS', 1800)
    store_verification_code(email, code, expire)

    # 发送邮件
    try:
        send_verification_email(email, code)
    except Exception as e:
        current_app.logger.error(f"发送邮件失败: {e}")
        # 发送失败时清理 Redis，允许用户重试
        delete_stored_code(email)
        raise ValidationError('邮件发送失败，请稍后重试')

    return {'message': '验证码已发送', 'expire_seconds': expire}


def verify_email_code(email: str, code: str):
    """校验邮箱验证码"""
    if not email or not code:
        raise ValidationError('邮箱和验证码不能为空')

    stored_code = get_stored_code(email)
    if not stored_code:
        raise AuthenticationError('验证码已过期或不存在')

    if stored_code != code.strip():
        raise AuthenticationError('验证码错误')

    return True


def register_or_login_by_email(email: str, code: str, nickname: str = None):
    """
    邮箱验证码注册/登录
    - 若邮箱已存在且已验证，则登录
    - 若邮箱不存在，则自动注册
    """
    # 校验验证码
    verify_email_code(email, code)

    # 查找用户
    user = User.query.filter_by(email=email).first()

    if user:
        # 用户存在，检查状态
        if user.status == 0:
            raise AuthenticationError('账号已被禁用')
    else:
        # 新用户注册
        if not nickname:
            nickname = f"用户{email.split('@')[0]}"

        user = User(
            email=email,
            nickname=nickname,
            status=1,
            role='user'
        )
        db.session.add(user)
        db.session.flush()

        # 创建 email 认证记录
        auth = UserAuth(
            user_id=user.id,
            auth_type='email',
            auth_key=email.lower(),
            auth_secret=None
        )
        db.session.add(auth)
        db.session.commit()

    # 删除已使用的验证码（防止重放攻击）
    delete_stored_code(email)

    # 生成 JWT
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }


def refresh_access_token(user_id: str):
    """刷新访问令牌"""
    access_token = create_access_token(identity=user_id)
    return {'access_token': access_token}
