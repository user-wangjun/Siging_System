from app.models.activity import Activity
from app.models.user import User
from app.models.checkin import CheckinLog
from app.models.registration import Registration
from app.extensions import db
from app.utils.exceptions import NotFoundError, AuthorizationError
from app.services import notification_service


def get_pending_activities(page=1, per_page=20):
    """获取待审核活动列表"""
    pagination = Activity.query.filter_by(status='pending').order_by(
        Activity.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }


def audit_activity(activity_id, operator_id, action, reason=None):
    """审核活动"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise NotFoundError('活动不存在')

    if action == 'approve':
        activity.status = 'published'
    elif action == 'reject':
        activity.status = 'draft'
    elif action == 'suspend':
        activity.status = 'cancelled'

    db.session.commit()

    # 发送通知：审核结果
    try:
        notification_service.notify_activity_audited(
            user_id=activity.created_by,
            activity_title=activity.title,
            approved=(action == 'approve'),
            reason=reason
        )
    except Exception:
        pass

    return activity


def get_platform_stats():
    """获取平台统计数据"""
    total_users = User.query.count()
    total_activities = Activity.query.count()
    total_registrations = Registration.query.count()
    total_checkins = CheckinLog.query.count()

    # 计算签到率
    approved_registrations = Registration.query.filter_by(status='approved').count()
    checkin_rate = round(total_checkins / approved_registrations * 100, 2) if approved_registrations > 0 else 0

    return {
        'total_users': total_users,
        'total_activities': total_activities,
        'total_registrations': total_registrations,
        'total_checkins': total_checkins,
        'checkin_rate': checkin_rate,
    }


def get_users_list(page=1, per_page=20, status=None):
    """获取用户列表"""
    query = User.query
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        'items': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }


def update_user_status(user_id, new_status):
    """更新用户状态（禁用/启用）"""
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('用户不存在')

    user.status = new_status
    db.session.commit()
    return user
