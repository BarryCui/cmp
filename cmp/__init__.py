from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from celery import Celery

app = Flask('cmp')
app.config.from_pyfile('settings.py')
#app.jinja_env.trim_blocks = True
#app.jinja_env.lstrip_blocks = True

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

from cmp import views, errors, commands
