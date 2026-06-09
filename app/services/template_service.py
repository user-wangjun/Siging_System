"""
活动模板管理服务
"""

from app.models.activity import ActivityTemplate, Activity
from app.models.organization import OrgMember
from app.extensions import db
from app.utils.exceptions import NotFoundError, AuthorizationError, ValidationError


def create_template(user_id, org_id, name, description=None, default_form=None):
    """创建活动模板"""
    # 校验权限
    member = OrgMember.query.filter_by(org_id=org_id, user_id=user_id, status='active').first()
    if not member or member.role not in ['owner', 'admin']:
        raise AuthorizationError('无权创建模板')

    if not name or not name.strip():
        raise ValidationError('模板名称不能为空')

    template = ActivityTemplate(
        org_id=org_id,
        name=name.strip(),
        description=description,
        default_form=default_form,
        created_by=user_id
    )
    db.session.add(template)
    db.session.commit()
    return template


def get_org_templates(org_id, user_id, page=1, per_page=20):
    """获取组织下的模板列表"""
    # 校验权限
    member = OrgMember.query.filter_by(org_id=org_id, user_id=user_id, status='active').first()
    if not member:
        raise AuthorizationError('无权查看该组织的模板')

    pagination = ActivityTemplate.query.filter_by(org_id=org_id).order_by(
        ActivityTemplate.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': [t.to_dict() for t in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }


def get_template_detail(template_id, user_id):
    """获取模板详情"""
    template = ActivityTemplate.query.get(template_id)
    if not template:
        raise NotFoundError('模板不存在')

    # 校验权限
    member = OrgMember.query.filter_by(org_id=template.org_id, user_id=user_id, status='active').first()
    if not member:
        raise AuthorizationError('无权查看该模板')

    return template


def update_template(template_id, user_id, name=None, description=None, default_form=None):
    """更新模板"""
    template = ActivityTemplate.query.get(template_id)
    if not template:
        raise NotFoundError('模板不存在')

    # 只有创建者或组织 owner/admin 可以更新
    member = OrgMember.query.filter_by(org_id=template.org_id, user_id=user_id, status='active').first()
    if not member or (member.role not in ['owner', 'admin'] and template.created_by != user_id):
        raise AuthorizationError('无权更新该模板')

    if name is not None:
        template.name = name.strip()
    if description is not None:
        template.description = description
    if default_form is not None:
        template.default_form = default_form

    db.session.commit()
    return template


def delete_template(template_id, user_id):
    """删除模板"""
    template = ActivityTemplate.query.get(template_id)
    if not template:
        raise NotFoundError('模板不存在')

    # 只有创建者或组织 owner/admin 可以删除
    member = OrgMember.query.filter_by(org_id=template.org_id, user_id=user_id, status='active').first()
    if not member or (member.role not in ['owner', 'admin'] and template.created_by != user_id):
        raise AuthorizationError('无权删除该模板')

    db.session.delete(template)
    db.session.commit()


def apply_template_to_activity(template_id, activity_id, user_id):
    """将模板应用到活动（复制模板的默认表单配置）"""
    template = ActivityTemplate.query.get(template_id)
    if not template:
        raise NotFoundError('模板不存在')

    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    # 校验权限
    member = OrgMember.query.filter_by(org_id=activity.org_id, user_id=user_id, status='active').first()
    if not member or member.role not in ['owner', 'admin']:
        raise AuthorizationError('无权操作')

    # 关联模板
    activity.template_id = template_id

    # 如果活动没有描述，复制模板的描述
    if not activity.description and template.description:
        activity.description = template.description

    db.session.commit()
    return activity
