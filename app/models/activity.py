from app.extensions import db
from datetime import datetime


class ActivityTemplate(db.Model):
    __tablename__ = 'activity_templates'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    org_id = db.Column(db.BigInteger, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    default_form = db.Column(db.JSON, nullable=True)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'name': self.name,
            'description': self.description,
            'default_form': self.default_form,
            'created_by': self.created_by,
        }


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    org_id = db.Column(db.BigInteger, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    template_id = db.Column(db.BigInteger, db.ForeignKey('activity_templates.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    registration_start = db.Column(db.DateTime, nullable=True)
    registration_end = db.Column(db.DateTime, nullable=True)
    max_participants = db.Column(db.Integer, default=0)
    current_count = db.Column(db.Integer, default=0)
    status = db.Column(
        db.Enum('draft', 'pending', 'published', 'ongoing', 'ended', 'cancelled', name='activity_status'),
        default='draft'
    )
    checkin_type = db.Column(db.Enum('qrcode', 'manual', 'both', name='checkin_type'), default='both')
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = db.relationship('ActivitySession', backref='activity', lazy='dynamic', cascade='all, delete-orphan')
    registrations = db.relationship('Registration', backref='activity', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'title': self.title,
            'description': self.description,
            'cover_url': self.cover_url,
            'location': self.location,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'registration_start': self.registration_start.isoformat() if self.registration_start else None,
            'registration_end': self.registration_end.isoformat() if self.registration_end else None,
            'max_participants': self.max_participants,
            'current_count': self.current_count,
            'status': self.status,
            'checkin_type': self.checkin_type,
            'created_by': self.created_by,
        }


class ActivitySession(db.Model):
    __tablename__ = 'activity_sessions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.BigInteger, db.ForeignKey('activities.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    max_participants = db.Column(db.Integer, default=0)
    current_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('active', 'full', 'cancelled', name='session_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'max_participants': self.max_participants,
            'current_count': self.current_count,
            'status': self.status,
        }
