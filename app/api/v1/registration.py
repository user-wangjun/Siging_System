from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import registration_service
from app.utils.response import success, error
from app.utils.exceptions import APIException
from app.utils.qrcode_generator import generate_checkin_qrcode

bp = Blueprint('registration', __name__)


@bp.route('/activities/<int:activity_id>/register', methods=['POST'])
@jwt_required()
def register(activity_id):
    """提交报名"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    registration = registration_service.submit_registration(
        user_id=user_id,
        activity_id=activity_id,
        form_data=data.get('form_data', {}),
        session_id=data.get('session_id')
    )
    return success(data=registration.to_dict())


@bp.route('/registrations/<int:registration_id>/qrcode', methods=['GET'])
@jwt_required()
def get_qrcode(registration_id):
    """获取报名签到二维码"""
    from app.models.registration import Registration
    from app.models.activity import Activity

    user_id = int(get_jwt_identity())
    registration = Registration.query.get(registration_id)
    if not registration:
        return error(message='报名记录不存在', code=404, status_code=404)

    # 只能查看自己的二维码
    if registration.user_id != user_id:
        return error(message='无权查看', code=403, status_code=403)

    if registration.status != 'approved':
        return error(message='报名未通过审核，无法获取签到码', code=400, status_code=400)

    activity = Activity.query.get(registration.activity_id)
    activity_title = activity.title if activity else None

    qrcode_image = generate_checkin_qrcode(registration.checkin_code, activity_title)

    return success(data={
        'qrcode_image': qrcode_image,
        'checkin_code': registration.checkin_code
    })


@bp.route('/registrations/<int:registration_id>', methods=['GET'])
@jwt_required()
def get_registration(registration_id):
    """报名详情"""
    from app.models.registration import Registration
    registration = Registration.query.get(registration_id)
    if not registration:
        return error(message='报名记录不存在', code=404, status_code=404)
    return success(data=registration.to_dict())


@bp.route('/registrations/<int:registration_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(registration_id):
    """取消报名"""
    user_id = int(get_jwt_identity())
    registration = registration_service.cancel_registration(user_id, registration_id)
    return success(data=registration.to_dict())


@bp.route('/activities/<int:activity_id>/registrations', methods=['GET'])
@jwt_required()
def list_registrations(activity_id):
    """活动报名列表（组织者视角）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = registration_service.get_activity_registrations(activity_id, page, per_page)
    return success(data=result)


@bp.route('/registrations/<int:registration_id>/status', methods=['PUT'])
@jwt_required()
def audit_registration(registration_id):
    """审核报名"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    new_status = data.get('status')

    registration = registration_service.audit_registration(user_id, registration_id, new_status)
    return success(data=registration.to_dict())
