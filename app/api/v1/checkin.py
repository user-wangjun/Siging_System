from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import checkin_service
from app.utils.response import success, error
from app.utils.exceptions import APIException

bp = Blueprint('checkin', __name__)


@bp.route('/qrcode', methods=['POST'])
@jwt_required()
def checkin_qrcode():
    """二维码签到"""
    operator_id = int(get_jwt_identity())
    data = request.get_json()
    checkin_code = data.get('checkin_code')
    location_info = data.get('location_info')

    if not checkin_code:
        return error(message='签到码不能为空')

    result = checkin_service.checkin_by_qrcode(checkin_code, operator_id, location_info)
    return success(data=result.to_dict())


@bp.route('/manual', methods=['POST'])
@jwt_required()
def checkin_manual():
    """手动搜索签到"""
    operator_id = int(get_jwt_identity())
    data = request.get_json()
    activity_id = data.get('activity_id')
    keyword = data.get('keyword')

    if not activity_id or not keyword:
        return error(message='活动ID和搜索关键词不能为空')

    result = checkin_service.checkin_by_manual(activity_id, keyword, operator_id)
    return success(data=result)


@bp.route('/activities/<int:activity_id>/stats', methods=['GET'])
@jwt_required()
def checkin_stats(activity_id):
    """签到统计"""
    stats = checkin_service.get_checkin_stats(activity_id)
    return success(data=stats)
