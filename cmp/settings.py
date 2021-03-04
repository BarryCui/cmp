import os
from dotenv import load_dotenv
from cmp import app


if os.path.exists('/cmp/env/.env'):
    load_dotenv(dotenv_path='/cmp/env/.env') # load environment variables
elif os.path.exists('/home/vagrant/cmp/cmp/env/.env'):
    load_dotenv(dotenv_path='/home/vagrant/cmp/cmp/env/.env') # load environment variables

#dev_db = 'sqlite:///' + os.path.join(os.path.dirname(app.root_path), 'data.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
#SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', dev_db)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
