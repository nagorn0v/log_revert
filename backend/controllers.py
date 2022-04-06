import datetime

from flask import Response, request, jsonify

from app import app, db
from models import List, Task


@app.route('/')
def hello_world():
    return "<p>Hello from flask</p>"


@app.route('/lists', methods=['GET', 'POST'])
def read_create_lists() -> Response:
    if request.method == 'GET':
        lists = List.query.all()
        return jsonify([list.as_dict() for list in lists])
    elif request.method == 'POST':
        data = request.json

        try:  # todo test key error
            list = List(name=data['name'], color=data['color'], is_archived=False)
        except KeyError:
            return '<h1>Bar request</h1>'

        db.session.add(list)

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return '<h1>External server error</h1>'
        else:
            return jsonify(list.as_dict())


@app.route('/lists/<list_id>', methods=['GET', 'PATCH'])
def read_update_list(list_id: int):
    list = List.query.get(list_id)

    if request.method == 'GET':
        if list:  # todo test found
            return jsonify(list.as_dict())
        else:  # todo test not found
            return '<h1>not found</h1>'

    elif request.method == 'PATCH':
        data = request.json
        for key, value in data.items():
            setattr(list, key, value)

        db.session.add(list)

        try:
            db.session.rollback()
            db.session.commit()
        except Exception:
            return '<h1>Internal server error</h1>'
        else:
            return jsonify(list.as_dict())


@app.route('/tasks', methods=['GET', 'POST'])
def read_create_tasks():
    if request.method == 'GET':
        tasks = Task.query.all()
        return jsonify([task.as_dict() for task in tasks])
    elif request.method == 'POST':
        data = request.json

        try:  # todo test key error
            task = Task(title=data['title'], description=data['description'],
                        due_date=datetime.datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M:%S'),
                        list_id=data['list_id'])

        except KeyError:
            return '<h1>bad request</h1>'

        print(task)
        db.session.add(task)

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return '<h1>External server error</h1>'
        else:
            return jsonify(task.as_dict())


@app.route('/tasks/<task_id>', methods=['GET', 'PATCH'])
def read_update_task(task_id: int):
    task = Task.query.get(task_id)
    if request.method == 'GET':
        if task:
            return jsonify(task.as_dict())
        else:
            # todo response not found
            pass
    elif request.method == 'PATCH':
        data = request.json

        for key, value in data.items():
            if key == 'due_date':
                setattr(task, key, datetime.datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M:%S'))
            setattr(task, key, value)

        db.session.add(task)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return '<h1>Internal server error</h1>'
        else:
            return jsonify(task.as_dict())