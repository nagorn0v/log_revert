import datetime
import re

from flask import jsonify, make_response
from werkzeug.exceptions import abort


def format_json_date(json_date):
    try:
        return datetime.datetime.strptime(json_date, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        abort(make_response(jsonify({'message': 'Invalid datetime format'}), 400))


def parse_log(string):
    return re.findall(r'\d\d\d\d-\d\d-\d\d\ \d\d:\d\d:\d\d.\d{6}|\[.*?\]', string)


def update_model(obj, data):
    for field, value in data.items():
        if field in (str(i).split('.')[1] for i in obj.__table__.columns):
            # check if value is datetime
            if re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2,}', str(value)):
                setattr(obj, field, format_json_date(value))
            else:
                setattr(obj, field, value)

    return obj
