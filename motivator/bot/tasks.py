import random
from tempfile import NamedTemporaryFile
from typing import List

from celery.task import Task

from bot.models import SlackUser, MemeTemplate
from bot.trello import *
from bot.slack import client


class ActionReminderTask(Task):
    def run(self, users: List[str], action: str, action_type: int):
        conversation = client.conversations_open(users=users)
        channel_id = conversation['channel']['id']

        template = random.choice(MemeTemplate.objects.all())
        with NamedTemporaryFile() as f:
            template.create_meme(f, action)
            f.flush()
            f.seek(0)
            client.files_upload(file=f.name, channels=channel_id)


class ActionReminderDispatchTask(Task):
    def run(self, action_type, *args, **kwargs):
        endpoint = f'lists/{TRELLO_LISTS[action_type]}/cards'
        cards = trello_api_request(endpoint, {'fields': 'idMembers,name'})
        for card in cards:
            users = list(SlackUser.objects.filter(has_notification_enabled=True, trello_id__in=card['idMembers']).values_list('slack_user_id', flat=True))
            if users:
                ActionReminderTask().apply_async(args=(users, card['name'], action_type))
