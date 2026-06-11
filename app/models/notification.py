from app.extensions import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.Enum('sms', 'email', 'in_app', name='notification_type'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'sent', 'failed', 'read', name='notification_status'), default='pending')
    sent_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class NotificationTemplate(db.Model):
    __tablename__ = 'notification_templates'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    org_id = db.Column(db.BigInteger, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum('sms', 'email', 'in_app', name='template_type'), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    content_template = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
