from app.models.organization import Organization, OrgMember
from app.models.user import User
from app.extensions import db
from app.utils.exceptions import NotFoundError, AuthorizationError, ConflictError
from app.services import notification_service
from datetime import datetime


def create_org(user_id, name, description=None, logo_url=None):
    """创建组织，创建者自动成为 owner"""
    org = Organization(
        name=name,
        description=description,
        logo_url=logo_url,
        owner_id=user_id,
        status='active'
    )
    db.session.add(org)
    db.session.flush()

    # 创建者自动加入为 owner
    member = OrgMember(
        org_id=org.id,
        user_id=user_id,
        role='owner',
        status='active',
        joined_at=datetime.utcnow()
    )
    db.session.add(member)
    db.session.commit()

    return org


def get_user_orgs(user_id):
    """获取用户所属组织列表"""
    memberships = OrgMember.query.filter_by(user_id=user_id, status='active').all()
    org_ids = [m.org_id for m in memberships]
    return Organization.query.filter(Organization.id.in_(org_ids)).all()


def update_org(org_id, user_id, name=None, description=None, logo_url=None):
    """更新组织信息"""
    org = Organization.query.get(org_id)
    if not org:
        raise NotFoundError('组织不存在')

    # 只有 owner 可以更新
    member = OrgMember.query.filter_by(org_id=org_id, user_id=user_id, status='active').first()
    if not member or member.role != 'owner':
        raise AuthorizationError('只有组织所有者可以更新组织信息')

    if name is not None:
        org.name = name
    if description is not None:
        org.description = description
    if logo_url is not None:
        org.logo_url = logo_url

    db.session.commit()
    return org


def delete_org(org_id, user_id):
    """解散组织"""
    org = Organization.query.get(org_id)
    if not org:
        raise NotFoundError('组织不存在')

    # 只有 owner 可以解散
    member = OrgMember.query.filter_by(org_id=org_id, user_id=user_id, status='active').first()
    if not member or member.role != 'owner':
        raise AuthorizationError('只有组织所有者可以解散组织')

    db.session.delete(org)
    db.session.commit()


def get_org_detail(org_id, user_id):
    """获取组织详情，校验成员权限"""
    org = Organization.query.get(org_id)
    if not org:
        raise NotFoundError('组织不存在')

    member = OrgMember.query.filter_by(org_id=org_id, user_id=user_id, status='active').first()
    if not member:
        raise AuthorizationError('无权访问该组织')

    return org


def invite_member(org_id, inviter_id, invitee_id, role='member'):
    """邀请成员加入组织"""
    # 校验邀请人权限
    inviter = OrgMember.query.filter_by(org_id=org_id, user_id=inviter_id, status='active').first()
    if not inviter or inviter.role not in ['owner', 'admin']:
        raise AuthorizationError('无权邀请成员')

    # 检查是否已是成员
    existing = OrgMember.query.filter_by(org_id=org_id, user_id=invitee_id).first()
    if existing:
        raise ConflictError('该用户已是组织成员')

    member = OrgMember(
        org_id=org_id,
        user_id=invitee_id,
        role=role,
        status='invited',
        invited_by=inviter_id
    )
    db.session.add(member)
    db.session.commit()

    # 发送通知：组织邀请
    try:
        org = Organization.query.get(org_id)
        inviter = User.query.get(inviter_id)
        if org and inviter:
            notification_service.notify_org_invite(
                user_id=invitee_id,
                org_name=org.name,
                inviter_name=inviter.nickname or inviter.email
            )
    except Exception:
        pass

    return member


def update_member_role(org_id, operator_id, target_user_id, new_role):
    """更新成员角色"""
    operator = OrgMember.query.filter_by(org_id=org_id, user_id=operator_id, status='active').first()
    if not operator or operator.role != 'owner':
        raise AuthorizationError('只有组织所有者可以修改角色')

    member = OrgMember.query.filter_by(org_id=org_id, user_id=target_user_id).first()
    if not member:
        raise NotFoundError('成员不存在')

    member.role = new_role
    db.session.commit()
    return member


def remove_member(org_id, operator_id, target_user_id):
    """移除成员"""
    operator = OrgMember.query.filter_by(org_id=org_id, user_id=operator_id, status='active').first()
    if not operator or operator.role not in ['owner', 'admin']:
        raise AuthorizationError('无权移除成员')

    member = OrgMember.query.filter_by(org_id=org_id, user_id=target_user_id).first()
    if not member:
        raise NotFoundError('成员不存在')

    member.status = 'removed'
    db.session.commit()
    return member
