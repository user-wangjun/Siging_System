from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), nullable=True, unique=True, index=True)
    nickname = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    real_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    status = db.Column(db.SmallInteger, default=1, comment='0-禁用, 1-正常')
    role = db.Column(db.Enum('user', 'org_admin', 'platform_admin', name='user_role'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    auths = db.relationship('UserAuth', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    org_memberships = db.relationship('OrgMember', foreign_keys='OrgMember.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'real_name': self.real_name,
            'email': self.email,
            'status': self.status,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class UserAuth(db.Model):
    __tablename__ = 'user_auth'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    auth_type = db.Column(db.Enum('phone', 'wechat', 'email', name='auth_type'), default='email')
    auth_key = db.Column(db.String(100), nullable=False, comment='手机号/openid/邮箱')
    auth_secret = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('auth_type', 'auth_key', name='uk_auth'),
    )
