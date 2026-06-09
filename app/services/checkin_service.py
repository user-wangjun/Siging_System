from app.models.checkin import CheckinLog
from app.models.registration import Registration
from app.models.activity import Activity
from app.extensions import db
from app.utils.exceptions import NotFoundError, ValidationError
from app.services import notification_service
from datetime import datetime


def checkin_by_qrcode(checkin_code, operator_id, location_info=None):
    """扫码签到"""
    registration = Registration.query.filter_by(checkin_code=checkin_code).first()
    if not registration:
        raise NotFoundError('无效的签到码')

    if registration.status != 'approved':
        raise ValidationError('报名未通过审核')

    if registration.checked_in:
        raise ValidationError('已签到，请勿重复签到')

    activity = Activity.query.get(registration.activity_id)
    if activity and activity.status not in ['published', 'ongoing']:
        raise ValidationError('活动未开始或已结束')

    # 校验权限：只有活动所在组织的 owner/admin 可以执行签到
    if activity:
        from app.models.organization import OrgMember
        from app.utils.exceptions import AuthorizationError
        member = OrgMember.query.filter_by(
            org_id=activity.org_id, user_id=operator_id, status='active'
        ).first()
        if not member or member.role not in ['owner', 'admin']:
            raise AuthorizationError('无权执行签到')

    registration.checked_in = 1
    registration.checked_in_at = datetime.utcnow()
    registration.checked_in_by = operator_id

    log = CheckinLog(
        activity_id=registration.activity_id,
        registration_id=registration.id,
        user_id=registration.user_id,
        checkin_type='qrcode',
        operator_id=operator_id,
        location_info=location_info
    )

    db.session.add(log)
    db.session.commit()

    # 发送通知：签到成功
    try:
        if activity:
            notification_service.notify_checkin_success(registration.user_id, activity.title)
    except Exception:
        pass

    return log


def checkin_by_manual(activity_id, keyword, operator_id):
    """手动搜索签到（按姓名/手机号）"""
    from app.models.user import User
    from app.models.organization import OrgMember
    from app.utils.exceptions import AuthorizationError

    # 校验权限：只有活动所在组织的 owner/admin 可以执行手动签到
    activity = Activity.query.get(activity_id)
    if activity:
        member = OrgMember.query.filter_by(
            org_id=activity.org_id, user_id=operator_id, status='active'
        ).first()
        if not member or member.role not in ['owner', 'admin']:
            raise AuthorizationError('无权执行签到')

    # 搜索报名用户
    query = db.session.query(Registration, User).join(
        User, Registration.user_id == User.id
    ).filter(
        Registration.activity_id == activity_id,
        Registration.status == 'approved',
        Registration.checked_in == 0
    )

    # 按手机号后4位或姓名搜索
    registrations = query.filter(
        db.or_(
            User.phone.like(f'%{keyword}'),
            User.real_name.contains(keyword)
        )
    ).all()

    if not registrations:
        raise NotFoundError('未找到匹配的报名记录')

    # 如果只有一个结果，直接签到
    if len(registrations) == 1:
        registration, user = registrations[0]
        registration.checked_in = 1
        registration.checked_in_at = datetime.utcnow()
        registration.checked_in_by = operator_id

        log = CheckinLog(
            registration_id=registration.id,
            activity_id=activity_id,
            user_id=user.id,
            checkin_type='manual',
            operator_id=operator_id
        )
        db.session.add(log)
        db.session.commit()

        # 发送通知：签到成功
        try:
            activity = Activity.query.get(activity_id)
            if activity:
                notification_service.notify_checkin_success(user.id, activity.title)
        except Exception:
            pass

        return log

    # 多个结果返回列表供选择
    return {
        'multiple': True,
        'options': [
            {
                'registration_id': r.Registration.id,
                'user_name': r.User.real_name or r.User.nickname,
                'phone': r.User.phone,
                'form_data': r.Registration.form_data
            }
            for r in registrations
        ]
    }


def get_checkin_stats(activity_id):
    """获取活动签到统计"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    total_registrations = Registration.query.filter_by(activity_id=activity_id, status='approved').count()
    total_checkins = CheckinLog.query.filter_by(activity_id=activity_id).count()

    return {
        'activity_id': activity_id,
        'total_registrations': total_registrations,
        'total_checkins': total_checkins,
        'checkin_rate': round(total_checkins / total_registrations * 100, 2) if total_registrations > 0 else 0
    }
