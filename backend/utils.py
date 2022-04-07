import datetime

from flask import jsonify, make_response
from werkzeug.exceptions import abort


def format_json_date(json_date):
    try:
        return datetime.datetime.strptime(json_date, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        abort(make_response(jsonify({'message': 'Invalid datetime format'}), 400))
