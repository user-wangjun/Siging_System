from app.models.user import User
from app.extensions import db
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.validators import validate_phone


def update_user_profile(user_id, nickname=None, phone=None, real_name=None, avatar_url=None):
    """更新用户个人资料"""
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('用户不存在')

    if nickname is not None:
        user.nickname = nickname

    if phone is not None:
        if phone and not validate_phone(phone):
            raise ValidationError('手机号格式不正确')
        # 检查手机号是否已被其他用户使用
        if phone:
            existing = User.query.filter(User.phone == phone, User.id != user_id).first()
            if existing:
                raise ValidationError('该手机号已被使用')
        user.phone = phone

    if real_name is not None:
        user.real_name = real_name

    if avatar_url is not None:
        user.avatar_url = avatar_url

    db.session.commit()
    return user
