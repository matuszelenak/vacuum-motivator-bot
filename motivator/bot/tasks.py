from celery.task import Task
from django.db import transaction

from bot.models import SlackUser, TrelloCard, TrelloList
from bot.trello import *
from bot.slack import client


class SyncTrelloBoard(Task):
    @transaction.atomic
    def run(self):
        lists = trello_api_request(f'/boards/{settings.TRELLO_BOARD_ID}/lists/', {'fields': 'id,name'})

        for list_data in lists:
            l, _ = TrelloList.objects.get_or_create(trello_id=list_data['id'])
            l.name = list_data['name']
            l.save()

            cards = trello_api_request(f'lists/{list_data["id"]}/cards', {'fields': 'id,idMembers,name'})

            for card_data in cards:
                card, _ = TrelloCard.objects.get_or_create(trello_id=card_data['id'], defaults={'list': l})
                card.list = l
                card.name = card_data['name']
                assignees = list(SlackUser.objects.filter(trello_id__in=card_data['idMembers'])) if card_data['idMembers'] else list(SlackUser.objects.all())
                card.assignees.set(assignees)
                card.save()


class ActionReminderDispatchTask(Task):
    def run(self, *args, **kwargs):
        users = SlackUser.objects.filter(has_notification_enabled=True)
        for user in users:
            conversation = client.conversations_open(users=[user.slack_user_id])
            instance = user.generate_meme()
            client.files_upload(file=instance.meme.path, channels=conversation['channel']['id'])
