import importlib
import json
import os.path

from flask import request, jsonify
from app import app, db
from config import basedir
from models import List, Task

from utils import format_json_date, parse_log, update_model
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


@app.route('/tasks/<task_id>', methods=['GET', 'PATCH', 'DELETE'])
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
        elif request.method == 'DELETE':
            db.session.delete(task)
            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({'message': str(e.__dict__['orig'])}), 400
            else:
                return jsonify({'message': 'file deleted'}), 200
    else:
        return jsonify({'message': f'Task with id {task_id} not found'}), 404


@app.route('/lists/<list_id>/tasks/<task_id>', methods=['POST'])
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


@app.route('/modifications', methods=['POST'])
def make_modifications():
    data = request.get_json()

    for operation, value in data.items():
        for entity in value:
            try:
                model = getattr(importlib.import_module('models'), entity['model_name'])
                if operation == 'create':
                    updated_model = update_model(model(), entity)
                    db.session.add(updated_model)
                elif operation == 'update' or operation == 'delete':
                    instance = model.query.get(entity['model_id'])
                    if operation == 'update':
                        update_model(instance, entity)
                        db.session.add(instance)
                    else:
                        db.session.delete(instance)
            except KeyError as e:
                return jsonify({'message': f'{e}'}), 400
            except exc.SQLAlchemyError as e:
                return jsonify({'message': str(e.__dict__.get('orig', 'DB error'))}), 400
    else:
        db.session.commit()

    return jsonify({'message': 'Successful modification'}), 200


@app.route('/actions', methods=['GET'])
def get_user_changes():
    user_id = request.headers['x-user-id']
    filename = os.path.join(basedir, 'logs', f'{user_id}.log')

    try:
        with open(filename, 'r') as f:
            actions = []
            for i, line in enumerate(f, 1):
                log = parse_log(line)
                print(json.loads(log[1]))
                actions.append({'id': i, 'timestamp': log[0], 'action': json.loads(log[1])})
    except FileNotFoundError:
        return jsonify([]), 200
    else:
        return jsonify(actions), 200


@app.route('/actions/undo', methods=['GET'])
def undo_user_changes():
    user_id = request.headers['x-user-id']
    filename = os.path.join(basedir, 'logs', f'{user_id}.log')

    try:
        file = open(filename)
        lines = file.readlines()
        last_index = len(lines)

        with open(filename, 'r') as fr:
            last_line = fr.readlines()[last_index - 1]
            parsed_line = parse_log(last_line)

            update_models = {}
            for i in json.loads(parsed_line[1]):
                if i['commit_type'] == 'insert':
                    model = getattr(importlib.import_module('models'), i['model_name'])
                    entity = model.query.get(i['id'])
                    db.session.delete(entity)
                    db.session.commit()
                elif i['commit_type'] == 'update':
                    update_models.setdefault(i['model_name'], []).append(i['id'])
                else:
                    model = getattr(importlib.import_module('models'), i['model_name'])()
                    update_model(model, i)
                    db.session.add(model)
                    db.session.commit()

            if update_models:
                fr.seek(0)
                iter_counter = 0
                for i, line in reversed(list(enumerate(fr.readlines()[:last_index - 1], 1))):

                    items_to_remove = {}
                    for j in json.loads(parse_log(line)[1]):
                        if j['model_name'] in update_models.keys() \
                                and j['id'] in update_models[j['model_name']]:
                            items_to_remove.setdefault(j['model_name'], []).append(j['id'])
                            # get model Class
                            model = getattr(importlib.import_module('models'), j['model_name'])
                            # get model instance
                            entity = model.query.get(j['id'])
                            update_model(entity, j)
                            db.session.add(entity)
                            db.session.commit()

                    for r_key, r_value in items_to_remove.items():
                        update_models[r_key] = list(set(update_models[r_key]) - set(r_value))
                    else:
                        update_models = {k: v for k, v in update_models.items() if v}

                        if not update_models:
                            break
                    iter_counter += 1

        # remove extra lines
        with open(filename, 'w') as fw:
            for i, line in enumerate(lines):
                if i < last_index - 1:
                    fw.write(line)
            else:
                file.close()

    except exc.SQLAlchemyError as e:
        return jsonify({'message': str(e.__dict__['orig'])}), 500

    except (FileNotFoundError, IndexError):
        return jsonify({'message': 'There are no actions to undo '}), 400
    else:
        return jsonify({'message': 'Successfully undo'}), 200
