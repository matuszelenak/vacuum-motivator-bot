import dj_database_url

from .base import *

DEBUG = False

PRODUCTION = True

ALLOWED_HOSTS += ['vacuum-motivator-bot.herokuapp.com']

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN')
SLACK_BOT_USER_TOKEN = os.environ.get('SLACK_BOT_USER_TOKEN')
TRELLO_TOKEN = os.environ.get('TRELLO_TOKEN')
TRELLO_KEY = os.environ.get('TRELLO_KEY')
