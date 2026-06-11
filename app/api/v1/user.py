from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.utils.response import success, error

bp = Blueprint('user', __name__)


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取个人资料"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error(message='用户不存在', code=404, status_code=404)
    return success(data=user.to_dict())


@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    """更新个人资料"""
    user_id = get_jwt_identity()
    data = request.get_json()
    from app.services import user_service
    user = user_service.update_user_profile(
        user_id=user_id,
        nickname=data.get('nickname'),
        phone=data.get('phone'),
        real_name=data.get('real_name'),
        avatar_url=data.get('avatar_url')
    )
    return success(data=user.to_dict())


@bp.route('/me/registrations', methods=['GET'])
@jwt_required()
def my_registrations():
    """我的报名列表"""
    user_id = get_jwt_identity()
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    from app.models.registration import Registration
    from app.models.activity import Activity

    query = Registration.query.filter_by(user_id=user_id)

    if status and status != 'all':
        query = query.filter_by(status=status)

    pagination = query.order_by(Registration.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = []
    for r in pagination.items:
        activity = Activity.query.get(r.activity_id)
        item = r.to_dict()
        item['activity_title'] = activity.title if activity else '未知活动'
        item['activity_start_time'] = activity.start_time.isoformat() if activity and activity.start_time else None
        item['activity_location'] = activity.location if activity else None
        items.append(item)

    return success(data={
        'items': items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
