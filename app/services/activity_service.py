from app.models.activity import Activity, ActivitySession, ActivityTemplate
from app.extensions import db
from app.utils.exceptions import NotFoundError, AuthorizationError, ValidationError
from app.models.organization import OrgMember


def create_activity(user_id, org_id, title, description=None, cover_url=None, location=None,
                    start_time=None, end_time=None, registration_start=None, registration_end=None,
                    max_participants=0, sessions=None, form_fields=None, template_id=None):
    """创建活动

    Args:
        form_fields: 报名表单字段定义，如 [
            {"name": "姓名", "type": "text", "required": true},
            {"name": "手机号", "type": "phone", "required": true},
            {"name": "公司", "type": "text", "required": false}
        ]
        template_id: 活动模板ID（可选）
    """
    from app.models.registration import RegistrationForm
    from app.models.activity import ActivityTemplate

    # 校验组织权限
    member = OrgMember.query.filter_by(org_id=org_id, user_id=user_id, status='active').first()
    if not member or member.role not in ['owner', 'admin']:
        raise AuthorizationError('无权创建活动')

    # 如果指定了模板，读取模板的默认配置
    template_default_form = None
    template_description = None
    if template_id:
        template = ActivityTemplate.query.get(template_id)
        if template and template.org_id == org_id:
            template_default_form = template.default_form
            template_description = template.description

    activity = Activity(
        org_id=org_id,
        template_id=template_id,
        title=title,
        description=description or template_description,
        cover_url=cover_url,
        location=location,
        start_time=start_time,
        end_time=end_time,
        registration_start=registration_start,
        registration_end=registration_end,
        max_participants=max_participants,
        created_by=user_id,
        status='draft'
    )
    db.session.add(activity)
    db.session.flush()

    # 创建场次
    if sessions:
        for session_data in sessions:
            session = ActivitySession(
                activity_id=activity.id,
                name=session_data.get('name', '默认场次'),
                start_time=session_data.get('start_time', start_time),
                end_time=session_data.get('end_time', end_time),
                location=session_data.get('location', location),
                max_participants=session_data.get('max_participants', max_participants)
            )
            db.session.add(session)

    # 创建报名表单定义
    # 优先使用传入的 form_fields，其次使用模板的 default_form
    final_form_fields = form_fields if form_fields is not None else template_default_form
    if final_form_fields:
        reg_form = RegistrationForm(
            activity_id=activity.id,
            fields=final_form_fields
        )
        db.session.add(reg_form)

    db.session.commit()
    return activity


def publish_activity(activity_id, user_id):
    """发布活动（提交审核或直接发布）"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    # 校验权限
    member = OrgMember.query.filter_by(org_id=activity.org_id, user_id=user_id, status='active').first()
    if not member or member.role not in ['owner', 'admin']:
        raise AuthorizationError('无权发布活动')

    if activity.status != 'draft':
        raise ValidationError('只有草稿状态的活动可以发布')

    activity.status = 'pending'  # 首期先进入待审核状态
    db.session.commit()
    return activity


def list_activities(org_id=None, status=None, page=1, per_page=20):
    """活动列表查询"""
    query = Activity.query
    if org_id:
        query = query.filter_by(org_id=org_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        'items': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }


def update_activity(activity_id, user_id, title=None, description=None, cover_url=None,
                    location=None, start_time=None, end_time=None,
                    registration_start=None, registration_end=None, max_participants=None):
    """更新活动"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    # 校验权限
    member = OrgMember.query.filter_by(org_id=activity.org_id, user_id=user_id, status='active').first()
    if not member or member.role not in ['owner', 'admin']:
        raise AuthorizationError('无权更新该活动')

    if title is not None:
        activity.title = title
    if description is not None:
        activity.description = description
    if cover_url is not None:
        activity.cover_url = cover_url
    if location is not None:
        activity.location = location
    if start_time is not None:
        activity.start_time = start_time
    if end_time is not None:
        activity.end_time = end_time
    if registration_start is not None:
        activity.registration_start = registration_start
    if registration_end is not None:
        activity.registration_end = registration_end
    if max_participants is not None:
        activity.max_participants = max_participants

    db.session.commit()
    return activity


def delete_activity(activity_id, user_id):
    """删除活动"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    # 校验权限
    member = OrgMember.query.filter_by(org_id=activity.org_id, user_id=user_id, status='active').first()
    if not member or member.role not in ['owner', 'admin']:
        raise AuthorizationError('无权删除该活动')

    db.session.delete(activity)
    db.session.commit()


def get_activity_detail(activity_id):
    """获取活动详情"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    result = activity.to_dict()
    result['sessions'] = [s.to_dict() for s in activity.sessions]
    return result
