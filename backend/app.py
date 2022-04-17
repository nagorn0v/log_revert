import os.path

import pathlib
import re

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, models_committed

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db)

pathlib.Path('logs').mkdir(parents=True, exist_ok=True)

from controllers import *
from models import *


@app.before_request
def handle_request():
    """Simple function that check if user has rights for crud operations"""
    x_user_id = request.headers.get('X-USER-ID', None)
    if x_user_id is None:
        return jsonify({'message': 'x-user-id header not provided'}), 403

    try:
        x_user_id = int(x_user_id)
    except TypeError:
        return jsonify({'message': 'Invalid x-user-id format'}), 400
    if int(x_user_id) not in (0, 1):
        return jsonify({'message': 'Invalid x-user-id'}), 401


@models_committed.connect
def write_log(app, changes):
    # preventing execute for test cases
    if request:

        user = request.headers['x-user-id']
        filename = os.path.join(basedir, 'logs', f'{user}.log')

        # check if file for user exists
        if os.path.exists(filename):
            open_flag = 'a'
        else:
            open_flag = 'w'

        with open(filename, open_flag) as f:
            log = str(datetime.datetime.now())
            models = []
            for i in changes:
                model = {}
                for key, value in i[0].__dict__.items():
                    if key != '_sa_instance_state':
                        if isinstance(value, datetime.datetime):
                            model[key] = value.isoformat()
                        else:
                            model[key] = value
                else:
                    model['commit_type'] = i[1]
                    model['model_name'] = re.search(r"(?<=\.)(.*?)(?=\')", str(type(i[0]))).group()
                models.append(model)
            log = log + ' ' + json.dumps(models, default=str, sort_keys=True)
            f.write(log + '\n')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
