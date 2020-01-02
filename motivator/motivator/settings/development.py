import json

from .base import *

DEBUG = True

PRODUCTION = False

credentials_data = json.load(open('../credentials.json'))

SLACK_VERIFICATION_TOKEN = credentials_data.get('SLACK_VERIFICATION_TOKEN')
SLACK_BOT_USER_TOKEN = credentials_data.get('SLACK_BOT_USER_TOKEN')
TRELLO_TOKEN = credentials_data.get('TRELLO_TOKEN')
TRELLO_KEY = credentials_data.get('TRELLO_KEY')
