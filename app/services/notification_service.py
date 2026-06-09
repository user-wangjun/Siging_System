from app.models.notification import Notification, NotificationTemplate
from app.extensions import db
from app.utils.exceptions import NotFoundError, ValidationError
from datetime import datetime


def create_notification(user_id, notification_type, title, content, commit=True):
    """创建通知记录

    Args:
        user_id: 接收通知的用户ID
        notification_type: 通知类型 ('sms', 'email', 'in_app')
        title: 通知标题
        content: 通知内容
        commit: 是否立即提交（批量创建时设为 False，统一提交）
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        content=content,
        status='pending'
    )
    db.session.add(notification)
    if commit:
        db.session.commit()
    return notification


def get_user_notifications(user_id, page=1, per_page=20):
    """获取用户通知列表"""
    pagination = Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': [n.to_dict() for n in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }


def mark_as_read(notification_id, user_id):
    """标记通知为已读"""
    notification = Notification.query.get(notification_id)
    if not notification:
        raise NotFoundError('通知不存在')

    if notification.user_id != user_id:
        raise ValidationError('无权操作')

    notification.status = 'read'
    notification.read_at = datetime.utcnow()
    db.session.commit()
    return notification


def mark_all_as_read(user_id):
    """标记用户所有未读通知为已读"""
    db.session.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.status != 'read'
    ).update({'status': 'read', 'read_at': datetime.utcnow()}, synchronize_session=False)
    db.session.commit()


def get_unread_count(user_id):
    """获取用户未读通知数量"""
    return Notification.query.filter(
        Notification.user_id == user_id,
        Notification.status != 'read'
    ).count()


# ========== 业务通知便捷方法 ==========

def notify_registration_success(user_id, activity_title):
    """通知用户：报名成功"""
    create_notification(
        user_id=user_id,
        notification_type='in_app',
        title='报名成功',
        content=f'您已成功报名活动「{activity_title}」，请留意活动开始时间。'
    )


def notify_registration_audited(user_id, activity_title, approved):
    """通知用户：报名审核结果"""
    if approved:
        create_notification(
            user_id=user_id,
            notification_type='in_app',
            title='报名通过',
            content=f'您报名的活动「{activity_title}」已通过审核，请准时参加。'
        )
    else:
        create_notification(
            user_id=user_id,
            notification_type='in_app',
            title='报名未通过',
            content=f'很遗憾，您报名的活动「{activity_title}」未通过审核。'
        )


def notify_activity_audited(user_id, activity_title, approved, reason=None):
    """通知组织者：活动审核结果"""
    if approved:
        create_notification(
            user_id=user_id,
            notification_type='in_app',
            title='活动审核通过',
            content=f'您创建的活动「{activity_title}」已通过审核，现已对外发布。'
        )
    else:
        content = f'您创建的活动「{activity_title}」未通过审核。'
        if reason:
            content += f' 原因：{reason}'
        create_notification(
            user_id=user_id,
            notification_type='in_app',
            title='活动审核未通过',
            content=content
        )


def notify_org_invite(user_id, org_name, inviter_name):
    """通知用户：被邀请加入组织"""
    create_notification(
        user_id=user_id,
        notification_type='in_app',
        title='组织邀请',
        content=f'「{inviter_name}」邀请您加入组织「{org_name}」，请前往组织页面查看。'
    )


def notify_checkin_success(user_id, activity_title):
    """通知用户：签到成功"""
    create_notification(
        user_id=user_id,
        notification_type='in_app',
        title='签到成功',
        content=f'您已在活动「{activity_title}」中完成签到。'
    )


def notify_activity_cancelled(user_id, activity_title):
    """通知用户：活动取消"""
    create_notification(
        user_id=user_id,
        notification_type='in_app',
        title='活动取消',
        content=f'活动「{activity_title}」已被取消，敬请谅解。'
    )
