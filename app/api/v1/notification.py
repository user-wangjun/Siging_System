from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import notification_service
from app.utils.response import success, error
from app.utils.exceptions import APIException

bp = Blueprint('notification', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    """通知列表"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = notification_service.get_user_notifications(user_id, page, per_page)
    return success(data=result)


@bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    """未读通知数量"""
    user_id = int(get_jwt_identity())
    count = notification_service.get_unread_count(user_id)
    return success(data={'unread_count': count})


@bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """全部标记已读"""
    user_id = int(get_jwt_identity())
    notification_service.mark_all_as_read(user_id)
    return success(message='已全部标记为已读')


@bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    """标记已读"""
    user_id = int(get_jwt_identity())
    notification = notification_service.mark_as_read(notification_id, user_id)
    return success(data=notification.to_dict())
