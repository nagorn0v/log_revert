import datetime

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

    def as_dict(self):
        task = {}
        for column in self.__table__.columns:
            column_value = getattr(self, column.name)
            if isinstance(column_value, datetime.datetime):
                task[column.name] = column_value.isoformat()
            else:
                task[column.name] = column_value
        return task
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class List(db.Model):
    __tablename__ = 'lists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    color = db.Column(db.String(128))
    is_archived = db.Column(db.Boolean)

    def __repr__(self):
        return f'<List {self.name}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
