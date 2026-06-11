from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import activity_service
from app.utils.response import success, error
from app.utils.exceptions import APIException

bp = Blueprint('activity', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_activity():
    """创建活动"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    activity = activity_service.create_activity(
        user_id=user_id,
        org_id=data.get('org_id'),
        title=data.get('title'),
        description=data.get('description'),
        cover_url=data.get('cover_url'),
        location=data.get('location'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        registration_start=data.get('registration_start'),
        registration_end=data.get('registration_end'),
        max_participants=data.get('max_participants', 0),
        sessions=data.get('sessions'),
        form_fields=data.get('form_fields'),
        template_id=data.get('template_id')
    )
    return success(data=activity.to_dict())


@bp.route('', methods=['GET'])
def list_activities():
    """活动列表"""
    org_id = request.args.get('org_id', type=int)
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = activity_service.list_activities(org_id, status, page, per_page)
    return success(data=result)


@bp.route('/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    """活动详情"""
    activity = activity_service.get_activity_detail(activity_id)
    return success(data=activity)


@bp.route('/<int:activity_id>', methods=['PUT'])
@jwt_required()
def update_activity(activity_id):
    """更新活动"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    activity = activity_service.update_activity(
        activity_id=activity_id,
        user_id=user_id,
        title=data.get('title'),
        description=data.get('description'),
        cover_url=data.get('cover_url'),
        location=data.get('location'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        registration_start=data.get('registration_start'),
        registration_end=data.get('registration_end'),
        max_participants=data.get('max_participants')
    )
    return success(data=activity.to_dict())


@bp.route('/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """取消/删除活动"""
    user_id = int(get_jwt_identity())
    activity_service.delete_activity(activity_id, user_id)
    return success(message='活动已删除')


@bp.route('/<int:activity_id>/publish', methods=['POST'])
@jwt_required()
def publish_activity(activity_id):
    """发布活动"""
    user_id = int(get_jwt_identity())
    activity = activity_service.publish_activity(activity_id, user_id)
    return success(data=activity.to_dict())
