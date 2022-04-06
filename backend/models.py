from sqlalchemy.sql import expression

from app import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'))

    def __repr__(self):
        return f'<Task {self.title}>'


class List(db.Model):
    __tablename__ = 'lists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    color = db.Column(db.String(128))
    is_archived = db.Column(db.Boolean)
    task = db.relationship('Task')
