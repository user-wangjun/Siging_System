from app.extensions import db
from datetime import datetime
import secrets


class RegistrationForm(db.Model):
    __tablename__ = 'registration_forms'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.BigInteger, db.ForeignKey('activities.id', ondelete='CASCADE'), nullable=False)
    fields = db.Column(db.JSON, nullable=False, comment='表单字段定义(JSON Schema)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.BigInteger, db.ForeignKey('activities.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.BigInteger, db.ForeignKey('activity_sessions.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    form_data = db.Column(db.JSON, nullable=False)
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', 'cancelled', 'waitlist', name='reg_status'),
        default='pending'
    )
    checkin_code = db.Column(db.String(32), nullable=True, index=True)
    checked_in = db.Column(db.SmallInteger, default=0)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    checked_in_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('activity_id', 'user_id', name='uk_activity_user'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'form_data': self.form_data,
            'status': self.status,
            'checkin_code': self.checkin_code,
            'checked_in': self.checked_in,
            'checked_in_at': self.checked_in_at.isoformat() if self.checked_in_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
