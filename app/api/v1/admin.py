from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import admin_service
from app.utils.response import success, error
from app.utils.decorators import role_required
from app.utils.exceptions import APIException

bp = Blueprint('admin', __name__)


@bp.route('/activities/pending', methods=['GET'])
@jwt_required()
@role_required('platform_admin')
def pending_activities():
    """待审核活动列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = admin_service.get_pending_activities(page, per_page)
    return success(data=result)


@bp.route('/activities/<int:activity_id>/audit', methods=['PUT'])
@jwt_required()
@role_required('platform_admin')
def audit_activity(activity_id):
    """审核活动"""
    operator_id = int(get_jwt_identity())
    data = request.get_json()

    action = data.get('action')
    reason = data.get('reason')

    if action not in ['approve', 'reject', 'suspend']:
        return error(message='无效的审核操作')

    activity = admin_service.audit_activity(activity_id, operator_id, action, reason)
    return success(data=activity.to_dict())


@bp.route('/stats', methods=['GET'])
@jwt_required()
@role_required('platform_admin')
def platform_stats():
    """平台数据看板"""
    stats = admin_service.get_platform_stats()
    return success(data=stats)


@bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('platform_admin')
def users_list():
    """用户管理列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')

    result = admin_service.get_users_list(page, per_page, status)
    return success(data=result)


@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@role_required('platform_admin')
def update_user_status(user_id):
    """更新用户状态（禁用/启用）"""
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['active', 'inactive']:
        return error(message='无效的状态值，应为 active 或 inactive')

    user = admin_service.update_user_status(user_id, new_status)
    return success(data=user.to_dict())
