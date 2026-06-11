from app.models.registration import Registration, RegistrationForm
from app.models.activity import Activity, ActivitySession
from app.extensions import db
from app.utils.exceptions import NotFoundError, ConflictError, ValidationError
from app.services import notification_service
import secrets


def generate_checkin_code():
    """生成唯一签到码"""
    return secrets.token_urlsafe(16)


def submit_registration(user_id, activity_id, form_data, session_id=None):
    """提交报名"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    if activity.status != 'published':
        raise ValidationError('活动未开放报名')

    # 检查是否已报名
    existing = Registration.query.filter_by(activity_id=activity_id, user_id=user_id).first()
    if existing:
        raise ConflictError('您已报名该活动')

    # 名额控制
    if activity.max_participants > 0 and activity.current_count >= activity.max_participants:
        status = 'waitlist'
    else:
        status = 'approved'
        activity.current_count += 1

    registration = Registration(
        activity_id=activity_id,
        session_id=session_id,
        user_id=user_id,
        form_data=form_data,
        status=status,
        checkin_code=generate_checkin_code()
    )
    db.session.add(registration)
    db.session.commit()

    # 发送通知：报名成功
    try:
        notification_service.notify_registration_success(user_id, activity.title)
    except Exception:
        pass  # 通知失败不影响主流程

    return registration


def cancel_registration(user_id, registration_id):
    """取消报名"""
    registration = Registration.query.get(registration_id)
    if not registration:
        raise NotFoundError('报名记录不存在')

    if registration.user_id != user_id:
        raise ValidationError('无权取消该报名')

    if registration.status == 'approved':
        # 回退名额
        activity = Activity.query.get(registration.activity_id)
        if activity:
            activity.current_count = max(0, activity.current_count - 1)

    registration.status = 'cancelled'
    db.session.commit()
    return registration


def audit_registration(operator_id, registration_id, new_status):
    """审核报名"""
    registration = Registration.query.get(registration_id)
    if not registration:
        raise NotFoundError('报名记录不存在')

    # 校验权限：只有活动所在组织的 owner/admin 可以审核
    activity = Activity.query.get(registration.activity_id)
    if activity:
        from app.models.organization import OrgMember
        member = OrgMember.query.filter_by(
            org_id=activity.org_id, user_id=operator_id, status='active'
        ).first()
        if not member or member.role not in ['owner', 'admin']:
            raise AuthorizationError('无权审核该报名')

    if new_status == 'approved' and registration.status != 'approved':
        if activity and activity.max_participants > 0:
            if activity.current_count >= activity.max_participants:
                raise ValidationError('活动名额已满')
            activity.current_count += 1

    registration.status = new_status
    db.session.commit()

    # 发送通知：审核结果
    try:
        if activity:
            notification_service.notify_registration_audited(
                user_id=registration.user_id,
                activity_title=activity.title,
                approved=(new_status == 'approved')
            )
    except Exception:
        pass

    return registration


def get_activity_registrations(activity_id, page=1, per_page=20):
    """获取活动报名列表"""
    pagination = Registration.query.filter_by(activity_id=activity_id).order_by(
        Registration.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }
