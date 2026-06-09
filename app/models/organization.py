from app.extensions import db
from datetime import datetime


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True)
    level = db.Column(db.SmallInteger, default=1, comment='1-一级, 2-二级')
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'pending', name='org_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', foreign_keys='Organization.owner_id', backref='owned_orgs')
    members = db.relationship('OrgMember', backref='organization', lazy='dynamic', cascade='all, delete-orphan')
    children = db.relationship('Organization', backref=db.backref('parent', remote_side=[id]))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logo_url': self.logo_url,
            'parent_id': self.parent_id,
            'level': self.level,
            'owner_id': self.owner_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class OrgMember(db.Model):
    __tablename__ = 'org_members'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    org_id = db.Column(db.BigInteger, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.Enum('owner', 'admin', 'member', name='member_role'), default='member')
    status = db.Column(db.Enum('active', 'invited', 'removed', name='member_status'), default='invited')
    invited_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    joined_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('org_id', 'user_id', name='uk_org_user'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'user_id': self.user_id,
            'role': self.role,
            'status': self.status,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
        }
