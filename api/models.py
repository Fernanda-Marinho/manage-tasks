import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = db.Column(db.String(200), nullable=False)
    
    description = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.Enum('PENDING', 'IN_PROGRESS', 'DONE', name='task_status'), nullable=False, default='PENDING')
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=True)
    
    deleted_at = db.Column(db.DateTime, nullable=True) # new column for track soft delete

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(100), unique=True, nullable=False)
    
    tasks = db.relationship('Task', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }