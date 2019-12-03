from typing import List

from celery.task import Task

from bot.models import SlackUser
from bot.trello import *
from bot.slack import client


class ActionReminderTask(Task):
    def run(self, users: List[str], action: str, action_type: int):
        conversation = client.conversations_open(users=users)
        channel_id = conversation['channel']['id']
        client.chat_postMessage(channel_id=channel_id, text=action)


class ActionReminderDispatchTask(Task):
    def run(self, action_type, *args, **kwargs):
        endpoint = f'lists/{TRELLO_LISTS[action_type]}/cards'
        cards = trello_api_request(endpoint, {'fields': 'idMembers,name'})
        print(cards)
        for card in cards:
            users = SlackUser.objects.filter(has_notification_enabled=True, trello_id__in=card['idMembers']).values('slack_user_id')
            if users:
                ActionReminderTask().apply_async(users, card['name'], action_type)
