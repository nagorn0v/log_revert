from flask import request, jsonify
from app import app, db
from models import List, Task

from utils import format_json_date
from sqlalchemy import exc


@app.route('/')
def hello_world():
    return "<p>Hello from flask</p>"


def update_task_attrs(obj, data):
    for key, value in data.items():
        if key == 'id':
            return jsonify({'message': 'Cannot change id'}), 404
        elif key == 'due_date':
            setattr(obj, key, format_json_date(value))
        else:
            setattr(obj, key, value)


def update_list_attrs(obj, data):
    for key, value in data.items():
        if key == 'id':
            return jsonify({'message': 'Cannot change id'}), 404
        setattr(obj, key, value)


@app.route('/lists', methods=['GET', 'POST'])
def read_create_lists():
    if request.method == 'GET':
        lists = List.query.all()
        return jsonify([list.as_dict() for list in lists])
    elif request.method == 'POST':
        data = request.json

        try:
            list = List(name=data['name'], color=data['color'], is_archived=False)
        except KeyError as e:
            field = str(e).strip("'")
            return jsonify({'message': f'{field} field not found'}), 400

        db.session.add(list)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'message': str(e.__dict__['orig'])}), 400
        else:
            return jsonify(list.as_dict()), 201


@app.route('/lists/<list_id>', methods=['GET', 'PATCH'])
def read_update_list(list_id: int):
    list = List.query.get(list_id)

    if list:
        if request.method == 'GET':
            return jsonify(list.as_dict())

        elif request.method == 'PATCH':
            data = request.json
            update_list_attrs(list, data)

            db.session.add(list)

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({'message': str(e.__dict__['orig'])}), 400
            else:
                return jsonify(list.as_dict())
    else:
        return jsonify({'message': f'List with id {list_id} not found'}), 404




@app.route('/tasks', methods=['GET', 'POST'])
def read_create_tasks():
    if request.method == 'GET':
        tasks = Task.query.all()
        return jsonify([task.as_dict() for task in tasks])
    elif request.method == 'POST':
        data = request.json
        try:
            task = Task(title=data['title'],
                        description=data['description'],
                        due_date=format_json_date(data['due_date']),
                        list_id=data['list_id'])

        except KeyError as e:
            field = str(e).strip("'")
            return jsonify({'message': f'{field} field not found'}), 400

        db.session.add(task)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'message': str(e.__dict__['orig'])}), 400
        else:
            return jsonify(task.as_dict()), 201


@app.route('/tasks/<task_id>', methods=['GET', 'PATCH'])
def read_update_task(task_id: int):
    task = Task.query.get(task_id)
    if task:
        if request.method == 'GET':
            return jsonify(task.as_dict())
        elif request.method == 'PATCH':
            data = request.json
            update_task_attrs(task, data)

            db.session.add(task)

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({'message': str(e.__dict__['orig'])}), 400
            else:
                return jsonify(task.as_dict())
    else:
        return jsonify({'message': f'Task with id {task_id} not found'}), 404


@app.route('/lists/<list_id>/tasks/<task_id>', methods=['PATCH'])
def update_list_task(list_id: int, task_id: int):
    data = request.json

    list = List.query.get(list_id)
    task = Task.query.get(task_id)
    print(list, task)

    if not list:
        return jsonify({'message': f'List with id {list_id} not found'}), 404
    if not task:
        return jsonify({'message': f'Task with id {task_id} not found'}), 404

    update_list_attrs(list, data.get('list'))
    update_task_attrs(task, data.get('task'))

    db.session.add(list)
    db.session.add(task)

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e.__dict__['orig'])}), 400
    else:
        return jsonify([list.as_dict(), task.as_dict()]), 200
