"""
活动模板 API
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import template_service
from app.utils.response import success, error
from app.utils.exceptions import APIException

bp = Blueprint('template', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_template():
    """创建活动模板"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    template = template_service.create_template(
        user_id=user_id,
        org_id=data.get('org_id'),
        name=data.get('name'),
        description=data.get('description'),
        default_form=data.get('default_form')
    )
    return success(data=template.to_dict())


@bp.route('/org/<int:org_id>', methods=['GET'])
@jwt_required()
def list_templates(org_id):
    """获取组织模板列表"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = template_service.get_org_templates(org_id, user_id, page, per_page)
    return success(data=result)


@bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """获取模板详情"""
    user_id = int(get_jwt_identity())
    template = template_service.get_template_detail(template_id, user_id)
    return success(data=template.to_dict())


@bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """更新模板"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    template = template_service.update_template(
        template_id=template_id,
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description'),
        default_form=data.get('default_form')
    )
    return success(data=template.to_dict())


@bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """删除模板"""
    user_id = int(get_jwt_identity())
    template_service.delete_template(template_id, user_id)
    return success(message='模板已删除')


@bp.route('/<int:template_id>/apply/<int:activity_id>', methods=['POST'])
@jwt_required()
def apply_template(template_id, activity_id):
    """将模板应用到活动"""
    user_id = int(get_jwt_identity())
    activity = template_service.apply_template_to_activity(template_id, activity_id, user_id)
    return success(data=activity.to_dict())
