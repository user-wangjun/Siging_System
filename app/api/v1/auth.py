from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import auth_service
from app.utils.response import success, error
from app.utils.exceptions import APIException

bp = Blueprint('auth', __name__)


@bp.route('/email/code', methods=['POST'])
def send_email_code():
    """发送邮箱验证码"""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()

    if not email:
        return error(message='邮箱不能为空')

    try:
        result = auth_service.send_email_code(email)
        return success(data=result, message='验证码已发送')
    except APIException as e:
        return error(message=e.message, code=e.code, status_code=e.status_code)
    except Exception as e:
        return error(message='发送失败，请稍后重试', code=500, status_code=500)


@bp.route('/email/login', methods=['POST'])
def email_login():
    """邮箱验证码登录/注册"""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    code = data.get('code', '').strip()
    nickname = data.get('nickname', '').strip() or None

    if not email or not code:
        return error(message='邮箱和验证码不能为空')

    try:
        result = auth_service.register_or_login_by_email(email, code, nickname)
        return success(data=result, message='登录成功')
    except APIException as e:
        return error(message=e.message, code=e.code, status_code=e.status_code)
    except Exception as e:
        return error(message='登录失败，请稍后重试', code=500, status_code=500)


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    user_id = get_jwt_identity()
    result = auth_service.refresh_access_token(user_id)
    return success(data=result)


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取当前用户信息"""
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error(message='用户不存在', code=404, status_code=404)
    return success(data=user.to_dict())


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """登出（将当前 Access Token 加入黑名单）"""
    from flask_jwt_extended import get_jwt
    from app.extensions import get_redis_client
    from datetime import datetime, timezone

    jti = get_jwt()['jti']
    exp = get_jwt()['exp']
    now = datetime.now(timezone.utc).timestamp()
    ttl = int(exp - now)

    if ttl > 0:
        get_redis_client().setex(f"jwt:blacklist:{jti}", ttl, 'revoked')

    return success(message='登出成功')
