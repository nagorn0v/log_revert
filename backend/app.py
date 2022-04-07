import json
import os.path

import flask_sqlalchemy
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, models_committed, before_models_committed

from config import Config, basedir

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from controllers import *
from models import *


@models_committed.connect
def test(app, changes):
    user = request.headers['x-user-id']

    with open(os.path.join(basedir, 'logs', f'{user}.txt'), 'a') as f:
        for i in changes:
            model = {k: v for k, v in i[0].__dict__.items() if k != '_sa_instance_state'}
            f.write(json.dumps(model) + '\n')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
