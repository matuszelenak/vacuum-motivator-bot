from django.conf import settings
from slack import WebClient

client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)
