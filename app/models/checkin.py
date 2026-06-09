from app.extensions import db
from datetime import datetime


class CheckinLog(db.Model):
    __tablename__ = 'checkin_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.BigInteger, db.ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False)
    activity_id = db.Column(db.BigInteger, db.ForeignKey('activities.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    checkin_type = db.Column(db.Enum('qrcode', 'manual', name='checkin_type_enum'), nullable=False)
    operator_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    checkin_at = db.Column(db.DateTime, default=datetime.utcnow)
    location_info = db.Column(db.String(255), nullable=True)
    remark = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'registration_id': self.registration_id,
            'activity_id': self.activity_id,
            'user_id': self.user_id,
            'checkin_type': self.checkin_type,
            'operator_id': self.operator_id,
            'checkin_at': self.checkin_at.isoformat() if self.checkin_at else None,
            'location_info': self.location_info,
        }
