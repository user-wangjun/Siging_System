from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.exceptions import AuthorizationError


def role_required(*roles):
    """角色权限校验装饰器"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            from app.models.user import User
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role not in roles:
                raise AuthorizationError('Permission denied')
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def org_permission_required(min_role='member'):
    """组织权限校验装饰器（需在视图函数中接收 org_id）"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            # 从 kwargs 或请求参数中获取 org_id
            org_id = kwargs.get('org_id')
            if not org_id:
                from flask import request
                org_id = request.view_args.get('org_id') if request.view_args else None
            if not org_id:
                org_id = request.args.get('org_id', type=int)
            if not org_id:
                org_id = request.get_json(silent=True) and request.get_json().get('org_id')

            if not org_id:
                raise AuthorizationError('缺少组织ID')

            from app.models.organization import OrgMember
            member = OrgMember.query.filter_by(
                org_id=org_id, user_id=user_id, status='active'
            ).first()

            if not member:
                raise AuthorizationError('无权访问该组织')

            role_levels = {'member': 1, 'admin': 2, 'owner': 3}
            if role_levels.get(member.role, 0) < role_levels.get(min_role, 1):
                raise AuthorizationError('权限不足')

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def activity_permission_required(min_role='admin'):
    """活动权限校验装饰器（校验用户是否为活动所在组织的 owner/admin）"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            from flask import request
            activity_id = kwargs.get('activity_id')
            if not activity_id:
                activity_id = request.view_args.get('activity_id') if request.view_args else None

            if not activity_id:
                raise AuthorizationError('缺少活动ID')

            from app.models.activity import Activity
            from app.models.organization import OrgMember

            activity = Activity.query.get(activity_id)
            if not activity:
                raise AuthorizationError('活动不存在')

            member = OrgMember.query.filter_by(
                org_id=activity.org_id, user_id=user_id, status='active'
            ).first()

            if not member:
                raise AuthorizationError('无权操作该活动')

            role_levels = {'member': 1, 'admin': 2, 'owner': 3}
            if role_levels.get(member.role, 0) < role_levels.get(min_role, 2):
                raise AuthorizationError('权限不足，需要管理员权限')

            return fn(*args, **kwargs)
        return wrapper
    return decorator
