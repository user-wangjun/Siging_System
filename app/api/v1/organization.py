from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import org_service
from app.utils.response import success, error
from app.utils.exceptions import APIException

bp = Blueprint('organization', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_org():
    """创建组织"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name')
    if not name:
        return error(message='组织名称不能为空')

    org = org_service.create_org(
        user_id=user_id,
        name=name,
        description=data.get('description'),
        logo_url=data.get('logo_url')
    )
    return success(data=org.to_dict())


@bp.route('', methods=['GET'])
@jwt_required()
def list_orgs():
    """获取我的组织列表"""
    user_id = int(get_jwt_identity())
    orgs = org_service.get_user_orgs(user_id)
    return success(data=[o.to_dict() for o in orgs])


@bp.route('/<int:org_id>', methods=['GET'])
@jwt_required()
def get_org(org_id):
    """获取组织详情"""
    user_id = int(get_jwt_identity())
    org = org_service.get_org_detail(org_id, user_id)
    return success(data=org.to_dict())


@bp.route('/<int:org_id>', methods=['PUT'])
@jwt_required()
def update_org(org_id):
    """更新组织信息"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    org = org_service.update_org(
        org_id=org_id,
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description'),
        logo_url=data.get('logo_url')
    )
    return success(data=org.to_dict())


@bp.route('/<int:org_id>', methods=['DELETE'])
@jwt_required()
def delete_org(org_id):
    """解散组织"""
    user_id = int(get_jwt_identity())
    org_service.delete_org(org_id, user_id)
    return success(message='组织已解散')


@bp.route('/<int:org_id>/members', methods=['POST'])
@jwt_required()
def invite_member(org_id):
    """邀请成员"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    invitee_id = data.get('user_id')
    role = data.get('role', 'member')

    member = org_service.invite_member(org_id, user_id, invitee_id, role)
    return success(data=member.to_dict())


@bp.route('/<int:org_id>/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(org_id, member_id):
    """更新成员角色"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    new_role = data.get('role')

    member = org_service.update_member_role(org_id, user_id, member_id, new_role)
    return success(data=member.to_dict())


@bp.route('/<int:org_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_member(org_id, member_id):
    """移除成员"""
    user_id = int(get_jwt_identity())
    member = org_service.remove_member(org_id, user_id, member_id)
    return success(data=member.to_dict())
